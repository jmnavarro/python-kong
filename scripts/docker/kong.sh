#!/bin/bash
docker run -d -p 8000:8000 -p 8001:8001 --name kong --link cassandra:cassandra vikingco/kong
