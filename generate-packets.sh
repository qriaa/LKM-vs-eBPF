#!/usr/bin/env bash

source ./pktgen-functions.sh

PGDEV=kpktgend_0

pg_set $PGDEV "rem_device_all"
pg_set $PGDEV "add_device enp0s3"
pg_ctrl "start"
