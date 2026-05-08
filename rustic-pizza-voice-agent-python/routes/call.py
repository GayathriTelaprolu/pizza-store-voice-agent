import os
import sys
import traceback
from flask import Blueprint, request, Response
from utils.session import get_session, delete_session, add_order_item, pending_confirmations
from services.groq import get_agent_response, get_greeting
from services.twiml import build_gather_response, build_hangup_response, build_silence_response
from services.sms import send_sms_confirmation, send_receipt_sms
from services.email import send_order_to_restaurant

call_bp = Blueprint('call', __name__)

@call_bp.route('/incoming', methods=['POST'])
def incoming():
    try:
        call_sid = request.form.get('CallSid')
        caller_phone = request.form.get('From', '')
        print(f'=== INCOMING CALL ===', flush=True)
        print(f'CallSid: {call_sid}', flush=True)
        print(f'From: {caller_phone}', flush=True)
        session = get_session(call_sid)
        session.customer_phone = caller_phone
        session.state = 'get_name'
        greeting = get_greeting()
        print(f'Greeting OK', flush=True)
        xml = build_gather_response(greeting['speech'])
        print(f'XML OK', flush=True)
        return Response(xml, mimetype='text/xml')
    except Exception as e:
        print(f'ERROR in /incoming: {e}', flush=True)
        traceback.print_exc(file=sys.stdout)
        return Response(
            '<?xml version="1.0" encoding="UTF-8"?><Response><Say voice="alice">Sorry, there was a technical error. Please try again.</Say></Response>',
            mimetype='text/xml'
        )

@call_bp.route('/process', methods=['POST'])
def process():
    try:
        call_sid = request.form.get('CallSid')
        speech_result = request.form.get('SpeechResult', '').strip()
        confidence = float(request.form.get('Confidence', 0))
        print(f'[{call_sid}] Speech: {speech_result} (conf: {confidence})', flush=True)
        session = get_session(call_sid)
        if not speech_result or confidence < 0.3:
            return Response(
                build_gather_response('I am sorry, I did not catch that. Could you please repeat?'),
                mimetype='text/xml'
            )
        reply = get_agent_response(session, speech_result)
        print(f'Action: {reply.get("action")} | Speech: {reply.get("speech")}', flush=True)
        if reply.get('customer_name') and not session.customer_name:
            session.customer_name = reply['customer_name']
        if reply.get('order_type') and not session.order_type:
            session.order_type = reply['order_type']
        if reply.get('delivery_address') and not session.delivery_address:
            session.delivery_address = reply['delivery_address']
        action = reply.get('action', 'continue')
        if action == 'add_items' and reply.get('items'):
            for item in reply['items']:
                add_order_item(session, item.get('name',''), float(item.get('price',0)), int(item.get('qty',1)), item.get('note',''))
            session.state = 'ordering'
        if action == 'order_done':
            session.state = 'confirm'
            if session.customer_phone:
                send_sms_confirmation(session.customer_phone, session)
                pending_confirmations[session.customer_phone] = call_sid
            confirm_speech = reply['speech'] + ' I have also sent you an SMS with your order details. Please reply YES to confirm or NO to make changes.'
            return Response(build_gather_response(confirm_speech), mimetype='text/xml')
        if action == 'hangup':
            if session.customer_phone:
                send_receipt_sms(session.customer_phone, session)
            send_order_to_restaurant(session)
            delete_session(call_sid)
            return Response(build_hangup_response(reply['speech']), mimetype='text/xml')
        return Response(build_gather_response(reply['speech']), mimetype='text/xml')
    except Exception as e:
        print(f'ERROR in /process: {e}', flush=True)
        traceback.print_exc(file=sys.stdout)
        return Response(
            build_gather_response('I am sorry, something went wrong. Could you please repeat that?'),
            mimetype='text/xml'
        )

@call_bp.route('/silence', methods=['POST'])
def silence():
    call_sid = request.form.get('CallSid')
    session = get_session(call_sid)
    if session.state == 'confirm':
        prompt = 'Are you still there? Please say YES to confirm or NO to make changes.'
    elif session.state == 'ordering':
        prompt = 'Are you still there? What would you like to add to your order?'
    else:
        prompt = 'Are you still there? How can I help you?'
    return Response(build_silence_response(prompt), mimetype='text/xml')
