import os
from twilio.twiml.voice_response import VoiceResponse, Gather, Say


def build_gather_response(speech_text: str) -> str:
    base_url = os.getenv("BASE_URL", "")
    response = VoiceResponse()

    gather = Gather(
        input="speech",
        action=f"{base_url}/call/process",
        method="POST",
        speech_timeout="auto",
        speech_model="phone_call",
        enhanced="true",
        language="en-US",
        timeout=5,
    )

    gather.say(
        speech_text,
        voice="alice",
    )

    response.append(gather)
    response.redirect(f"{base_url}/call/silence", method="POST")

    return str(response)


def build_hangup_response(speech_text: str) -> str:
    response = VoiceResponse()
    response.say(
        speech_text,
        voice="alice",
    )
    response.hangup()
    return str(response)


def build_silence_response(speech_text: str) -> str:
    return build_gather_response(speech_text)