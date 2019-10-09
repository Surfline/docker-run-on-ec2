import logging
import sys
from typing import List

import boto3
from botocore.exceptions import ClientError

EC2_CLIENT = boto3.client('ec2')
EC2_RESOURCE = boto3.resource('ec2')

logger = logging.getLogger('run-on-ec2')


class TempKeyPair:
    """
    Create a temporary EC2 Key Pair.

    On enter a Key Pair is created. The private key is returned.

    On exit the Key Pair is deleted.

    Arguments:
        key_name: Name of Key Pair to create.
    """

    def __init__(self, key_name: str):
        self.key_name = key_name

    def __enter__(self):
        logger.info(f'Creating key pair {self.key_name}...')
        key_pair = EC2_CLIENT.create_key_pair(KeyName=self.key_name)
        pem = key_pair['KeyMaterial']
        return pem

    def __exit__(self, type, value, traceback):
        logger.info(f'Deleting key pair {self.key_name}...')
        EC2_CLIENT.delete_key_pair(KeyName=self.key_name)


class TempInstance():
    """
    Create a temporary EC2 Instance from a list of launch templates.
    If creating an EC2 instance with a launch template fails,
    then the next launch template given in the list will be used.
    If creating an EC2 instance with every launch templates fails,
    then the program will exit.

    On enter an Instance is created and tagged with a name. The Instance is
    returned after it is successfully running.

    On exit the Instance is terminated.

    Arguments:
        name: Name to tag Instance with.
        launch_template_names: A list of launch templates to be
                               used to create EC2 instances.
                               The launch templates will be used
                               in the order they are passed in.
        key_name: Name of Key Pair to associate Instance with.
        subnet_id: ID for subnet to launch Instance in.
    """

    def __init__(
        self,
        name: str,
        launch_template_names: List[str],
        key_name: str,
        subnet_id: str,
    ):
        self.name = name
        self.launch_template_names = launch_template_names
        self.key_name = key_name
        self.subnet_id = subnet_id
        self.instance = None

    def __launch_instance(self, index: int = 0):
        if index == len(self.launch_template_names):
            raise Exception('No instance can be launched.')

        try:
            logger.info(f'Launching instance {self.name} using template: {self.launch_template_names[index]}')
            self.instance = EC2_RESOURCE.create_instances(
                LaunchTemplate={'LaunchTemplateName': self.launch_template_names[index]},
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
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'InsufficientInstanceCapacity' or error_code == 'SpotMaxPriceTooLow':
                logger.error(f'The use of launch template: {self.launch_template_names[index]} failed.')
                return self.__launch_instance(index+1)
            else:
                raise

        logger.info(f'Waiting for instance {self.instance.instance_id} to be ready...')
    
        self.instance.wait_until_running()
        return self.instance

    def __enter__(self):
        try:
            return self.__launch_instance()
        finally:
            self.__exit__(*sys.exc_info())

    def __exit__(self, type, value, traceback):
        if self.instance:
            logger.info(f'Terminating instance {self.instance.instance_id}...')
            self.instance.terminate()
