# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views import generic
from django.http.response import HttpResponse
from django.shortcuts import render

import json, requests, random, re
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from pprint import pprint
from chatbot import settings

# Create your views here.
class FbBotView(generic.View):

    post_message_url = 'https://graph.facebook.com/v2.6/me/thread_settings?access_token=%s' %(settings.FACEBOOK_PAGE_ACCESS_TOKEN)
    response_msg = json.dumps({"setting_type":"greeting","greeting":{"text": "This is greeting text"}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    pprint(status.json())

    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == '123456789123456789':
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse("Error, invalid token")

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    def init_feedback(self):
        feedback = {}
        feedback['title'] = 'Facebook messenger feedback'
        feedback['address'] = ''
        feedback['description'] = ''
        feedback['phase'] = 0
        feedback['lat'] = ''
        feedback['long'] = ''
        feedback['media'] = ''
        feedback['timestamp'] = ''
        return feedback

    def check_input(self, phase, user_input):
        user_input = user_input.lower()
        if phase == 0:
            string_length = len(user_input)
            if (string_length > 10) and (string_length < 5000):
                return True
            return False

        elif phase == 1 or phase == 3 or phase == 5:
            user_input.strip(',.-!?:;')
            accept_answers = ['kyllä', 'joo', 'juu', 'k']
            decline_answers = ['ei', 'e']
            for user_input in accept_answers:
                return True
            for user_input in decline_answers:
                # feedback['phase'] = phase+2
                # save_to_database(feedback)
                return True
            return False

        # elif phase == 2:
        #     #Tarkistetaan, että Käyttäjä on lisännyt kuvan joko puhelimestaan tai suorana linkkinä.
        # elif phase == 4:
        #     # Tarkistetaan, että käyttäjä on jakanut sijainnin
        # elif phase == 6:
        #     # Tarkistetaan, että käyttäjä on kirjoittanut jonkin osoitteen
        return True

    # Post function to handle Facebook messages
    def post(self, request, *args, **kwargs):
        feedback = self.init_feedback()
        # Converts the text payload into a python dictionary
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                # Check to make sure the received call is a message call
                # This might be delivery, optin, postback for other events 
                if 'message' in message:
                    pprint(message)
                    if (self.check_input(0, message['message']['text'])):
                        post_facebook_message(message['sender']['id'], feedback['title'])
                    # Assuming the sender only sends text. Non-text messages like stickers, audio, pictures
                    # are sent as attachments and must be handled accordingly. 


                    # if message['message']['text'] == 'echo':
                    #     post_facebook_message(message['sender']['id'], message['message']['text'])
                    # else:
                    #     post_facebook_message(message['sender']['id'], 'couldn\'t echo that')
        return HttpResponse()

def post_facebook_message(fbid, recevied_message):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s' %(settings.FACEBOOK_PAGE_ACCESS_TOKEN)
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":recevied_message}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    pprint(status.json())
