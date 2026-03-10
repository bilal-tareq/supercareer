"""
Custom Email Backend that bypasses SSL certificate verification.
Used for development on Windows where SSL cert verification can fail.
DO NOT use this in production - use proper SSL certificates instead.
"""
import ssl
from django.core.mail.backends.smtp import EmailBackend as DjangoEmailBackend
from django.core.mail.utils import DNS_NAME


class UnverifiedSSLEmailBackend(DjangoEmailBackend):
    """
    SMTP email backend that overrides open() to use an unverified SSL context.
    This bypasses the SSL certificate verification error on Windows development.
    """

    def open(self):
        if self.connection:
            return False

        # Create an unverified SSL context that bypasses cert verification
        unverified_context = ssl.create_default_context()
        unverified_context.check_hostname = False
        unverified_context.verify_mode = ssl.CERT_NONE

        connection_params = {"local_hostname": DNS_NAME.get_fqdn()}
        if self.timeout is not None:
            connection_params["timeout"] = self.timeout
        if self.use_ssl:
            connection_params["context"] = unverified_context

        try:
            self.connection = self.connection_class(
                self.host, self.port, **connection_params
            )

            if not self.use_ssl and self.use_tls:
                self.connection.starttls(context=unverified_context)

            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except OSError:
            if not self.fail_silently:
                raise
