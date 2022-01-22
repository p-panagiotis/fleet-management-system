FROM python:3.10.1

WORKDIR /publisher

COPY ./requirements.txt /publisher/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /publisher/requirements.txt

COPY ./.env /publisher
COPY ./database /publisher/database
COPY ./publisher/publisher.py /publisher

CMD ["python", "/publisher/publisher.py"]
