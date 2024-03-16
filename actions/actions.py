from typing import Any, Text, Dict, List

import arrow
import dateparser
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
import psycopg2
import pandas as pd

city_db = {'brussels': 'Europe/Brussels',
           'zagreb': 'Europe/Zagreb',
           'london': 'Europe/Dublin',
           'lisbon': 'Europe/Lisbon',
           'amsterdam': 'Europe/Amsterdam',
           'seattle': 'US/Pacific'}

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

class ActionTellTime(Action):

    def name(self) -> Text:
        return "action_tell_time"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        current_place = next(tracker.get_latest_entity_values("place"), None)
        
        if not current_place:
            msg = f"You didn't specify the place"
            dispatcher.utter_message(text=msg)
            return []
        
        if current_place != 'Izola'.lower():
            msg = "You didn't enter the right place"
            dispatcher.utter_message(text=msg)
            return []

        cur.execute("SELECT * FROM event WHERE location LIKE '%izola%'")
        msg = ''
        # Fetch the results
        events = cur.fetchall()
        for event in events:
            msg = msg + event[1] + '\n'
        
        dispatcher.utter_message(text=msg)
        return []

class ActionRememberWhere(Action):
    def name(self) -> Text:
        return "action_remember_where"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        current_place = next(tracker.get_latest_entity_values("place"), None)
        utc = arrow.utcnow()

        if not current_place:
            msg = f"I didn't get where you lived. Are you sure it's spelled correctly?"
            dispatcher.utter_message(text=msg)
            return []
        
        tz_string = city_db.get(current_place, None)
        if not tz_string:
            msg = f"I didn't recognize {current_place}. Is it spelled correctly?"
            dispatcher.utter_message(text=msg)
            return []
        
        msg = f"Sure thing. I'll remember that you live in {current_place}."
        dispatcher.utter_message(text=msg)

        return [SlotSet("location", current_place)]
    

class ActionTimeDifference(Action):
    def name(self) -> Text:
        return "action_time_difference"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        timezone_to = next(tracker.get_latest_entity_values("place"), None)
        timezone_in = tracker.get_slot("location")

        if not timezone_in:
            msg = "To calculate the time difference I need to know where you live!"
            dispatcher.utter_message(text=msg)
            return []
        
        if not timezone_to:
            msg = "I didn't get the timezone you would like to compare with."
            dispatcher.utter_message(text=msg)
            return []
        
        tz_string = city_db.get(timezone_to, None)
        if not tz_string:
            msg = f"I didn't recognize the {timezone_to}."
            dispatcher.utter_message(text=msg)
            return []
        

        t1 = arrow.utcnow().to(city_db[timezone_in])
        t2 = arrow.utcnow().to(city_db[timezone_to])

        max_t, min_t = max(t1, t2), min(t1, t2)
        diff_seconds = dateparser.parse(str(max_t)[:19]) - dateparser.parse([min_t][:19])
        diff_hours = int(diff_seconds.seconds/3600)

        msg = f"There is a {min(diff_hours, 24-diff_hours)}H time difference"
        dispatcher.utter_message(text=msg)

        return[]