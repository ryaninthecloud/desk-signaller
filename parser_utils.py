'''
Contains code to simplify the parsing
and handling of any dignal data 
that is received.
'''
import os
import json

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
        if not _message_address.upper() in signals_of_interest:
            return False

    return True

def read_configuration_file(file_location: str) -> dict:
    '''
    read configuration file

    args:
        file_location: str: including file name
    returns:
        dict: of file configuration if valid else empty
    '''
    try:
        raw_file = open(file_location).read()
    except Exception as e:
        print(f'critical: cannot find file at {file_location}')
        return {}

    try:
        config_file = json.loads(raw_file)
        config_file = dict(config_file)
    except Exception as e:
        print('critical: cannot parse the config file into json', e)
        return {}

    top_level_keys = config_file.keys()

    if not top_level_keys:
        return {}

    for _k in top_level_keys:
        try:
            address_level_keys = config_file[_k].keys()
        except Exception as e:
            print(f'critical: could not access keys for area {_k}')
            return {}

        if not address_level_keys:
            print(f'critical: no address level keys available')
            return {}

        for address_key in address_level_keys:
            address_value = config_file[_k][address_key]
            if not isinstance(address_value, list):
                print(f'''critical: cannot parse config, address at area {_k} and
                      address {address_key} is not a list''')
                return {}

            for light_configuration in address_value:
                if not isinstance(light_configuration, dict):
                    print(f'''critical: cannot parse config, address
                          {address_key} does not contain a valid light
                          configuration''')
                    return {}

            required_light_keys = ['platform', 'element_position',\
                                   'green_pin',\
                                   'red_pin']

            if not all(rk in light_configuration for rk in required_light_keys):
                print(f'''critical: required light configuration is missing
                         keys, {light_configuration}''')
                return {}

    return config_file