#!/bin/bash
eval $(ssh-agent)
git add *.png
git commit -m "New graph"
git push

