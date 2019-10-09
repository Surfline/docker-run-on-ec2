# Run on EC2

Executable Docker image for running commands on custom ephemeral EC2 instances defined by launch templates.

## Usage

Docker image creates a Key Pair and initializes an EC2 instance both with the `NAME` variable. The command is run on the EC2 instance via SSH using the Key Pair. The Key Pair is deleted and EC2 instance terminated upon success, kill, or failure of the command.

### Environment Variables

These variables can be [passed into the Docker run](https://docs.docker.com/engine/reference/commandline/run/#set-environment-variables--e---env---env-file) using the `-e` or `--env-file` flags:

- `NAME` - Used to name EC2 Key Pair and Instance. UUID is appended to the end.
- `LAUNCH_TEMPLATE_NAMES` - A comma separated list of launch templates to be used to
create EC2 instances. The launch templates will be used in the order they are passed in.
If creating an EC2 instance with a launch template fails, then the next launch template given
in the list will be used. If creating an EC2 instance with every launch templates fails,
then the program will exit.
Example: `launch-template-1,launch-template-2`
- `SUBNET_ID` - ID for subnet to launch EC2 Instance in.
- `AWS_DEFAULT_REGION` - AWS region to launch EC2 Instance in.
- `AWS_ACCESS_KEY_ID` - AWS access key ID used to create EC2 Key Pair and Instance.
- `AWS_SECRET_ACCESS_KEY` - AWS secret access key used to create EC2 Key Pair and Instance.

### Example

```sh
$ cp .env.sample .env # Fill out .env file
$ docker pull surfline/run-on-ec2
$ docker run --rm -it --env-file=.env surfline/run-on-ec2 echo \"hello world\"

Creating key pair run-on-ec2-5f8b4f4b-1a2b-45d5-9685-57f9d2794f9d...
Launching instance run-on-ec2...
Waiting for instance i-049278b0da448e7a2 to be ready...
Waiting for SSH to become available on 10.128.130.130...
Running command "echo "hello world "" on 10.128.130.130...
hello world
Closing SSH connection to 10.128.130.130...
Terminating instance i-049278b0da448e7a2...
Deleting key pair run-on-ec2-5f8b4f4b-1a2b-45d5-9685-57f9d2794f9d...
```

## Development

### Setup Environment

Use [Miniconda](https://conda.io/miniconda.html) to setup Python virtual environment.

```sh
$ conda env create -f environment.yml
$ source activate run-on-ec2
```

### Run Locally

```sh
$ cp .env.sample .env # Fill out .env file
$ env $(xargs < .env) python main.py echo \"hello world\"

Creating key pair run-on-ec2-5f8b4f4b-1a2b-45d5-9685-57f9d2794f9d...
Launching instance run-on-ec2...
Waiting for instance i-049278b0da448e7a2 to be ready...
Waiting for SSH to become available on 10.128.130.130...
Running command "echo "hello world "" on 10.128.130.130...
hello world
Closing SSH connection to 10.128.130.130...
Terminating instance i-049278b0da448e7a2...
Deleting key pair run-on-ec2-5f8b4f4b-1a2b-45d5-9685-57f9d2794f9d...
```
