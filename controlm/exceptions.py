

class CtmXmlParserException (BaseException):

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code

