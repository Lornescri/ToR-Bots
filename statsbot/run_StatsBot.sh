#!/usr/bin/env bash
while true; do
	python3 StatsBot-2.0.0.py
	echo Bot died!
	echo Restarting in 5 Seconds...
	python3 MessageMe.py StatsBot offline
	sleep 5
done
