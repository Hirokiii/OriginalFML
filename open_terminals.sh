#!/bin/bash

# Define the directory and source
DIR="/home/hiroki/Projects/Personal/MegaData"
SOURCE="venv/bin/activate"

# Open 3 terminals and run your commands
for i in {1..3}
do
    gnome-terminal -- bash -c "cd $DIR && source $SOURCE && cd src; exec bash"
done
