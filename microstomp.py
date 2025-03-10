'''
Contains code to handle the STOMP communication and subscription.
'''
import usocket
import random

class Frame:
    '''
    A STOMP frame structure which adheres to
    STOMP 1.2
    '''
    def __init__(
            self,
            command: str,
            headers: dict,
            body: str
    ):
        '''
        Initialises the Frame
        :params:
        :command: must be string of CONNECT, STOMP, SUBSCRIBE, UNSUBSCRIBE, DISCONNECT
        '''
        if command.upper() not in [
            'CONNECT',
            'STOMP',
            'SUBSCRIBE',
            'UNSUBSCRIBE',
            'DISCONNECT'
        ]:
            raise ValueError('Invalid command supplied.')

        self.command = command.upper()
        self.headers = headers
        self.body = body
        self.built_frame = self.__build_frame()

    def __build_frame(self) -> str:
        '''
        Builds frame by concatenating values provided with required encoding.
        Calculates length of BODY content in bytes.
        Always adds content-length header.

        :returns:
        : _: utf-8 encoded string conforming to STOMP 1.2
        '''
        _ = self.command + '''\r\n'''
        body_length = len(self.body.encode("utf-8"))

        for header, value in self.headers.items():
            _ += f'''{header}:{value}\r\n'''

        _ += f'''content-length:{body_length}\r\n'''

        _ += '''\r\n'''
        _ += self.body + '''\x00'''

        return _.encode("utf-8")

class MicroSTOMPClient:
    '''
    A client for sending and receiving messages to a STOMP server.
    '''
    def __init__(self,
                 host,
                 port,
                 client_id,
                 username,
                 password,
                 on_message_callback):
        '''
        :params:
        :host: str - STOMP server or broker address
        :port: int - STOMP server or broker port
        :client_id: str - identifier for client connection
        :username: str -  auth username
        :password: str - auth password
        :on_message_callback: function - callback function
        '''
        self.cx_socket = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
        self.cx_host = host
        self.cx_port = port
        self.cx_client_id = client_id
        self.cx_username = username
        self.cx_password = password
        self.on_message_callback = on_message_callback
        self.connected_to_broker = False

    def connect(self):
        '''
        Connects to server provided and returns socket
        '''

        print("(info): beginning connection to server")

        connect_frame = Frame(
            command = 'CONNECT',
            headers = {
                'accept-version':'1.2',
                'host':self.cx_host,
                'login':self.cx_username,
                'passcode':self.cx_password
            },
            body=''
        ).built_frame

        try:
            self.cx_socket.connect((self.cx_host, self.cx_port))
        except Exception as e:
            print('(fatal): cannot connect to specified host - ', e)
            return 1

        self.cx_socket.send(connect_frame)
        server_response = self.cx_socket.recv(1024).decode("utf-8")

        print('(info): server responded to connect with ', server_response)

        self.connected_to_broker = True

    def disconnect(self):
        '''
        Gracefully closes the connection with the server.
        Sets property connected_to_broker to True
        '''
        print('(info): disconnection initiated...')

        if not self.connected_to_broker:
            print('(info): no active connection to close.')

        disconnect_reference = 100200
        disconnect_frame = Frame(
            command = 'DISCONNECT',
            headers = {
                'receipt-id' : disconnect_reference
            },
            body=''
        ).built_frame

        self.cx_socket.send(disconnect_frame)
        disconnect_response = self.cx_socket.recv(1024).decode("utf-8")
        
        print('(info): received response from server ', disconnect_frame)

        if 'DISCONNECT' in disconnect_response and str(disconnect_reference) in disconnect_response:
            print('(info): graceful disconnect transaction completed')
            self.cx_socket.close()
            self.connected_to_broker = False
        else:
            print('(info): could not gracefully disconnect, force closing')
            self.cx_socket.close()
            self.connected_to_broker = False
