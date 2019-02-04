#!/bin/bash

# Installs or updates dependancies, then starts the program

# Make sure we've got pipenv installed
if ! [ -x `which pipenv` ]
then
	echo "Pipenv required! Please install pipenv."
	return 1
fi

# Kill any other instance of this bot
if [ -f pid ]; then
  kill `cat pid`
fi

# Install dependancies
pipenv install
echo

# Run the program
pipenv run python ./bot.py &
echo $! > pid
wait $!

# Remove the pid file if it's still our's
if [ -f pid ]; then
  if [ `cat pid` == $! ]; then
    rm pid
  fi
fi

