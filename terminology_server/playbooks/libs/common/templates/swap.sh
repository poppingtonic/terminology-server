#!/usr/bin/env bash
set -euo pipefail

if [ ! -f /allocated_swapfile ]; then
    fallocate -l 2G /allocated_swapfile && chmod 600 /allocated_swapfile && mkswap /allocated_swapfile && swapon /allocated_swapfile
fi
