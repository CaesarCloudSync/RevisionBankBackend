from raspsendemail import RaspEmail

if __name__ == "__main__":
    email = "amari.lawal@gmail.com"
    message = "Hello World"
    subject = f"RevisionBank Send Now"
    RaspEmail.send(**{"email":email,"message":message,"subject":subject})