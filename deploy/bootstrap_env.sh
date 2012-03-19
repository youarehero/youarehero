#!/bin/bash

project_name=$1

if [[ -z $project_name ]] 
then echo "Usage: $0 project_name" && exit 1;
fi

git clone https://template:template@git.ampad.de/var/git/django_template $project_name
cd $project_name
