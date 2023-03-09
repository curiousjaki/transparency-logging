from flask import Flask
from waitress import serve
from lorem_text import lorem
from tilt.logging import TiltLogger
#from tilt.pellucid import Pellucid

app = Flask(__name__)

# Create the tilt Logger
tl = TiltLogger("TILT")

#pellucid = Pellucid()
#pellucid.personal_data
#pellucid.purpose
#@pellucid.activity_name("Rechnung")
#@pellucid.data_disclosed(["firstname","name","address","payment_card"])
#@pellucid.purposes(["Rechnungslegung"])
#@pellucid.log()


@app.route('/')
@tl.log(concept_name = "HelloWorld", tilt = {"data_disclosed":["username"],"purposes":["marketing"],"legal_bases":["gdpr sec 4."]}, msg = "Logging")
def hello():
    e = {
        'id': "MYID",
        'value': lorem.sentence()
    }

    return e

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8089)