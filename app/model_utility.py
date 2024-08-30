# Utilities
from app import mongo, mail, s3_client
from datetime import datetime, timedelta
import pytz
# from app import mail
from flask import render_template_string
from flask_mail import Message
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from io import BytesIO


class Utility():
    @staticmethod
    def update_live_status():
        # Get current time in EST
        est = pytz.timezone('US/Eastern')
        current_time_est = datetime.now(est)
        try:
    
            # Update documents where the current time in EST is greater than the date_time and live is still true
            result = mongo.db.webinar_data.update_many(
                {
                    "date_time": {"$lt": current_time_est},
                    "sessionLive": True
                },
                {"$set": {"sessionLive": False}}
            )
            return {"success":True, "message":"live session updated"}
        
        except Exception as e:
            return {"success":False, "message":str(e)}

    
    
    @staticmethod
    def generate_pdf(Webinar,customername, country, websiteUrl, customeremail, date_time_str, webinardate, comma_separated_keys, orderamount, invoice_number):
        # File and document details
        documentTitle = 'Payment Receipt'
        title = 'Invoice Details'
        
        # Sections of the Invoice
        leftSection = [
            f'Invoice Number - {invoice_number}',
            f'Order Date - {date_time_str}'
        ]
        rightSection = [
            f'Order Amount - {orderamount}'
        ]
        customerDetails = [
            'Customer Details:',
            f'Customer Name -  {customername}',
            f'Registered Email - {customeremail}',
            f'Country - {country}',
            # f'Webinar Date: {webinardate}',
            # f'Webinar Session: {comma_separated_keys}'
        ]
        webinarDetails = [
            'Webinar Name -',
            f'{Webinar}'  # Line break handled by keeping as separate lines
        ]
        thankYouNote = 'query?reach out to us at support@pharmprofs.com !'
        signature = 'Webinar Organizer Team'

        # Create PDF in memory
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Set the title of the document
        pdf.setTitle(documentTitle)

        # Add border around the page
        pdf.rect(20, 20, width - 40, height - 40, stroke=1, fill=0)

        # Shift all content downward
        y_shift = 40  # Shift content down by 40 units

        # Document Title at the top
        pdf.setFont('Helvetica-Bold', 20)
        pdf.drawCentredString(width / 2, height - 40 - y_shift, documentTitle)

        # Create the title by setting its font and putting it on the canvas
        pdf.setFont('Helvetica-Bold', 16)
        pdf.drawCentredString(width / 2, height - 80 - y_shift, title)

        # First section - Invoice details
        pdf.setFont("Helvetica-Bold", 14)
        text = pdf.beginText(40, height - 120 - y_shift)
        for line in leftSection:
            text.textLine(line)
        pdf.drawText(text)

        text = pdf.beginText(width - 250, height - 120 - y_shift)
        for line in rightSection:
            text.textLine(line)
        pdf.drawText(text)

        # Line separator for the second section
        pdf.line(40, height - 160 - y_shift, width - 40, height - 160 - y_shift)

        # Second section - Customer details
        text = pdf.beginText(40, height - 180 - y_shift)
        text.setFont("Helvetica-Bold", 14)
        text.textLine(customerDetails[0])  # Customer Details heading
        text.setFont("Helvetica", 14)  # Change font for the rest of the text
        text.moveCursor(0, 20)  # Add space after the heading

        for line in customerDetails[1:]:
            text.textLine(line)
            text.moveCursor(0, 15)  # Add space between lines to avoid overwriting
        pdf.drawText(text)

        # Line separator for the third section
        pdf.line(40, height - 340 - y_shift, width - 40, height - 340 - y_shift)

        # Third section - Webinar details
        text = pdf.beginText(40, height - 360 - y_shift)
        text.setFont("Helvetica-Bold", 14)
        for line in webinarDetails:
            text.textLine(line)
        pdf.drawText(text)

        # Add the thank you note and signature at the bottom of the page
        pdf.setFont("Helvetica-Oblique", 12)
        pdf.setFillColor(colors.black)
        pdf.drawCentredString(width / 2, 80, thankYouNote)
        pdf.drawCentredString(width / 2, 60, signature)
        
        # Add the website URL at the bottom-most position
        pdf.setFont("Helvetica", 12)
        pdf.drawCentredString(width / 2, 40, f'Website - {websiteUrl}')

        # Save the PDF to the in-memory buffer
        pdf.save()
        buffer.seek(0)

        # Upload the PDF to S3
        bucket_name = "webinarprofs"
        object_key = f'websiteorder/{invoice_number}.pdf'
        s3_client.put_object(
            Body=buffer,
            Bucket=bucket_name,
            Key=object_key
        )

        # Generate S3 URL
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{object_key}"
        return s3_url
    
    @staticmethod
    def subscribe_list(subscriber_email, subscriber_name, subscription_type, subscriber_jobtitle):
       current_datetime = datetime.now()
       try:
            mongo.db.subscriber_list.insert_one({"email":subscriber_email, "name":subscriber_name,"jobtitle":subscriber_jobtitle,"subscription_type":subscription_type,"type":"subscriber", "date":current_datetime})
            return ({"success": True, "message": "subscribed successfully"}),201
       except Exception as e:
            return ({"success": False, "message": str(e)}), 403

    @staticmethod
    def unsubscribe_list(unsubscriber):
       current_datetime = datetime.now()
       try:
            mongo.db.subscriber_list.insert_one({"email":unsubscriber, "type":"unsubscriber", "date":current_datetime})
            return ({"success": True, "message": "unsubscribed successfully"}),201
       except Exception as e:
            return ({"success": False, "message": str(e)}), 403
       
    @staticmethod
    def forgotpassword(email, website):
        try:
            usercredentails =list(mongo.db.user_data.find({"$and":[{"email":email},{"website":website}]}))
            if usercredentails:
               try:
                    usercredentail = usercredentails[0]
                    email = usercredentail.get("email")
                    password = usercredentail.get("password")
                    websiteUrl = usercredentail.get("websiteUrl")
                    
                    msg = Message('Your Account Credentials', sender = 'registration@pharmaprofs.com', recipients = [email])
                    
                    msg.body = f"""
                                   Dear Customer,

                                   Welcome to our website!

                                   Here are your account credentials:

                                   Email: {email}
                                   Password: {password}
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
                                   """, email=email, password=password, website=websiteUrl)
                    mail.send(msg)
                    return ({"success": True, "message": "email sent successfully"}),200
               except Exception as e:
                   return ({"success": False, "message": str(e)}), 403

            else:
               return ({"success": False, "message": "User doesnot exists"}), 200
        except Exception as e:
            return ({"success": False, "message": str(e)}), 403
        
         

      