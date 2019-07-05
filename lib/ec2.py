import sys

import boto3

EC2_CLIENT = boto3.client('ec2')
EC2_RESOURCE = boto3.resource('ec2')


class TempKeyPair:
    """
    Create a temporary EC2 Key Pair.

    On enter a Key Pair is created. The private key is returned.

    On exit the Key Pair is deleted.

    :param key_name: Name of Key Pair to create.
    :type key_name: str
    """

    def __init__(self, key_name: str):
        self.key_name = key_name

    def __enter__(self):
        print(f'Creating key pair {self.key_name}...')
        key_pair = EC2_CLIENT.create_key_pair(KeyName=self.key_name)
        pem = key_pair['KeyMaterial']
        return pem

    def __exit__(self, type, value, traceback):
        print(f'Deleting key pair {self.key_name}...')
        EC2_CLIENT.delete_key_pair(KeyName=self.key_name)


class TempInstance():
    """
    Create a temporary EC2 Instance from a launch template.

    On enter an Instance is created and tagged with a name. The Instance is
    returned after it is successfully running.

    On exit the Instance is terminated.

    :param name: Name to tag Instance with.
    :type name: str
    :param launch_template_name: Name of launch template to launch Instance
        with.
    :type launch_template_name: str
    :param subnet_id: ID for subnet to launch Instance in.
    :type subnet_id: str
    """

    def __init__(
        self,
        name: str,
        launch_template_name: str,
        key_name: str,
        subnet_id: str,
    ):
        self.name = name
        self.launch_template_name = launch_template_name
        self.key_name = key_name
        self.subnet_id = subnet_id

    def __enter__(self):
        print(f'Launching instance {self.name}...')
        self.instance = EC2_RESOURCE.create_instances(
            LaunchTemplate={'LaunchTemplateName': self.launch_template_name},
            KeyName=self.key_name,
            MinCount=1,
            MaxCount=1,
            SubnetId=self.subnet_id,
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': self.name,
                        },
                    ],
                },
            ],
        )[0]
        print(f'Waiting for instance {self.instance.instance_id} to be '
              'ready...')

        try:
            self.instance.wait_until_running()
            return self.instance
        except BaseException:
            self.__exit__(*sys.exc_info())
            raise

    def __exit__(self, type, value, traceback):
        print(f'Terminating instance {self.instance.instance_id}...')
        self.instance.terminate()
