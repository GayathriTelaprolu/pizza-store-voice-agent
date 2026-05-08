import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from utils.session import Session, get_subtotal, get_tax, get_total


def build_receipt_html(session: Session) -> str:
    """Build a nice HTML receipt email."""
    now = datetime.now().strftime("%B %d, %Y %I:%M %p")
    sub = get_subtotal(session)
    tax = get_tax(session)
    total = get_total(session)

    rows = ""
    for item in session.order:
        note_html = f"<br><small style='color:#666'>{item.note}</small>" if item.note else ""
        rows += f"""
        <tr>
            <td style="padding:8px;border-bottom:1px dashed #eee;">
                {item.qty}x {item.name}{note_html}
            </td>
            <td style="padding:8px;border-bottom:1px dashed #eee;text-align:right;">
                ${item.price * item.qty:.2f}
            </td>
        </tr>"""

    addr_row = ""
    if session.order_type == "Delivery":
        addr_row = f"""
        <tr>
            <td style="padding:8px;"><b>Delivery Address</b></td>
            <td style="padding:8px;text-align:right;">{session.delivery_address}</td>
        </tr>"""

    return f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family:Arial,sans-serif;max-width:500px;margin:0 auto;padding:20px;color:#333;">
        <div style="text-align:center;margin-bottom:20px;">
            <h2 style="margin:0;color:#d32f2f;">Rustic Pizza</h2>
            <p style="margin:4px 0;font-size:13px;color:#666;">21 South Main Street, Sherborn MA | 508-655-6900</p>
            <p style="margin:4px 0;font-size:12px;color:#999;">{now}</p>
        </div>
        <div style="background:#f9f9f9;border-radius:8px;padding:16px;margin-bottom:16px;">
            <p style="margin:2px 0;font-size:13px;"><b>Customer:</b> {session.customer_name}</p>
            <p style="margin:2px 0;font-size:13px;"><b>Phone:</b> {session.customer_phone}</p>
            <p style="margin:2px 0;font-size:13px;"><b>Order Type:</b> {session.order_type}</p>
            {"<p style='margin:2px 0;font-size:13px;'><b>Address:</b> " + session.delivery_address + "</p>" if session.order_type == "Delivery" else ""}
        </div>
        <table style="width:100%;border-collapse:collapse;">
            {rows}
            <tr>
                <td style="padding:8px;border-top:1px solid #eee;">Subtotal</td>
                <td style="padding:8px;border-top:1px solid #eee;text-align:right;">${sub:.2f}</td>
            </tr>
            <tr>
                <td style="padding:8px;">Tax (6.25%)</td>
                <td style="padding:8px;text-align:right;">${tax:.2f}</td>
            </tr>
            <tr style="font-weight:bold;font-size:16px;">
                <td style="padding:8px;border-top:2px solid #333;">TOTAL</td>
                <td style="padding:8px;border-top:2px solid #333;text-align:right;">${total:.2f}</td>
            </tr>
            {addr_row}
        </table>
        <div style="margin-top:20px;padding:12px;background:#e8f5e9;border-radius:8px;text-align:center;">
            <p style="margin:0;color:#2e7d32;font-weight:bold;">Order Confirmed!</p>
            <p style="margin:4px 0;font-size:13px;color:#388e3c;">Thank you, {session.customer_name}!</p>
        </div>
        <p style="text-align:center;font-size:11px;color:#999;margin-top:16px;">
            Rustic Pizza &bull; 21 South Main St, Sherborn MA &bull; 508-655-6900
        </p>
    </body>
    </html>"""


def _send_email(to: str, subject: str, html: str) -> dict:
    """Send email using Gmail SMTP (built into Python, no extra install)."""
    gmail_user = os.getenv("GMAIL_USER")
    gmail_pass = os.getenv("GMAIL_APP_PASSWORD")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Rustic Pizza <{gmail_user}>"
    msg["To"] = to
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_pass)
            server.sendmail(gmail_user, to, msg.as_string())
        print(f"Email sent to {to}")
        return {"success": True}
    except Exception as e:
        print(f"Email error: {e}")
        return {"success": False, "error": str(e)}


def send_receipt_email(to_email: str, session: Session) -> dict:
    """Send receipt to the customer."""
    now = datetime.now().strftime("%b %d, %Y")
    html = build_receipt_html(session)
    return _send_email(to_email, f"Your Rustic Pizza Receipt - {now}", html)


def send_order_to_restaurant(session: Session):
    """Email the order to the restaurant so they see it immediately."""
    restaurant_email = os.getenv("GMAIL_USER")
    now = datetime.now().strftime("%b %d, %Y %I:%M %p")
    html = build_receipt_html(session)
    _send_email(
        restaurant_email,
        f"New Order - {session.customer_name} - {now}",
        html,
    )
