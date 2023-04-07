"""Module that stores all the exceptions in Home Assistant format"""
from aiohttp.web_exceptions import HTTPForbidden, HTTPMethodNotAllowed, HTTPNotFound
from aiohttp import ClientConnectorError


class ListIndexError(IndexError, BaseException):
    def __init__(self) -> None:
        super().__init__()
        return None


class CodeTypeError(TypeError, BaseException):
    def __init__(self) -> None:
        super().__init__()
        return None


class DictionaryKeyError(KeyError, BaseException):
    def __init__(self) -> None:
        super().__init__()
        return None


class APINotFoundError(HTTPNotFound, BaseException):
    def __init__(self) -> None:
        super().__init__()
        return None


class APIForbiddenError(HTTPForbidden, BaseException):
    def __init__(self) -> None:
        super().__init__()
        return None


class APIMethodError(HTTPMethodNotAllowed, BaseException):
    def __init__(self, method=None, allowed_methods=None) -> None:
        super().__init__(method, allowed_methods)
        return None


class APIClientConnectorError(ClientConnectorError, BaseException):
    def __init__(self, connection_key=None, os_error=None) -> None:
        super().__init__(connection_key, os_error)
        return None
