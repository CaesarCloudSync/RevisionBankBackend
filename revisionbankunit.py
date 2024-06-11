import requests
import unittest
import base64
import json
from dotenv import load_dotenv
load_dotenv(".env")
import websockets
import asyncio
from websockets.exceptions import ConnectionClosedOK
from CaesarSQLDB.caesarcrud import CaesarCRUD
from CaesarSQLDB.caesarhash import CaesarHash
from RevisionBankSQLOps.revisionbanksqlops import RevisionBankSQLOps
from CaesarSQLDB.caesar_create_tables import CaesarCreateTables
caesarcrud = CaesarCRUD()
caesarcreatetables = CaesarCreateTables()
revsqlops = RevisionBankSQLOps(caesarcrud,caesarcreatetables)

uri = "http://127.0.0.1:8080"
#uri = "http://192.168.0.10:5000"
def getrevisioncards(url, data=""):
    async def inner():
        async with websockets.connect(url) as websocket:
            print("send")
            await websocket.send(data)
            while True:
                try:
                    response = await websocket.recv()
                    result = json.loads(response)
                    print(result)
                    if "message" in result:
                        await websocket.close()
                except ConnectionClosedOK as eok:
                    break
                
                
    return asyncio.get_event_loop().run_until_complete(inner())

class RevisionBankUnittest(unittest.TestCase):
    def test_signup(self):
        response = requests.post(f"{uri}/signupapi",json={"email":"amari.sql@gmail.com","password":"kya63amari"})
        def AssertSignup(response_json):
            if response_json.get("access_token"):
                return True
            if response_json.get("message"):
                return True

        self.assertEqual(True,AssertSignup(response.json()))

    def test_login(self):
        response = requests.post(f"{uri}/loginapi",json={"email":"amari.sql@gmail.com","password":"kya63amari"})
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
        response = requests.post(f"{uri}/storerevisioncards",json={"revisioncardscheduler":{"sendtoemail":"amari.lawal@gmail.com","revisionscheduleinterval":"30MI","revisioncards":[{"subject":"PA Consulting Test 0","revisioncardtitle":"Network Contacts Test 0",
                                                    "revisioncard":"Hello World","revisionscheduleinterval":"30MI","revisioncardimgname":[],"revisioncardimage":[]},{"subject":"PA Consulting Test 1","revisioncardtitle":"Network Contacts Test 1",
                                                    "revisioncard":"Hello World Again","revisionscheduleinterval":"6H","revisioncardimgname":[],"revisioncardimage":[]}]}},headers=header)
        self.assertEqual(response.json().get("message"),"revision card stored")
    def test_get_revision_cards(self):
        response = requests.post(f"{uri}/loginapi",json={"email":"amari.sql@gmail.com","password":"kya63amari"})
        access_token = response.json()["access_token"]
        header = {"headers":{"Authorization": f"Bearer {access_token}"}}
        getrevisioncards(f"ws://127.0.0.1:8080/getrevisioncardsws/test",json.dumps(header))
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
        response = requests.post(f"{uri}/storerevisioncards",json={"revisioncardscheduler":{"sendtoemail":"amari.lawal@gmail.com","revisionscheduleinterval":"30MI","revisioncards":[{"subject":"PA Consulting Test 2","revisioncardtitle":"Network Contacts Test 2",
                                                    "revisioncard":"Hello World","revisionscheduleinterval":"30MI","revisioncardimgname":["car0.jpeg"],"revisioncardimage":[car0]},{"subject":"PA Consulting Test 3","revisioncardtitle":"Network Contacts Test 3",
                                                    "revisioncard":"Hello World Again","revisionscheduleinterval":"6H","revisioncardimgname":["car1.jpeg","car2.png"],"revisioncardimage":[car1,car2]}]}},headers=header)
        self.assertEqual(response.json().get("message"),"revision card stored")

    def test_update_revision_card_no_images(self):
        json_data =  {"subject":"PA Consulting Test 3","revisioncardtitle":"Network Contacts Test 3",
        "revisioncard":"Hello World Again Again","revisionscheduleinterval":"6H", "newrevisioncard":"Hello World Again Lol"} 

        response = requests.post(f"{uri}/loginapi",json={"email":"amari.sql@gmail.com","password":"kya63amari"})
        self.assertNotEqual(None,response.json().get("access_token"))
        access_token = response.json().get("access_token")
        header = {"Authorization": f"Bearer {access_token}"}
        response = requests.post(f"{uri}/changerevisioncard",json=json_data,headers=header)
        print(response.json())
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
    def test_manage_change_card_image(self):
            response = requests.post(f"{uri}/loginapi",json={"email":"amari.sql@gmail.com","password":"kya63amari"})
            self.assertNotEqual(None,response.json().get("access_token"))
            access_token = response.json().get("access_token")
            header = {"Authorization": f"Bearer {access_token}"}
            with open("/home/amari/Desktop/RevisionBankData/RevisionBankBackend/RevisionBankUnitImages/batman.jpeg","rb") as f2:
                batman = f"data:image/png;base64,{base64.b64encode(f2.read()).decode()}"
            card_data = {"subject":"PA Consulting Test 2","revisioncardtitle":"Network Contacts Test 2","oldimagename":"car0.jpeg","newimagename":"batman.jpeg","newimage":batman}
            response = requests.post(f"{uri}/managechangecardimage",json=card_data,headers=header)
            print(response.json())
            self.assertEqual(response.json().get("message"),"revisioncard image was replaced.")




        


        
        #print(response.json())



if __name__ == "__main__":
    unittest.main()
