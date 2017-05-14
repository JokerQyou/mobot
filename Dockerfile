FROM python:3-alpine
ADD . /mobot
WORKDIR /mobot
RUN pip install -r requirements.txt
CMD ["python", "bot.py"]
