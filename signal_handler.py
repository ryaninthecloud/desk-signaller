'''
Signal Handler is the code-base for 
changing and updating signal element states. 
'''

import machine

class SignalObject:
    '''
    SignalObject contains
    the code to change the
    state of the Signal
    based on data provided
    by the STOMP connection.
    '''
    def __init__(
        self,
        signal_address: str,
        signal_element: int,
        signal_on: bool,
        signal_platform: str,
        green_signal_pin: machine.Pin,
        red_signal_pin: machine.Pin
    ):
        self.signal_address = signal_address
        self.signal_element = signal_element - 1
        self.signal_on = signal_on
        self.signal_platform = signal_platform
        self.signal_green_pin = green_signal_pin
        self.signal_red_pin = red_signal_pin
        self.signal_red_pin.value(1)

    def update_signal(self, element_data: str):
        '''
        When a STOMP message is received, method
        will parse the data provided and update
        the signal element state.
        
        Arguments:
        :str element_data: string of binary data
    
        Returns:
        None
        '''
        try:
            _ = str(element_data)[self.signal_element]
            self.signal_on = bool(int(_))
            self.set_signal_control_pin()
            print('SIGNAL ON', self.signal_on, 'for platform', self.signal_platform)
        except IndexError:
            print(self.signal_address, self.signal_element, 'unable to find element in data source.')
        except TypeError:
            print(self.signal_address, self.signal_element, 'cannot parse data given.')

    def set_signal_control_pin(self):
        '''
        Can be called to update the signal pin 
        value based on the current state of the 
        signal_on value.
        '''
        if self.signal_on is not None:
            if self.signal_on:
                self.signal_green_pin.value(1)
                self.signal_red_pin.value(0)
            else:
                self.signal_green_pin.value(0)
                self.signal_red_pin.value(1)
        else:
            print(f'Warn: Signal Control failed signal_on is None {self.signal_address}, {self.signal_element}')