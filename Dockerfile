FROM python:3.11

WORKDIR /tmp/
ADD MetadataToUTM.py .
RUN python /tmp/setup.py install && pip install setuptools natsort GPSPhoto tablib importlib 

CMD {"python", "MetadataToUTM.py"}