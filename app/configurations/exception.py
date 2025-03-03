import sys

def error_message_detail(error, error_detail: sys):
    '''
    Return the error message with file name and line number.
    
    Args:
        error (Exception): The raised exception.
        error_detail (sys): Information about the exception.

    Returns:
        str: Error message with file name and line number.
    '''
    _, _, exc_tb = error_detail.exc_info()         
    file_name = exc_tb.tb_frame.f_code.co_filename 
    line_no = exc_tb.tb_lineno                    
    
    error_message = "Error occurred in Python script '{0}', line number [{1}], error message: '{2}'".format(
        file_name, line_no, str(error))               

    return error_message

class CustomException(Exception):
    '''
    Custom Exception class with error message and details.
    '''
    def __init__(self, error_message, error_detail: sys):
        '''
        Initialize the error message.

        Args:
            error_message (str): The error message.
            error_detail (sys): Information about the error.
        '''
        super().__init__(error_message) 
        self.error_message = error_message_detail(
            error_message, error_detail=error_detail)

    def __str__(self):
        '''
        Return the error message.
        '''
        return self.error_message
    
