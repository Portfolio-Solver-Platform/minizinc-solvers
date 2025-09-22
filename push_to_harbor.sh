#!/bin/sh
HARBOR_URL ?= harbor.local

docker build -t minizinc-solver:latest .

docker tag minizinc-solver:latest harbor.local/psp/minizinc-solver:latest
docker push $HARBOR_URL/psp/minizinc-solver:latest