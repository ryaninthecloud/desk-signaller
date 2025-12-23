'''
Signal Element represents the
individual signal that is part
of a block of signals.
'''

import machine

class SignalElement:
    '''
    SignalElement contains
    the code to change the
    state of the Signal
    based on data provided
    by the STOMP connection.
    '''
    def __init__(
        self,
        signal_state: int,
        signal_platform: str,
        green_signal_pin: machine.Pin,
        red_signal_pin: machine.Pin
    ):
        self.signal_state = signal_state
        self.signal_platform = signal_platform
        self.signal_green_pin = green_signal_pin
        self.signal_red_pin = red_signal_pin
        self.signal_red_pin.value(1)

    def update_signal(self, new_signal_state: int):
        '''
        Takes an integer of 0 or 1 to indicate
        the state of the signal, 0 off (red) or
        1 on (green)

        Arguments:
            new_signal_state: int: 0/1 for red/green
        Returns:
            current_signal_state: int: once the stae
        '''
        if new_signal_state not in (0, 1):
            return 2

        if new_signal_state == 0:
            self.signal_green_pin.value(0)
            self.signal_red_pin.value(1)
        elif new_signal_state == 1:
            self.signal_green_pin.value(1)
            self.signal_red_pin.value(0)

        self.signal_state = new_signal_state
        return self.signal_state

