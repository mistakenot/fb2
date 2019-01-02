FROM python:3.7.2-stretch

RUN pip install facebook-sdk

ADD ./run.py /run.py

RUN chmod +x /run.py

ENTRYPOINT python /run.py