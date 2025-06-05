#!/usr/bin/env bash

. .env

rsync -r * "$REMOTE_USER@$REMOTE_ADDR:/LKM-vs-eBPF"
