#!/usr/bin/env sh

pgset() {
    local result
    echo $1 > $PGDEV
    result=`cat $PGDEV | grep 'Result: OK:'`
    if [ "$result" = "" ]; then
        cat $PGDEV | grep Result:
    fi
}

PGDEV=/proc/net/pktgen/kpktgend_0

pgset "rem_device_all"
pgset "add_device enp0s3"
