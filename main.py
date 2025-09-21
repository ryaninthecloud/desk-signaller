'''
The entry point of the app
that consumes data from the
STOMP messaging queue and 
updates individual element objects
and LEDs.
'''
from microstomp import MicroSTOMPClient, Frame
from signal_handler import SignalObject

import parser_utils
import settings

import machine
import json

SIGNAL_AREA_CODE = settings.SIGNAL_AREA_CODE

signals_of_interest = {
    '5A' : [
        SignalObject(
            signal_address='5A',
            signal_element=7,
            signal_on=False,
            signal_platform='2',
            green_signal_pin=machine.Pin(12, machine.Pin.OUT),
            red_signal_pin=machine.Pin(13, machine.Pin.OUT)
        )
    ]
}

def callback_method(frame_data):
    '''
    The method called when new
    a new STOMP message is received.
    '''
    frame = Frame.parse_frame(frame_data)
    client.send_ack_frame(transaction_id=str(frame.headers["message-id"]))

    if frame.is_error():
        print('ERROR: ', frame_data)
        return

    frame_body = json.loads(frame.body)

    for message in frame_body:
        if parser_utils.message_filtering_pass(message=message,
                                               message_type='SF_MSG',
                                               message_area_code='Y2',
                                               signals_of_interest=signals_of_interest):

            signal_address = parser_utils.get_signal_area_code(message['SF_MSG']['address'])
            signal_data = parser_utils.signal_data_parser(message['SF_MSG']['data'])

            for signal in signals_of_interest[signal_address]:
                signal.update_signal(signal_data)


client = MicroSTOMPClient(
    host=settings.NETWORK_RAIL_STOMP_HOST,
    port = settings.NETWORK_RAIL_STOMP_PORT,
    client_id= settings.NETWORK_RAIL_STOMP_CLIENT_ID,
    username= settings.NETWORK_RAIL_USERNAME,
    password= settings.NETWORK_RAIL_PASSWORD,
    on_message_callback=callback_method
)

client.connect()
client.subscribe('/topic/TD_LNE_NE_SIG_AREA', ack='client')
client.listen_for_messages()
print('INFO LISTENING FOR MESSAGES')
