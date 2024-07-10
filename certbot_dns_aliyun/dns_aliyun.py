"""DNS Authenticator for Aliyun DNS."""
import logging
import os

from certbot.plugins import dns_common

try:
    # Python 3.x
    from .alidns import AliDNSClient
except:
    # Python 2.x
    from alidns import AliDNSClient

logger = logging.getLogger(__name__)


class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for Aliyun DNS

    This Authenticator uses the Aliyun DNS API to fulfill a dns-01 challenge.
    """

    description = 'Obtain certificates using a DNS TXT record (if you are using Aliyun DNS).'
    ttl = 600
    _alidns_client = None

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)

        self.access_key = None
        self.access_key_secret = None

    @classmethod
    def add_parser_arguments(cls, add):  # pylint: disable=arguments-differ
        super(Authenticator, cls).add_parser_arguments(add, default_propagation_seconds=30)
        add('credentials', help='Aliyun DNS credentials INI file.')

    def more_info(self):  # pylint: disable=missing-docstring,no-self-use
        return 'This plugin configures a DNS TXT record to respond to a dns-01 challenge using ' + \
               'the Aliyun DNS API.'

    def _setup_credentials(self):
        self.access_key = os.environ.get('DNS_ALIYUN_ACCESS_KEY')
        self.access_key_secret = os.environ.get('DNS_ALIYUN_ACCESS_KEY_SECRET')
        if self.access_key and self.access_key_secret:
            return
        credentials = self._configure_credentials(
            'credentials',
            'Aliyun DNS credentials INI file',
            {
                'access-key': 'AccessKey for Aliyun DNS, obtained from Aliyun RAM',
                'access-key-secret': 'AccessKeySecret for Aliyun DNS, obtained from Aliyun RAM'
            }
        )
        self.access_key = credentials.conf('access-key')
        self.access_key_secret = credentials.conf('access-key-secret')

    def _perform(self, domain, validation_name, validation):
        self._get_alidns_client().add_txt_record(domain, validation_name, validation)

    def _cleanup(self, domain, validation_name, validation):
        self._get_alidns_client().del_txt_record(domain, validation_name, validation)

    def _get_alidns_client(self):
        if not self._alidns_client:
            self._alidns_client = AliDNSClient(
                self.access_key,
                self.access_key_secret,
                self.ttl)
        return self._alidns_client
