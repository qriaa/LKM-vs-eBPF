#!/usr/bin/env bash

# Ensure sudo
if [ "$EUID" != 0 ]; then
    sudo "$0" "$@"
    exit $?
fi

MODULE_FILE='./nf-hook.ko'
MODULE_NAME='nf_hook'
FUNCTION_NAME='udp_logger'

insmod $MODULE_FILE

# add probes
sudo perf probe -m $MODULE_NAME --add "$FUNCTION_NAME"
sudo perf probe -m $MODULE_NAME --add "$FUNCTION_NAME%return"

iperf3 -s -1 &
IPERF_PID=$!

perf record -q -a -g -e "cycles" -e "probe:$FUNCTION_NAME" -e "probe:${FUNCTION_NAME}__return" &
PERF_PID=$!

wait $IPERF_PID
kill -s SIGINT $PERF_PID
wait $PERF_PID

# remove probes
sudo perf probe -m $MODULE_NAME --del "$FUNCTION_NAME"
sudo perf probe -m $MODULE_NAME --del "${FUNCTION_NAME}__return"

rmmod $MODULE_NAME
