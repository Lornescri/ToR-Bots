FROM python:3.6.5-slim-jessie
RUN mkdir /bot
WORKDIR /bot
ADD requirements.txt /bot/
RUN pip install -r requirements.txt
ADD . /bot/
RUN chmod +x ./run_StatsBot.sh
RUN ls
CMD python3 StatsBot-2.0.0.py
