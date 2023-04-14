from raspsendemail import RaspEmail

if __name__ == "__main__":
    email = "amari.lawal@gmail.com"
    message = "Hello World"
    subject = f"RevisionBank Send Now"
    import requests
    #requests.post("http://192.168.0.23:7860/revisionbanksendemail",json={"email":"revisionbankedu@gmail.com","subject":"RevisionBank New User","message":"RevisionBank New User"})
    #RaspEmail.send(email = email,subject = subject,message = message,attachment = None)
    #RaspEmail.send(**{"email":"revisionbankedu@gmail.com","subject":"RevisionBank New User","message":"RevisionBank New User"})