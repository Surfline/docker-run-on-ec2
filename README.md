# Run on EC2

Executable Docker image for running commands on custom ephemeral EC2 instances defined by launch templates.

## Usage

Docker image creates a Key Pair and initializes an EC2 instance both with the `NAME` variable. The command is run on the EC2 instance via SSH using the Key Pair. The Key Pair is deleted and EC2 instance terminated upon success, kill, or failure of the command.

### Environment Variables

These variables can be [passed into the Docker run](https://docs.docker.com/engine/reference/commandline/run/#set-environment-variables--e---env---env-file) using the `-e` or `--env-file` flags:

- `NAME` - Used to name EC2 Key Pair and Instance. UUID is appended to the end.
- `LAUNCH_TEMPLATE_NAME` - Name of launch template to launch EC2 Instance.
- `SUBNET_ID` - ID for subnet to launch EC2 Instance in.
- `AWS_DEFAULT_REGION` - AWS region to launch EC2 Instance in.
- `AWS_ACCESS_KEY_ID` - AWS access key ID used to create EC2 Key Pair and Instance.
- `AWS_SECRET_ACCESS_KEY` - AWS secret access key used to create EC2 Key Pair and Instance.

### Example

```sh
$ cp .env.sample .env # Fill out .env file
$ docker pull surfline/run-on-ec2
$ docker run --rm -it --env-file=.env surfline/run-on-ec2 echo \"hello world\"

Creating key pair run-on-ec2-eb5f9910-1635-40e1-b120-0e08b06a60ce...
Launching instance run-on-ec2-eb5f9910-1635-40e1-b120-0e08b06a60ce...
Waiting for instance run-on-ec2-eb5f9910-1635-40e1-b120-0e08b06a60ce to be ready...
Running command "echo \"hello world\"" on 10.128.130.201...
hello world
Terminating instance run-on-ec2-eb5f9910-1635-40e1-b120-0e08b06a60ce...
Deleting key pair run-on-ec2-eb5f9910-1635-40e1-b120-0e08b06a60ce...
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

Creating key pair run-on-ec2-eb5f9910-1635-40e1-b120-0e08b06a60ce...
Launching instance run-on-ec2...
Waiting for instance run-on-ec2-eb5f9910-1635-40e1-b120-0e08b06a60ce to be ready...
Running command "echo \"hello world\"" on 10.128.130.201...
hello world
Terminating instance run-on-ec2-eb5f9910-1635-40e1-b120-0e08b06a60ce...
Deleting key pair run-on-ec2-eb5f9910-1635-40e1-b120-0e08b06a60ce...
```
