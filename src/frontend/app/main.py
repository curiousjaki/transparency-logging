from flask import Flask
from waitress import serve
from process_tilt_ciphersmaug.logging import TiltLogger
import concurrent.futures
import datetime
import requests
#from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry import trace


app = Flask(__name__)

#RequestsInstrumentor().instrument()


# Acquire a tracer
tracer = trace.get_tracer(__name__)
# Create the tilt Logger
tl = TiltLogger("TILT",tracer)

@app.route('/user/<id>')
@tl.log(concept_name = "Process User Request", tilt = {
    "data_disclosed": ["user.id"], 
    "purposes": ["personal data access"], 
    "legal_bases": ["GDPR-6-1-b"]
    }, msg = "Process User Request")
def user_information(id: int):
    #with concurrent.futures.ThreadPoolExecutor() as executor:
    #    future_user_info = executor.submit(get_user_information, id)
    #    future_last_access = executor.submit(get_last_access, id)
    return respond_user_information(get_user_information(id),get_last_access(id))#future_user_info.result(),future_last_access.result())

@tl.log(concept_name = "Send Data to User", tilt = {
    "data_disclosed": ["user.id"], 
    "purposes": ["personal data access"], 
    "legal_bases": ["GDPR-6-1-b"]
    }, msg = "Send Data to User")
def respond_user_information(info,last_accessed):
    return info|last_accessed

def get_user_information(id):
    with tracer.start_as_current_span("Process User Request 1"):
        response = requests.get(f"http://user-service/user/{id}")
        return response.json()

def get_last_access(id):
    with tracer.start_as_current_span("Process User Request 2"):
        response = requests.get(f"http://welcome-service/welcome/{id}")
        return response.json()

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8081)