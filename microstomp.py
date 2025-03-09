'''
Contains code to handle the STOMP communication and subscription.
'''

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