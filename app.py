from rauth import OAuth2Service
from flask import Flask, flash, request, redirect, session, url_for, render_template, session, abort
import os
from flask.json import jsonify
from firebase import firebase
import pyrebase
import re
import webbrowser
from flask import request
import requests
import json
import pprint

app = Flask(__name__)

foursquare = OAuth2Service(
                           client_id='2OCO5OCLZKWNOEPIHWYHTMWL2MQHTMHSKYKDDQNJLC4JMUZM',
                           client_secret='LSQJ44VLGONVTIY11ND52SGEP25IATFYROODVQ1WE4OLAJGH',
                           name='foursquare',
                           authorize_url='https://foursquare.com/oauth2/authenticate',
                           access_token_url='https://foursquare.com/oauth2/access_token',
                           base_url='https://api.foursquare.com/v2/')

redirect_uri = 'https://authentication201.herokuapp.com/callback'

params = {'response_type': 'token',
    'redirect_uri': redirect_uri}

authorize_url = 'https://foursquare.com/oauth2/authenticate?client_id=2OCO5OCLZKWNOEPIHWYHTMWL2MQHTMHSKYKDDQNJLC4JMUZM&response_type=code&redirect_uri=https://authentication201.herokuapp.com/callback'

config = {
  "apiKey": "AIzaSyAcdYepozWMh7M-AP--clyPmech8iZNsS8",
  "authDomain": "cs462-3.firebaseapp.com",
  "databaseURL": "https://cs462-3.firebaseio.com",
  "storageBucket": "cs462-3.appspot.com",
  "serviceAccount": "cs462-3-firebase-adminsdk-py5i6-007cbe15e0.json"
}

app.secret_key = '1234567'
firebase = pyrebase.initialize_app(config)
db = firebase.database()

@app.route("/")
def main():
    if not session.get('logged_in'):
        return render_template('index.html', users = db.child("users").get().val())
    else:
        userID=session['userID']
        return render_template('loggedIn.html', users = db.child("users").get().val(), profile = "/profile/" + userID)

@app.route("/logout")
def logout():
    session['logged_in'] = False
    session['userID'] = ""
    return main()

@app.route("/showSignUp")
def demo():
    return render_template('signup.html')
  
@app.route("/signUp", methods=['GET', 'POST'])
def signup():
    print("got into signUp, should redirect now...")
    return redirect('https://foursquare.com/oauth2/authenticate?client_id=2OCO5OCLZKWNOEPIHWYHTMWL2MQHTMHSKYKDDQNJLC4JMUZM&response_type=code&redirect_uri=https://authentication201.herokuapp.com/callback')


@app.route("/callback", methods=["GET"])
def callback():
    code = request.args.get('code')
    print('Code: ' + code);
    response = requests.get('https://foursquare.com/oauth2/access_token?client_id=2OCO5OCLZKWNOEPIHWYHTMWL2MQHTMHSKYKDDQNJLC4JMUZM&client_secret=LSQJ44VLGONVTIY11ND52SGEP25IATFYROODVQ1WE4OLAJGH&grant_type=authorization_code&redirect_uri=https://authentication201.herokuapp.com/callback&code='+code).json()
    print(response)
    access_token = response['access_token']
    print('Access Token: ' + access_token);
    
    
    user = requests.get('https://api.foursquare.com/v2/users/self?oauth_token='+ access_token +'&v=20170210').json()
    print(json.dumps(user, indent=2))
    userID = user['response']['user']['id']
    firstName = user['response']['user']['firstName']
    try:
      lastName = user['response']['user']['lastName']
      name = firstName + " " + lastName
    except KeyError:
      name = firstName
#     if 'lastName' in user:
#       name = firstName + " " + lastName
#     else:
#       name = firstName
    profilePic = user['response']['user']['photo']['prefix'] + "original" + user['response']['user']['photo']['suffix']
    try:
      email = user['response']['user']['contact']['email']
    except KeyError:
        email = ""
    checkins = requests.get('https://api.foursquare.com/v2/users/self/checkins?oauth_token='+ access_token +'&v=20170210').json()
    print(checkins['response']['checkins'])
    url = '/profile/' + userID
    data = {"name": name, "profilePic": profilePic, "email": email, "url": url, "checkins":checkins['response']['checkins'], "access_token":access_token}
    results = db.child("users").child(userID).set(data)
    session['logged_in'] = True
    session['userID'] = userID
#     return response
    return main()
 

@app.route("/profile/<userID>", methods=["GET"])
def profile(userID):
    print(userID)
    checkins = {}
    access_token = db.child("users").child(userID).child("access_token").get().val()
    checkinsResponse = requests.get('https://api.foursquare.com/v2/users/self/checkins?oauth_token='+ access_token +'&v=20170210').json()
    db.child("users").child(userID).child("checkins").set(checkinsResponse['response']['checkins'])
    name = db.child("users").child(userID).child("name").get().val()
    email = db.child("users").child(userID).child("email").get().val()
    profilePic = db.child("users").child(userID).child("profilePic").get().val()
    if (db.child("users").child(userID).child("checkins").child("count").get().val() > 0):
      for i in range (0, db.child("users").child(userID).child("checkins").child("count").get().val()):
        checkins[i] = {"name": db.child("users").child(userID).child("checkins").child("items").child(i).child("venue").child("name").get().val(), "address":db.child("users").child(userID).child("checkins").child("items").child(i).child("venue").child("location").child("city").get().val(), "catagory":db.child("users").child(userID).child("checkins").child("items").child(i).child("venue").child("categories").child("0").child("name").get().val()}
#     print(checkins)
    try:
      session['userID']
      if (userID == session['userID']):
        print('The Logged In User')
        return render_template('profile.html', name = name, email = email, profilePic = profilePic, userID = userID, checkins = checkins, checkinString = "Checkins")
      else:
        print('Not the Logged In User')
        if (db.child("users").child(userID).child("checkins").child("count").get().val() > 0):
          checkins = {"name": db.child("users").child(userID).child("checkins").child("items").child(0).child("venue").child("name").get().val()}
        return render_template('profile.html', name = name, email = email, profilePic = profilePic, userID = userID, checkins = checkins, checkinString = "Last Checkin", single = "single")
    except KeyError:
        if (db.child("users").child(userID).child("checkins").child("count").get().val() > 0):
          checkins = {"name": db.child("users").child(userID).child("checkins").child("items").child(0).child("venue").child("name").get().val()}
        return render_template('profile.html', name = name, email = email, profilePic = profilePic, userID = userID, checkins = checkins, checkinString = "Last Checkin", single = "single")
        

@app.route("/users", methods=["GET"])
def users():
  return jsonify(db.child("users").get().val());


if __name__ == "__main__":
#     app.secret_key = os.urandom(12)
    app.run()
