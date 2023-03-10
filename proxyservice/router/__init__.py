import base64
import brotli
from typing import Union
from urllib.parse import urlparse
from requests import Session, HTTPError, ConnectionError, Timeout
from requests.exceptions import ProxyError


from proxyservice.router.cache import InstanceDatabase

InstanceCache = InstanceDatabase(maxsize=5000, ttl=240)


def classify(url: str, keys: list = []):
    uri = urlparse(url)
    hostname = f'{uri.scheme}://{uri.netloc}/'

    safe_keys = list(filter(lambda x: x is not None, keys))

    keys_identifier = "".join(safe_keys)
    normal_identifier = f"{hostname}{keys_identifier}"
    return hash(normal_identifier)


def decode_brotli(compressed_str: str) -> str:
    try:
        decompressed_str = brotli.decompress(compressed_str)
        return decompressed_str.decode('utf-8')
    except Exception:
        return compressed_str


class Router:
    def __init__(
        self,
        url: str,
        proxy: Union[dict, str, None] = None,
        headers: Union[dict, None] = None,
        body: Union[dict, None] = None,
        timeout: Union[int, None] = None,
        disable_intercept: bool = False,
        verify_ssl: bool = True
    ):

        self.url = url
        self.body = body
        self.verify_ssl = verify_ssl

        self.disable_intercept = disable_intercept

        if timeout is None:
            self.timeout = 10
        else:
            self.timeout = timeout

        if headers is not None:
            self.headers = dict(headers)
        else:
            self.headers = None

        self.proxy = None

        if proxy:

            if isinstance(proxy, dict):

                if 'parsed' in proxy:
                    parsed = proxy['parsed']

                    self.proxy = {
                        'http': parsed,
                        'https': parsed.replace('https', 'http')
                    }

            if isinstance(proxy, str):
                self.proxy = {
                    'http': proxy,
                    'https': proxy.replace('https', 'http')
                }

        self.session = Session()

        self.identifier = classify(url)
        persisted = InstanceCache.get(self.identifier)

        if persisted:
            self.session.cookies.update(persisted['cookies'])
            self.session.headers.update(persisted['headers'])

    def __post_session_hook(self, status: int):
        if not self.disable_intercept:

            if status in [401, 403]:
                InstanceCache.set(self.identifier, None)
                return

            persisted = {
                "headers": self.session.headers,
                "cookies": self.session.cookies
            }

            InstanceCache.set(self.identifier, persisted)

    def submit_data(self, params: Union[dict, None] = None):
        try:
            if not self.headers:
                response = self.session.post(
                    self.url, proxies=self.proxy, params=params, data=self.body, timeout=self.timeout, verify=self.verify_ssl)
            else:
                response = self.session.post(
                    self.url, proxies=self.proxy, params=params, headers=self.headers, data=self.body, timeout=self.timeout, verify=self.verify_ssl)

            headers = dict(response.headers)

            finalresponse = response.text

            is_brotli_encoding = 'Content-Encoding' in headers and headers['Content-Encoding'] == 'br'

            if is_brotli_encoding:
                finalresponse = decode_brotli(finalresponse)

            encodedResponse = str(base64.urlsafe_b64encode(
                finalresponse.encode("utf-8")), 'utf-8')

            self.__post_session_hook(response.status_code)

            return {
                "response": finalresponse,
                "encoded": encodedResponse,
                "response_url": response.url,
                "status": response.status_code,
                "headers": headers,
                "success": True
            }

        except HTTPError as e:

            headers = dict(response.headers)

            finalresponse = e.response.text

            is_brotli_encoding = 'Content-Encoding' in headers and headers['Content-Encoding'] == 'br'

            if is_brotli_encoding:
                finalresponse = decode_brotli(finalresponse)

            return {
                "response": finalresponse,
                "response_url": e.response.url,
                "status": e.response.status_code,
                "headers": headers,
                "success": False
            }

        except ProxyError as e:
            return {
                'error': 'proxy-error',
                'message': str(e),
                'success': False
            }

        except Timeout as e:

            return {
                'error': 'connection-timeout',
                'message': str(e),
                'success': False
            }

        except ConnectionError as e:
            return {
                "error": 'connection-error',
                "message": str(e),
                "success": False
            }

        except Exception as e:

            return {
                "error": 'general-error',
                "message": str(e),
                "success": False
            }

    def fetch_page(self, params: Union[dict, None] = None):
        try:

            if not self.headers:
                response = self.session.get(
                    self.url, proxies=self.proxy, allow_redirects=self.disable_intercept, timeout=self.timeout, params=params, verify=self.verify_ssl)
            else:
                response = self.session.get(
                    self.url, proxies=self.proxy, headers=self.headers, allow_redirects=self.disable_intercept, timeout=self.timeout, params=params, verify=self.verify_ssl)

            headers = dict(response.headers)

            finalresponse = response.text

            is_brotli_encoding = 'Content-Encoding' in headers and headers['Content-Encoding'] == 'br'

            if is_brotli_encoding:
                finalresponse = decode_brotli(finalresponse)

            encodedResponse = str(base64.urlsafe_b64encode(
                finalresponse.encode("utf-8")), 'utf-8')

            self.__post_session_hook(response.status_code)

            return {
                "response": finalresponse,
                "encoded": encodedResponse,
                "response_url": response.url,
                "status": response.status_code,
                "headers": headers,
                "success": True
            }

        except HTTPError as e:

            headers = dict(response.headers)

            finalresponse = e.response.text

            is_brotli_encoding = 'Content-Encoding' in headers and headers['Content-Encoding'] == 'br'

            if is_brotli_encoding:
                finalresponse = decode_brotli(finalresponse)

            return {
                "response": finalresponse,
                "response_url": e.response.url,
                "status": e.response.status_code,
                "headers": headers,
                "success": False
            }

        except ProxyError as e:
            return {
                'error': 'proxy-error',
                'message': str(e),
                'success': False
            }

        except Timeout as e:

            return {
                'error': 'connection-timeout',
                'message': str(e),
                'success': False
            }

        except ConnectionError as e:
            return {
                "error": 'connection-error',
                "message": str(e),
                "success": False
            }

        except Exception as e:

            return {
                "error": 'general-error',
                "message": str(e),
                "success": False
            }
