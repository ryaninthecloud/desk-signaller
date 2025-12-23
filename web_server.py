'''
Web server provides a
user interface to monitor
and change the configuration
of the light appliance
'''
import common

import socket
import time

def landing_page_content():
    '''
    Returns landing page content
    '''
    sanitised_signal_state = return_area_signal_states(common.area_container)
    landing_page_html = f'''<html>
    <title>Desktop Signaller {common.appliance_name}</title>
    <h2>DESKTOP SIGNALLER APPLIANCE INTERFACE</h2>
    <table style="height: 417px; width: 670px;" border="1">
    <tbody>
    <tr style="height: 13px; background-color: #afeeee;">
    <td style="width: 409.671875px; height: 13px;" colspan="2"><strong>Appliance Settings</strong></td>
    </tr>
    <tr style="height: 13px;">
    <td style="width: 409.671875px; height: 13px;"><strong>Appliance Name</strong></td>
    <td style="width: 243.328125px; height: 13px;">{common.appliance_name}</td>
    </tr>
    <tr style="height: 13px;">
    <td style="width: 409.671875px; height: 13px;"><strong>Signal Area Codes Monitored</strong></td>
    <td style="width: 243.328125px; height: 13px;">{common.area_container}</td>
    </tr>
    <tr style="height: 13px;">
    <td style="width: 409.671875px; height: 13px;"><strong>Current Signal States</strong></td>
    
    <td style="width: 243.328125px; height: 13px;">{sanitised_signal_state}</td>
    </tr>
    <tr style="height: 13.21875px;">
    <td style="width: 409.671875px; height: 13.21875px;"><strong>Last Message Received</strong></td>
    <td style="width: 243.328125px; height: 13.21875px;">{common.stat_last_message_received}</td>
    </tr>
    <tr style="height: 13px;">
    <td style="width: 409.671875px; height: 13px;"><strong>Last Signal Block Change</strong></td>
    <td style="width: 243.328125px; height: 13px;">{common.stat_last_block_change}</td>
    </tr>
    <tr style="height: 13px;">
    <td style="width: 409.671875px; height: 13px; background-color: #afeeee;" colspan="2"><strong>Current Configuration File</strong></td>
    </tr>
    <tr style="height: 13px;">
    <td style="width: 409.671875px; height: 13px; background-color: white;" colspan="2">&nbsp;{common.config_current_configuration}</td>
    </tr>
    </tbody>
    </table></html>'''
    return landing_page_html

def web_server():
    '''
    Web server accepts and responds
    to web requests on the bound port

    '''
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    web_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    web_socket.bind(addr)
    web_socket.listen(1)
    print(f'(info): web server is bound to {addr}')
    while True:
        conn, addr = web_socket.accept()
        try:
            conn.recv(1024)
            print(f'(info): web cx received from {str(addr)}')
            response = landing_page_content()
            conn.send('HTTP/1.1 200 OK\r\nContent-type: text/html\r\n\r\n'.encode())
            conn.send(response.encode())
            print('(info): all responses sent')
            time.sleep(0.1)
            conn.close()
            print('(info): connection closed')
        except:
            conn.close()
            print('(web-error): connection force closed')

def return_area_signal_states(area_container: dict):
    '''
    Iterate all keys in the area container then
    the signal states for each signal in the
    area codes
    '''
    sanitised_results = {}
    for area in area_container:
        block_states = {}
        area_data = area_container[area]
        for signal_block in area_data:
            print('(debug): signal block is', signal_block) 
            block = area_data[signal_block]
            sig_state = ''
            for signal in block.signal_elements_container:
                if signal:
                    if signal.signal_state:
                        sig_state += 'GREEN'
                    else:
                        sig_state += 'RED'
            block_states[signal_block] = sig_state
        sanitised_results[area] = block_states
    return sanitised_results
                