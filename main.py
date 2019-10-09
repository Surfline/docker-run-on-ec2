from contextlib import ExitStack
import logging
import os
import sys
from uuid import uuid4

from lib.ec2 import TempKeyPair, TempInstance
from lib.ssh import SSH

logger = logging.getLogger('run-on-ec2')


def main():
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())

    name = os.environ['NAME']
    key_name = f'{name}-{uuid4()}'
    launch_template_names = os.environ['LAUNCH_TEMPLATE_NAMES'].split(',')
    subnet_id = os.environ['SUBNET_ID']
    command = ' '.join(sys.argv[1:])

    with ExitStack() as stack:
        private_key = stack.enter_context(TempKeyPair(key_name))
        instance = stack.enter_context(TempInstance(
            name,
            launch_template_names,
            key_name,
            subnet_id,
        ))
        host = instance.private_ip_address
        connection = stack.enter_context(SSH(host, 'ec2-user', private_key))

        escaped_command = command.replace("'", "\\'")
        logger.info(f'Running command "{escaped_command}" on {host}...')
        connection.run(f'exec $SHELL -l -c \'{escaped_command}\'')


if __name__ == '__main__':
    main()
