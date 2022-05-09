import socketio
from app import app, api, encoder, socketio
import json
import os
import datetime

from flask import make_response, render_template, redirect, request, url_for, session, jsonify, send_from_directory, request
from flask_socketio import SocketIO, send, join_room, leave_room, rooms, emit


@socketio.on('join')
def on_join(data):
    channel = data['channel']
    password = data['pass']
    if (api.check_auth(ch_name=channel,viewPass=password,editPass=password)):
        join_room(channel)
        session["Auth"] = True #not secure, change later
        print("Auth Passed, Joined " + channel)
        emit("updateRoom", {'msg':"joined room: " + channel, 'sid':request.sid}, to=data['channel'])
    else:
        session["Auth"] = False
        send("Authentication Failed")
        print("Auth Failed")
    

@socketio.on('WordsChanged')
def on_WordsChanged(data):
    if session["Auth"] == True:
        emit("wordsResponse", {'words':data['words'], 'sid':request.sid}, to=data['channel'])
    else:
        print("Failed Auth in send")

@socketio.on('saveIconChange')
def on_WordsChanged(data):
    if session["Auth"] == True:
        emit("IconChanged", to=data['channel'])
    else:
        print("Failed Auth in send")




# @socketio.on('message')
# def handleMessage(msg):
#     print("Message: " + msg)
#     send(msg, broadcast=True)

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')
