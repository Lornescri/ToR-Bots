#!/usr/bin/env bash
while true; do
	python3 charlie_the_collector.py
	echo Bot died!
	echo Restarting in 5 Seconds...
	python3 MessageMe.py Charlie offline
	sleep 5
done
