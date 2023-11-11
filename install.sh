#!/usr/bin/env bash
apt-get update
apt-get -y updrade
apt-get install -y tmux
apt-get install python3
python -m pip install jupyter
python -m pip install libtmux
python -m pip install tqdm
python -m pip install click