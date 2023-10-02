#!/bin/bash

set -eaux

pushd ../lab/main/static/vue/assets/
mv index*.js app.js
mv index*.css app.css

popd
