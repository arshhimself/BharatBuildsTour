import hashlib
from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.commerce.models import CheckoutSession, Order, OrderItem
from app.modules.identity.models import Business, Buyer

router = APIRouter(tags=["checkout"])


def _rupees(paise: int) -> str:
    return f"₹{paise / 100:,.2f}"


@router.get("/pay/{token}", response_class=HTMLResponse)
async def view_checkout(token: str, request: Request, db: Session = Depends(get_db)):
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    checkout_session = db.scalar(
        select(CheckoutSession).where(CheckoutSession.token_hash == token_hash)
    )
    if not checkout_session:
        raise HTTPException(status_code=404, detail="Checkout session not found.")

    order = db.scalar(select(Order).where(Order.id == checkout_session.order_id))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    business = db.scalar(select(Business).where(Business.id == order.business_id))
    buyer = db.scalar(select(Buyer).where(Buyer.id == order.buyer_id))

    order_items = db.scalars(select(OrderItem).where(OrderItem.order_id == order.id)).all()

    total_paise = sum(item.unit_price_paise * int(item.quantity) for item in order_items)

    if checkout_session.status == "completed":
        return HTMLResponse(
            content=f"""
        <html><head><meta name="viewport" content="width=device-width, initial-scale=1">
        <script src="https://cdn.tailwindcss.com"></script></head>
        <body class="bg-gray-50 flex items-center justify-center min-h-screen font-sans">
        <div class="bg-white p-8 rounded-2xl shadow-md max-w-md w-full text-center border border-gray-100">
            <div class="text-indigo-500 mb-6 flex justify-center">
                <svg class="w-20 h-20" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            </div>
            <h1 class="text-3xl font-bold text-gray-800 mb-2">Payment Successful</h1>
            <p class="text-gray-500 mb-8">Thank you, {buyer.display_name or "Customer"}! Your order has been placed.</p>

            <div class="bg-gray-50 rounded-xl p-4 mb-6 text-left">
                <p class="text-sm text-gray-500 mb-1">Order Number</p>
                <p class="font-semibold text-gray-800 mb-4">#{str(order.id)[:8]}</p>
                <p class="text-sm text-gray-500 mb-1">Amount Paid</p>
                <p class="font-semibold text-indigo-600 text-xl">{_rupees(total_paise)}</p>
            </div>

            <div class="text-left">
                <h3 class="font-semibold text-gray-700 mb-2">Delivery To:</h3>
                <p class="text-gray-600 text-sm">{order.delivery_address.get("address_line", "")}</p>
                <p class="text-gray-600 text-sm">{order.delivery_address.get("city", "")} {order.delivery_address.get("pincode", "")}</p>
            </div>
        </div>
        </body></html>
        """
        )

    if checkout_session.expires_at < datetime.now(UTC):
        checkout_session.status = "expired"
        db.commit()
        raise HTTPException(status_code=400, detail="Checkout link expired.")

    if checkout_session.status == "expired":
        raise HTTPException(status_code=400, detail="Checkout link expired.")

    items_html = ""
    for item in order_items:
        items_html += f"""
        <div class="flex justify-between items-center py-3 border-b border-gray-100 last:border-0">
            <div>
                <p class="font-medium text-gray-800">{item.name_snapshot}</p>
                <p class="text-sm text-gray-500">Qty: {item.quantity}</p>
            </div>
            <p class="font-semibold text-gray-800">{_rupees(item.unit_price_paise * int(item.quantity))}</p>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Checkout - {business.display_name}</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-50 min-h-screen text-gray-800 font-sans">
        <div class="max-w-md mx-auto bg-white min-h-screen shadow-sm md:my-8 md:min-h-fit md:rounded-xl md:shadow-lg overflow-hidden flex flex-col">
            <div class="bg-indigo-600 p-6 text-white text-center rounded-b-3xl shadow-md z-10 relative">
                <span class="absolute top-4 right-4 bg-yellow-400 text-yellow-900 text-xs font-bold px-2 py-1 rounded shadow-sm tracking-wide">TEST PAYMENT</span>
                <h1 class="text-2xl font-bold mt-2">{business.display_name}</h1>
                <p class="text-indigo-100 text-sm mt-1">Order #{str(order.id)[:8]}</p>
            </div>

            <div class="p-6 flex-1 -mt-4 pt-8 bg-gray-50 rounded-t-3xl relative z-0">
                <div class="bg-white rounded-xl shadow-sm p-4 mb-6 border border-gray-100">
                    <h2 class="text-sm uppercase tracking-wider text-gray-400 font-semibold mb-3">Order Summary</h2>
                    {items_html}

                    <div class="flex justify-between items-center mt-4 pt-4 border-t border-gray-200">
                        <span class="font-bold text-gray-800">Total</span>
                        <span class="font-bold text-2xl text-indigo-600">{_rupees(total_paise)}</span>
                    </div>
                </div>

                <div class="bg-white rounded-xl shadow-sm p-4 mb-6 border border-gray-100">
                    <h2 class="text-sm uppercase tracking-wider text-gray-400 font-semibold mb-3">Delivery Details</h2>
                    <p class="text-gray-800 font-medium">{buyer.display_name or "Customer"}</p>
                    <p class="text-gray-600 text-sm mt-1">{order.delivery_address.get("address_line", "")}</p>
                    <p class="text-gray-600 text-sm">{order.delivery_address.get("city", "")} {order.delivery_address.get("pincode", "")}</p>
                </div>
            </div>

            <div class="p-6 bg-white border-t border-gray-100">
                <form method="POST" action="/api/pay/test/{token}">
                    <button type="submit" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-4 rounded-xl shadow-md transition duration-200 flex items-center justify-center space-x-2">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
                        </svg>
                        <span>Complete Test Payment</span>
                    </button>
                </form>
                <p class="text-center text-xs text-gray-400 mt-4">
                    This is a demo environment. No real money will be charged.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@router.post("/api/pay/test/{token}")
async def process_test_payment(
    token: str, request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

    # 1. Fetch Session with lock
    checkout_session = db.scalar(
        select(CheckoutSession).where(CheckoutSession.token_hash == token_hash).with_for_update()
    )

    if not checkout_session:
        raise HTTPException(status_code=404, detail="Checkout session not found.")

    if checkout_session.status == "completed":
        return RedirectResponse(url=f"/pay/{token}", status_code=303)

    if checkout_session.expires_at < datetime.now(UTC):
        checkout_session.status = "expired"
        db.commit()
        raise HTTPException(status_code=400, detail="Checkout link expired.")

    if checkout_session.status == "expired":
        raise HTTPException(status_code=400, detail="Checkout link expired.")

    # 2. Fetch Order with lock
    order = db.scalar(select(Order).where(Order.id == checkout_session.order_id).with_for_update())
    if not order or order.status != "pending_payment":
        raise HTTPException(status_code=400, detail="Order is not pending payment.")

    business_id = checkout_session.business_id

    # 3. Mark CheckoutSession completed
    checkout_session.status = "completed"
    checkout_session.completed_at = datetime.now(UTC)

    # 4. Mark Order PAID
    order.status = "processing"

    # 5. Promote Buyer
    buyer = db.scalar(select(Buyer).where(Buyer.id == order.buyer_id).with_for_update())
    if buyer:
        buyer.is_customer = True

    db.commit()

    # Fire off async task to send WhatsApp message and generate Invoice
    background_tasks.add_task(
        handle_successful_payment_async,
        business_id=business_id,
        order_id=order.id,
        buyer_id=buyer.id,
    )

    return RedirectResponse(url=f"/pay/{token}", status_code=303)


async def handle_successful_payment_async(business_id: UUID, order_id: UUID, buyer_id: UUID):
    from pathlib import Path

    from app.core.config import get_settings
    from app.db.session import SessionLocal
    from app.modules.invoices.service import InvoiceDraft, generate_invoice_pdf_artifact
    from app.modules.whatsapp.client import send_message, send_text_message

    with SessionLocal() as db:
        order = db.scalar(select(Order).where(Order.id == order_id))
        buyer = db.scalar(select(Buyer).where(Buyer.id == buyer_id))
        order_items = db.scalars(select(OrderItem).where(OrderItem.order_id == order_id)).all()

        # 1. Send immediate confirmation WhatsApp message
        message_text = f"Payment received ✅\nOrder #{str(order.id)[:8]} placed successfully.\n\nAapki invoice generate ho rahi hai."

    if buyer and buyer.whatsapp_e164:
        await send_text_message(to=buyer.whatsapp_e164, text=message_text)

    with SessionLocal() as db:
        total_paise = sum(item.unit_price_paise * int(item.quantity) for item in order_items)

        # 2. Generate Invoice
        line_items = [
            {
                "name": item.name_snapshot,
                "quantity": item.quantity,
                "unit": "pcs",
                "unit_price_paise": item.unit_price_paise,
                "line_total_paise": item.unit_price_paise * int(item.quantity),
                "tax_paise": 0,
            }
            for item in order_items
        ]

        draft = InvoiceDraft(
            invoice_number=f"INV-TEST-{str(order.id)[:8].upper()}",
            run_id=str(order.id),
            buyer_name=buyer.display_name or "Customer",
            total_paise=total_paise,
            issued_at=datetime.now(UTC),
            line_items=line_items,
            payment_reference="TEST_PAYMENT",
        )

        settings = get_settings()
        artifact_root = Path(settings.invoice_artifact_root)
        invoice_artifact = generate_invoice_pdf_artifact(draft, artifact_root)

        # 3. Send WhatsApp Invoice
        pdf_url = f"{settings.public_artifact_base_url}/{invoice_artifact.artifact_key}"

    if buyer and buyer.whatsapp_e164:
        await send_message(
            to=buyer.whatsapp_e164,
            message_type="document",
            link=pdf_url,
            caption="Yeh rahi aapki order invoice. Thank you for shopping with us! 🛍️",
            filename=f"Invoice_{draft.invoice_number}.pdf",
        )
