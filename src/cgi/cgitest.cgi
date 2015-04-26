#!/bin/sh
echo "content-type: text/plain"
echo
env
( cd .. && ./oldest )
