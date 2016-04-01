#!/bin/bash
pushd `dirname $0` > /dev/null

docker-compose build
docker-compose up -d

popd > /dev/null
