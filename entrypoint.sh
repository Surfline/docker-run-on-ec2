#!/bin/bash
set -e
source activate run-on-ec2
python main.py "$@"
