FROM python:3.9-slim-buster
WORKDIR /usr/src/app
COPY requirements.txt ./
ENV PORT=8501
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app .
EXPOSE ${PORT}
ENTRYPOINT ["streamlit", "run", "Readme.py", "--server.port=8501", "--server.address=0.0.0.0"]