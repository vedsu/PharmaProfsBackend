# Speaker Component
from app import mongo
import pytz
from datetime import datetime, timedelta

class Speaker():

    @staticmethod
    def data_speaker(s_id):
        
        speaker_info = None  
        try:
            speaker_data = list(mongo.db.speaker_data.find({"id":s_id}))
            speaker = speaker_data[0]
            speaker_dict={
                "id": speaker.get("id"),
                "name": speaker.get("name"),
                "email":speaker.get("email"),
                "industry": speaker.get("industry"),
                "status": speaker.get("status"),
                "bio": speaker.get("bio"),
                "contact" :speaker.get("contact"),
                "photo": speaker.get("photo"),
                "history": speaker.get("history")
            }
            
            speaker_info = speaker_dict
        except Exception as e:
            speaker_info = None 
            
        
        return speaker_info
    
    
    @staticmethod
    def view_speaker():

        speaker_list =[]

        try:
            speaker_data = list(mongo.db.speaker_data.find({}).sort({"name":1}))
            for speaker in speaker_data:
                speaker_dict ={
                "id":speaker.get("id"),
                "name":speaker.get("name"),
                "email":speaker.get("email"),
                "contact": speaker.get("contact"),
                "industry":speaker.get("industry"),
                "status":speaker.get("status"),
                "bio":speaker.get("bio"),
                "photo": speaker.get("photo")
                }
                speaker_list.append(speaker_dict)
        except Exception as e:
            speaker_list =[ ]

        return speaker_list
    
    @staticmethod
    def speakerdashboard_data(email):
        dashboard_list = [] 
        try:
            speaker_data = list(mongo.db.speaker_data.find({"email":email}))
            speaker = speaker_data[0]
            history =  speaker.get("history")
            name = speaker.get("name")
            for topic in history:
                
                webinar_data  = list(mongo.db.webinar_data.find({"topic":topic}))
                if webinar_data:
                    # dashboard_list.append(topic)
                    webinar = webinar_data[0]
                

                    if webinar.get("speaker") == name:
                            date =  str(webinar.get("date_time"))
                            timezone = webinar.get("timeZone")
                            urlreturn = handle_timezone(date, timezone)
                            
                            if urlreturn is True:
                                urlLive = webinar.get("urlLive")
                            
                            else:
                                urlLive = ""
                            
                            
                            webinar_dict ={
                                
                                "webinar": topic,
                                "date": webinar.get("date"),
                                "time": webinar.get("time"),
                                "timeZone" : timezone,
                                "duration": webinar.get("duration"),
                                "urlLive": urlLive,
                                "website": webinar.get("website")
                            
                            }

                            dashboard_list.append(webinar_dict)

        except Exception as e:
            dashboard_list = [str(e)]

        return dashboard_list,history


def handle_timezone(webinar_datetime_str,timeZone):
        # Parsing the date and time string with timezone information
        try:
            webinar_datetime = datetime.fromisoformat(webinar_datetime_str.replace("Z", "+00:00"))
        except ValueError:
            return True

        # Time zones dictionary
        time_zones = {
            'PST': 'America/Los_Angeles',
            'EST': 'America/New_York',
            'IST': 'Asia/Kolkata',
            'UTC': 'UTC',
            'CST': 'America/Chicago'
        }

        # Validate the timeZone input
        if timeZone not in time_zones:
            return True
        
        # Convert to the specified timezone
        webinar_tz = pytz.timezone(time_zones[timeZone])
        webinar_datetime = webinar_datetime.astimezone(webinar_tz)

        # Convert to UTC
        webinar_datetime_utc = webinar_datetime.astimezone(pytz.UTC)

        # Get the current time in UTC
        current_datetime_utc = datetime.now(pytz.UTC).replace(second=0, microsecond=0)

        # Calculate the time difference
        time_difference = webinar_datetime_utc - current_datetime_utc

        # Check if the webinar is within the next 24 hours
        is_within_next_48_hours = timedelta(0) < time_difference < timedelta(hours=48)

        return is_within_next_48_hours
        




            
