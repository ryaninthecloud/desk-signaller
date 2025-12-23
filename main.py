'''
The entry point of the app
that consumes data from the
STOMP messaging queue and 
updates individual element objects
and LEDs.
'''
from microstomp import MicroSTOMPClient, Frame
from signal_handler import SignalObject
from signal_block import SignalBlock
from signal_element import SignalElement

import common
import web_server
import parser_utils
import settings

import _thread
import machine
import json
import time


common.config_current_configuration = parser_utils.read_configuration_file('./config.json')

if not common.config_current_configuration:
    print('(critical): configuration is empty')
    exit(0)

common.appliance_name = settings.APPLIANCE_NAME
common.areas_of_interest = common.config_current_configuration.keys()
common.area_container = {}
common.stat_last_message_received = None
common.stat_last_block_change = None

for area in common.areas_of_interest:
    print(f'(info): enumerating area {area}')
    area_data = common.config_current_configuration[area]
    block_map = {}
    for block_address in area_data:
        print(f'(info): enumerating block address {block_address}')
        _ = area_data[block_address]
        _block = SignalBlock(signal_block_address=block_address) 
        [_block.modify_signal_in_block(signal_position = _s['element_position'],
                                      signal_platform = _s['platform'],
                                      signal_green_pin = _s['green_pin'],
                                      signal_red_pin = _s['red_pin']) for _s in _]
        block_map[block_address] = _block
    common.area_container[area] = block_map
    print(f'(info): area container is now {common.area_container}')

web_thread = _thread.start_new_thread(web_server.web_server, tuple([]))

def new_callback_method(frame_data):
    '''
    Callback method for when a
    data frame is received from
    the STOMP subscription
    '''
    print('(info): frame received')
    frame = Frame.parse_frame(frame_data)
    client.send_ack_frame(transaction_id=str(frame.headers["message-id"]))

    if frame.is_error():
        print('(error):', frame_data)
        return

    frame_body = json.loads(frame.body)
    common.stat_last_message_received = str(time.localtime())
    for message in frame_body:
        for area in common.area_container:
            if parser_utils.message_filtering_pass(message=message,
                                                   message_type='SF_MSG',
                                                   message_area_code='Y2',
                                                   signals_of_interest = common.area_container[area]):
                print('(info): message passed filtering')
                message_address = parser_utils.get_signal_area_code(message['SF_MSG']['address'])
                message_data = message['SF_MSG']['data']

                print(f'(info): msg address {message_address} and data is {message_data}')
                if message_address in common.area_container[area]:
                    print(common.area_container[area][message_address])
                    common.area_container[area][message_address].update_from_hex(message_data)
                    print('(info): updated the address block within the container')
                    common.stat_last_block_change = str(time.localtime())




client = MicroSTOMPClient(
    host=settings.NETWORK_RAIL_STOMP_HOST,
    port = settings.NETWORK_RAIL_STOMP_PORT,
    client_id= settings.NETWORK_RAIL_STOMP_CLIENT_ID,
    username= settings.NETWORK_RAIL_USERNAME,
    password= settings.NETWORK_RAIL_PASSWORD,
    on_message_callback=new_callback_method
)

client.connect()
client.subscribe('/topic/TD_LNE_NE_SIG_AREA', ack='client')
client.listen_for_messages()
print('INFO LISTENING FOR MESSAGES')
