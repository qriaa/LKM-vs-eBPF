#!/usr/bin/env bash

. .env

iperf3 -u -4 -A 15 -b 1000M -t 10 -c "$REMOTE_ADDR"
