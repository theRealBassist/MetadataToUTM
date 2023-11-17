FROM python:3.11

ADD MetadataToUTM.py .

RUN pip install setuptools natsort GPSPhoto tablib importlib 

CMD {"python", "MetadataToUTM.py"}