#!/bin/bash
pushd `dirname $0` > /dev/null

docker rm -f red
bower install
docker build -t uji/red .
docker run -d -p 5002:5002 --name red uji/red

popd > /dev/null
