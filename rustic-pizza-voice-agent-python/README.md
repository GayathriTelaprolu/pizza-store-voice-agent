# Rustic Pizza Voice Agent — Python

A real AI phone agent built with Python (Flask) + Twilio + Groq AI.
Answers calls, takes orders, sends SMS confirmation, and emails receipts to the restaurant.

---

## How It Works

```
Customer calls Twilio number
        ↓
Twilio sends call to your Flask server (via ngrok)
        ↓
Agent greets customer, Twilio listens via built-in STT
        ↓
Groq AI (Llama 3.3) processes speech and decides response
        ↓
Twilio speaks reply back using Alice TTS voice
        ↓
Customer orders items → Agent adds to cart
        ↓
Customer says "done" → SMS sent to their phone
        ↓
Customer replies YES → Receipt SMS + Email sent to restaurant
        ↓
Call ends
```

---

## Free Services Used

| Service        | What it does              | Cost                   |
|----------------|---------------------------|------------------------|
| Twilio Trial   | Phone calls + SMS         | $15 free credit        |
| Groq API       | AI brain (Llama 3.3)      | Completely free        |
| Twilio Alice   | Voice (text-to-speech)    | Included in Twilio     |
| Twilio STT     | Speech-to-text            | Included in Twilio     |
| Gmail SMTP     | Email receipts            | Free (built-in Python) |
| ngrok          | Expose local server       | Free                   |

---

## Project Structure

```
rustic-pizza-voice-agent-python/
├── server.py              ← Start here (python server.py)
├── requirements.txt       ← Python dependencies
├── .env.example           ← Copy to .env and fill credentials
├── .env                   ← Your actual credentials (never share or commit!)
├── .gitignore             ← Prevents .env from being pushed to GitHub
├── routes/
│   ├── __init__.py
│   ├── call.py            ← Handles incoming calls + speech processing
│   └── sms.py             ← Handles customer YES/NO SMS replies
├── services/
│   ├── __init__.py
│   ├── groq.py            ← Groq AI brain (Llama 3.3-70b)
│   ├── twiml.py           ← Twilio voice response builder (Alice voice)
│   ├── sms.py             ← Send SMS via Twilio
│   └── email.py           ← Send email receipts via Gmail
└── utils/
    ├── __init__.py
    ├── menu.py            ← Full Rustic Pizza menu with prices
    └── session.py         ← Tracks each call state and order
```

---

## Step-by-Step Setup

### Step 1 — Install Python
Download Python 3.10 or higher from https://python.org

During install on Windows, check "Add Python to PATH" — very important!

Verify:
```bash
python --version
```

### Step 2 — Download and extract the project
1. Download the zip file
2. Right click and Extract All
3. Open the extracted folder in terminal or VS Code

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Get Twilio Trial Account (free $15 credit)
1. Go to https://twilio.com and Sign Up (no credit card needed)
2. Verify your phone number with OTP
3. Click Get a free phone number and confirm
4. From the dashboard copy:
   - Account SID (starts with AC...)
   - Auth Token (click eye icon to reveal)
   - Phone number (format: +1xxxxxxxxxx)

### Step 5 — Get Groq API Key (completely free)
1. Go to https://console.groq.com
2. Sign up with Google (free)
3. Click API Keys then Create API Key
4. Name it anything (e.g. rustic-pizza)
5. Copy the key (starts with gsk_...)

### Step 6 — Get Gmail App Password (free)
1. Go to https://myaccount.google.com
2. Click Security on the left
3. Turn on 2-Step Verification if not already on
4. Search "App Passwords" in the search bar
5. Type any app name and click Generate
6. Copy the 16-character password shown

### Step 7 — Set up ngrok (free)
1. Go to https://ngrok.com and sign up free
2. Download ngrok for your OS and extract ngrok.exe
3. Move ngrok.exe into your project folder
4. Get your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken
5. Run:
```bash
.\ngrok.exe config add-authtoken YOUR_TOKEN_HERE
```

### Step 8 — Configure .env file
```bash
copy .env.example .env
```

Open .env and fill in all values:
```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+1xxxxxxxxxx
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxx
GMAIL_USER=youremail@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop
BASE_URL=https://xxxx.ngrok-free.app
```

Leave BASE_URL empty for now and fill it in after Step 9.

IMPORTANT: Never share your .env file or commit it to GitHub.

### Step 9 — Start ngrok
Open a NEW terminal window and run:
```bash
.\ngrok.exe http 3000
```

You will see:
```
Forwarding  https://abc123.ngrok-free.app -> http://localhost:3000
```

Copy that https URL and paste it as BASE_URL in your .env file.

### Step 10 — Start the Flask server
Open another terminal window and run:
```bash
python server.py
```

You should see:
```
* Running on http://127.0.0.1:3000
* Debugger is active!
```

### Step 11 — Configure Twilio Webhooks
1. Go to https://console.twilio.com
2. Click Phone Numbers then Manage then Active Numbers
3. Click your phone number
4. Under Voice and Fax, A Call Comes In:
   - Set to: Webhook
   - URL: https://your-ngrok-url.ngrok-free.app/call/incoming
   - Method: HTTP POST
   - Click Save
5. Under Messaging, A Message Comes In:
   - Set to: Webhook
   - URL: https://your-ngrok-url.ngrok-free.app/sms/reply
   - Method: HTTP POST
   - Click Save

### Step 12 — Verify your phone number on Twilio (trial accounts only)
1. Go to https://console.twilio.com/us1/develop/phone-numbers/verified-caller-ids
2. Click Add a new Caller ID
3. Enter your phone number with country code (e.g. +91xxxxxxxxxx for India)
4. Verify with the OTP you receive

### Step 13 — Test it!
Call your Twilio phone number from your verified phone.
The agent will answer and say:
"Hello! Thank you for calling Rustic Pizza in Sherborn! I am your order agent. May I have your name please?"

---

## Full Order Flow

1. Customer calls your Twilio number
2. Agent greets and asks for name
3. Agent asks pickup or delivery
4. If delivery, agent asks for delivery address
5. Customer orders items — e.g. "One large BBQ pizza and large fries"
6. Agent confirms each item and asks if they want anything else
7. Customer says "done" — agent reads back full order with total
8. SMS sent to customer phone with full order details
9. Customer replies YES to the SMS
10. Receipt SMS sent to customer and order email sent to restaurant
11. Call ends

---

## Important Notes

### Two terminals needed at all times
- Terminal 1: ngrok running
- Terminal 2: python server.py running

Never close either terminal while testing.

### ngrok URL changes on every restart
Every time you restart ngrok free tier, you get a new URL. You must:
1. Copy the new URL from ngrok terminal
2. Update BASE_URL in .env
3. Update the webhook URL in Twilio Console
4. Restart the Flask server

### Twilio trial limitations
- Calls and SMS only work with verified phone numbers
- Upgrade to paid Twilio to allow calls from any number worldwide (~$1/month)

---

## Troubleshooting

**"Application error" when calling:**
- Check ngrok is still running
- Check BASE_URL in .env matches current ngrok URL exactly
- Check Twilio webhook URL matches current ngrok URL exactly

**Getting a deep tone instead of agent voice:**
- Your phone number is not verified on Twilio trial
- Go to Twilio Console, Verified Caller IDs, and add your number

**Agent answers but AI does not respond:**
- Check your GROQ_API_KEY in .env is correct
- Check server terminal for Groq API errors

**SMS not sending:**
- Add your number to Verified Caller IDs in Twilio Console

**Email not sending:**
- Use Gmail App Password, not your real Gmail password
- Make sure 2-Step Verification is ON in Google account

**Order items showing $0.00 in email:**
- Make sure you are using the latest version of services/groq.py

**Module not found error:**
```bash
pip install -r requirements.txt
```

---

## Upgrading to Production

| What to upgrade | How |
|-----------------|-----|
| Any number can call | Upgrade Twilio trial to paid |
| Permanent public URL | Deploy to Railway.app or Render.com |
| Save orders to database | Add SQLite or PostgreSQL |

---

## Tech Stack

| Component       | Technology               |
|-----------------|--------------------------|
| Web server      | Python Flask             |
| Phone calls     | Twilio Voice             |
| Speech to text  | Twilio built-in STT      |
| Text to speech  | Twilio Alice voice       |
| AI brain        | Groq API — Llama 3.3-70b |
| SMS             | Twilio Messaging         |
| Email           | Python smtplib + Gmail   |
| Local tunnel    | ngrok                    |
