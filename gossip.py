from flask import Flask, flash, request, redirect, session, url_for, render_template, session, abort
from threading import Thread
from flask.json import jsonify
from firebase import firebase
import pyrebase
from flask import request
import requests
from flask.ext.uuid import FlaskUUID

app = Flask(__name__)

var n = 5
var nodes = [];
var rumors = [];

def propagate(self, originURL):
    while true:
        for (peer in peers)
            q = getPeer(state)
            s = prepareMsg(state, q)
            <url> = lookup(q)
            send (<url>, s)
            time.sleep(n)
            
def createNode(self):
    var random_uuid = uuid.uuid4()
    var peers = generateRandomPeer()
    nodes.add({"id": random_uuid, "peers": peers})
    node = Thread()
    node.q = []
    node.messages = []
    node.wants = []
    node.propogate()
    node.handle()
    return random_uuid

    
def handle(id, msg):
    if msg.Rumor:
        msgs.push(msg)
    else if msg.Want:
        wants.push(msg)
        for (want in wants):
            var s = prepareMsg(state, w)
        var url = msg.Endpoint
        q.add(url)

if __name__ == "__main__":
#     app.secret_key = os.urandom(12)
    app.run()
