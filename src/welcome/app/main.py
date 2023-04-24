from flask import Flask
from waitress import serve
from process_tilt_ciphersmaug.logging import TiltLogger
import requests
import datetime
from opentelemetry import trace
#from opentelemetry.instrumentation.requests import RequestsInstrumentor
import sqlite3

def initialize_db():
    db = sqlite3.connect("welcome.sqlite")
    cursor = db.cursor()
    with open("login_time.sql",mode="r") as f:
        cursor.executescript(f.read())
    db.close()

tracer = trace.get_tracer(__name__)
app = Flask(__name__)
initialize_db()
#RequestsInstrumentor().instrument()
# Create the tilt Logger
tl = TiltLogger("TILT",tracer)


@app.route('/welcome/<id>')
def welcome_information(id: int):
    last_login = get_welcome_information(id)
    print(type(last_login))
    if last_login["last_login"]:
        last = datetime.datetime.strptime(last_login["last_login"],"%Y-%m-%d %H:%M:%S")
        easter = datetime.datetime.strptime("2022-04-01 12:00:00","%Y-%m-%d %H:%M:%S")
        if last < easter:
            send_marketing(id)
    return last_login

@tl.log(concept_name = "Inform Newsletter Service", tilt = {
    "data_disclosed": ["user.firstname","user.lastname","user.birthday","address.street","address.number","address.postcode"], 
    "purposes": ["newsletter"], 
    "legal_bases": ["GDPR-6-1-a"]
    }, msg = "Inform Newsletter Service")
def send_marketing(id):
    with tracer.start_as_current_span("Inform Newsletter Service"):
        response = requests.get(f"http://newsletter-service/newsletter/{id}")
        return response.json()


@tl.log(concept_name = "Read Last Login", tilt = {
    "data_disclosed": ["user.id"], 
    "purposes": ["welcome"], 
    "legal_bases": ["GDPR-6-1-b"]
    }, msg = "Read Last Login")
def get_welcome_information(id: int):
    if int(id) > 1000:
        return {}
    else:
        db = sqlite3.connect("welcome.sqlite")
        result = {}
        for row in db.execute(f"SELECT * from login_time WHERE id == {id}"):
            id,last_login = row
            result["last_login"]=last_login
            break
        db.close()
        return result

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8084)