import random
from raspsendemail import RaspEmail


class RevisionBankScheduler:
    def __init__(self,importcsv) -> None:
        #self.usercardstosend = list()
        self.importcsv = importcsv
    def sendimagecard(self,user,card):
        imagecardjson = {"email":user["sendtoemail"],"message":f"{card['revisioncardtitle']}\n{card['revisioncard']}","subject":card["subject"],"attachment":[{card["revisioncardimgname"][0]:card["revisioncardimage"][0]}]}
        ##print(user["sendtoemail"])
        RaspEmail.send(email = imagecardjson["email"],subject = imagecardjson["subject"],message = imagecardjson["message"],attachment = imagecardjson["attachment"])
        
        #response = requests.post("https://revisionbank-email.onrender.com/raspsendemail",json={"raspsendemail":{"email":user["sendtoemail"],"message":f"{card['revisioncardtitle']}\n{card['revisioncard']}","subject":card["subject"],"attachment":[{card["revisioncardimgname"][0]:card["revisioncardimage"][0]}]}})
        
        #print(response.text)
        #sendgrid_send(user["sendtoemail"],f"{card['revisioncardtitle']}\n{card['revisioncard']}",card["subject"])
    def sendtextcard(self,user,card):
        #print(user["sendtoemail"])
        #response = requests.post("https://revisionbank-email.onrender.com/raspsendemail",json={"raspsendemail":{"email":user["sendtoemail"],"message":f"{card['revisioncardtitle']}\n{card['revisioncard']}","subject":card["subject"]}})
        textcardjson = {"email":user["sendtoemail"],"message":f"{card['revisioncardtitle']}\n{card['revisioncard']}","subject":card["subject"]}
        #print(textcardjson["attachment"])
        #print(textcardjson)
        RaspEmail.send(email = textcardjson["email"],subject = textcardjson["subject"],message = textcardjson["message"])#,attachment = textcardjson["attachment"])
        
        #sendgrid_send(user["sendtoemail"],f"{card['revisioncardtitle']}\n{card['revisioncard']}",card["subject"])
        #print(response.text)
    #brlvuddpzmanpidi
    def getcarddetails(self):
        # TODO Separate cards to there own collection
        userscheduledcards = list(self.importcsv.db.scheduledcards.find())
        usercardstosend = []
        for user in userscheduledcards:
            usercardstosend.append({"sendtoemail":user["sendtoemail"],"revisioncards":user["revisioncards"],"revisionscheduleinterval":user["revisionscheduleinterval"]})
        return usercardstosend
    def runschedule(self):
        def setprobabilities(revisioncard):
            try:
                revcolor = revisioncard["color"]
                if revcolor == "green":
                    return 25
                if revcolor == "amber":
                    return 50
                if revcolor == "red":
                    return 75
            except Exception as ex:
                #print(type(ex),ex)
                return 100
        
        print("Revision card loading...")
        usercardstosend = self.getcarddetails()
        #print("Revision card loaded.")
        #print(usercardstosend)
        for user in usercardstosend:
            # Creating a name list
            revisioncards = user["revisioncards"]
            #print(revisioncards)
            weights = list(map(setprobabilities,revisioncards))
            trafficlightemailsleft = 3


            for card,weight in zip(revisioncards,weights):
                #print(card)
                #print(weight)
                if weight == 100:
                    # send email
                    print("Sending revision card...")
                    #time.sleep(10)
                    #print(card)
                    #
                    if "revisioncardimage" in card :
                        if card["revisioncardimage"] != [] :
                            self.sendimagecard(user,card)

                            print("Card sent.")
                            trafficlightemailsleft -= 1
                        elif card["revisioncardimage"] == []:
                            #print("hi")
                            self.sendtextcard(user,card)
                            print("Card sent.")
                            trafficlightemailsleft -= 1

                    elif "revisioncardimage" not in card:
                        self.sendtextcard(user,card)       
                        print("Card sent.")
                        trafficlightemailsleft -= 1
                #elif 
            #print(revisioncards)
            #print(weights)
            
            #if len(revisioncards) < 3:
            try:
                # Makes sure that no duplicates are sent. Whilst also picking each card randomly with red 
                duplicates = True
                
                while duplicates == True:
                    trafficlightemails = random.choices(revisioncards, weights=weights, k=trafficlightemailsleft)
                    #print(len(trafficlightemails))
                    if trafficlightemails != []:
                        original = list(map(lambda x:x["revisioncard"],trafficlightemails))
                        duplicateset = set(original)
                        #print(len(original),len(duplicateset))
                        #print(original,duplicateset)
                        if len(duplicateset) < len(original):
                            trafficlightemails = random.choices(revisioncards, weights=weights, k=trafficlightemailsleft)
                            trafficlightemailsleft -= 1
                            #duplicates = False
                        if len(duplicateset) == len(original):
                            duplicates = False
                    elif trafficlightemails == []:
                        duplicates = False 
                        
                #print(trafficlightemailsleft)

                
                for card in trafficlightemails:
                    #user["revisionscheduleinterval"]
                    print("Sending traffic light revision card...")
                    #time.sleep(10)
                    ##192.168.0.180
                    if "revisioncardimage" in card:
                        #print([{card["revisioncardimgname"][0]:card["revisioncardimage"][0]}])
                        imagecardjson = {"email":user["sendtoemail"],"message":f"{card['revisioncardtitle']}\n{card['revisioncard']}","subject":card["subject"],"attachment":[{card["revisioncardimgname"][0]:card["revisioncardimage"][0]}]}
                        RaspEmail.send(email = imagecardjson["email"],subject = imagecardjson["subject"],message = imagecardjson["message"],attachment = imagecardjson["attachment"])
                        
                        #response = requests.post("https://revisionbank-email.onrender.com/raspsendemail",json={"raspsendemail":{"email":user["sendtoemail"],"message":f"{card['revisioncardtitle']}\n{card['revisioncard']}","subject":card["subject"],"attachment":[{card["revisioncardimgname"][0]:card["revisioncardimage"][0]}]}})
                        #sendgrid_send(user["sendtoemail"],f"{card['revisioncardtitle']}\n{card['revisioncard']}",card["subject"])
                        print("Traffic light card sent.")
                    elif "revisioncardimage" not in card:
                        #response = requests.post("https://revisionbank-email.onrender.com/raspsendemail",json={"raspsendemail":{"email":user["sendtoemail"],"message":f"{card['revisioncardtitle']}\n{card['revisioncard']}","subject":card["subject"]}})
                        textcardjson = {"email":user["sendtoemail"],"message":f"{card['revisioncardtitle']}\n{card['revisioncard']}","subject":card["subject"]}
                        RaspEmail.send(email = textcardjson["email"],subject = textcardjson["subject"],message = textcardjson["message"],attachment = textcardjson["attachment"])
                        
                        #sendgrid_send(user["sendtoemail"],f"{card['revisioncardtitle']}\n{card['revisioncard']}",card["subject"])
                        print("Traffic light card sent.")
            except IndexError as ex:
                #print(type(ex),ex)
                continue