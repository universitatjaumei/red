#!/bin/bash
pushd `dirname $0` > /dev/null

bower install
docker-compose build
docker-compose up -d

popd > /dev/null
