from flask import Flask
from waitress import serve
from lorem_text import lorem
from fluent import sender
from fluent import event
sender.setup('fluentd.test')

app = Flask(__name__)

@app.route('/')
def hello():
    e = {
        'id': "MYID",
        'value':  lorem.sentence() 
        }
    event.Event('follow', e)
    return e

if __name__ == "__main__":
    serve(app)