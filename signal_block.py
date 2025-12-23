'''
Signal Block is a logical representation
of a block containing 8 signal elements
which are referenced via the "address"
parameter in the STOMP message

Signal Block also performs an inversion
of the bits in a received message as the
message sends bits in Big Endian

Abstract Purpose:
    A message is received and parsed by the STOMP client
    if it matches the address of a signal in the
    signals of interest dictionary, e.g. 5A then
    the object at the key 5A.

Class Properties:
    signal_block_address: this is the address used in the STOMP client,
    count_elements_in_block: value between 1-8 inclusive,
    current_bit_status_hex: the last hex status received,
    last_updated: the datetime that the last message was received
    signal_element_container: list containing signal element objects

Functionality:
    Signal Block is a an abstract structure and acts
    as a container for the Signal Element class.

    > init(self, signal_block_address, elements_in_block=8, opening_state_hex)
    > update(self, updated_hex_status, message_received)
    > register_signal(self, signal_settings_dict)
        >> signal_identifier
        >> signal_data
            >>>> (k/v) -> state
            >>>> platform
            >>>> green_signal_pin
            >>>> red_signal_in

Architectural Questions:
    > How should a Signal Block be insantiated? Is it via an existing hexcode?
    > Can a hex status contain less than 8 bits?

'''
import machine
from signal_element import SignalElement

class SignalBlock:
    '''
    Signal Block contains
    up to 8 elements which individually
    represent Signal Elements that
    control the state of the LED
    pins associated with them
    '''
    def __init__(self,
                 signal_block_address: str,
                 number_elements_in_block: int = 8,
                 opening_state_hex: str | None = None
                ) -> None:
        '''
        Construct a Signal Block instance.

        args:
            signal_block_address: str, the STOMP address that the block represents
            number_elements_in_block: int, if less than 8 elements, then can be
                specified here
            opening_state_hex: str | None, can represent opening state but
                optional
        returns:
            None
        '''
        self.signal_block_address = signal_block_address
        self.number_elements_in_block = number_elements_in_block
        #sort of a bit dirty but allows for positional access to signals
        self.signal_elements_container = [None for x in range(0,8)]

    def modify_signal_in_block(self,
                               signal_position: int,
                               signal_platform: str,
                               signal_green_pin: machine.Pin,
                               signal_red_pin: machine.Pin,
                               signal_state: int = 0
                              ) -> int:
        '''
        Called to create or modify a signal at the given position
        in the signal element block.

        Position argument must be between 0-7 which represent the 8
        bits in the byte.

        args:
            signal_position: int: the position of the signal from 0-7
            signal_platform: str: the platform that element represents
            signal_state: optional int: default 0, can be 1

        returns:
            int: number of signal element objects in the block

        '''
        if signal_position > 7:
            return 1

        self.signal_elements_container[signal_position] = SignalElement(\
                                                                        signal_state,
                                                                        signal_platform,
                                                                        machine.Pin(signal_green_pin, machine.Pin.OUT),
                                                                        machine.Pin(signal_red_pin, machine.Pin.OUT)
                                                                       )
        return 0

    def return_little_endian(self, hex_value: str) -> str:
        '''
        Parse the hex value provided into a little
        endian representation of the binary  in a string

        args:
            hex_value: str
        returns:
            str: string representation of binary value in little endian
        '''
        signal_data = bin(int(hex_value, 16))[2:]
        if len(signal_data):
            _ = 8 - len(signal_data)
            signal_data = '0' * _ + signal_data
        signal_data = signal_data[::1]
        return signal_data


    def update_from_hex(self, hex_value) -> int:
        '''
        Update the signal block individual elements
        based on the hex value provided.

        args:
            hex_value: str: hex value given via the STOMP msg
        returns:
            int: 0 represent success
        '''
        signal_state_in_binary = self.return_little_endian(hex_value)

        for i, signal_element in enumerate(self.signal_elements_container):
            if signal_element and isinstance(signal_element, SignalElement):
                if len(signal_state_in_binary) >= i:
                    signal_element.update_signal(new_signal_state=int(signal_state_in_binary[i]))

        return 0
