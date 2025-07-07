

class ModerationError(Exception):
    """Исключение для ошибок модерации"""
    
    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class ValidationError(Exception):
    """Исключение для ошибок валидации"""
    
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


class APIError(Exception):
    """Исключение для ошибок внешних API"""
    
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)
