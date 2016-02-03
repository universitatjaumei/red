#!/bin/bash
pushd `dirname $0` > /dev/null

bower install
docker-compose build
docker-compose --x-networking up

popd > /dev/null
