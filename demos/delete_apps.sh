#!/bin/bash

# Check if file exists
if [ ! -f "heroku_apps.txt" ]; then
    echo "File applist.txt not found"
    exit 1
fi

# Read file line by line and execute command
while IFS= read -r appname; do
    echo "Destroying Heroku app: $appname"
    heroku apps:destroy -a "$appname" --confirm "$appname"
done < "heroku_apps.txt"

#empty file
> "heroku_apps.txt"
> "save_links.txt"