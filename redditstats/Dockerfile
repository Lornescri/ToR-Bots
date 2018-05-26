FROM python:3.6.5-slim-jessie
RUN mkdir /redditstats
WORKDIR /redditstats
ADD requirements.txt /redditstats/
RUN pip install -r requirements.txt
ADD . /redditstats/
CMD python3 reddit_stats.py
