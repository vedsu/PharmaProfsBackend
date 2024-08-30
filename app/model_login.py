# Login and Registration Component

from app import mongo
from app import mail
from flask_mail import Message
from flask import render_template_string

class Login():

    @staticmethod
    def register(register_email, register_password, register_confirmpassword, register_type, website):
        
        # Create WebsiteUrl for respective Websites
        if website =="PHARMAPROFS":
            websiteUrl = "https://pharmaprofs.com/"
        else: 
            websiteUrl = " "
        
        if register_password == register_confirmpassword:

            user = mongo.db.user_data.find_one({"email": register_email})
            if user:
                return ({"success": False, "message": "User already registered, Please Login"}),403
            else:
                try:
                    msg = Message('Your Account Credentials', sender = 'registration@pharmaprofs.com', recipients = [register_email])
                    
                    msg.body = f"""
                                   Dear Customer,

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
                                   <p>Dear Customer,</p>
                                   <p>Welcome to our website!</p>
                                   <p>Here are your account credentials:</p>
                                   <ul>
                                        <li><b>Email:</b> {{ email }}</li>
                                        <li><b>Password:</b> {{ password }}</li>
                                        <li><b>Website:</b> <a href="{{ website }}">{{ website }}</a></li>
                                   </ul>
                                   <p>Please keep this information secure and do not share it with anyone.</p>
                                   <p>Thanks & Regards!<br>Webinar Organizer Team</p>
                                   """, email=register_email, password=register_password, website=websiteUrl)
                    mail.send(msg)
                    
                    if register_type == "Attendee":
                        try:
                            mongo.db.user_data.insert_one({"email":register_email, "password":register_password, "UserType": register_type, "website":website,"history_purchased":[], "history_pending":[]})
                            return ({"success": True, "message": "user registered successfully, email sent"}),201
                        except Exception as e:
                            return ({"success": False, "message": str(e)}),403

                    else:
                        
                        try:
                            mongo.db.user_data.insert_one({"email":register_email, "password":register_password, "UserType": register_type, "website":website})
                            return ({"success": True, "message": "user registered successfully, email sent"}),201
                        except Exception as e:
                            return ({"success": False, "message": str(e)}),403

                except Exception as e:
                    return ({"success": False, "message": str(e)}),403
        else:
            return ({"success": False, "message": "password mismatch"}),403


    @staticmethod
    def authenticate(login_email, login_password, login_type, website):

        try:
            user = mongo.db.user_data.find_one({"email":login_email, "password": login_password, "UserType": login_type,"website":website})
            if user:
                return ({"success": True, "message": "login successfull"}),200
            else:
                return ({"success": False, "message": "invalid credentials"}),403
            
        except Exception as e:
            return ({"success": False, "message":str(e)}),403      
        

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
            return ({"success": False, "message":str(e)}),403