#!/bin/bash
if [ "$1" != 'flask' ]; then
    echo "usage: zsh ./cli.sh flask <command>"
    exit 1
fi
CONTAINER_ID="$(docker container ls | grep -i "pigeon-backend" | awk '{print $1}')"
if ((${#CONTAINER_ID} == 0)); then
    echo "pigeon-backend container not found. run docker-compose up to start pigeon!"
    exit 1
fi
docker exec -i $CONTAINER_ID "$@"