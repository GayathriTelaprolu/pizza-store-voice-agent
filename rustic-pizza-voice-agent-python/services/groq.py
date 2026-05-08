import os
import json
from groq import Groq
from utils.menu import get_menu_text
from utils.session import Session

client = Groq(api_key=os.getenv('GROQ_API_KEY'))

JSON_FORMAT = '{"speech": "what you say out loud", "action": "continue or collect_name or collect_type or collect_address or add_items or order_done or hangup or repeat", "items": [{"name": "EXACT menu item name", "price": 17.50, "qty": 1, "note": ""}], "order_type": "Pickup or Delivery or empty", "customer_name": "name or empty", "delivery_address": "address or empty"}'

SYSTEM_PROMPT = f"""You are a friendly phone order agent for Rustic Pizza, 21 South Main Street, Sherborn MA. Phone: 508-655-6900. Keep responses SHORT - 1 to 3 sentences only. This is a voice call.

{get_menu_text()}

RULES:
- Be polite and warm
- Keep responses very short for voice
- Confirm items when customer orders
- Ask for delivery address if delivery
- Minimum delivery order is 15 dollars
- When customer says done, read back full order with total

CRITICAL: Every time the customer mentions ANY food item, you MUST include it in the items array with the EXACT name from the menu and the EXACT price. Never leave items empty if food was ordered.

Always respond with ONLY valid JSON, no extra text, no markdown:
{JSON_FORMAT}

IMPORTANT RULES FOR JSON:
- When customer orders food: action must be add_items AND items array must have ALL ordered items with correct prices
- When customer says done or wants to checkout: action must be order_done AND items array must have ALL ordered items again
- When customer confirms order: action must be hangup AND items array must have ALL ordered items again
- Never send empty items array if food was mentioned in the entire conversation
- Use exact menu item names and exact prices from the menu above
- For order_done and hangup actions, always repeat ALL items from the entire conversation"""


def get_greeting():
    return {
        'speech': 'Hello! Thank you for calling Rustic Pizza in Sherborn! I am your order agent. May I have your name please?',
        'action': 'collect_name',
        'items': [],
        'order_type': '',
        'customer_name': '',
        'delivery_address': '',
    }


def get_agent_response(session, user_speech):
    session.conversation_history.append({
        'role': 'user',
        'content': user_speech
    })

    if len(session.conversation_history) > 20:
        session.conversation_history = session.conversation_history[-20:]

    try:
        response = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            max_tokens=500,
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                *session.conversation_history,
            ],
        )

        raw_text = response.choices[0].message.content.strip()
        raw_text = raw_text.replace('```json', '').replace('```', '').strip()

        parsed = json.loads(raw_text)

        session.conversation_history.append({
            'role': 'assistant',
            'content': raw_text
        })

        return parsed

    except json.JSONDecodeError as e:
        print(f'JSON parse error: {e}')
        return _fallback()

    except Exception as e:
        print(f'Groq API error: {e}')
        return _fallback()


def _fallback():
    return {
        'speech': 'I am sorry, I did not catch that. Could you please repeat?',
        'action': 'repeat',
        'items': [],
        'order_type': '',
        'customer_name': '',
        'delivery_address': '',
    }