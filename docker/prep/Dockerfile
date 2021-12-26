FROM python:3.9

RUN apt-get update
RUN apt-get -y upgrade

WORKDIR /jobert

COPY ./app/ .

RUN pip install -r requirements-app.txt

CMD ["python", "prep.py"]