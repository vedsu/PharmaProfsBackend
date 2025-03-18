from app import app, mongo, s3_client, mail
from flask import request, jsonify, session, render_template_string
from flask_mail import Message
from dotenv import load_dotenv
import string
import random
import datetime
import pytz
import stripe
import json
import io
from io import BytesIO
import os
from app.model_login import Login
from app.model_webinar import Webinar
from app.model_speaker import Speaker
from app.model_utility import Utility
from app.model_order import Order
from app.model_newsletter import Newsletter


load_dotenv()
stripe.api_key = os.environ.get("stripe_secret_key")

# webinar
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
                'postal_code': 75201
            },
            source = data['stripeToken']
        )

        charge = stripe.Charge.create(
            customer=customer.id,
            amount = data['amount']*100,
            currency='inr',
            description=data['invoice_number']
        )
        created_time = datetime.datetime.fromtimestamp(customer['created']).astimezone()
        return jsonify({'success': True, 'amount': data['amount'], 'date_time':created_time})
        
      
    except stripe.error.CardError as e:
        return jsonify({'success': False, 'error': str(e) })
    except stripe.error.StripeError as e:
        return jsonify({'success': False, 'error': str(e) })
    except Exception as e:
        return jsonify(error=str(e)), 403
@app.route('/')
def home():
    response = Utility.update_live_status()
    speaker_list = []
    webinar_list = []
    # coupon_list = Utility.view_coupon()
    webinar_list = Webinar.view_webinar()
    speaker_list  = Speaker.view_speaker()
    
    return jsonify(webinar_list, speaker_list),200

@app.route('/coupon')
def coupon():
    # response = Utility.update_live_status()
    # speaker_list = []
    # webinar_list = []
    coupon_list = Utility.view_coupon()
    # webinar_list = Webinar.view_webinar()
    # speaker_list  = Speaker.view_speaker()
    
    return jsonify(coupon_list),200

@app.route('/<w_id>', methods= ['GET'])
def view_webinar(w_id):    
    
    webinar_data = Webinar.data_webinar(w_id)
    
    if request.method =='GET':
        
        return webinar_data,200
    
# speaker
@app.route('/speaker/<s_id>', methods =['GET'])
def view_speakerdetails(s_id):
    
    if request.method == 'GET':
        speaker_data = Speaker.data_speaker(s_id)
       
        return jsonify(speaker_data),200

# register and login
@app.route('/register', methods = ['POST'])
def user_register():
    if request.method == 'POST':
        register_name = request.form.get("Name")
        register_email = request.form.get("Email")
        register_role = request.form.get("Role")
        register_number = request.form.get("Contact")
        register_password = request.form.get("Password")
        # register_confirmpassword = request.form.get("ConfirmPassword")
        register_type = request.form.get("UserType")
        # website = request.form.get("Website")
        website = "PHARMAPROFS"

        response = Login.register(register_name,register_email,register_role,register_number,register_password,register_type,website)
        return response

@app.route('/login', methods=['POST'])
def user_login():
    if request.method == 'POST':
        login_email = request.form.get("Email")
        login_password = request.form.get("Password")
        login_type = request.form.get("UserType")
        # website = request.form.get("Website")
        website = "PHARMAPROFS"
        response_login = Login.authenticate(login_email, login_password, login_type, website)
            
        return response_login

@app.route('/forgotpassword', methods =['POST'])
def forgot_password():
    if request.method == "POST":
        email = request.json.get("Email")
        # website = request.form.get("Website")
        website = "PHARMAPROFS"

        response = Utility.forgotpassword(email, website)
        return response




# utilities
@app.route('/subscribe', methods = ['POST'])
def subscriber():
    if request.method == 'POST':
        subscriber_email = request.json.get("Subscriber")
        subscriber_name = request.json.get("subscriber_name")
        subscription_type = request.json.get("subscription_type")
        subscriber_jobtitle = request.json.get("subscriber_jobtitle")
        
        response = Utility.subscribe_list(subscriber_email, subscriber_name, subscription_type, subscriber_jobtitle)
        return response

@app.route('/unsubscribe', methods = ['POST'])
def unsubscriber():
    if request.method == 'POST':
        unsubscriber = request.json.get("Unsubscriber")
        response = Utility.unsubscribe_list(unsubscriber)
        return response

@app.route('/contactus', methods = ['POST'])
def contact_us():
    if request.method == 'POST':
        query_email = "support@pharmaprofs.com"
        name = request.json.get("Name")
        email = request.json.get("Email")
        message_content = request.json.get("Message")
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
        

@app.route('/speakeropportunity', methods = ['POST'])
def speaker_opportunity():
    if request.method in 'POST':
        query_email = "brian@profstraining.com"
        name = request.form.get("Name")
        email = request.form.get("Email")
        education = request.form.get("Education")
        country = request.form.get("Country")
        phone = request.form.get("Phone")
        industries = request.form.get("Industries")
        bio = request.form.get("Bio")
        try:
            msg = Message('Speaker Opportunity',
                  sender='support@pharmaprofs.com',
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

# order and dashboard
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


# orders
@app.route('/corportateorder', methods = ['POST'])
def corporateorder():
    try: 
        paymentstatus = None
        current_time_ist = None
        invoice_number = None
        country = None
        zip_code = None #updated 26.02.25
        discount = 0 # 26.02.25
        total_price = 0 # 26.02.25
        customername = None
        billingemail = None
        attendees = None
        total_attendee = 0
        session = []
        
        response_confirmationmail = {"success":False,"message":"Order Not Placed"}
        # Get the current time in UTC
        now_utc = datetime.datetime.now(pytz.utc)
        orderdate =  now_utc.date()
        ordertime =  now_utc.time()
        ordertimezone = now_utc.tzinfo
        
        id = len(list(mongo.db.corporate_order.find({})))+1
        id = str(id)+"_"+"CO"
        if request.method in 'POST':
            
            customeremail = request.form.get('customeremail')
            paymentstatus = request.form.get("paymentstatus")
            website = request.form.get("website")
            Webinar = request.form.get("topic")
            orderamount =  request.form.get("orderamount")
            webinardate = request.form.get("webinardate")
            
    
            sessionLive =  request.form.get("sessionLive") #True /False
            priceLive = request.form.get('priceLive')
            quantityLive = request.form.get('quantityLive') # Default 0
            if sessionLive == "true":
                total_attendee+=int(quantityLive)
                total_price += int(priceLive) #26.02.25
                session.append({"Live": priceLive})
            
            sessionRecording = request.form.get("sessionRecording") # True/ False
            priceRecording = request.form.get('priceRecording')
            quantityRecording = request.form.get('quantityRecording') # Default 0
            if sessionRecording == "true":
                total_price += int(priceRecording) #26.02.25
                total_attendee+=int(quantityRecording)
                session.append({"Recording": priceRecording})
            
            sessionDigitalDownload = request.form.get('sessionDigitalDownload') # True or False
            priceDigitalDownload =  request.form.get('priceDigitalDownload')
            quantityDigitalDownload = request.form.get('quantityDigitalDownload') # Default 0
            if sessionDigitalDownload == "true":
                total_price += int(priceDigitalDownload) #26.02.25
                total_attendee+=int(quantityDigitalDownload)
                session.append({"DigitalDownload": priceDigitalDownload})
            
            sessionTranscript = request.form.get("sessionTranscript") # True or False
            priceTranscript = request.form.get('priceTranscript')
            quantityTranscript = request.form.get('quantityTranscript') # Default 0
            if sessionTranscript == "true":
                total_attendee+=int(quantityTranscript)
                session.append({"Transcript":priceTranscript})
            
            # Extract keys and store them as a comma-separated string
            keys = [list(item.keys())[0] for item in session]
            comma_separated_keys = ', '.join(keys)
            discount = int(total_price) - int(orderamount) #26.02.25
            if paymentstatus == "purchased":
                billingemail = request.form.get("billingemail")
                customername = request.form.get("customername")
                country =  request.form.get("country")
                attendees = request.form.get("attendees") #for corporate purchase
                zip_code = request.form.get("zipcode") #26.02.2025
                # total_attendee = request.form.get("total_attendee") # for corporate purchase that is sum of quantity of all webinars quantity
                
                order_datetimezone = request.form.get("order_datetimezone")
                date_time_str = order_datetimezone
                
                # Define the format of your date-time string
                date_time_format = "%a, %d %b %Y %H:%M:%S %Z"
                # Parse the date-time string into a datetime object
                date_time_obj = datetime.datetime.strptime(date_time_str, date_time_format)
                # orderdate =  date_time_obj.date()
                # ordertime = date_time_obj.time()
                # ordertimezone = pytz.timezone('GMT')
                
                # Define the source timezone (GMT) and the target timezone (EST)
                gmt_timezone = pytz.timezone('GMT')
                est_timezone = pytz.timezone('US/Eastern')
                ist_timezone = pytz.timezone('Asia/Kolkata')
    
                # Localize the datetime object to the GMT timezone
                gmt_datetime = gmt_timezone.localize(date_time_obj)
                # Convert the GMT datetime to EST
                est_datetime = gmt_datetime.astimezone(est_timezone)
                # Convert the GMT datetime to IST
                ist_datetime = gmt_datetime.astimezone(ist_timezone)

                
                # Extract the date, time, and timezone
                orderdate = est_datetime.date()
                ordertime = est_datetime.time()
                ordertimezone = est_datetime.tzinfo
                order_datetime_str = f"{orderdate} {ordertime} EST"
                invoice_number = request.form.get("invoice_number")
                
                #website name
                website="PHARMAPROFS"
                websiteUrl = "https://pharmaprofs.com/"
                current_time_ist = get_current_time_ist()
                
    
                # document = Utility.generate_pdf(Webinar, customername, country, websiteUrl, billingemail, date_time_str, orderamount, invoice_number)
                document = Utility.generate_pdf(Webinar, customername, country, websiteUrl, billingemail, order_datetime_str, orderamount, invoice_number, discount, zip_code, id)
                document_ist = Utility.generatelocal_pdf(Webinar, customername, country, websiteUrl, billingemail, current_time_ist, orderamount, invoice_number, discount, zip_code, id)
            
            else:
                
                document = ""
                document_ist ="" #26.02.25
            
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
                "quantityLive": request.form.get('quantityLive'), #for corporate purchase
                
                "sessionRecording":request.form.get("sessionRecording"), # True/ False
                "priceRecording": request.form.get('priceRecording'),
                "quantityRecording": request.form.get('quantityRecording'),#for corporate purchase
                
                "sessionDigitalDownload":request.form.get('sessionDigitalDownload'), # True or False
                "priceDigitalDownload": request.form.get('priceDigitalDownload'),
                "quantityDigitalDownload": request.form.get('quantityDigitalDownload'),#for corporate purchase
                
                "sessionTranscript":request.form.get("sessionTranscript"), # True or False
                "priceTranscript": request.form.get('priceTranscript'),
                "quantityTranscript": request.form.get('quantityTranscript'),#for corporate purchase
                "attendees" : attendees,
                "customername": customername,
                "billingemail": billingemail,
                "orderamount": orderamount,
                "country": country,
                "website": website , # Current Website
                "document" : document,
                "document_ist":document_ist,
                "ist_time" : current_time_ist,
                "invoice_number" : invoice_number,
                "total_attendee":total_attendee,
                "order_type":"corporate",
                "zip_code":zip_code
                
                }
            
    
            response_order, response_user = Order.update_corporateorder(order_data), Login.user_order(customeremail, paymentstatus, Webinar)
            Order.update_order(order_data) #update corporate order in orders documents also
            if paymentstatus == "purchased":
                
                
                try:
                    msg = Message('Order Confirmation and Thank You',
                        sender='support@pharmaprofs.com',
                        recipients=[billingemail],
                        bcc=['fulfillmentteam@aol.com'])
    
                    msg.body = f"""
                    Dear Customer,
    
                    Thank you for your order!
    
                    Here are your Order Details:
                    Webinar Name: {Webinar}
                    Order Amount: {orderamount}
                    Session: {comma_separated_keys}
                    Participants: {total_attendee}
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
                        <li><b>Participants:</b> {{ total_attendee }}</li>
                        <li><b>Invoice:</b> <a href="{{ s3_link }}">{{ s3_link }}</a></li>
                        <li><b>Website:</b> <a href="{{ website_url }}">{{ website_url }}</a></li>
                    </ul>
                    <p>We appreciate your business and look forward to seeing you at the webinar.</p>
                    <p>Thanks & Regards!<br>Fullfillment Team</p>
                    """, webinar_name=Webinar, s3_link=document, session=comma_separated_keys, total_attendee= total_attendee, order_amount=orderamount, website_url=websiteUrl)
    
                    mail.send(msg)
                    response_confirmationmail = {"success":True, "message":"Confimation mail delivered"}
                
                except Exception as e:
                    response_confirmationmail = {"success":False,"message":str(e)}
            
            
            return jsonify(response_order, response_user, response_confirmationmail)
    
    except Exception as e:
            return jsonify({"error": str(e)}), 500
# orders
@app.route('/order', methods = ['POST'])
def order():
    try: 
        paymentstatus = None
        current_time_ist = None
        invoice_number = None
        country = None
        zip_code = None #updated 26.02.25
        discount = 0 # 26.02.25
        total_price = 0 # 26.02.25
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
        id = str(id)+"_"+"O"
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
                total_price += int(priceLive) #26.02.25
                session.append({"Live": priceLive})
            
            sessionRecording = request.form.get("sessionRecording") # True/ False
            priceRecording = request.form.get('priceRecording')
            if sessionRecording == "true":
                total_price += int(priceRecording) #26.02.25
                session.append({"Recording": priceRecording})
            
            sessionDigitalDownload = request.form.get('sessionDigitalDownload') # True or False
            priceDigitalDownload =  request.form.get('priceDigitalDownload')
            if sessionDigitalDownload == "true":
                total_price += int(priceDigitalDownload) #26.02.25
                session.append({"DigitalDownload": priceDigitalDownload})
            
            sessionTranscript = request.form.get("sessionTranscript") # True or False
            priceTranscript = request.form.get('priceTranscript')
            if sessionTranscript == "true":
                session.append({"Transcript":priceTranscript})
            
            # Extract keys and store them as a comma-separated string
            keys = [list(item.keys())[0] for item in session]
            comma_separated_keys = ', '.join(keys)
            discount = int(total_price) - int(orderamount) #26.02.25
            if paymentstatus == "purchased":
                billingemail = request.form.get("billingemail")
                customername = request.form.get("customername")
                country =  request.form.get("country")
                zip_code = request.form.get("zipcode") #26.02.2025
                
                order_datetimezone = request.form.get("order_datetimezone")
                date_time_str = order_datetimezone
                
                # Define the format of your date-time string
                date_time_format = "%a, %d %b %Y %H:%M:%S %Z"
                # Parse the date-time string into a datetime object
                date_time_obj = datetime.datetime.strptime(date_time_str, date_time_format)
                # Define the source timezone (GMT) and the target timezone (EST)
                gmt_timezone = pytz.timezone('GMT')
                est_timezone = pytz.timezone('US/Eastern')
                ist_timezone = pytz.timezone('Asia/Kolkata')
    
                # Localize the datetime object to the GMT timezone
                gmt_datetime = gmt_timezone.localize(date_time_obj)
                # Convert the GMT datetime to EST
                est_datetime = gmt_datetime.astimezone(est_timezone)
                # Convert the GMT datetime to IST
                ist_datetime = gmt_datetime.astimezone(ist_timezone)

                
                # Extract the date, time, and timezone
                orderdate = est_datetime.date()
                ordertime = est_datetime.time()
                ordertimezone = est_datetime.tzinfo
                order_datetime_str = f"{orderdate} {ordertime} EST"
                # orderdate =  date_time_obj.date()
                # ordertime = date_time_obj.time()
                # ordertimezone = pytz.timezone('GMT')
                invoice_number = request.form.get("invoice_number")
                
                #website name
                website="PHARMAPROFS"
                websiteUrl = "https://pharmaprofs.com/"
                current_time_ist = ist_datetime
                # current_time_ist = get_current_time_ist()
                
    
                # document = Utility.generate_pdf(Webinar, customername, country, websiteUrl, billingemail, date_time_str, orderamount, invoice_number)
                # document = Utility.generate_pdf(Webinar, customername, country, websiteUrl, billingemail, order_datetime_str, orderamount, invoice_number)
                # document_ist = Utility.generatelocal_pdf(Webinar, customername, country, websiteUrl, billingemail, current_time_ist, orderamount, invoice_number)
                document = Utility.generate_pdf(Webinar, customername, country, websiteUrl, billingemail, order_datetime_str, orderamount, invoice_number, discount, zip_code, id)
                document_ist = Utility.generatelocal_pdf(Webinar, customername, country, websiteUrl, billingemail, current_time_ist, orderamount, invoice_number, discount, zip_code, id)
                
            
            else:
                
                document = ""
                document_ist = "" #26.02.25
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
                "document_ist":document_ist,
                "ist_time" : current_time_ist,
                "invoice_number" : invoice_number,
                "order_type":"individual",
                "zip_code":zip_code
                }
            
    
            response_order, response_user = Order.update_order(order_data), Login.user_order(customeremail, paymentstatus, Webinar) 
            if paymentstatus == "purchased":
                
                
                try:
                    msg = Message('Order Confirmation and Thank You',
                        sender='support@pharmaprofs.com',
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

@app.route('/newsletterorder', methods = ['POST'])
def newsletter_order():
    try: 
        paymentstatus = None
        current_time_ist = None
        invoice_number = None
        
        zip_code = "N/A" #updated 26.02.25
        discount = 0 # 26.02.25
        total_price = 0 # 26.02.25
       
        billingemail = None
        customeremail  = None
        country = "N/A"
        customername = "N/A"
      
        response_confirmationmail = {"success":False,"message":"Order Not Placed"}
        # Get the current time in UTC
        now_utc = datetime.datetime.now(pytz.utc)
        orderdate =  now_utc.date()
        ordertime =  now_utc.time()
        ordertimezone = now_utc.tzinfo
        
        id = len(list(mongo.db.newsletter_order.find({})))+1
        id = str(id)+"_"+"NO"
        if request.method == 'POST':
            
            website = "PHARMAPROFS"
            customeremail = request.form.get('customeremail')
            paymentstatus = request.form.get("paymentstatus")
            newsletter = request.form.get("topic")
            orderamount =  request.form.get("orderamount")
           
            if paymentstatus == "purchased":
                billingemail = request.form.get("billingemail")
                if int(orderamount) != 0:
                    try:
                    #     newsletter_data = list(mongo.db.newsletter_data.find({"topic": newsletter},{"price": 1, "_id": 0}))
                    #     newsletter = newsletter_data[0]
                    #     price_value = newsletter.get("price")
                    #     discount = int(price_value) - int(orderamount)
                    #     # price = mongo.db.newsletter_data.find_one({"topic": newsletter}, {"price": 1, "_id": 0})
                    #     # Extract the 'price' value and convert to int
                    #     # price_value = int(price["price"]) if price and "price" in price else 0
                      newsletter_data = mongo.db.newsletter_data.find_one({"topic": newsletter}, {"price": 1, "_id": 0})
                      if newsletter_data:  # Ensure it's not None
                            price_value = newsletter_data.get("price", 0)
                            discount = int(price_value) - int(orderamount)
                      else:
                            discount = 0
                    except:
                        discount = 0
                    
                    customername = request.form.get("customername")
                    country =  request.form.get("country")
                    zip_code = request.form.get("zipcode") #26.02.2025
                
                
                order_datetimezone = request.form.get("order_datetimezone")
                date_time_str = order_datetimezone
                try:
                    # Define the format of your date-time string
                    date_time_format = "%a, %d %b %Y %H:%M:%S %Z"
                    # Parse the date-time string into a datetime object
                    date_time_obj = datetime.datetime.strptime(date_time_str, date_time_format)
                    gmt_timezone = pytz.timezone('GMT')
                    est_timezone = pytz.timezone('US/Eastern')
                    ist_timezone = pytz.timezone('Asia/Kolkata')

                    # Localize the datetime object to the GMT timezone
                    gmt_datetime = gmt_timezone.localize(date_time_obj)
                    # Convert the GMT datetime to EST
                    est_datetime = gmt_datetime.astimezone(est_timezone)
                    # Convert the GMT datetime to IST
                    ist_datetime = gmt_datetime.astimezone(ist_timezone)
                    # orderdate =  date_time_obj.date()
                    # ordertime = date_time_obj.time()
                    # ordertimezone = pytz.timezone('GMT')
                    orderdate =  est_datetime.date()
                    ordertime = est_datetime.time()
                    ordertimezone = est_datetime.tzinfo
                    order_datetime_str = f"{orderdate} {ordertime} EST"
                    current_time_ist = ist_datetime
                except:
                    # country = "N/A"
                    # customername = "N/A"
                    # Date string from frontend
                    date_time_format = "2024-11-13T07:20:16.033Z"
                    # Remove the `GMT` and timezone name from the string
                    # date_str = date_time_str.replace("GMT", "").split(" (")[0]
                    # Parse the date string to datetime object
                    # date_time_obj = datetime.datetime.strptime(date_str, '%a %b %d %Y %H:%M:%S %z')
                    
                    # Convert to ISO 8601 format (YYYY-MM-DDTHH:MM:SS.sss+00:00)
                    # iso_format_date = date_time_obj.isoformat()
                    date_time_obj = datetime.datetime.fromisoformat(date_time_str.replace("Z", "+00:00"))
                    orderdate =  date_time_obj.date()
                    ordertime = date_time_obj.time()
                    # ordertimezone = pytz.timezone('GMT')
                    ordertimezone = pytz.timezone('US/Eastern')
                    order_datetime_str = f"{orderdate} {ordertime} EST"
                    # Define the IST timezone
                    ist_timezone = pytz.timezone('Asia/Kolkata')
                    
                    # Get the current time in UTC
                    utc_now = datetime.datetime.utcnow()
                    
                    # Localize the UTC time and convert it to IST
                    ist_now = pytz.utc.localize(utc_now).astimezone(ist_timezone)
                    current_time_ist = ist_now
                    
               
                
                
        
                
                invoice_number = request.form.get("invoice_number")
                # order_datetime_str = f"{orderdate} {ordertime} EST"
                #website name
                website="PHARMAPROFS"
                websiteUrl = "https://pharmaprofs.com/"
                
                
    
                # document = Utility.generate_pdf(newsletter, customername, country, websiteUrl, billingemail, date_time_str, orderamount, invoice_number)
                document = Utility.generate_pdf(newsletter, customername, country, websiteUrl, billingemail, order_datetime_str, orderamount, invoice_number, discount, zip_code, id)
                document_ist = Utility.generatelocal_pdf(newsletter, customername, country, websiteUrl, billingemail, current_time_ist, orderamount, invoice_number, discount, zip_code, id)
            
            else:
                
                document = ""
                document_ist = ""
            
            order_data = {
                "id":id,
                "topic": newsletter,
                "customeremail":  customeremail, # Login email
                "paymentstatus": paymentstatus,
                "orderdate": str(orderdate),
                "ordertime": str(ordertime),
                "ordertimezone" : str(ordertimezone),
                "customername": customername,
                "billingemail": billingemail,
                "orderamount": orderamount,
                "discount": discount,
                "country": country,
                "website": website , # Current Website
                "document" : document,
                "document_ist":document_ist,
                "ist_time" : current_time_ist,
                "invoice_number" : invoice_number,
                "order_type":"newsletter",
                "zip_code":zip_code,
                }
            
            # for newsletter login component needs to be updated
            response_order, response_user = Order.update_newsletterorder(order_data), Login.user_newsletterorder(customeremail, paymentstatus, newsletter)
            Order.update_order(order_data) #update newsletter order in orders documents also
            if paymentstatus == "purchased":
                
                
                try:
                    msg = Message('Order Confirmation and Thank You',
                        sender='support@pharmaprofs.com',
                        recipients=[billingemail],
                        bcc=['fulfillmentteam@aol.com'])
    
                    msg.body = f"""
                    Dear Customer,
    
                    Thank you for your order!
    
                    Here are your Order Details:
                    Newsletter Name: {newsletter}
                    Order Amount: {orderamount}
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
                        <li><b>Newsletter Name:</b> {{ newsletter_name }}</li>
                        <li><b>Order Amount:</b> {{ order_amount }}</li>
                        <li><b>Invoice:</b> <a href="{{ s3_link }}">{{ s3_link }}</a></li>
                        <li><b>Website:</b> <a href="{{ website_url }}">{{ website_url }}</a></li>
                    </ul>
                    <p>We appreciate your business and look forward to seeing you at the webinar.</p>
                    <p>Thanks & Regards!<br>Fullfillment Team</p>
                    """, newsletter_name=newsletter, s3_link=document, order_amount=orderamount, website_url=websiteUrl)
    
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
        newsletter_list, newsletter_purchased, newsletter_pending = Order.find_newsletterorder(email)
        """ 1. take email and search as customeremail in order_data
            2. if take topic, sessions from orderdata
            3. use topic to search topic,speaker, category, sessions url,date, time from webinar data
            4. display user history also whether paid or pending
        """ 
        
        return jsonify(dashboard_list, history_pending, history_purchased,newsletter_list, newsletter_purchased, newsletter_pending)



# newsletter section -> updating for masterdata backend
# masterdatabackend

@app.route('/newsletter_panel/create_newsletter', methods = ['POST'])
def create_newsletter():
    newsletters = Newsletter.count_newsletter() # edit this function to count_newsletter
    id = str(len(newsletters)+1)

    if request.method == 'POST':
        newsletter_topic = request.form.get("topic")
        category = request.form.get("category")
        website = request.form.get("website")
        description = request.form.get("description")
        price = request.form.get("price")
        document = request.form.get("document")
        published_date = request.form.get("published_date")
        dt = datetime.strptime(published_date,"%Y-%m-%dT%H:%M:%S.%fZ" )
        date_str = dt.strftime("%Y-%m-%d")

        thumbnail = request.files.get("thumbnail")
        

        N=3
        res = ''.join(random.choices(string.ascii_uppercase+string.digits, k=N))
        n_id = res+"_"+id
        bucket_name = "webinarprofs"
        object_key = ''.join(newsletter_topic.split(" "))+n_id
        # object_key_document = ''.join(newsletter_topic.split(" "))+"_"+id
        try:
            s3_client.put_object(
            Body=thumbnail, 
            Bucket=bucket_name, 
            Key=f'newsletter/{object_key}.jpeg'
            )
            s3_url_thumbnail = f"https://{bucket_name}.s3.amazonaws.com/newsletter/{object_key}.jpeg"
           
            
        except:
            s3_url_thumbnail = None
            
        
        newsletter_data = {
            "id":n_id,
            "topic": newsletter_topic,
            "category": category,
            "description": description,
            "website": website,
            "price": price,
            "status": "Active",
            "thumbnail":s3_url_thumbnail,
            "document":document,
            "published_date":date_str,

        }

        response = Newsletter.create_newsletter(newsletter_data)
        if response.get("success") == True:
            return response,201
        else:
            return response,400
#hcprofs status == Active, sort by published_date      
@app.route('/newsletter_panel', methods = ['GET'])
def view_newsletter():
    if request.method == 'GET':
        response = Newsletter.activelist_newsletter()
        return response,200

#hcprofs backend
@app.route('/webinar/<w_id>')
def webinar_details(w_id):
    webinar_info = Webinar.data_webinar(w_id)
    return webinar_info

#hcprofs backend
@app.route('/newsletter/<n_id>')
def newsletter_details(n_id):
        newsletter_info = Newsletter.view_newsletter(n_id)
        return newsletter_info

#masterdata backend
@app.route('/newsletter_panel/<n_id>', methods = ['GET','POST'])
def update_newsletter(n_id):
    if request.method == 'GET':
        newsletter_info = Newsletter.view_newsletter(n_id)
        return newsletter_info
        
    if request.method == 'POST':
        newsletter_status = request.json.get("status")
        response = Newsletter.edit_newsletter(n_id, newsletter_status)
        if response.get("success") == True:
            return response.get("message"),201
        else:
            return response.get("message"),304
