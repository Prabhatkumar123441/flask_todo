FROM python:3.8
RUN apt update
EXPOSE 5000
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]