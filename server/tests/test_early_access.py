import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.main import create_app
from app.db.base import Base
from app.db.session import get_db
from app.modules.early_access.models import EarlyAccessLead

from sqlalchemy.pool import StaticPool

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(name="db_session")
def db_session_fixture():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    EarlyAccessLead.__table__.create(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(name="client")
def client_fixture(db_session: Session):
    app = create_app()

    def _get_db_override():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_db_override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_submit_valid_early_access_lead(client: TestClient, db_session: Session):
    payload = {
        "full_name": "Rehbar Khan",
        "business_name": "Zeliora Fashion",
        "phone": "+91 9876543210",
        "email": "rehbar@zeliora.in",
        "business_type": "Retail Apparel",
        "city": "Mumbai",
        "about_business": "We sell women's kurtis and ethnic wear via Instagram and WhatsApp.",
        "daily_whatsapp_orders": "25 enquiries/day",
    }

    response = client.post("/early-access/leads", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["status"] == "new"
    assert "lead_id" in data

    # Verify DB record
    lead = db_session.query(EarlyAccessLead).filter_by(id=data["lead_id"]).first()
    assert lead is not None
    assert lead.full_name == "Rehbar Khan"
    assert lead.business_name == "Zeliora Fashion"
    assert lead.phone == "+919876543210"
    assert lead.email == "rehbar@zeliora.in"
    assert lead.payment_status == "not_started"
    assert lead.status == "new"


def test_duplicate_lead_graceful_response(client: TestClient, db_session: Session):
    payload = {
        "full_name": "Anita Sharma",
        "business_name": "Sharma Electronics",
        "phone": "+91 9812345678",
        "email": "anita@sharmaelec.com",
        "business_type": "Retail Electronics",
        "city": "Pune",
        "about_business": "We sell electronic accessories.",
    }

    resp1 = client.post("/early-access/leads", json=payload)
    assert resp1.status_code == 201

    # Second click / submit
    resp2 = client.post("/early-access/leads", json=payload)
    assert resp2.status_code == 201
    data2 = resp2.json()
    assert data2["success"] is True
    assert "already have your request" in data2["message"]


def test_invalid_lead_validation(client: TestClient):
    # Invalid email
    resp1 = client.post("/early-access/leads", json={
        "full_name": "Test User",
        "business_name": "Test Business",
        "phone": "9876543210",
        "email": "not-an-email",
        "business_type": "Retail",
        "city": "Delhi",
        "about_business": "Test about business details",
    })
    assert resp1.status_code == 422

    # Invalid phone (too short)
    resp2 = client.post("/early-access/leads", json={
        "full_name": "Test User",
        "business_name": "Test Business",
        "phone": "123",
        "email": "test@example.com",
        "business_type": "Retail",
        "city": "Delhi",
        "about_business": "Test about business details",
    })
    assert resp2.status_code == 422


def test_list_early_access_leads_unauthenticated(client: TestClient):
    resp = client.get("/early-access/leads")
    assert resp.status_code == 401


def test_list_early_access_leads_authenticated(client: TestClient):
    from uuid import uuid4
    from app.api.owner_auth import get_current_user
    from app.modules.identity.owner_models import User

    fake_user = User(
        id=uuid4(),
        business_id=uuid4(),
        phone_number="+919999999999",
        name="Admin Test",
    )

    app = client.app
    app.dependency_overrides[get_current_user] = lambda: fake_user
    try:
        resp = client.get("/early-access/leads")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
    finally:
        app.dependency_overrides.pop(get_current_user, None)
