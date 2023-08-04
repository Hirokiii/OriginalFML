#!/bin/bash

# Define the directory and source
DIR="/home/hiroki/Projects/Personal/MegaData"
SOURCE="venv/bin/activate"

# Start a new tmux session in the background
tmux new-session -d -s my_session "cd $DIR && source $SOURCE; bash"

# Split the tmux session horizontally
tmux split-window -h -t my_session "cd $DIR && source $SOURCE; bash"

# Select pane 0 and split it vertically
tmux select-pane -t 0
tmux split-window -v -t my_session "cd $DIR && source $SOURCE; bash"

# Attach to the tmux session
tmux attach -t my_session
