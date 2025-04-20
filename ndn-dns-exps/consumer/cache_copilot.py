import time
from collections import OrderedDict
import hashlib
import base64
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature

class DNSCache:
    def __init__(self, max_size=100):
        # Initialize the cache with a maximum size and an OrderedDict for LRU eviction
        self.cache = OrderedDict()
        self.max_size = max_size

    def add_record(self, domain, record_type, record_value, ttl):
        """
        Add a DNS record to the cache, including DNSSEC-specific records.
        :param domain: The domain name (e.g., example.com)
        :param record_type: The type of DNS record (e.g., A, AAAA, CNAME, RRSIG, DNSKEY, DS)
        :param record_value: The value of the DNS record
        :param ttl: Time-to-live in seconds
        """
        expiry_time = time.time() + ttl
        key = (domain, record_type)
        self.cache[key] = {'value': record_value, 'expiry': expiry_time}
        self.cache.move_to_end(key)  # Mark as most recently used

        # Evict least recently used item if cache exceeds max size
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)

    def get_record(self, domain, record_type):
        """
        Retrieve a DNS record from the cache, including DNSSEC-specific records.
        :param domain: The domain name
        :param record_type: The type of DNS record (e.g., A, AAAA, CNAME, RRSIG, DNSKEY, DS)
        :return: The record value if found and not expired, otherwise None
        """
        key = (domain, record_type)
        if key in self.cache:
            record = self.cache[key]
            if time.time() < record['expiry']:
                self.cache.move_to_end(key)  # Mark as most recently used
                return record['value']
            else:
                # Remove expired record
                del self.cache[key]
        return None

    def validate_dnssec(self, domain, record_type, record_value):
        """
        Validate DNSSEC records (e.g., RRSIG, DNSKEY) for authenticity.
        :param domain: The domain name
        :param record_type: The type of DNS record (e.g., RRSIG, DNSKEY)
        :param record_value: The value of the DNSSEC record
        :return: True if validation is successful, False otherwise
        """
        if record_type != "RRSIG":
            return False  # Only validate RRSIG records

        try:
            # Extract RRSIG components (this is a simplified example)
            rrsig = record_value['signature']
            dnskey = record_value['dnskey']
            signed_data = record_value['signed_data']

            # Decode the DNSKEY and RRSIG
            public_key = rsa.RSAPublicNumbers(
                e=dnskey['e'], n=dnskey['n']
            ).public_key()

            # Verify the signature
            public_key.verify(
                base64.b64decode(rrsig),
                signed_data.encode(),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return True
        except (InvalidSignature, KeyError, ValueError):
            return False

    def cleanup_expired_records(self):
        """
        Remove all expired records from the cache, including DNSSEC-specific records.
        """
        current_time = time.time()
        keys_to_delete = [key for key, record in self.cache.items() if record['expiry'] < current_time]
        for key in keys_to_delete:
            del self.cache[key]
