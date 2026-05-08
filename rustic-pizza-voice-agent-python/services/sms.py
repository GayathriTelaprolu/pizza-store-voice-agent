import os
from twilio.rest import Client
from utils.session import Session, get_subtotal, get_tax, get_total

client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))


def send_sms_confirmation(to_phone: str, session: Session) -> dict:
    """Send order summary SMS asking customer to confirm with YES or NO."""
    lines = [f"{i.qty}x {i.name} - ${i.price * i.qty:.2f}" for i in session.order]
    addr_line = f"\nDeliver to: {session.delivery_address}" if session.order_type == "Delivery" else ""

    message = (
        f"Hi {session.customer_name}! Your Rustic Pizza order:\n\n"
        + "\n".join(lines)
        + f"\n\nSubtotal: ${get_subtotal(session):.2f}\n"
        + f"Tax: ${get_tax(session):.2f}\n"
        + f"Total: ${get_total(session):.2f}\n"
        + f"Type: {session.order_type}{addr_line}\n\n"
        + "Reply YES to confirm or NO to cancel.\n"
        + "- Rustic Pizza 508-655-6900"
    )

    try:
        result = client.messages.create(
            body=message,
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=to_phone,
        )
        print(f"SMS confirmation sent to {to_phone}: {result.sid}")
        return {"success": True, "sid": result.sid}
    except Exception as e:
        print(f"SMS confirmation error: {e}")
        return {"success": False, "error": str(e)}


def send_receipt_sms(to_phone: str, session: Session) -> dict:
    """Send final receipt SMS after customer confirms."""
    from datetime import datetime
    now = datetime.now().strftime("%b %d, %Y %I:%M %p")

    lines = [f"{i.qty}x {i.name} - ${i.price * i.qty:.2f}" for i in session.order]
    addr_line = f"\nDeliver to: {session.delivery_address}" if session.order_type == "Delivery" else ""

    message = (
        f"FINAL RECEIPT - Rustic Pizza\n"
        + f"{now}\n\n"
        + f"Customer: {session.customer_name}\n"
        + f"Type: {session.order_type}{addr_line}\n\n"
        + "\n".join(lines)
        + f"\n\nSubtotal: ${get_subtotal(session):.2f}\n"
        + f"Tax: ${get_tax(session):.2f}\n"
        + f"TOTAL: ${get_total(session):.2f}\n\n"
        + f"Order Confirmed! Thank you, {session.customer_name}!\n"
        + "Rustic Pizza - 21 South Main St, Sherborn MA\n"
        + "508-655-6900"
    )

    try:
        result = client.messages.create(
            body=message,
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=to_phone,
        )
        print(f"Receipt SMS sent to {to_phone}: {result.sid}")
        return {"success": True, "sid": result.sid}
    except Exception as e:
        print(f"Receipt SMS error: {e}")
        return {"success": False, "error": str(e)}
