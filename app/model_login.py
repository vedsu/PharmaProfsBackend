from app import mongo
from app import mail
from flask_mail import Message
from flask import render_template_string

class Login():

    @staticmethod
    def register(register_name,register_email,register_role,register_number,register_password,register_type,website):
        
        websiteUrl = "https://pharmaprofs.com/"
        
        user = mongo.db.user_data.find_one({"email":register_email})
        
        if user:
            return ({"success":False, "message":"User already registered, Please Login"}),203
        else:
            try:
                msg = Message('Your Account Credentials', sender = 'registration@pharmaprofs.com', recipients = [register_email])
                    
                msg.body = f"""
                                   Dear Customer {register_name},

                                   Welcome to our website!

                                   Here are your account credentials:

                                   Email: {register_email}
                                   Password: {register_password}
                                   Website: {websiteUrl}

                                   Please keep this information secure and do not share it with anyone.

                                   Thanks & Regards!
                                   Webinar Organizer Team
                                   
                                   """
                msg.html = render_template_string("""
                                   <p>Dear Customer {{name}},</p>
                                   <p>Welcome to our website!</p>
                                   <p>Here are your account credentials:</p>
                                   <ul>
                                        <li><b>Email:</b> {{ email }}</li>
                                        <li><b>Password:</b> {{ password }}</li>
                                        <li><b>Website:</b> <a href="{{ website }}">{{ website }}</a></li>
                                   </ul>
                                   <p>Please keep this information secure and do not share it with anyone.</p>
                                   <p>Thanks & Regards!<br>Webinar Organizer Team</p>
                                   """, name = register_name,email=register_email, password=register_password, website=websiteUrl)
                mail.send(msg)
                user = {"name":register_name,"role":register_role,"email":register_email,"contact":register_number}
                if register_type == "Attendee":
                    
                    try:
                        
                        mongo.db.user_data.insert_one({"name":register_name,"role":register_role,"email":register_email,"contact":register_number, "password":register_password,
                                                        "UserType": register_type, "website":website,
                                                        "history_purchased":[], "history_pending":[],"newsletter_purchased":[], "newsletter_pending":[] })
                        return  ({"success": True, "message":user}),201
                    except Exception as e:
                        return ({"success":False, "message":"Error in registering user"}),203
                else:
                    
                    try:
                            mongo.db.user_data.insert_one({"name":register_name,"role":register_role,"email":register_email,"contact":register_number, "password":register_password, "UserType": register_type, "website":website})
                            return ({"success": True, "message": user}),201
                    except Exception as e:
                            return ({"success": False, "message": str(e)}),203

            except Exception as e:
                return({"success":False, "message":str(e)}),203
    
    @staticmethod
    def authenticate(login_email, login_password, login_type, website):

        try:
            # user = mongo.db.user_data.find_one({"email":login_email, "password": login_password, "UserType": login_type,"website":website})
            
            user = mongo.db.user_data.find_one({"email":login_email, "password": login_password, "UserType": login_type,"website":website},{"_id":0})
            if user:
                # return ({"success": True, "message": "login successfull"}),200
                return ({"success": True, "message": user}),200
            else:
                return ({"success": False, "message": "invalid credentials"}),203
            
        except Exception as e:
            return ({"success": False, "message":str(e)}),203          
    
    
    @staticmethod
    def user_order(user, order_type, webinar):
            
        try:
            if order_type == "purchased":
                mongo.db.user_data.update_one(
                {"email":user},
                {"$addToSet":{"history_purchased":webinar}}
                )
            else:
                mongo.db.user_data.update_one(
                {"email":user},
                {"$addToSet":{"history_pending":webinar}}
                )

            return ({"success": True, "message":"webinar updated for user"}),200
        
        except Exception as e:
            return ({"success": False, "message":str(e)}),203
        
    
    @staticmethod
    def user_newsletterorder(user, order_type, webinar):
            
        try:
            if order_type == "purchased":
                mongo.db.user_data.update_one(
                {"email":user},
                {"$addToSet":{"newsletter_purchased":webinar}}
                )
            else:
                mongo.db.user_data.update_one(
                {"email":user},
                {"$addToSet":{"newsletter_pending":webinar}}
                )

            return ({"success": True, "message":"newsletter updated for user"}),200
        
        except Exception as e:
        
            return ({"success": False, "message":str(e)}),203
