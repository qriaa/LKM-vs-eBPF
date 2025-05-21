#!/usr/bin/env bash

source ./pktgen-functions.sh

THREAD=0
PGDEV=lo

pg_ctrl "reset"
pg_thread $THREAD "rem_device_all"
pg_thread $THREAD "add_device $PGDEV"

pg_set $PGDEV "flag IPSRC_RND"
pg_set $PGDEV "src_min 127.0.0.0"
pg_set $PGDEV "src_max 127.0.0.255"
pg_set $PGDEV "count 20000"

pg_ctrl "start"

cat /proc/net/pktgen/$PGDEV
