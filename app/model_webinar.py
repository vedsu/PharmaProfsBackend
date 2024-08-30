# Webinar Component

from app import mongo

class Webinar():

    @staticmethod
    def data_webinar(w_id, website):
        
        webinar_info = None
        try: 
            
            webinar_data = list(mongo.db.webinar_data.find({"$and":[{"webinar_url":w_id}, {"website":website}]}))
            webinar = webinar_data[0]
               
            webinar_data_dict ={
            
                    "id":webinar.get("id"),

                    "topic":webinar.get("topic"),
                    "industry":webinar.get("industry"),
                    "speaker":webinar.get("speaker"),
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
            webinar_info = webinar_data_dict
        except Exception as e:
            webinar_info = None
        
        return webinar_info
    
    @staticmethod
    def view_webinar():
        webinar_list = []
        try:
            webinar_data = list(mongo.db.webinar_data.find({"status":"Active"}).sort({"date_time":-1}))
            for webinar in webinar_data:
                webinar_dict = {

                "id":webinar.get("id"),

                "topic":webinar.get("topic"),
                "industry":webinar.get("industry"),
                "speaker":webinar.get("speaker"),
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

