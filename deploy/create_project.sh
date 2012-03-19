#!/bin/bash
template_url=https://template:template@git.ampad.de/django_template

project_name=$1

if [[ -z $project_name ]]; then
    echo "Usage: $0 project_name"
    exit 1
fi

if [[ -d $project_name ]]; then
    echo "Project folder already exists";
    exit 1
fi

GIT_SSL_NO_VERIFY=true git clone $template_url $project_name || (echo "Error while checking out project template" && exit 1);

if [[ ! -d $project_name ]]; then
    echo "Unable to cd into project folder";
    exit 1
fi
