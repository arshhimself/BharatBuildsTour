"""Demo Checkout and Authoritative Test Payment Routes."""

import hashlib
import logging
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import transaction_session
from app.modules.commerce.lifecycle import mark_order_paid_from_verified_payment
from app.modules.commerce.models import CheckoutSession, Order, OrderItem
from app.modules.identity.models import Business, Buyer, StoreProfile
from app.modules.invoices.models import Invoice
from app.modules.invoices.pdf import render_invoice_pdf
from app.modules.invoices.service import _allocate_number
from app.modules.payments.models import Payment
from app.modules.whatsapp.service import send_whatsapp_media, send_whatsapp_message

logger = logging.getLogger(__name__)

router = APIRouter(tags=["checkout"])


def get_db():
    with transaction_session() as session:
        yield session


def get_public_base_url() -> str:
    from app.core.config import get_settings

    settings = get_settings()
    if settings.public_artifact_base_url and not settings.public_artifact_base_url.startswith(
        "http://localhost"
    ):
        url = settings.public_artifact_base_url.rstrip("/")
        if url.endswith("/artifacts"):
            url = url[:-10]
        return url
    for origin in settings.cors_origins:
        if origin.startswith("https://") and "localhost" not in origin:
            return origin.rstrip("/")
    return "https://app.stockaware.vaaani.co.in"


def prepare_checkout_session(db: Session, business_id: UUID, order_id: UUID) -> dict[str, str]:
    """Cryptographically generate a token and record CheckoutSession."""
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    expires_at = datetime.now(UTC) + timedelta(hours=24)

    checkout_session = CheckoutSession(
        business_id=business_id,
        order_id=order_id,
        token_hash=token_hash,
        status="pending",
        expires_at=expires_at,
    )
    db.add(checkout_session)
    db.flush()

    base_url = get_public_base_url()
    return {
        "raw_token": raw_token,
        "payment_url": f"{base_url}/pay/{raw_token}",
        "expires_at": expires_at.isoformat(),
        "checkout_session_id": str(checkout_session.id),
    }


@router.get("/pay/{token}", response_class=HTMLResponse)
def get_checkout_page(token: str, db: Session = Depends(get_db)):
    """Render mobile-first demo checkout page."""
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    session_rec = db.scalar(select(CheckoutSession).where(CheckoutSession.token_hash == token_hash))

    if not session_rec:
        return HTMLResponse(
            "<html><body style='font-family:sans-serif;text-align:center;padding:50px;'><h2>Invalid Payment Link</h2><p>This checkout link is not valid.</p></body></html>",
            status_code=404,
        )

    if session_rec.status == "completed":
        return HTMLResponse(
            f"<html><body style='font-family:sans-serif;text-align:center;padding:50px;'><h2 style='color:green;'>Payment Completed ✅</h2><p>Order #{session_rec.order_id} has already been paid.</p></body></html>"
        )

    now = datetime.now(UTC)
    if session_rec.expires_at < now or session_rec.status == "expired":
        return HTMLResponse(
            "<html><body style='font-family:sans-serif;text-align:center;padding:50px;'><h2 style='color:red;'>Link Expired</h2><p>This payment link has expired.</p></body></html>",
            status_code=400,
        )

    order = db.scalar(select(Order).where(Order.id == session_rec.order_id))
    business = db.scalar(select(Business).where(Business.id == session_rec.business_id))

    items = db.scalars(select(OrderItem).where(OrderItem.order_id == order.id)).all()

    total_paise = sum(item.unit_price_paise * item.quantity for item in items)
    total_rupees = total_paise / 100.0

    store_name = business.display_name if business else "Demo Store"

    items_html = ""
    for item in items:
        price = item.unit_price_paise / 100.0
        variant_desc = f" ({item.size_snapshot})" if item.size_snapshot else ""
        items_html += f"""
        <div style="display:flex;justify-content:space-between;padding:12px 0;border-bottom:1px solid #eee;">
            <div>
                <strong>{item.name_snapshot}{variant_desc}</strong>
                <div style="font-size:0.85em;color:#666;">Qty: {item.quantity} × ₹{price:.2f}</div>
            </div>
            <div style="font-weight:600;">₹{price * item.quantity:.2f}</div>
        </div>
        """

    address_str = "Standard Delivery"
    if order.delivery_address and isinstance(order.delivery_address, dict):
        street = order.delivery_address.get("street", "")
        city = order.delivery_address.get("city", "")
        address_str = f"{street}, {city}".strip(", ")

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{store_name} - Demo Payment</title>
        <style>
            * {{ box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
            body {{ background-color: #f4f6f8; margin: 0; padding: 20px; display: flex; justify-content: center; }}
            .card {{ background: #ffffff; max-width: 440px; width: 100%; border-radius: 16px; padding: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); }}
            .badge {{ background: #fff3cd; color: #856404; padding: 6px 12px; border-radius: 20px; font-size: 0.8em; font-weight: bold; text-align: center; margin-bottom: 16px; }}
            .header {{ text-align: center; margin-bottom: 20px; }}
            .header h1 {{ margin: 0; font-size: 1.4em; color: #1a1a1a; }}
            .total-box {{ background: #f8f9fa; padding: 16px; border-radius: 12px; text-align: center; margin: 20px 0; }}
            .total-amount {{ font-size: 2em; font-weight: 700; color: #0f172a; margin-top: 4px; }}
            .btn {{ background: #2563eb; color: #ffffff; border: none; width: 100%; padding: 16px; border-radius: 12px; font-size: 1.1em; font-weight: 600; cursor: pointer; transition: background 0.2s; }}
            .btn:hover {{ background: #1d4ed8; }}
            .footer {{ text-align: center; margin-top: 16px; font-size: 0.8em; color: #94a3b8; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="badge">TEST PAYMENT DEMO</div>
            <div class="header">
                <h1>{store_name}</h1>
                <p style="color:#64748b;margin:4px 0 0 0;font-size:0.9em;">Order #{str(order.id)[:8]}</p>
            </div>

            <div style="margin-bottom:16px;">
                <div style="font-size:0.85em;color:#64748b;margin-bottom:4px;">Delivery To</div>
                <div style="font-weight:500;color:#334155;">{address_str}</div>
            </div>

            <div style="margin-top:20px;">
                {items_html}
            </div>

            <div class="total-box">
                <div style="font-size:0.85em;color:#64748b;">Total Amount Due</div>
                <div class="total-amount">₹{total_rupees:.2f}</div>
            </div>

            <button class="btn" onclick="payNow()">Pay Now (Test Mode)</button>

            <div class="footer">
                Powered by StockAware Commerce System
            </div>
        </div>

        <script>
            function payNow() {{
                const btn = document.querySelector('.btn');
                btn.disabled = true;
                btn.innerText = 'Processing Payment...';
                fetch('/api/pay/test/{token}', {{ method: 'POST' }})
                    .then(r => r.json())
                    .then(data => {{
                        if (data.status === 'success' || data.status === 'already_paid') {{
                            document.body.innerHTML = `
                                <div class="card" style="text-align:center;padding:40px 20px;">
                                    <div style="font-size:3em;margin-bottom:12px;">✅</div>
                                    <h2 style="color:#0f172a;margin:0;">Payment Successful!</h2>
                                    <p style="color:#64748b;">Your order #${{data.order_id.slice(0,8)}} is confirmed. Check WhatsApp for your invoice!</p>
                                </div>
                            `;
                        }} else {{
                            alert('Payment failed: ' + (data.error || 'Unknown error'));
                            btn.disabled = false;
                            btn.innerText = 'Pay Now (Test Mode)';
                        }}
                    }})
                    .catch(err => {{
                        alert('Network error during payment.');
                        btn.disabled = false;
                        btn.innerText = 'Pay Now (Test Mode)';
                    }});
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(html_content)


@router.post("/api/pay/test/{token}")
def process_test_payment(token: str, db: Session = Depends(get_db)):
    """Authoritative test payment completion endpoint."""
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    # 1. Lock checkout session row
    session_rec = db.scalar(
        select(CheckoutSession).where(CheckoutSession.token_hash == token_hash).with_for_update()
    )

    if not session_rec:
        raise HTTPException(status_code=404, detail="Checkout session not found")

    if session_rec.status == "completed":
        existing_inv = db.scalar(
            select(Invoice).where(
                Invoice.business_id == session_rec.business_id,
                Invoice.order_id == session_rec.order_id,
            )
        )
        inv_num = (
            existing_inv.invoice_number
            if existing_inv
            else f"INV-{str(session_rec.order_id)[:8].upper()}"
        )
        return {
            "status": "already_paid",
            "order_id": str(session_rec.order_id),
            "invoice_number": inv_num,
        }

    now = datetime.now(UTC)
    if session_rec.expires_at < now or session_rec.status == "expired":
        session_rec.status = "expired"
        db.flush()
        raise HTTPException(status_code=400, detail="Checkout session expired")

    # Load Order & server-side derived amounts
    order = db.scalar(
        select(Order)
        .where(Order.business_id == session_rec.business_id, Order.id == session_rec.order_id)
        .with_for_update()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    business = db.scalar(select(Business).where(Business.id == session_rec.business_id))
    profile = db.scalar(
        select(StoreProfile).where(StoreProfile.business_id == session_rec.business_id)
    )
    buyer = db.scalar(select(Buyer).where(Buyer.id == order.buyer_id))

    items = db.scalars(select(OrderItem).where(OrderItem.order_id == order.id)).all()
    total_paise = sum(item.unit_price_paise * item.quantity for item in items)
    if total_paise <= 0:
        raise HTTPException(status_code=400, detail="Invalid order total amount")

    # 2. Persist authoritative Payment record using existing Payment model conventions
    payment = db.scalar(
        select(Payment).where(
            Payment.business_id == session_rec.business_id,
            Payment.order_id == session_rec.order_id,
        )
    )
    if not payment:
        ref_id = f"test_ref_{str(session_rec.order_id)[:8]}"
        pay_id = f"test_pay_{str(session_rec.order_id)[:8]}"
        payment = Payment(
            business_id=session_rec.business_id,
            order_id=session_rec.order_id,
            status="PAID",
            amount_paise=total_paise,
            currency="INR",
            provider_account_key="test_demo_account",  # pragma: allowlist secret
            provider_reference_id=ref_id,
            provider_payment_id=pay_id,
            link_expires_at=now + timedelta(hours=24),
            paid_at=now,
        )
        db.add(payment)
        db.flush()

    # 3. Transition Order to PAID
    mark_order_paid_from_verified_payment(
        db, session_rec.business_id, session_rec.order_id, payment.id
    )

    # 4. Promote Buyer to customer
    if buyer:
        buyer.is_customer = True

    # 5. Persist durable Invoice record using existing Invoice & InvoiceSequence models
    invoice = db.scalar(
        select(Invoice).where(
            Invoice.business_id == session_rec.business_id,
            Invoice.order_id == session_rec.order_id,
        )
    )
    if not invoice:
        invoice_number = _allocate_number(db, business, now)
        snapshot = {
            "invoice_number": invoice_number,
            "issued_at": now.isoformat(),
            "seller": {
                "legal_name": business.display_name if business else "Rehbar Clothing",
                "billing_address": profile.address_line
                if profile and profile.address_line
                else "Mumbai, India",
            },
            "buyer": {
                "legal_name": buyer.display_name or buyer.whatsapp_e164 or "Customer"
                if buyer
                else "Customer",
                "billing_address": str(order.delivery_address or "Standard Delivery"),
            },
            "provider_payment_id": payment.provider_payment_id,
            "items": [
                {
                    "sku": item.sku_snapshot or "ITEM",
                    "name": f"{item.name_snapshot}"
                    + (f" ({item.size_snapshot})" if item.size_snapshot else ""),
                    "quantity": str(item.quantity),
                    "taxable_paise": item.unit_price_paise * item.quantity,
                    "tax_paise": 0,
                }
                for item in items
            ],
            "total_paise": total_paise,
        }
        from app.modules.invoices.storage import LocalArtifactStore

        pdf_bytes = render_invoice_pdf(snapshot)
        artifact_sha = hashlib.sha256(pdf_bytes).hexdigest()
        artifact_key = f"{session_rec.business_id}/{session_rec.order_id}.pdf"
        store = LocalArtifactStore()
        store.write(artifact_key, pdf_bytes)

        invoice = Invoice(
            business_id=session_rec.business_id,
            order_id=session_rec.order_id,
            payment_id=payment.id,
            invoice_number=invoice_number,
            status="GENERATED",
            currency="INR",
            total_paise=total_paise,
            snapshot=snapshot,
            artifact_key=artifact_key,
            artifact_sha256=artifact_sha,
            issued_at=now,
            generated_at=now,
        )
        db.add(invoice)

    # 6. Mark CheckoutSession completed
    session_rec.status = "completed"
    session_rec.completed_at = now

    # 7. COMMIT DB TRANSACTION BEFORE ANY NETWORK / WHATSAPP CALLS
    db.commit()

    # 8. POST-COMMIT WHATSAPP MESSAGING (network errors will NOT roll back committed DB state)
    if buyer and buyer.whatsapp_e164:
        try:
            from app.core.config import get_settings

            settings = get_settings()
            base_url = get_public_base_url()
            pdf_url = f"{base_url}/api/invoices/public/{invoice.id}/artifact"
            sending_phone_id = (
                settings.whatsapp_test_phone_number_id or settings.whatsapp_biz_phone_number_id
            )

            text_msg = (
                f"Payment received ✅\n"
                f"Order #{str(order.id)[:8]} confirmed!\n"
                f"Invoice #{invoice.invoice_number} generate ho gaya hai. Below invoice pdf check kar lo 👇"
            )
            send_whatsapp_message(buyer.whatsapp_e164, text_msg, phone_number_id=sending_phone_id)

            send_whatsapp_media(
                to=buyer.whatsapp_e164,
                media_url=pdf_url,
                caption=f"Invoice #{invoice.invoice_number}",
                message_type="document",
                filename=f"Invoice-{invoice.invoice_number}.pdf",
                phone_number_id=sending_phone_id,
            )
        except Exception as exc:
            logger.warning(f"Failed to send post-commit WhatsApp notification: {exc}")

    return {
        "status": "success",
        "order_id": str(session_rec.order_id),
        "invoice_number": invoice.invoice_number,
    }


@router.get("/api/invoices/public/{invoice_id}/artifact")
def get_public_invoice_artifact(invoice_id: UUID, db: Session = Depends(get_db)):
    """Public unauthenticated endpoint to download invoice PDF (for WhatsApp delivery)."""
    from fastapi.responses import FileResponse

    from app.modules.invoices.storage import LocalArtifactStore

    invoice = db.scalar(select(Invoice).where(Invoice.id == invoice_id))
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    store = LocalArtifactStore()
    if invoice.artifact_key:
        try:
            file_path = store.path(invoice.artifact_key)
            if file_path.exists():
                return FileResponse(
                    file_path,
                    media_type="application/pdf",
                    filename=f"Invoice-{invoice.invoice_number}.pdf",
                )
        except ValueError:
            pass

    if invoice.snapshot:
        pdf_bytes = render_invoice_pdf(invoice.snapshot)
        key = f"{invoice.business_id}/{invoice.order_id}.pdf"
        store.write(key, pdf_bytes)
        file_path = store.path(key)
        return FileResponse(
            file_path,
            media_type="application/pdf",
            filename=f"Invoice-{invoice.invoice_number}.pdf",
        )

    raise HTTPException(status_code=404, detail="Invoice artifact not found")
