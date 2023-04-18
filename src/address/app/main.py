from flask import Flask
from waitress import serve
from process_tilt_ciphersmaug.logging import TiltLogger
from opentelemetry import trace
import sqlite3

def initialize_db():
    db = sqlite3.connect("address.sqlite")
    cursor = db.cursor()
    with open("addresses.sql",mode="r") as f:
        cursor.executescript(f.read())
    db.close()

tracer = trace.get_tracer(__name__)
app = Flask(__name__)
initialize_db()
# Create the tilt Logger
tl = TiltLogger("TILT",tracer)
@app.route('/address/<id>')
def address_information(id: int):
    address = get_address(id)
    return address

@tl.log(concept_name = "Gather User Address", tilt = {
    "data_disclosed": ["address.street","address.number","address.postcode"], 
    "purposes": ["marketing"], 
    "legal_bases": ["gdpr sec 6."]
    }, msg = "Gather User Address")
def get_address(id: int):
    if int(id) > 1000:
        return {}
    else:
        db = sqlite3.connect("address.sqlite")
        result = {}
        for row in db.execute(f"SELECT * from addresses WHERE id == {id}"):
            print(row)
            id,country,state,city,street,number,postcode = row
            result["street"]=street
            result["number"]=number
            result["postcode"]=postcode
            break
        db.close()
        return {"address":result}

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8083)