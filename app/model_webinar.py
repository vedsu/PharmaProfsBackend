# Webinar Component

from app import mongo
from datetime import datetime

class Webinar():

    @staticmethod
    def data_webinar(w_id):
        
        
        try: 
            
            # webinar_data = list(mongo.db.webinar_data.find({"$and":[{"id":w_id}, {"website":"PHARMAPROFS"}]}))
            webinar_data = list(mongo.db.webinar_data.find({"$and":[{"webinar_url":w_id}, {"website":"PHARMAPROFS"}]})) 
            # webinar_data = list(mongo.db.webinar_data.find({}))
            # return webinar_data
            if webinar_data:
                webinar = webinar_data[0]
                # return webinar
                speaker = webinar.get("speaker")
                speaker_detail = mongo.db.speaker_data.find_one({"name":speaker},{"_id":0,"photo":1,"id":1})
                webinar_data_dict ={
                
                        "id":webinar.get("id"),

                        "topic":webinar.get("topic"),
                        "industry":webinar.get("industry"),
                        "speaker": speaker,
                        "speaker_id": speaker_detail.get("id"),
                        "speaker_image": speaker_detail.get("photo"),
                    
                        
                        "date":webinar.get("date_time"),
                        "time":webinar.get("time"),
                        "timeZone":webinar.get("timeZone"),
                        "duration":webinar.get("duration"),
                        "category":webinar.get("category"),
                        
                        "sessionLive":webinar.get("sessionLive"),
                        "priceLive":webinar.get("priceLive"),
                        "urlLive":webinar.get("urlLive"),
                        
                        "sessionRecording":webinar.get("sessionRecording"),
                        "priceRecording":webinar.get("priceRecording"),
                        "urlRecording":webinar.get("urlRecording"),

                        "sessionDigitalDownload":webinar.get("sessionDigitalDownload"),
                        "priceDigitalDownload":webinar.get("priceDigitalDownload"),
                        "urlDigitalDownload":webinar.get("urlDigitalDownload"),
                        
                        "sessionTranscript":webinar.get("sessionTranscript"),
                        "priceTranscript":webinar.get("priceTranscript"),
                        "urlTranscript":webinar.get("urlTranscript"),

                        "status":webinar.get("status"),
                        "webinar_url": webinar.get("webinar_url"),
                        "description":webinar.get("description"),

                        }
                return webinar_data_dict
        
        except Exception as e:
            
            return str(e)
        
        
    
    @staticmethod
    def view_webinar():
        webinar_list = []
        try:
            # Get the current date and time
            current_date = datetime.now()
            
            # Fetch and sort future webinars
            future_webinars = list(
                mongo.db.webinar_data.find({
                    "$and": [
                        {"status": "Active"},
                        {"website": "PHARMAPROFS"},
                        {"date_time": {"$gte": current_date}}
                    ]
                }).sort("date_time", 1)  # Sort in descending order
            )

            # Fetch and sort past webinars
            past_webinars = list(
                mongo.db.webinar_data.find({
                    "$and": [
                        {"status": "Active"},
                        {"website": "PHARMAPROFS"},
                        {"date_time": {"$lt": current_date}}
                    ]
                }).sort("date_time", -1)  # Sort in descending order
            )

            # Combine future and past webinars into a single list
            webinar_data = future_webinars + past_webinars
        
            # webinar_data = list(mongo.db.webinar_data.find({"$and":[{"status":"Active"},{"website":"HEALTHPROFS"}]}).sort({"date_time":-1}))
            for webinar in webinar_data:

                speaker = webinar.get("speaker")
                speaker_photo = mongo.db.speaker_data.find_one({"name":speaker},{"_id":0,"photo":1})
                webinar_dict = {

                "id":webinar.get("id"),

                "topic":webinar.get("topic"),
                "industry":webinar.get("industry"),
                "speaker":speaker,
                "speaker_image": speaker_photo.get("photo"),
                "website":webinar.get("website"),
                "date":webinar.get("date"),
                "time":webinar.get("time"),
                "timeZone":webinar.get("timeZone"),
                "duration":webinar.get("duration"),
                "category":webinar.get("category"),
                
                "sessionLive":webinar.get("sessionLive"),
                "priceLive":webinar.get("priceLive"),
                "urlLive":webinar.get("urlLive"),
                
                "sessionRecording":webinar.get("sessionRecording"),
                "priceRecording":webinar.get("priceRecording"),
                "urlRecording":webinar.get("urlRecording"),

                "sessionDigitalDownload":webinar.get("sessionDigitalDownload"),
                "priceDigitalDownload":webinar.get("priceDigitalDownload"),
                "urlDigitalDownload":webinar.get("urlDigitalDownload"),
                
                "sessionTranscript":webinar.get("sessionTranscript"),
                "priceTranscript":webinar.get("priceTranscript"),
                "urlTranscript":webinar.get("urlTranscript"),

                "status":webinar.get("status"),
                "webinar_url": webinar.get("webinar_url"),
                "description":webinar.get("description"),
                    
                    }
                webinar_list.append(webinar_dict)
        
        except Exception as e:
            
            webinar_list = []
        
        return webinar_list
