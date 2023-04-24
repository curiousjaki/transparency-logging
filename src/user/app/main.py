from flask import Flask
from waitress import serve
from process_tilt_ciphersmaug.logging import TiltLogger
import requests
from opentelemetry import trace
#from opentelemetry.instrumentation.requests import RequestsInstrumentor
import sqlite3

def initialize_db():
    db = sqlite3.connect("user.sqlite")
    cursor = db.cursor()
    with open("user.sql",mode="r") as f:
        cursor.executescript(f.read())
    db.close()

tracer = trace.get_tracer(__name__)
app = Flask(__name__)
initialize_db()
#RequestsInstrumentor().instrument()
# Create the tilt Logger
tl = TiltLogger("TILT",tracer)


@app.route('/user/<id>')
def user_information(id: int):
    address = request_address(id)
    user_information = get_user_information(id)
    return user_information | address

@tl.log(concept_name = "Combine User Data", tilt = {
    "data_disclosed": ["user.firstname","user.lastname","user.birthday","address.street","address.postcode","address.number"], 
    "purposes": ["personal data access"], 
    "legal_bases": ["GDPR-6-1-b"]
    }, msg = "Combine User Data")
def get_user_information(id: int):
    
    if int(id) > 1000:
        return {}
    else:
        db = sqlite3.connect("user.sqlite")
        result = {}
        for row in db.execute(f"SELECT * from user WHERE id == {id}"):
            id,lastname,firstname,email,sex,ip = row
            result["firstname"]=firstname
            result["lastname"]=lastname
            result["birthday"]=ip
            result["description"]=email
            break
        db.close()
        return result
    

@tl.log(concept_name = "Request User Address", tilt = {
    "data_disclosed": ["user.id"], 
    "purposes": ["personal data access"], 
    "legal_bases": ["GDPR-6-1-b"]
    }, msg = "Request User Address")
def request_address(id: int):
    with tracer.start_as_current_span("Request User Address"):
        response = requests.get(f"http://address-service/address/{id}")
        return response.json()

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8082)