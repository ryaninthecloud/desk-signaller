'''
Contains code to simplify the parsing
and handling of any dignal data 
that is received.
'''

def signal_data_parser(data_passed: str) -> str:
    '''
    Parses a hexadecimal byte into
    an 8-bit binary representation
    of the signal element state.
    Due to the Big Endian nature
    of the signal data (where the highest
    signal element state i.e. signal element 8
    is received first) it is also
    necessary to reverse the binary byte
    string.
    
    :Arguments:
    :str data_passed: the hexadecimal data from STOMP message.
    
    :Returns:
    :str signal_data: a binary representation of signal element state.
    '''

    signal_data = bin(int(data_passed, 16))[2:]
    if len(signal_data):
        _ = 8-len(signal_data)
        signal_data = '0' * _ + signal_data
    signal_data = signal_data[::-1]
    return signal_data

def get_signal_area_code(address: str) -> str:
    '''
    Splits the signal address out
    from the element address.
    
    Then returns only the area code i.e. Y2

    :Arguments:
    :str address: address i.e. Y2:5A

    :Returns:
    :str: of area code
    '''
    return address.split(':')[0]

def message_filtering_pass(message: dict,
                           message_type: str | None, 
                           message_area_code: str | None,
                           signals_of_interest: dict | None) -> bool:
    '''
    Method containing logic for filtering
    messages based on message type, area code
    and signals of interest.
    
    :Arguments:
    :dict message: dictionary of individual message from STOMP aggregated message
    
    :Returns:
    :bool: whether message matches requirements (True is pass, False is fail)
    '''

    if message_type:
        if not message_type in message.keys():
            return False

    if message_area_code:
        if 'area_id' in message[message_type].keys():
            if message_area_code.upper() != get_signal_area_code(message[message_type]['area_id']):
                return False
        else:
            return False

    if signals_of_interest:
        _message_address = str(message[message_type]['address'])
        if not _message_address.upper() in signals_of_interest.keys():
            return False

    return True