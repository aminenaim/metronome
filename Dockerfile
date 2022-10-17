FROM python:3

WORKDIR /app

COPY requirements.txt ./
RUN apt-get update
RUN apt-get install libgl1 poppler-utils -y
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src .

CMD [ "python","-u", "./parser.py" ]