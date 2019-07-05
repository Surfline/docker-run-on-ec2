from io import StringIO
from time import sleep
from timeit import default_timer

from fabric import Connection
from paramiko import RSAKey
from paramiko.ssh_exception import NoValidConnectionsError


class SSH():
    """
    SSH context manager for creating an SSH connection.

    On enter an SSH connection is attempted every 5 seconds until successful.
    An exception is raised after 5 minutes.

    On exit the connection is closed.

    :param host: Host to connect to.
    :type host: str
    :param user: User to connect with.
    :type user: str
    :param private_key: RSA private key.
    :type private: str
    """

    def __init__(self, host: str, user: str, private_key):
        self.host = host
        self.user = user
        self.private_key = RSAKey.from_private_key(StringIO(private_key))

    def __enter__(self):
        self.connection = Connection(
            host=self.host,
            user=self.user,
            connect_kwargs={'pkey': self.private_key},
        )
        print(f'Waiting for SSH to become available on {self.host}...')
        self.wait_for_ssh(default_timer())
        return self.connection

    def __exit__(self, type, value, traceback):
        print(f'Closing SSH connection to {self.host}...')
        self.connection.close()

    def wait_for_ssh(self, start):
        try:
            self.connection.open()
        except NoValidConnectionsError:
            # Error after 5 minutes. Otherwise retry.
            now = default_timer()
            if now - start > 300:
                raise

            sleep(5)
            self.wait_for_ssh(start)
