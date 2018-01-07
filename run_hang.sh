#!/usr/bin/env bash
while true; do
	python3 HangBot.py
	echo Bot died!
	echo Restarting in 5 Seconds...
	python3 MessageMe.py HangBot offline
	sleep 5
done
