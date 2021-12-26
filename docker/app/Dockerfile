FROM python:3.9

RUN apt-get update
RUN apt-get -y upgrade

# Prepare jobert in /jobert
WORKDIR /jobert

COPY ./app/ .

RUN pip install -r requirements-app.txt

# Run app.py on port 8080
ENV PORT=8080

EXPOSE 8080

CMD ["python", "app.py"]