FROM python:latest

#WORKDIR /
#ENV PYTHONPATH=/

COPY . .

RUN apt-get update && apt-get install -y
RUN pip install --upgrade pip
RUN apt install python3-opencv -y
RUN pip install -r requirements.txt

EXPOSE 8777

CMD ["python", "tyto.py"]

#CMD ["gunicorn", "-b","0.0.0.0:8777","run:app"]