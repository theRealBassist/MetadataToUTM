FROM python:3.11

ADD MetadataToUTM.py .

run pip install natsort GPSPhoto tablib importlib

CMD {"python", "MetadataToUTM.py"}