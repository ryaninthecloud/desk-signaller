'''
Code Tests for all modules within desk-signaller
'''
import unittest

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
        index_first_newline = frame.built_frame.index('\n')
        index_final_newline = frame.built_frame.rindex('\n')

        parsed_command = frame.built_frame[:index_first_newline]
        parsed_headers = frame.built_frame[index_first_newline:index_final_newline].split('\n')

        for header in parsed_headers:
            if all(x for x in ['valid_header_key', 'valid_header_value', ':']):
                header = header.rstrip().split(':')
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

        index_first_newline = frame.built_frame.index('\n')
        index_final_newline = frame.built_frame.rindex('\n')

        parsed_command = frame.built_frame[:index_first_newline]
        parsed_headers = frame.built_frame[index_first_newline:index_final_newline].split('\n')

        with self.subTest():
            self.assertTrue(parsed_headers[-1] == '',
                            'line termination is not present in headers')

        for header in parsed_headers:
            if 'content-length' in header:
                header = header.rstrip().split('\n')
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
        index_first_newline = frame.built_frame.index('\n')
        index_final_newline = frame.built_frame.rindex('\n')

        parsed_command = frame.built_frame[:index_first_newline]
        parsed_headers = frame.built_frame[index_first_newline:index_final_newline].split('\n')

        for header in parsed_headers:
            if 'content-length' in header:
                header = header.rstrip().split(':')
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
