FROM python:3-alpine
ADD . /mobot
WORKDIR /mobot
RUN pip install -r requirements.txt
ENV REDIS_URL redis://redis_db:6379
CMD ["python", "-m", "mobot.bot"]
