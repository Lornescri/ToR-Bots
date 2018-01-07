#!/usr/bin/env bash
while true; do
	python3 StatsBot.py
	echo Bot died!
	echo Restarting in 5 Seconds...
	python3 MessageMe.py StatsBot offline
	sleep 5
done
