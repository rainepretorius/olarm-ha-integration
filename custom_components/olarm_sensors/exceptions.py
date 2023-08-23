"""Module that stores all the exceptions in Home Assistant format"""
from typing import Optional, Tuple
from aiohttp.client_reqrep import ClientResponse, RequestInfo
from aiohttp.typedefs import LooseHeaders
from aiohttp.web_exceptions import HTTPForbidden, HTTPMethodNotAllowed, HTTPNotFound
from aiohttp import ClientConnectorError, ContentTypeError


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


class APIContentTypeError(ContentTypeError, BaseException):
    def __init__(
        self,
        request_info: RequestInfo,
        history: Tuple[ClientResponse, ...],
        *,
        code: int | None = None,
        status: int | None = None,
        message: str = "",
        headers: LooseHeaders | None = None,
    ) -> None:
        super().__init__(
            request_info,
            history,
            code=code,
            status=status,
            message=message,
            headers=headers,
        )
