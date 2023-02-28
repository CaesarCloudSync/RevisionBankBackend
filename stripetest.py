import requests
import requests
resptoken = requests.post("https://revisionbankapi.herokuapp.com/loginapi",json={"email":"amari.lawal05@gmail.com","password":"kya63amari"})
print()
'headers:'
config = {'headers:{Authorization: Bearer {}'.format(resptoken.json()["access_token"])}
resptoken = requests.post("https://revisionbankapi.herokuapp.com/revisionbankstripepayment",json={"price"},headers=
#import stripe
#stripe.api_key = "sk_test_51La4WnLpfbhhIhYRjP1w036wUwBoatAgqNRYEoj9u6jMd7GvSmBioKgmwJsabjgAY8V5W8i2r3QdelOPe5VNOueB00zDxeXtDQ"#
#
#striperesponse = stripe.PaymentIntent.create(
#  amount=2000,
#  currency="gbp",
#  payment_method_types=["card"],
#)
#clientsecret= striperesponse["client_secret"]

