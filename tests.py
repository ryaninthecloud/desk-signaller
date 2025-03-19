'''
Code Tests for all modules within desk-signaller
'''
import unittest
import re

from microstomp import Frame
class TestFrameClass(unittest.TestCase):
    '''
    Contains all tests for Frame class
    '''

    def test_valid_command_instantiation(self):
        '''
        Test a valid instantiation of a new Frame object
        '''
        valid_commands = [
            'MESSAGE',
            'CONNECT',
            'STOMP',
            'SUBSCRIBE',
            'UNSUBSCRIBE',
            'DISCONNECT'
        ]

        for command in valid_commands:
            f = Frame(
                command = command,
                headers = {
                    'valid_header':'valid_value'
                },
                body = 'a normal string'
            )
            with self.subTest():
                self.assertEqual(f.command, command, f'''Command {command}
                                was passed but 
                                frame command is 
                                different {f.command}.''')
            f = Frame(
                command = command.lower(),
                headers = {
                    'valid_header':'valid_value'
                },
                body = 'a normal string'
            )
            with self.subTest():
                self.assertEqual(f.command, command, f'''Command {command}
                                was passed but 
                                frame command is 
                                different {f.command}.''')

    def test_invalid_command_passed_asserts_value_error(self):
        '''
        Test that exception is raised by providing an invalid
        STOMP argument.
        '''
        with self.assertRaises(ValueError):
            Frame(
                command = 'INVALID_COMMAND',
                headers = {
                    'valid_header':'valid_value'
                },
                body = 'a normal string'
            )

    def test_valid_instantiation_of_headers(self):
        '''
        Test that headers are parsed correctly from
        instantiation to built frame.
        '''
        headers_to_add = {
            'valid_header_key' : 'valid_header_value'
        }
        frame = Frame(
            command = 'CONNECT',
            headers = headers_to_add,
            body = 'a normal string'
        )
        command_and_headers = re.search('(?s:.*)\n', frame.built_frame).group(0).split('\n')
        command_and_headers.pop(0)

        for header in command_and_headers:
            if all(x for x in ['valid_header_key', 'valid_header_value', ':']):
                header = re.split('[:]', str(header).rstrip())
                self.assertTrue(header[0] == 'valid_header_key' and
                                header[1] == 'valid_header_value',
                            'header or value is different to input in. out > {header}')          

    def test_empty_insantiation_of_headers(self):
        '''
        Test that empty header input to Frame object terminates headers with
        content-length successfully.
        '''
        frame = Frame(
            command='CONNECT',
            headers = {},
            body = 'a normal string'
        )

        command_and_headers = re.search('(?s:.*)\n', frame.built_frame).group(0)
        command_and_headers = command_and_headers.split('\n')
        command_and_headers.pop(0)
        with self.subTest():
            self.assertTrue(command_and_headers[-1] == '',
                            'line termination is not present in headers')

        for header in command_and_headers:
            if 'content-length' in header:
                header = re.split('[:]', str(header).rstrip())
                with self.subTest():
                    self.assertTrue(header[0] == 'content-length',
                                    'content length header key not valid')

    def test_content_length_is_accurate(self):
        '''
        Test that the content-length header is accurate
        when providing a body to the Frame
        '''
        body_content = 'this is a normal string'
        body_content_byte_size = 23
        frame = Frame(
            command = 'STOMP',
            headers = {},
            body=body_content
        )
        command_and_headers = re.search('(?s:.*)\n', frame.built_frame).group(0)
        command_and_headers = command_and_headers.split('\n')
        for header in command_and_headers:
            if 'content-length' in header:
                header = re.split('[:]', str(header).rstrip())
                with self.subTest():
                    self.assertTrue(int(header[1]) == body_content_byte_size,
                                    'content length value not accurate')

    def test_parsing_frame(self):
        '''
        To be implemented, testing frame parsing function.
        '''
        pass

if __name__ == '__main__':
    unittest.main()
