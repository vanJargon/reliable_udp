#!/bin/bash

sudo python topo.py --bw-host 1000 \
                --bw-net 1.5 \
                --delay 10 \
                --dir ./ \
                --nflows 1 \
                --maxq 100 \
                -n 5 \


