from flask import Flask
from waitress import serve
from process_tilt_ciphersmaug.logging import TiltLogger
import requests
from opentelemetry import trace
import sqlite3
import json

tracer = trace.get_tracer(__name__)
app = Flask(__name__)
# Create the tilt Logger
tl = TiltLogger("TILT",tracer)

@app.route('/newsletter/<id>')
def process_newsletter(id: int):
    get_newsletter_information(id)
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@tl.log(concept_name = "Send Newsletter", tilt = {
    "data_disclosed": ["user.firstname","user.lastname","address.street","address.number","address.postcode"], 
    "purposes": ["newsletter"], 
    "legal_bases": ["GDPR-6-1-a"]
    }, msg = "Send Newsletter")
def get_newsletter_information(id: int):
    pass
    
if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8085)