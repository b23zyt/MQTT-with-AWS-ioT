#!/usr/bin/env bash
# stop script on error
set -e

# Check for python 3
if ! command -v python3 &> /dev/null; then
  printf "\nERROR: python3 must be installed.\n"
  exit 1
fi

# Set up virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  printf "\nCreating virtual environment...\n"
  python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip (recommended)
pip install --upgrade pip

# Download root CA if missing
if [ ! -f ./root-CA.crt ]; then
  printf "\nDownloading AWS IoT Root CA certificate from AWS...\n"
  curl -sS https://www.amazontrust.com/repository/AmazonRootCA1.pem -o root-CA.crt
fi

# Clone SDK repo if not already present
if [ ! -d "./aws-iot-device-sdk-python-v2" ]; then
  printf "\nCloning the AWS SDK...\n"
  git clone https://github.com/aws/aws-iot-device-sdk-python-v2.git --recursive
fi

# Install SDK if not already installed
if ! python3 -c "import awscrt" &> /dev/null; then
  printf "\nInstalling AWS SDK into virtual environment...\n"
  pip install ./aws-iot-device-sdk-python-v2
fi

# Run the sample app
printf "\nRunning pub/sub sample application...\n"
python3 aws-iot-device-sdk-python-v2/samples/pubsub.py \
  --endpoint aqu7583chrlrw-ats.iot.us-east-2.amazonaws.com \
  --ca_file root-CA.crt \
  --cert my_device.cert.pem \
  --key my_device.private.key \
  --client_id basicPubSub \
  --topic sdk/test/python \
  --count 0
