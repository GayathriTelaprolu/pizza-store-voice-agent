from dataclasses import dataclass, field
from typing import List, Dict
import time

# ── Data classes ───────────────────────────────────────────────────────────────

@dataclass
class OrderItem:
    name: str
    price: float
    qty: int = 1
    note: str = ""


@dataclass
class Session:
    call_sid: str
    state: str = "greeting"        # greeting | get_name | get_type | get_address | ordering | confirm | done
    customer_name: str = ""
    customer_phone: str = ""
    order_type: str = ""           # Pickup | Delivery
    delivery_address: str = ""
    order: List[OrderItem] = field(default_factory=list)
    conversation_history: List[Dict] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)


# ── In-memory stores ────────────────────────────────────────────────────────────

_sessions: Dict[str, Session] = {}
pending_confirmations: Dict[str, str] = {}  # phone → call_sid


# ── Session CRUD ────────────────────────────────────────────────────────────────

def get_session(call_sid: str) -> Session:
    if call_sid not in _sessions:
        _sessions[call_sid] = Session(call_sid=call_sid)
    return _sessions[call_sid]


def delete_session(call_sid: str):
    _sessions.pop(call_sid, None)


# ── Order helpers ───────────────────────────────────────────────────────────────

def add_order_item(session: Session, name: str, price: float, qty: int = 1, note: str = ""):
    for item in session.order:
        if item.name == name:
            item.qty += qty
            return
    session.order.append(OrderItem(name=name, price=price, qty=qty, note=note))


def get_subtotal(session: Session) -> float:
    return sum(i.price * i.qty for i in session.order)


def get_tax(session: Session) -> float:
    return get_subtotal(session) * 0.0625


def get_total(session: Session) -> float:
    return get_subtotal(session) + get_tax(session)


def get_order_summary_text(session: Session) -> str:
    if not session.order:
        return "No items yet."
    lines = [f"{i.qty}x {i.name} - ${i.price * i.qty:.2f}" for i in session.order]
    lines += [
        f"Subtotal: ${get_subtotal(session):.2f}",
        f"Tax (6.25%): ${get_tax(session):.2f}",
        f"Total: ${get_total(session):.2f}",
        f"Type: {session.order_type}",
    ]
    if session.order_type == "Delivery":
        lines.append(f"Address: {session.delivery_address}")
    return "\n".join(lines)
