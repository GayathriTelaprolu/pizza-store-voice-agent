from flask import Blueprint, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from utils.session import get_session, delete_session, pending_confirmations
from services.sms import send_receipt_sms
from services.email import send_order_to_restaurant

sms_bp = Blueprint("sms", __name__)


@sms_bp.route("/reply", methods=["POST"])
def reply():
    """
    Twilio calls this endpoint when the customer replies to the confirmation SMS.
    Customer replies YES to confirm or NO to cancel.
    """
    from_phone = request.form.get("From", "")
    body = request.form.get("Body", "").strip().upper()

    print(f"\nSMS reply from {from_phone}: '{body}'")

    twiml = MessagingResponse()

    # Find the active session for this phone number
    call_sid = pending_confirmations.get(from_phone)

    if not call_sid:
        twiml.message(
            "Hi! We don't have an active order for your number. "
            "Please call 508-655-6900 to place an order. Thank you!"
        )
        return Response(str(twiml), mimetype="text/xml")

    session = get_session(call_sid)

    if body in ("YES", "Y", "CONFIRM", "OK", "OKAY"):
        # ── Confirmed ──────────────────────────────────────────────────────────
        send_receipt_sms(from_phone, session)
        send_order_to_restaurant(session)

        # Clean up
        pending_confirmations.pop(from_phone, None)
        delete_session(call_sid)

        twiml.message(
            f"Your order is confirmed, {session.customer_name}! "
            f"We're preparing it now. "
            f"Thank you for choosing Rustic Pizza! See you soon!"
        )

    elif body in ("NO", "N", "CANCEL", "STOP"):
        # ── Cancelled ─────────────────────────────────────────────────────────
        pending_confirmations.pop(from_phone, None)
        delete_session(call_sid)

        twiml.message(
            "Your order has been cancelled. "
            "Please call us at 508-655-6900 to place a new order. Thank you!"
        )

    else:
        # ── Unrecognised reply ────────────────────────────────────────────────
        twiml.message("Please reply YES to confirm your order or NO to cancel.")

    return Response(str(twiml), mimetype="text/xml")
