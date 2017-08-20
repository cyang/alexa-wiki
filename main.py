"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
from bs4 import BeautifulSoup
from urllib2 import Request, urlopen, HTTPError, URLError
import re

WIKI_URL = "https://en.wikipedia.org/wiki/"

SKILL_NAME = "Wiki Summary"
SAMPLE_PROMPT = "Please tell me a topic you want to look up by saying, " \
                    "get summary for Donald Trump. "
INTENT_NAME = "getWikiSummaryIntent"
WRONG_INPUT_PROMPT = "I'm not sure what your topic is. "

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + \
            session_started_request['requestId'] + \
            ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] + \
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] + \
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == INTENT_NAME:
        return get_wiki_summary(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif (intent_name == "AMAZON.StopIntent" or
            intent_name == "AMAZON.CancelIntent"):
        return get_halt_response()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] + \
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Functions that control the skill's behavior ------------------


def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the Alexa " + SKILL_NAME + " skill. " + SAMPLE_PROMPT

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = SAMPLE_PROMPT

    should_end_session = False
    return build_response(session_attributes, build_speechlet_response( \
        card_title, speech_output, reprompt_text, should_end_session))

def get_halt_response():
    """Stops skill"""
    return build_response({}, build_speechlet_response( \
        SKILL_NAME + " skill has been canceled", "", "", True))

def get_wiki_summary(intent, session):
    card_title = SKILL_NAME
    session_attributes = {}
    should_end_session = False

    if 'topic' in intent['slots']:
        slots = intent['slots']
        try:
            topic = slots['topic']['value']
        except KeyError, e:
            print('Key error - reason "%s"' % str(e))
            speech_output = "Please try again. With a non-empty or valid topic"
            reprompt_text = SAMPLE_PROMPT
            return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


        card_title += " for " + topic
        
        if topic == "":
            speech_output = 'Topic is empty. '
            speech_output += "Please try again."
            reprompt_text = SAMPLE_PROMPT

            return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

        req = WIKI_URL + topic.replace(" ", "_")
        try:
            print("Opening url " + req)
            response = urlopen(req)
            print("Opened url " + req)
        except HTTPError as e:
            speech_output = 'The server couldn\'t fulfill the request. '
            speech_output += "Please try again."
            reprompt_text = SAMPLE_PROMPT
            print('Error code: ', e.code)
        except URLError as e:
            speech_output = 'We failed to reach a server. '
            speech_output += "Please try again."
            reprompt_text = SAMPLE_PROMPT
            print('Reason: ', e.reason)
        else:
            # everything is fine
            soup = BeautifulSoup(response, 'html.parser')
            print("Opened soup")
            speech_output = soup.find("div", {"class" :
                'mw-parser-output'}).find("p",
                        recursive=False).get_text()
            print("Parsed soup")
            # Clean up output
            speech_output = re.sub(r'/.+?/', '', speech_output)
            speech_output = re.sub(r'\(.+?\)', '', speech_output)
            speech_output = re.sub(r'\{.+?\}', '', speech_output)
            speech_output = re.sub(r'\[.+?\]', '', speech_output)
            speech_output.replace('\\', '')
            reprompt_text = ""

            should_end_session = True;
    else:
        speech_output = WRONG_INPUT_PROMPT + "Please try again."
        reprompt_text = WRONG_INPUT_PROMPT + SAMPLE_PROMPT
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

