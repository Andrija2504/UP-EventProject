from typing import Any, Text, Dict, List

import arrow
import dateparser
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, FollowupAction
from rasa_sdk.executor import CollectingDispatcher
import psycopg2
import pandas as pd

city_db = {'brussels': 'Europe/Brussels',
           'zagreb': 'Europe/Zagreb',
           'london': 'Europe/Dublin',
           'lisbon': 'Europe/Lisbon',
           'amsterdam': 'Europe/Amsterdam',
           'seattle': 'US/Pacific',
           'izola': 'Europe/Slovenia',
           'ljubljana': 'Europe/Slovenia'}

# Connect to your database
conn = psycopg2.connect(
    dbname='test', 
    user='postgres', 
    password='', 
    host='localhost',
    client_encoding='UTF8'
)

# Open a cursor to perform database operations
cur = conn.cursor()
cur.execute("SET client_encoding TO 'UTF8'")

class ActionAskEventName(Action):
    def name(self):
        return "action_what_is_event_name"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Get the current intent
        current_intent = tracker.latest_message['intent'].get('name')
        print(current_intent)
        # Prompt the user for the event name
        dispatcher.utter_message(text="What event are you talking about?")

        # Return a SlotSet event to save the current intent
        return [SlotSet("last_intent_slot", current_intent)]

class ActionAskAreaName(Action):
    def name(self):
        return "action_where_are_you_going"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Get the current intent
        current_intent = tracker.latest_message['intent'].get('name')
        print(current_intent)

        # Prompt the user for the event name
        dispatcher.utter_message(text="Where are you going?")

        # Return a SlotSet event to save the current intent
        return [SlotSet("last_intent_slot", current_intent)]

class ActionRememberArea(Action):
    def name(self) -> Text:
        return "action_remember_area"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        areaName = next(tracker.get_latest_entity_values("place"), None)
        last_intent = tracker.get_slot("last_intent_slot")

        # Here you would handle the event name, e.g., validate it or fetch relevant information
        if not areaName:
            msg = f"I didn't get the event name. Could you please repeat that?"
            dispatcher.utter_message(text=msg)
            return []
        
        tz_string = city_db.get(areaName, None)
        if not tz_string:
            msg = f"I didn't recognize {areaName}. Is it spelled correctly?"
            dispatcher.utter_message(text=msg)
            return []

        SlotSet("place_slot", areaName)

        print(f"Last intent is {last_intent}")
        # Based on the last intent, trigger the appropriate follow-up action
        if last_intent == "general_information":
            return [FollowupAction("return_events")]

        return []

class ActionHandleEventName(Action):
    def name(self):
        return "action_remember_event"

    def run(self, dispatcher, tracker, domain):
        eventName = next(tracker.get_latest_entity_values("event"), None)
        last_intent = tracker.get_slot("last_intent_before_eventname")

        # Here you would handle the event name, e.g., validate it or fetch relevant information
        if not eventName:
            msg = f"I didn't get the event name. Could you please repeat that?"
            dispatcher.utter_message(text=msg)
            return []
        
        tz_string = city_db.get(eventName, None)
        if not tz_string:
            msg = f"I didn't recognize {eventName}. Is it spelled correctly?"
            dispatcher.utter_message(text=msg)
            return []
        
        SlotSet("eventname_slot", eventName)

        # Based on the last intent, trigger the appropriate follow-up action
        if last_intent == "ticket_information":
            return [FollowupAction("give_ticket_information")]
        elif last_intent == "location_information":
            return [FollowupAction("give_location_information")]
        elif last_intent == "datetime_inforation":
            return [FollowupAction("give_datetime_information")]
        # Add more conditions for other intents

        return []

class ActionGeneralInformation(Action):
    def name(self) -> Text:
        return "return_events"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        areaName = tracker.get_slot("place_slot")
        
        cur.execute(f"SELECT * FROM event WHERE location LIKE '%{areaName}%'")
        msg = ''
        # Fetch the results
        events = cur.fetchall()
        for event in events:
            msg = msg + event[1] + '\n'
        
        dispatcher.utter_message(text=msg)

        return[]

class ActionTicketInformation(Action):
    def name(self) -> Text:
        return "give_ticket_information"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        eventname = tracker.get_slot("eventname_slot")
        
        cur.execute(f"SELECT * FROM event WHERE location LIKE '%{eventname}%'")
        msg = ''
        # Fetch the results
        events = cur.fetchall()
        for event in events:
            msg = msg + event[1] + '\n'
        
        dispatcher.utter_message(text=msg)

        return[]