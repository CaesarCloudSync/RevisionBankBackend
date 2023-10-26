import requests
import unittest
import base64
from dotenv import load_dotenv
load_dotenv(".env")
from csv_to_db import ImportCSV
from CaesarSQLDB.caesarcrud import CaesarCRUD
from CaesarSQLDB.caesarhash import CaesarHash
from RevisionBankSQLOps.revisionbanksqlops import RevisionBankSQLOps
from CaesarSQLDB.caesar_create_tables import CaesarCreateTables
caesarcrud = CaesarCRUD()
caesarcreatetables = CaesarCreateTables()
revsqlops = RevisionBankSQLOps(caesarcrud,caesarcreatetables)

uri = "http://127.0.0.1:8080"
#uri = "http://192.168.0.10:5000"
importcsv = ImportCSV("RevisionBankDB",maindb=0)
class RevisionBankRevisionCards(unittest.TestCase):
    def test_signup(self):
        response = requests.post(f"{uri}/signupapi",json={"email":"amari.sql@gmail.com","password":"kya63amari"})
        def AssertSignup(response_json):
            if response_json.get("access_token"):
                return True
            if response_json.get("message"):
                return True

        self.assertEqual(True,AssertSignup(response.json()))

        
        #self.assertNotEqual(None,response.json().get("access_token"))
    def test_store_revision_card_no_image(self):
        response = requests.post(f"{uri}/loginapi",json={"email":"amari.sql@gmail.com","password":"kya63amari"})
        self.assertNotEqual(None,response.json().get("access_token"))
        access_token = response.json().get("access_token")
        header = {"Authorization": f"Bearer {access_token}"}
        response = requests.post(f"{uri}/storerevisioncards",json={"sendtoemail":"amari.lawal@gmail.com","revisionscheduleinterval":"30MI","revisioncards":[{"subject":"PA Consulting Test 0","revisioncardtitle":"Network Contacts Test 0",
                                                    "revisioncard":"Hello World","revisionscheduleinterval":"30MI","revisioncardimgname":[],"revisioncardimage":[]},{"subject":"PA Consulting Test 1","revisioncardtitle":"Network Contacts Test 1",
                                                    "revisioncard":"Hello World Again","revisionscheduleinterval":"6H","revisioncardimgname":[],"revisioncardimage":[]}]},headers=header)
        self.assertEqual(response.json().get("message"),"revision card stored")

    def test_store_revision_card_with_images(self):
        with open("/home/amari/Desktop/RevisionBankBackend/RevisionBankUnitImages/car0.jpeg","rb") as f0:
            car0 = f"data:image/jpeg;base64,{base64.b64encode(f0.read()).decode()}"
        with open("/home/amari/Desktop/RevisionBankBackend/RevisionBankUnitImages/car1.jpeg","rb") as f1:
            car1 = f"data:image/jpeg;base64,{base64.b64encode(f1.read()).decode()}"
            
        with open("/home/amari/Desktop/RevisionBankBackend/RevisionBankUnitImages/car2.png","rb") as f2:
            car2 = f"data:image/png;base64,{base64.b64encode(f2.read()).decode()}"
            
        response = requests.post(f"{uri}/loginapi",json={"email":"amari.sql@gmail.com","password":"kya63amari"})
        self.assertNotEqual(None,response.json().get("access_token"))
        access_token = response.json().get("access_token")
        header = {"Authorization": f"Bearer {access_token}"}
        response = requests.post(f"{uri}/storerevisioncards",json={"sendtoemail":"amari.lawal@gmail.com","revisionscheduleinterval":"30MI","revisioncards":[{"subject":"PA Consulting Test 2","revisioncardtitle":"Network Contacts Test 2",
                                                    "revisioncard":"Hello World","revisionscheduleinterval":"30MI","revisioncardimgname":["car0.jpeg"],"revisioncardimage":[car0]},{"subject":"PA Consulting Test 3","revisioncardtitle":"Network Contacts Test 3",
                                                    "revisioncard":"Hello World Again","revisionscheduleinterval":"6H","revisioncardimgname":["car1.jpeg","car2.png"],"revisioncardimage":[car1,car2]}]},headers=header)
        self.assertEqual(response.json().get("message"),"revision card stored")

    def test_update_revision_card_no_images(self):
        json_data =  {"subject":"PA Consulting Test 3","revisioncardtitle":"Network Contacts Test 3",
        "revisioncard":"Hello World Again Again","revisionscheduleinterval":"6H", "newrevisioncard":"Hello World Again Lol"} 

        response = requests.post(f"{uri}/loginapi",json={"email":"amari.sql@gmail.com","password":"kya63amari"})
        self.assertNotEqual(None,response.json().get("access_token"))
        access_token = response.json().get("access_token")
        header = {"Authorization": f"Bearer {access_token}"}
        response = requests.post(f"{uri}/changerevisioncard",json=json_data,headers=header)
        self.assertEqual(response.json().get("message"),"revision card changed.")
        
    def test_update_revsisioncard_metadata(self):
            oldcard_data = {"oldsubject":"PA Consulting Test 3","oldrevisioncardtitle":"Network Contacts Test 3",
                            "oldrevisionscheduleinterval":"6H","newsubject":"PA Consulting Test 3 Man","newrevisioncardtitle":"Network Contacts Test 3 Man","newrevisionscheduleinterval":"30MI"}
            response = requests.post(f"{uri}/loginapi",json={"email":"amari.sql@gmail.com","password":"kya63amari"})
            self.assertNotEqual(None,response.json().get("access_token"))
            access_token = response.json().get("access_token")
            header = {"Authorization": f"Bearer {access_token}"}
            response = requests.post(f"{uri}/changerevisioncardmetadata",json=oldcard_data,headers=header)
            self.assertEqual(response.json().get("message"),"revision card meta data changed.")

    def test_update_revsisioncard_metadata(self):
            oldcard_data = {"oldsubject":"PA Consulting Test 3","oldrevisioncardtitle":"Network Contacts Test 3",
                            "oldrevisionscheduleinterval":"6H","newsubject":"PA Consulting Test 3 Man","newrevisioncardtitle":"Network Contacts Test 3 Man","newrevisionscheduleinterval":"30MI"}
            response = requests.post(f"{uri}/loginapi",json={"email":"amari.sql@gmail.com","password":"kya63amari"})
            self.assertNotEqual(None,response.json().get("access_token"))
            access_token = response.json().get("access_token")
            header = {"Authorization": f"Bearer {access_token}"}
            response = requests.post(f"{uri}/changerevisioncardmetadata",json=oldcard_data,headers=header)
            self.assertEqual(response.json().get("message"),"revision card meta data changed.")

        #self.assertEqual(response.json().get("message"),"revision card scheduled")
                    




        


        
        #print(response.json())

class RevisionBankManageRevisionCards(unittest.TestCase):
    pass

class RevisionBankSchedule(unittest.TestCase):
    def test_schedule_revision_card(self):
        with open("/home/amari/Desktop/RevisionBankBackend/RevisionBankUnitImages/car0.jpeg","rb") as f0:
            car0 = f"data:image/jpeg;base64,{base64.b64encode(f0.read()).decode()}"
        json_data = {"sendtoemail":"amari.lawal@gmail.com","revisionscheduleinterval":"30MI","revisioncards":[{"subject":"PA Consulting Test 2","revisioncardtitle":"Network Contacts Test 2",
                                                    "revisioncard":"Hello World","revisionscheduleinterval":"30MI","revisioncardimgname":["car0.jpeg"],"revisioncardimage":[car0]}]}
        response = requests.post(f"{uri}/loginapi",json={"email":"amari.sql@gmail.com","password":"kya63amari"})
        self.assertNotEqual(None,response.json().get("access_token"))
        access_token = response.json().get("access_token")
        header = {"Authorization": f"Bearer {access_token}"}
        response = requests.post(f"{uri}/schedulerevisioncard",json=json_data,headers=header)
        self.assertNotEqual(None,response.json().get("message"))
    def test_check_schedule_revision_card(self):
        response = requests.post(f"{uri}/loginapi",json={"email":"amari.sql@gmail.com","password":"kya63amari"})
        self.assertNotEqual(None,response.json().get("access_token"))
        access_token = response.json().get("access_token")
        header = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{uri}/checkschedulerevisioncard",headers=header)
        print(response.json())
class RevisionBankMongoToSQLMigrate(unittest.TestCase):
    def test_migrate_users_details(self):
        numsuccesses = []
        count = 0
        user_data = importcsv.db.users.find({ "email": { "$exists": "true" } } )
        for user in user_data:
            res = caesarcrud.post_data(("email","password"),(user["email"],user["password"]),"users")
            if res:
                print(f"Success: {count}")
                numsuccesses.append(res)
                count += 1
            else:
                print(f"Failure {count}")
                numsuccesses.append(res)
                count += 1
        allsucessresult = list(set(numsuccesses))[0]
        self.assertEqual(True,allsucessresult)
    def test_migrate_account_revisioncards(self):

        #import json
        #with open("data.json","r") as f:
        #    account_revisioncards_data = [json.load(f)]

        numsuccesses = []
        count = 0
        account_revisioncards_data = importcsv.db.accountrevisioncards.find({ "email": { "$exists": "true" } } )

            
        for account_card in account_revisioncards_data:
            
            email = account_card["email"]
            sendtoemail = account_card["sendtoemail"]
            revisioncards = account_card["revisioncards"]
            for revisioncard in revisioncards:
                print("Loading Revision Card...")
                subject = revisioncard["subject"]
                revisioncardtitle = revisioncard["revisioncardtitle"]
                revisioncardtext = revisioncard["revisioncard"]
                revisioncardhash = CaesarHash.hash_text(email + subject + revisioncardtitle)
                revisionscheduleinterval = revisioncard.get("revisionscheduleinterval")
                if not revisionscheduleinterval:
                    revisionscheduleinterval = "30MI"
                revisioncardimgname = revisioncard.get("revisioncardimgname")
                revisioncardimage = revisioncard.get("revisioncardimage")
                print("Storing in database.")
                if revisioncardimgname:
                    res = caesarcrud.post_data(("email","sendtoemail","subject","revisioncardtitle","revisionscheduleinterval","revisioncard","revisioncardimgname","revisioncardhash"),
                        (email,sendtoemail,subject,revisioncardtitle,revisionscheduleinterval,revisioncardtext,"true",revisioncardhash),"accountrevisioncards")
                    for ind,imagename in enumerate(revisioncardimgname):
                        res = revsqlops.store_revisoncard_image(email,imagename,revisioncardimage[ind],revisioncardhash)

                else:
                    res = caesarcrud.post_data(("email","sendtoemail","subject","revisioncardtitle","revisionscheduleinterval","revisioncard","revisioncardhash"),
                                                (email,sendtoemail,subject,revisioncardtitle,revisionscheduleinterval,revisioncardtext,revisioncardhash),"accountrevisioncards")
                print("Stored.")
                
                if res:
                    print(f"Success: {count}")
                    numsuccesses.append(res)
                    count += 1
                else:
                    print(f"Failure {count}")
                    numsuccesses.append(res)
                    count += 1
        allsucessresult = list(set(numsuccesses))[0]
        self.assertEqual(True,allsucessresult)


     
        #self.assertNotEqual(None,response.json().get("message"))

#class RevisionBankAuth(unittest.TestCase):
#    def signup(self):
#        response = requests.post(f"{uri}/signupapi",json={"email":"amari.lawaltesth@gmail.com","password":"kya63amari"})
#        print(response.json())
#    def signin(self):
#        response = requests.post(f"{uri}/loginapi",json={"email":"amari.lawaltesth@gmail.com","password":"kya63amari"})
#        print(response.json())
#    def checkgeneric(self):
#        response = requests.post(f"{uri}/forgotpassword",json={"email":"amari.lawaltesth@gmail.com","password":"kya63amari"})
#        print(response.json())

        

    
        


if __name__ == "__main__":
    unittest.main()
