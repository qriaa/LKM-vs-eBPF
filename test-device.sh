#!/usr/bin/env bash

# Ensure sudo
if [ "$EUID" != 0 ]; then
    sudo "$0" "$@"
    exit $?
fi

iperf3 -s -1 &
IPERF_PID=$!

perf record -q -a -g &
PERF_PID=$!

wait $IPERF_PID
kill -s SIGINT $PERF_PID
