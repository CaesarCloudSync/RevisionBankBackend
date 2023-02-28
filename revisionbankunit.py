import requests
import unittest
uri = "http://0.0.0.0:7860"
#uri = "http://192.168.0.10:5000"
class RevisionBankAuth(unittest.TestCase):
    def signup(self):
        response = requests.post(f"{uri}/signupapi",json={"email":"amari.lawaltesth@gmail.com","password":"kya63amari"})
        print(response.json())
    def signin(self):
        response = requests.post(f"{uri}/loginapi",json={"email":"amari.lawaltesth@gmail.com","password":"kya63amari"})
        print(response.json())
    def checkgeneric(self):
        response = requests.post(f"{uri}/forgotpassword",json={"email":"amari.lawaltesth@gmail.com","password":"kya63amari"})
        print(response.json())
        

    
        


if __name__ == "__main__":
    unittest.main()