#!/bin/bash
pushd `dirname $0` > /dev/null

docker rm -f red
bower install
docker build -t uji/red .
docker run -d -p 5000:5000 -v /opt/devel/workspaces/uji/red/data:/data --name red uji/red

popd > /dev/null
