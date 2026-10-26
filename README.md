# 📞🍕 Pizza Store Voice Agent

An **AI phone ordering agent** for a real pizzeria — Rustic Pizza in Sherborn. Customers call a phone number and talk to the agent naturally: it takes their name, asks pickup or delivery, collects the address, adds menu items to the order, reads back the total, and confirms the order by SMS. Once the customer replies **YES**, they get a text receipt and the restaurant gets the order by email.

Built with **Python (Flask)**, **Twilio Voice & SMS**, and **Groq (Llama 3.3 70B)** as the conversational brain, with the menu loaded live from **Google Sheets**.

> 📘 Detailed, step-by-step setup (Twilio, Groq, Gmail, ngrok, webhooks, troubleshooting) is in [`rustic-pizza-voice-agent-python/README.md`](rustic-pizza-voice-agent-python/README.md).

---

## ✨ Features

- **Natural voice ordering** — Twilio speech-to-text in, Twilio text-to-speech ("Alice") out, with an LLM deciding every reply
- **Structured LLM output** — the model returns strict JSON (`speech`, `action`, `items`, `order_type`, `customer_name`, `delivery_address`) that drives a small state machine, so the agent can actually *do* things, not just talk
- **Menu-grounded ordering** — the full menu with prices is injected into the system prompt, and the agent must use exact item names and prices
- **Live menu from Google Sheets** — owners update items, prices and availability in a spreadsheet; a hardcoded menu is used as a fallback
- **Pickup or delivery**, with address capture and a $15 delivery minimum
- **SMS confirmation loop** — order summary texted to the caller; reply **YES** to confirm or **NO** to cancel
- **Receipts** — final SMS receipt to the customer and an HTML email ticket to the restaurant
- **Robust call handling** — low-confidence speech re-prompts, silence detection ("Are you still there?"), and graceful fallbacks on LLM or JSON errors
- 6.25% MA sales tax calculated automatically

---

## 🏗️ How It Works

```
 Customer's phone
       │  call
       ▼
 ┌──────────────┐   POST /call/incoming    ┌───────────────────────────┐
 │ Twilio Voice │ ───────────────────────▶ │  Flask server             │
 │  STT + TTS   │ ◀─────── TwiML ───────── │                           │
 └──────────────┘   POST /call/process     │  session (per CallSid)    │
                    POST /call/silence     │        │                  │
                                           │        ▼                  │
                                           │  Groq · Llama 3.3 70B     │
                                           │  menu-grounded prompt     │
                                           │  → JSON {speech, action,  │
                                           │          items, ...}      │
                                           └─────┬───────────┬─────────┘
                                                 │           │
                         order_done → SMS        │           │  menu
                                                 ▼           ▼
                                        ┌──────────────┐  ┌──────────────┐
 Customer replies YES ─ POST /sms/reply▶│ Twilio SMS   │  │ Google Sheets│
                                        └──────────────┘  └──────────────┘
                                                 │
                                                 ▼
                                   Receipt SMS + email to restaurant (Gmail)
```

### Conversation actions

Each LLM turn returns one `action` that the server acts on:

| Action | What the server does |
|--------|----------------------|
| `collect_name` / `collect_type` / `collect_address` | Stores customer name, Pickup/Delivery, delivery address |
| `add_items` | Adds the returned items (name, price, qty, note) to the order |
| `order_done` | Reads back the order and texts the customer a confirmation SMS |
| `hangup` | Sends the receipt SMS and restaurant email, then ends the call |
| `continue` / `repeat` | Speaks the reply and keeps listening |

---

## 🧰 Tech Stack

| Component        | Technology |
|------------------|------------|
| Web server       | Python, Flask (blueprints) |
| Telephony        | Twilio Voice (`<Gather>` speech input, `phone_call` enhanced model) |
| Text-to-speech   | Twilio "Alice" voice |
| LLM              | Groq API — `llama-3.3-70b-versatile` |
| SMS              | Twilio Messaging |
| Email            | Gmail SMTP (`smtplib`) with HTML receipts |
| Menu             | Google Sheets via `gspread` + service account (with hardcoded fallback) |
| Local tunnel     | ngrok |

---

## 📁 Project Structure

```
pizza-store-voice-agent/
├── .env.example                      # Environment variable template
└── rustic-pizza-voice-agent-python/
    ├── server.py                     # Flask app entry point (port 3000)
    ├── requirements.txt
    ├── README.md                     # Detailed setup guide
    ├── routes/
    │   ├── call.py                   # /call/incoming, /call/process, /call/silence
    │   └── sms.py                    # /sms/reply — YES / NO confirmations
    ├── services/
    │   ├── groq.py                   # System prompt, LLM call, JSON parsing, fallback
    │   ├── twiml.py                  # TwiML builders (gather, hangup, silence)
    │   ├── sms.py                    # Confirmation & receipt SMS
    │   └── email.py                  # HTML receipt + restaurant order email
    └── utils/
        ├── menu.py                   # Google Sheets menu loader + fallback menu
        └── session.py                # Per-call session state & order totals
```

---

## 🚀 Quick Start

```bash
git clone https://github.com/GayathriTelaprolu/pizza-store-voice-agent.git
cd pizza-store-voice-agent

cp .env.example .env              # then fill in your keys
cd rustic-pizza-voice-agent-python
pip install -r requirements.txt

python server.py                  # runs on http://localhost:3000
ngrok http 3000                   # in a second terminal
```

Then in the Twilio Console, point your number's webhooks at your ngrok URL:

| Event | Webhook (HTTP POST) |
|-------|---------------------|
| A call comes in | `https://<your-ngrok-url>/call/incoming` |
| A message comes in | `https://<your-ngrok-url>/sms/reply` |

Call your Twilio number and place an order. See the [detailed setup guide](rustic-pizza-voice-agent-python/README.md) for getting each API key and for troubleshooting.

### Environment variables

| Variable | Description |
|----------|-------------|
| `TWILIO_ACCOUNT_SID` | Twilio account SID |
| `TWILIO_AUTH_TOKEN` | Twilio auth token |
| `TWILIO_PHONE_NUMBER` | Your Twilio number (`+1xxxxxxxxxx`) |
| `GROQ_API_KEY` | Groq API key |
| `GMAIL_USER` | Gmail address that sends receipts and receives restaurant orders |
| `GMAIL_APP_PASSWORD` | Gmail app password (not your account password) |
| `BASE_URL` | Public URL of the server (your ngrok URL), used in TwiML callbacks |
| `GOOGLE_CREDENTIALS_JSON` | *Optional.* Google service-account JSON (as one line) for the Sheets menu |

### Google Sheets menu (optional)

Create a spreadsheet named **`Rustic Pizza Menu`**, share it with your service account's email, and use these columns on the first sheet:

| Category | Name | Price | Keywords | Available |
|----------|------|-------|----------|-----------|
| Pizza | Margarita Pizza | 17.50 | margarita pizza, margherita, margarita | Yes |

Rows with `Available` other than `Yes` are skipped. Without credentials, the agent uses the built-in menu in `utils/menu.py`.

---

## 💬 Example Call

> **Agent:** Hello! Thank you for calling Rustic Pizza in Sherborn! I am your order agent. May I have your name please?
> **Caller:** It's Sam.
> **Agent:** Thanks, Sam! Is this for pickup or delivery?
> **Caller:** Pickup. Can I get a large cheese pizza and large fries?
> **Agent:** Got it — one large cheese pizza and large fries. Anything else?
> **Caller:** That's it.
> **Agent:** Your total is $28.15 with tax. I've sent you an SMS — reply YES to confirm.

---

## ⚠️ Current Limitations

- Sessions and pending confirmations are kept **in memory**, so they reset when the server restarts, and it should run as a single process.
- Orders are delivered by email/SMS only — they aren't written to a database or a POS yet.
- Twilio trial accounts can only call and text **verified** numbers.


## 🗺️ Roadmap

- Persist sessions and orders (Redis / PostgreSQL)
- Send confirmed orders straight into the [Rustic Pizza POS](https://github.com/GayathriTelaprolu/rustic-pizza)
- Validate Twilio request signatures
- Deploy to a permanent host (Render / Railway / Cloud Run)
- Support modifiers like half-and-half pizzas and extra toppings

---

## 👩‍💻 Author

**Gayathri Telaprolu** — [GitHub](https://github.com/GayathriTelaprolu)
