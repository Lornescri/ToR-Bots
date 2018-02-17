#!/usr/bin/env bash
while true; do
	python3 reddit_stats.py
	echo Bot died!
	echo Restarting in 5 Seconds...
	python3 MessageMe.py reddit_stats offline
	sleep 5
done
