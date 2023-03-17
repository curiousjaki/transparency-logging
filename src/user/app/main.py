from flask import Flask
from waitress import serve
from lorem_text import lorem
from process_tilt_ciphersmaug.logging import TiltLogger
import datetime
from opentelemetry import trace

tracer = trace.get_tracer(__name__)
app = Flask(__name__)

# Create the tilt Logger
tl = TiltLogger("TILT",tracer)


@app.route('/user/<id>')
def user_information(id: int):
    address = request_address(id)
    user_information = get_user_information(id, address)
    return user_information

@tl.log(concept_name = "Combine User Data", tilt = {
    "data_disclosed": ["firstname","lastname","birthday","address"], 
    "purposes": ["marketing"], 
    "legal_bases": ["gdpr sec 6."]
    }, msg = "Combine User Data")
def get_user_information(id: int, address):
    if(int(id)==1):
        return {
        "firstname":"ciph",
        "lastname":"smaug",
        "birthday": datetime.date(2000,1,1),
        "description": lorem.sentence()
        } | address
    else:
        return {}

def request_address(id: int):
    if(int(id)==1):
        return {
            "address": {
                "street":"Bundesallee",
                "number":"1A",
                "postcode":"12345"
                }
            }
    else:
        return {}

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8082)