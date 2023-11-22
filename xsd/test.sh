#!/bin/bash

set -e #exit on failure

function apply() { git apply "$@"; }

cd ..

for patch in xsd/patch-testing xsd/patch-testing-fail; do

    echo testing $patch

    apply $patch
    ./strava-cli.py gps --update-cache=false 9641066260 >xsd/test.gpx
    apply --reverse $patch
    xmlstarlet val --xsd xsd/gpxwrapper.xsd xsd/test.gpx
    #xmllint --schema xsd/gpxwrapper.xsd --noout xsd/test.gpx

    echo

done


