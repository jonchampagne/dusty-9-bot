#!/bin/bash

# Installs or updates dependancies, then starts the program

# Make sure we've got pipenv installed
if ! [ -x `which pipenv` ]
then
	echo "Pipenv required! Please install pipenv."
	return 1
fi

# Install dependancies
pipenv install

# Run the program
pipenv run python ./bot.py
