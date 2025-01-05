#!/bin/bash
export HOSTPORT=5432
export CONTAINERPORT=5432
export IMAGE="taxi"
export CONTAINERNAME="nyc_taxi"

#password comes from .env file, ignoring comments
export $(grep -v '^#' docker_password.env | xargs)

sudo docker run --rm -d --name $CONTAINERNAME -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD -p $HOSTPORT:$CONTAINERPORT $IMAGE
