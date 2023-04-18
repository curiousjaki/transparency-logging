from flask import Flask
from waitress import serve
from process_tilt_ciphersmaug.logging import TiltLogger
import concurrent.futures
import datetime
import requests
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry import trace


app = Flask(__name__)

RequestsInstrumentor().instrument()


# Acquire a tracer
tracer = trace.get_tracer(__name__)
# Create the tilt Logger
tl = TiltLogger("TILT",tracer)

@app.route('/user/<id>')
@tl.log(concept_name = "HelloWorld", tilt = {
    "data_disclosed": ["username"], 
    "purposes": ["marketing"], 
    "legal_bases": ["gdpr sec 4."]
    }, msg = "Getting User Information")
def user_information(id: int):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_user_info = executor.submit(get_user_information, id)
        future_last_access = executor.submit(get_last_access, id)
    return future_user_info.result()|future_last_access.result()

def get_user_information(id):
    with tracer.start_as_current_span("GetUserInformation") as user_span:
        response = requests.get(f"http://user-service/user/{id}")
    return response.json()

def get_last_access(id):
    response = requests.get(f"http://welcome-service/welcome/{id}")
    return response.json()

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8081)
    #0x3a4eebf6dc087bc65b711b5651d46cb1