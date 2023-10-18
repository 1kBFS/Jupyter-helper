#!/usr/bin/env bash
set -Eeuo pipefail # Fail fast
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P) # location
python3 $script_dir/main.py $@
