FROM python:3.9

RUN apt-get update
RUN apt-get -y upgrade

# Install and configure cron
RUN apt-get install -y cron

WORKDIR /jobert

# Copy and run scripts daily
COPY ./scrape/ .

RUN printf '00 12 * * * /usr/local/bin/python /jobert/scrape.py \n' >> /etc/cron.d/scrape-cron

RUN crontab /etc/cron.d/scrape-cron

RUN pip install -r requirements-scrape.txt

CMD ["cron", "-f"]