import ssl
import sys

from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

# https://github.com/encode/httpx/blob/0.23.0/httpx/_compat.py
if sys.version_info >= (3, 10) or (
    sys.version_info >= (3, 7) and ssl.OPENSSL_VERSION_INFO >= (1, 1, 0, 7)
):

    def set_minimum_tls_version_1_2(context: ssl.SSLContext) -> None:
        # The OP_NO_SSL* and OP_NO_TLS* become deprecated in favor of
        # 'SSLContext.minimum_version' from Python 3.7 onwards, however
        # this attribute is not available unless the ssl module is compiled
        # with OpenSSL 1.1.0g or newer.
        # https://docs.python.org/3.10/library/ssl.html#ssl.SSLContext.minimum_version
        # https://docs.python.org/3.7/library/ssl.html#ssl.SSLContext.minimum_version
        context.minimum_version = ssl.TLSVersion.TLSv1_2

else:

    def set_minimum_tls_version_1_2(context: ssl.SSLContext) -> None:
        # If 'minimum_version' isn't available, we configure these options with
        # the older deprecated variants.
        context.options |= ssl.OP_NO_SSLv2
        context.options |= ssl.OP_NO_SSLv3
        context.options |= ssl.OP_NO_TLSv1
        context.options |= ssl.OP_NO_TLSv1_1


def create_custom_urllib3_context():
    """
    needed to avoid cloudflare bot detector that returns 403 on some requests
    this makes the requests library have the same TLS fingerprint as httpx
    in the future cloudflare may ban this signature also
    in that case we can use different cipher suite to alter TLS signature even further
    https://stackoverflow.com/questions/64967706/python-requests-https-code-403-without-but-code-200-when-using-burpsuite
    """

    CIPHERS = ('DEFAULT:@SECLEVEL=2')

    context = create_urllib3_context(ciphers=CIPHERS)
    set_minimum_tls_version_1_2(context)
    context.options &= ~ssl.OP_NO_TICKET

    return context


class HTTPAdapterTLS(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        kwargs["ssl_context"] = create_custom_urllib3_context()
        return super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        kwargs["ssl_context"] = create_custom_urllib3_context()
        return super().proxy_manager_for(*args, **kwargs)
