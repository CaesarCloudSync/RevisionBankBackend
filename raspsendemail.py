import smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class RaspEmail:
    @staticmethod
    def send(receiver_email,subject,htmlmessage,attachment=None):
        sender_email = "revisionbankedu@gmail.com"
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = receiver_email
        password = "ktqgjfzgcbfacsve"


        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(htmlmessage, "html")

        # Add HTML/plain-text parts to MIMEMultipart message.
        # The email client will try to render the last part first

        message.attach(part1)
        # files should be a dictionary of filenames & base64 content
        #print(attachment)
        if attachment != None:
            for file in attachment:
                for key,val in file.items():
                    if ".png" in key:
                        part2 = MIMEBase('image', 'png')
                        image = val.replace("data:image/png;base64,","")
                        part2.set_payload(image)
                        part2.add_header('Content-Transfer-Encoding', 'base64')
                        part2['Content-Disposition'] = 'attachment; filename="%s"' % key
                        message.attach(part2)
                    elif ".jpg" in key or "jpeg" in key:
                        part2 = MIMEBase('image', 'jpeg')
                        image = val.replace("data:image/jpeg;base64,","")
                        part2.set_payload(image)
                        part2.add_header('Content-Transfer-Encoding', 'base64')
                        part2['Content-Disposition'] = 'attachment; filename="%s"' % key
                        message.attach(part2)

            

        # Create secure connection with server and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )
    @staticmethod
    def send_attachment(receiver_email,subject,filename,htmlmessage):
        sender_email = "revisionbankedu@gmail.com"
        password = "ktqgjfzgcbfacsve"

        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        message["Bcc"] = receiver_email  # Recommended for mass emails
        
        part1 = MIMEText(htmlmessage, "html")
        # Add body to email
        message.attach(part1)

        # Open PDF file in binary mode
        with open(filename, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )

        # Add attachment to message and convert message to string
        message.attach(part)
        text = message.as_string()

        # Log in to server using secure context and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, text)
