# Order Component
from app import mongo
from datetime import datetime, timedelta
import pytz
class Order():

    @staticmethod
    def update_order(order_data):

        try:
            mongo.db.order_data.insert_one(order_data)
            return ({"success": True, "message": "order placed successfully"}),201
        except Exception as e:
            return ({"success": False, "message": str(e)}), 403
        
    def find_order(customeremail):

        dashboard_list =[]
        try:
            orders = list(mongo.db.order_data.find({"customeremail":customeremail}))
            user_data = list(mongo.db.user_data.find({"email": customeremail}))
            if user_data:
                user = user_data[0]
                history_pending = user.get("history_pending") 
                history_purchased = user.get("history_purchased")
                
                
                for order in orders:
                    
                    live_url, recording_url, digitaldownload_url, transcript_url = None, None, None, None
                    topic = order.get("topic")
                    customeremail = order.get("customeremail")
                    paymentstatus = order.get("paymentstatus")
                    sessionLive = order.get("sessionLive") #True /False
                    sessionRecording = order.get("sessionRecording") # True/ False
                    sessionDigitalDownload = order.get('sessionDigitalDownload') # True or False
                    sessionTranscript = order.get("sessionTranscript") # True or False
                    customername = order.get("customername")
                    document = order.get("document")

                    if paymentstatus == "purchased":
                        projection ={"_id":0}
                        webinar_data  = list(mongo.db.webinar_data.find({"topic":topic}, projection))
                        if webinar_data:
                            webinar = webinar_data[0]
                            # print("YES")
                            date = webinar.get("date")
                            time = webinar.get("time")
                            topic = webinar.get("topic")
                            speaker = webinar.get("speaker")
                            date_time = str(webinar.get("date_time"))
                            timeZone = webinar.get("timeZone")
                            duration = webinar.get("duration")
                            urlLive = webinar.get("urlLive")
                            urlRecording = webinar.get("urlRecording")
                            urlDigitalDownload = webinar.get("urlDigitalDownload")
                            urlTranscript = webinar.get("urlTranscript")
                            handle_live = handle_timezone(date_time, timeZone)
                            handle_other = handle_othertimezone(date_time, timeZone)
                            
                            if sessionLive == "True" and handle_live:
                                live_url =  urlLive
                            if sessionRecording == "True" and handle_other:
                                recording_url = urlRecording
                            if sessionDigitalDownload == "True" and handle_other:
                                digitaldownload_url = urlDigitalDownload
                            if sessionTranscript == "True" and handle_other:
                                transcript_url = urlTranscript
                            
                            dashboard_dict = {
                            "customername":customername ,
                            "webinar" : topic,
                            "speaker" : speaker ,
                            "date" : date,
                            "time" : time,
                            "timeZone" : timeZone,
                            "duration" : duration,
                            "live_url" : live_url,
                            "recording_url": recording_url,
                            "digitaldownload_url": digitaldownload_url,
                            "transcript_url" : transcript_url,
                            "document" : document
                            }

                            dashboard_list.append(dashboard_dict)

                        
        except Exception as e:

                dashboard_list=[str(e)]

        return dashboard_list, history_pending, history_purchased


def handle_othertimezone(webinar_datetime_str,timeZone):
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
        is_more_than_24_hours = timedelta(24) < time_difference < timedelta(hours=1440)

        return is_more_than_24_hours
          



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
        is_within_next_24_hours = timedelta(0) < time_difference < timedelta(hours=24)

        return is_within_next_24_hours