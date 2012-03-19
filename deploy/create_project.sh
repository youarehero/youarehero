#!/bin/bash

project_name=$1

if [[ -z $project_name ]]; then
    echo "Usage: $0 project_name"
    exit 1
fi

git clone --depth 1 https://template:template@git.ampad.de/var/git/django_template $project_name || echo "Error while checking out project template" && exit 1;

if [[ ! -d $project_name ]]; then
    echo "Unable to cd into project folder";
    exit 1
fi

cd $project_name

#sed -i .git/config/
