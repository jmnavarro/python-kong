#!/bin/bash
# Script provided by Circle support to reliably ensure that Cassandra has been started
set -x
set -e

echo "describe cluster;" > /tmp/dc
for i in {1..5}; do
  echo Attempt $i
  if [ "$(nodetool status | grep 127.0.0.1 | grep ^UN)" ]; then
    exit 0
  else
    sudo service cassandra stop; sudo service cassandra start
    sleep 10
  fi
done
exit 1
