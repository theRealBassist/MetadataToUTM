FROM python:3.11

ADD MetadataToUTM.py .
RUN pip install natsort GPSPhoto tablib  

CMD {"python", "MetadataToUTM.py"}