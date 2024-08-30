
from app import app
from app import mongo
from flask import request, jsonify, session, render_template_string
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from app.model_login import Login
from app.model_webinar import Webinar
from app.model_speaker import Speaker
from app.model_order import Order
from app.model_utility import Utility
import string
import random
import datetime
import pytz
from app import s3_client, s3_resource
from flask_mail import Message
from app import mail
import stripe
import json
from dotenv import load_dotenv
import os
load_dotenv()

stripe.api_key = os.environ.get("stripe_secret_key")


@app.route('/')
def home():
    response = Utility.update_live_status()
    speaker_list = []
    webinar_list = []
    webinar_list = Webinar.view_webinar()
    speaker_list  = Speaker.view_speaker()
    return jsonify(webinar_list, speaker_list)

@app.route('/speaker/<s_id>', methods =['GET'])
def view_speakerdetails(s_id):
    
    if request.method in 'GET':
        speaker_data = Speaker.data_speaker(s_id)
       
        return jsonify(speaker_data),200

@app.route('/create-payment-intent', methods=['POST'])
def create_payment_intent():
    
    data = request.json
    
    try:
        customer = stripe.Customer.create(
            email = data['email'],
            
            name = data['name'],
            address={
                'line1': "Address",
                'city': "City",
                'state': "State",
                'country': data['country'],
                'postal_code': 444444
            },
            source = data['stripeToken']
        )

        charge = stripe.Charge.create(
            customer=customer.id,
            amount = data['amount']*100,
            currency='inr',
            description='Stripe Charge'
        )
        created_time = datetime.datetime.fromtimestamp(customer['created']).astimezone()
        return jsonify({'success': True, 'amount': data['amount'], 'date_time':created_time})
        
      
    except stripe.error.CardError as e:
        return jsonify({'success': False, 'error': str(e) })
    except stripe.error.StripeError as e:
        return jsonify({'success': False, 'error': str(e) })
    except Exception as e:
        return jsonify(error=str(e)), 403

@app.route('/subscribe', methods = ['POST'])
def subscriber():
    if request.method in 'POST':
        subscriber_email = request.form.get("Subscriber")
        subscriber_name = request.form.get("subscriber_name")
        subscription_type = request.form.get("subscription_type")
        subscriber_jobtitle = request.form.get("subscriber_jobtitle")
        
        response = Utility.subscribe_list(subscriber_email, subscriber_name, subscription_type, subscriber_jobtitle)
        return response

@app.route('/unsubscribe', methods = ['POST'])
def unsubscriber():
    if request.method in 'POST':
        unsubscriber = request.form.get("Unsubscriber")
        response = Utility.unsubscribe_list(unsubscriber)
        return response
    

@app.route('/contactus', methods = ['POST'])
def contact_us():
    if request.method in 'POST':
        query_email = "support@pharmaprofs.com"
        name = request.form.get("Name")
        email = request.form.get("Email")
        message_content = request.form.get("Message")
        try:
            msg = Message('Query',
                  sender='registration@pharmaprofs.com',
                  recipients=[query_email])

            msg.body = f"""
            Dear Team,

            We have received a query from:

            Name: {name}
            Email: {email}
            Message: {message_content}

            Best regards
           
            """

            msg.html = render_template_string("""
            <p>Dear Team,</p>
            <p>We have received a query from:</p>
            <ul>
                <li><b>Name:</b> {{ name }}</li>
                <li><b>Email:</b> {{ email }}</li>
            </ul>
            <p><b>Message:</b></p>
            <p>{{ message_content }}</p>
            <p>Best regards<br></p>
            """, name=name, email=email, message_content=message_content)

            mail.send(msg)
            return {"Message": "Thanks for contacting us. Our team will reach out to you shortly."}
        except Exception as e:
            return {"Message": "Failed to receive your request. Please try again later."}
            # return {"Message": str(e)}

@app.route('/speakeropportunity', methods = ['POST'])
def speaker_opportunity():
    if request.method in 'POST':
        query_email = "brian@pharmaprofs.com"
        name = request.form.get("Name")
        email = request.form.get("Email")
        education = request.form.get("Education")
        country = request.form.get("Country")
        phone = request.form.get("Phone")
        industries = request.form.get("Industries")
        bio = request.form.get("Bio")
        try:
            msg = Message('Speaker Opportunity',
                  sender='registration@pharmaprofs.com',
                  recipients=[query_email])
            msg.body = f"""
                Dear Team,

                We have received a new speaker opportunity query from:

                Name: {name}
                Email: {email}
                Education: {education}
                Country: {country}
                Phone: {phone}
                Industries: {industries}
                BIO: {bio}

                Best regards
                
               """
            msg.html = render_template_string("""
            <p>Dear Team,</p>
            <p>We have received a new speaker opportunity query from:</p>
            <ul>
                <li><b>Name:</b> {{ name }}</li>
                <li><b>Email:</b> {{ email }}</li>
                <li><b>Education:</b> {{ education }}</li>
                <li><b>Country:</b> {{ country }}</li>
                <li><b>Phone:</b> {{ phone }}</li>
                <li><b>Industries:</b> {{ industries }}</li>
                <li><b>BIO:</b> {{ bio }}</li>
            </ul>
            <p>Best regards,<br></p>
            """, name=name, email=email, education=education, country=country, phone=phone, industries=industries, bio=bio)

            mail.send(msg)
            
            return {"Message": "Your query has been successfully received. Our team will reach out to you shortly."}
        except Exception as e:
            return {"Message": "Failed to receive your query. Please try again later."}



@app.route('/<w_id>/<website>', methods= ['GET','PUT','POST','DELETE'])
def view_webinar(w_id,website):    
    
    webinar_data = Webinar.data_webinar(w_id,website)
    
    if request.method in ['GET']:
        
        return webinar_data,200

@app.route('/register', methods = ['POST'])
def user_register():
    if request.method in 'POST':
        register_email = request.form.get("Email")
        register_password = request.form.get("Password")
        register_confirmpassword = request.form.get("ConfirmPassword")
        register_type = request.form.get("UserType")
        website = request.form.get("Website")

        response = Login.register(register_email, register_password, register_confirmpassword, register_type, website)
        return response
        

@app.route('/login', methods=['POST'])
def user_login():
    if request.method in 'POST':
        login_email = request.form.get("Email")
        login_password = request.form.get("Password")
        login_type = request.form.get("UserType")
        website = request.form.get("Website")
        response_login = Login.authenticate(login_email, login_password, login_type, website)
            
        return response_login


@app.route('/forgotpassword', methods =['POST'])
def forgot_password():
    if request.method in "POST":
        email = request.form.get("Email")
        website = request.form.get("Website")

        response = Utility.forgotpassword(email, website)
        return response


def get_current_time_ist():
    # Define the IST timezone
    ist_timezone = pytz.timezone('Asia/Kolkata')
    
    # Get the current time in UTC
    utc_now = datetime.datetime.utcnow()
    
    # Convert the UTC time to IST
    ist_now = utc_now.astimezone(ist_timezone)
    
    # Format the time as desired
    formatted_ist_now = ist_now.strftime("%Y-%m-%d %H:%M:%S")
    
    return formatted_ist_now
    
@app.route('/order', methods = ['POST'])
def order():
    try: 
        paymentstatus = None
        current_time_ist = None
        invoice_number = None
        country = None
        customername = None
        billingemail = None
        session = []
        response_confirmationmail = {"success":False,"message":"Order Not Placed"}
        # Get the current time in UTC
        now_utc = datetime.datetime.now(pytz.utc)
        orderdate =  now_utc.date()
        ordertime =  now_utc.time()
        ordertimezone = now_utc.tzinfo
        
        id = len(list(mongo.db.order_data.find({})))+1
        if request.method in 'POST':
            
            customeremail = request.form.get('customeremail')
            paymentstatus = request.form.get("paymentstatus")
            website = request.form.get("website")
            Webinar = request.form.get("topic")
            orderamount =  request.form.get("orderamount")
            webinardate = request.form.get("webinardate")
            
    
            sessionLive =  request.form.get("sessionLive") #True /False
            priceLive = request.form.get('priceLive')
            
            if sessionLive == "true":
                session.append({"Live": priceLive})
            sessionRecording = request.form.get("sessionRecording") # True/ False
            priceRecording = request.form.get('priceRecording')
            
            if sessionRecording == "true":
                session.append({"Recording": priceRecording})
            sessionDigitalDownload = request.form.get('sessionDigitalDownload') # True or False
            priceDigitalDownload =  request.form.get('priceDigitalDownload')
            
            if sessionDigitalDownload == "true":
                session.append({"DigitalDownload": priceDigitalDownload})
            sessionTranscript = request.form.get("sessionTranscript") # True or False
            priceTranscript = request.form.get('priceTranscript')
            
            if sessionTranscript == "true":
                session.append({"Transcript":priceTranscript})
            
            # Extract keys and store them as a comma-separated string
            keys = [list(item.keys())[0] for item in session]
            comma_separated_keys = ', '.join(keys)
            
            if paymentstatus == "purchased":
                billingemail = request.form.get("billingemail")
                customername = request.form.get("customername")
                country =  request.form.get("country")
                
                order_datetimezone = request.form.get("order_datetimezone")
                date_time_str = order_datetimezone
                
                # Define the format of your date-time string
                date_time_format = "%a, %d %b %Y %H:%M:%S %Z"
                # Parse the date-time string into a datetime object
                date_time_obj = datetime.datetime.strptime(date_time_str, date_time_format)
                orderdate =  date_time_obj.date()
                ordertime = date_time_obj.time()
                ordertimezone = pytz.timezone('GMT')
                invoice_number = request.form.get("invoice_number")
                # Create WebsiteUrl for respective Websites
                if website=="PHARMAPROFS":
                    websiteUrl = "https://pharmaprofs.com/"
                else: 
                    websiteUrl = " "
                
                current_time_ist = get_current_time_ist()
                
    
                document = Utility.generate_pdf(Webinar, customername, country, websiteUrl, billingemail, date_time_str, webinardate, comma_separated_keys, orderamount, invoice_number)
            
            else:
                
                document = ""
            
            order_data = {
                "id":id,
                "topic": Webinar,
                "customeremail":  customeremail, # Login email
                "paymentstatus": paymentstatus,
                "orderdate": str(orderdate),
                "ordertime": str(ordertime),
                "ordertimezone" : str(ordertimezone),
                
                "webinardate": webinardate,
                "session": session,# Array
                "sessionLive": request.form.get("sessionLive"), #True /False
                "priceLive": request.form.get('priceLive'),
                "sessionRecording":request.form.get("sessionRecording"), # True/ False
                "priceRecording": request.form.get('priceRecording'),
                "sessionDigitalDownload":request.form.get('sessionDigitalDownload'), # True or False
                "priceDigitalDownload": request.form.get('priceDigitalDownload'),
                "sessionTranscript":request.form.get("sessionTranscript"), # True or False
                "priceTranscript": request.form.get('priceTranscript'),
                "customername": customername,
                "billingemail": billingemail,
                "orderamount": orderamount,
                "country": country,
                "website": website , # Current Website
                "document" : document,
                "ist_time" : current_time_ist,
                "invoice_number" : invoice_number,
                }
            
    
            response_order, response_user = Order.update_order(order_data), Login.user_order(request.form.get("customeremail"), paymentstatus, request.form.get("topic")) 
            if paymentstatus == "purchased":
                
                
                try:
                    msg = Message('Order Confirmation and Thank You',
                        sender='registration@pharmaprofs.com',
                        recipients=[billingemail],
                        bcc=['fulfillmentteam@aol.com'])
    
                    msg.body = f"""
                    Dear Customer,
    
                    Thank you for your order!
    
                    Here are your Order Details:
                    Webinar Name: {Webinar}
                    Order Amount: {orderamount}
                    Session: {comma_separated_keys}
                    Invoice: {document}
                    Website: {websiteUrl}
    
    
                    We appreciate your business and look forward to seeing you at the webinar.
    
                    Thanks & Regards!
                    Fullfillment Team
                    """
    
                    msg.html = render_template_string("""
                    <p>Dear Customer,</p>
                    <p>Thank you for your order!</p>
                    <p><b>Here are your Order Details:</b></p>
                    <ul>
                        <li><b>Webinar Name:</b> {{ webinar_name }}</li>
                        <li><b>Order Amount:</b> {{ order_amount }}</li>
                        <li><b>Session:</b> {{ session }}</li>
                        <li><b>Invoice:</b> <a href="{{ s3_link }}">{{ s3_link }}</a></li>
                        <li><b>Website:</b> <a href="{{ website_url }}">{{ website_url }}</a></li>
                    </ul>
                    <p>We appreciate your business and look forward to seeing you at the webinar.</p>
                    <p>Thanks & Regards!<br>Fullfillment Team</p>
                    """, webinar_name=Webinar, s3_link=document, session=comma_separated_keys, order_amount=orderamount, website_url=websiteUrl)
    
                    mail.send(msg)
                    response_confirmationmail = {"success":True, "message":"Confimation mail delivered"}
                except Exception as e:
                    response_confirmationmail = {"success":False,"message":str(e)}
            
            
    
            return jsonify(response_order, response_user, response_confirmationmail)
    except Exception as e:
            return jsonify({"error": str(e)}), 500
      

@app.route('/dashboard/<email>/<user_type>', methods =['GET'])
def dashboard(email, user_type):
    if user_type == "Speaker":
        
        dashboard_list,history = Speaker.speakerdashboard_data(email)
        return jsonify(dashboard_list,history)
    
    else:
        dashboard_list, history_pending, history_purchased = Order.find_order(email)
        """ 1. take email and search as customeremail in order_data
            2. if take topic, sessions from orderdata
            3. use topic to search topic,speaker, category, sessions url,date, time from webinar data
            4. display user history also whether paid or pending
        """ 
        
        return jsonify(dashboard_list, history_pending, history_purchased)

       