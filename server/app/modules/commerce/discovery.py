"""Deterministic interpretation of customer catalog discovery messages."""

import re
import unicodedata
from dataclasses import dataclass
from enum import StrEnum


class DiscoveryKind(StrEnum):
    CHAT = "chat"
    BROWSE = "browse"
    SEARCH = "search"
    PRICE_FILTER = "price_filter"
    SELECT_REFERENCE = "select_reference"
    INVENTORY = "inventory"


@dataclass(frozen=True)
class DiscoveryRequest:
    kind: DiscoveryKind
    query: str | None = None
    min_price_paise: int | None = None
    max_price_paise: int | None = None
    reference_index: int | None = None


_TOKEN_RE = re.compile(r"[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)?|[\u0900-\u097f]+")
_BROWSE_WORDS = {
    "catalog",
    "bechte",
    "catalogue",
    "item",
    "items",
    "option",
    "options",
    "product",
    "products",
    "sell",
    "selling",
    "बेचते",
    "प्रोडक्ट",
    "प्रोडक्ट्स",
    "सामान",
}
_REQUEST_WORDS = {
    "aap",
    "aapke",
    "aapka",
    "acha",
    "available",
    "bata",
    "batao",
    "bechte",
    "chahiye",
    "dikha",
    "dikhao",
    "do",
    "hai",
    "hain",
    "have",
    "ho",
    "i",
    "jaanna",
    "janna",
    "ka",
    "ke",
    "ki",
    "ko",
    "kuch",
    "kya",
    "main",
    "me",
    "mein",
    "mujhe",
    "please",
    "show",
    "the",
    "to",
    "what",
    "wala",
    "wali",
    "you",
    "आप",
    "आपके",
    "क्या",
    "कुछ",
    "दिखाओ",
    "बताओ",
    "मुझे",
    "है",
    "हैं",
}
_PRICE_WORDS = {
    "andar",
    "below",
    "beech",
    "between",
    "budget",
    "cheap",
    "cheaper",
    "kam",
    "less",
    "range",
    "sasta",
    "saste",
    "se",
    "tak",
    "to",
    "under",
}
_INVENTORY_WORDS = {"availability", "available", "inventory", "stock"}
_REFERENCE_WORDS = {"iska", "iski", "iske", "this", "that", "ye", "woh"}
_PAYMENT_WORDS = {"paid", "payment", "pay"}
_GREETING_WORDS = {"hello", "hey", "hi", "hii", "namaste", "salaam"}
_ORDINALS = {
    "first": 0,
    "pehla": 0,
    "pehli": 0,
    "1st": 0,
    "second": 1,
    "dusra": 1,
    "dusri": 1,
    "doosra": 1,
    "doosri": 1,
    "2nd": 1,
    "third": 2,
    "teesra": 2,
    "teesri": 2,
    "3rd": 2,
}
_QUERY_SYNONYMS = {
    "light": "led",
    "lights": "led",
}


def _tokens(text: str) -> list[str]:
    normalized = unicodedata.normalize("NFKC", text).casefold()
    return _TOKEN_RE.findall(normalized)


def _clean_query(tokens: list[str]) -> str:
    ignored = _REQUEST_WORDS | _BROWSE_WORDS | _PRICE_WORDS | _INVENTORY_WORDS
    cleaned = [_QUERY_SYNONYMS.get(token, token) for token in tokens if token not in ignored]
    return " ".join(cleaned).strip()


def _money_values(tokens: list[str]) -> list[int]:
    values: list[int] = []
    for token in tokens:
        try:
            rupees = float(token.replace(",", ""))
        except ValueError:
            continue
        if 0 < rupees < 100_000_000:
            values.append(round(rupees * 100))
    return values


def interpret_discovery_message(text: str) -> DiscoveryRequest:
    """Classify discovery intent and derive safe arguments from this turn only."""
    tokens = _tokens(text)
    token_set = set(tokens)
    if not tokens:
        return DiscoveryRequest(DiscoveryKind.CHAT)

    if token_set & _PAYMENT_WORDS:
        return DiscoveryRequest(DiscoveryKind.CHAT)

    for token, index in _ORDINALS.items():
        if token in token_set:
            return DiscoveryRequest(DiscoveryKind.SELECT_REFERENCE, reference_index=index)
    if "last" in token_set or "aakhri" in token_set:
        return DiscoveryRequest(DiscoveryKind.SELECT_REFERENCE, reference_index=-1)

    values = _money_values(tokens)
    has_price_language = bool(token_set & _PRICE_WORDS)
    if has_price_language:
        if len(values) >= 2 and token_set & {"between", "beech", "se"}:
            low, high = sorted(values[:2])
            return DiscoveryRequest(
                DiscoveryKind.PRICE_FILTER,
                min_price_paise=low,
                max_price_paise=high,
            )
        if values:
            return DiscoveryRequest(DiscoveryKind.PRICE_FILTER, max_price_paise=values[0])
        if token_set & {"cheap", "cheaper", "sasta", "saste", "kam"}:
            return DiscoveryRequest(DiscoveryKind.PRICE_FILTER)

    query = _clean_query(tokens)
    has_inventory_language = bool(token_set & _INVENTORY_WORDS)
    has_reference_language = bool(token_set & _REFERENCE_WORDS)
    if has_inventory_language and (has_reference_language or not query):
        return DiscoveryRequest(DiscoveryKind.INVENTORY)

    if token_set <= _GREETING_WORDS:
        return DiscoveryRequest(DiscoveryKind.CHAT)

    if token_set & _BROWSE_WORDS and not query:
        return DiscoveryRequest(DiscoveryKind.BROWSE)

    if query:
        return DiscoveryRequest(DiscoveryKind.SEARCH, query=query)

    return DiscoveryRequest(DiscoveryKind.CHAT)
