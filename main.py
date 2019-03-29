from contextlib import ExitStack
import os
import sys
from uuid import uuid4
from lib.ec2 import TempKeyPair, TempInstance
from lib.ssh import SSH

if __name__ == '__main__':
    name = os.environ['NAME']
    unique_name = f'{name}-{uuid4()}'
    launch_template_name = os.environ['LAUNCH_TEMPLATE_NAME']
    subnet_id = os.environ['SUBNET_ID']
    command = ' '.join(sys.argv[1:])

    with ExitStack() as stack:
        private_key = stack.enter_context(TempKeyPair(unique_name))
        instance = stack.enter_context(TempInstance(
            unique_name,
            launch_template_name,
            subnet_id,
        ))
        host = instance.private_ip_address
        connection = stack.enter_context(SSH(host, 'ec2-user', private_key))

        escaped_command = command.replace('"', '\\"')
        print(f'Running command "{escaped_command}" on {host}...')
        connection.run(f'exec $SHELL -l -c \'{escaped_command}\'')
