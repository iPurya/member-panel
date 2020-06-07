#!/usr/bin/env bash
sudo apt-get -y update && sudo apt-get -y upgrade
sudo apt-get -y install git wget screen tmux make unzip redis-server software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get -y update
sudo apt-get -y install python3.8
sudo apt-get -y install python3.8-dev
sudo apt-get -y install python3.8-distutils
wget https://bootstrap.pypa.io/get-pip.py
python3.8 get-pip.py
sudo rm -rf get-pip.py
pip3.8 install setuptools
pip3.8 install pyrogram[fast]
pip3.8 install -U tgcrypto
pip3.8 install -U requests[socks]
pip3.8 install redis
pip3.8 install bs4
pip3.8 install pyTelegramBotAPI
pip3.8 install fake_useragent
RED='\033[0;31m'
echo -e "${RED}Installed Requirements!${NC}"
exit