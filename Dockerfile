FROM python:3.11

ADD MetadataToUTM.py .
RUN python /usr/local/lib/python3.11/site-packages/setuptools/setup.py install && pip install setuptools natsort GPSPhoto tablib importlib 

CMD {"python", "MetadataToUTM.py"}