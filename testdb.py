import json
current_user = "amari.lawal05@gmail.com"
with open("revision.json","r") as f:
    user_revision_cards = json.load(f)
with open("schedule.json","r") as f:
    user_scheduled_cards =  json.load(f)
with open("input.json","r") as f:
    data =  json.load(f)

if user_scheduled_cards:
    for card in user_scheduled_cards["revisioncards"]:
        oldcard = {i:data[i] for i in data if i!='newrevisioncard'}
        if card == oldcard:
            user_scheduled_cards["revisioncards"].remove(card)
    #importcsv.db.scheduledcards.delete_many({"email":current_user})
    #importcsv.db.scheduledcards.insert_one(user_scheduled_cards)
    #importcsv.db.scheduledcards.replace_one(
    #print(user_scheduled_cards)
    #            {"email":current_user},user_scheduled_cards
    #            )


for card in user_revision_cards["revisioncards"]:
    oldcard = {i:data[i] for i in data if i!='newrevisioncard'}
    if card == oldcard:
        user_revision_cards["revisioncards"].remove(card)
#print(user_revision_cards)
del data["revisioncard"]
data["revisioncard"] = data["newrevisioncard"]
del data["newrevisioncard"]
user_revision_cards["revisioncards"].append(data)
for rev in user_revision_cards["revisioncards"]:
    print(rev)
#importcsv.db.accountrevisioncards.replace_one(
#                {"email":current_user},user_revision_cards
#                )
#importcsv.db.accountrevisioncards.delete_many({"email":current_user})
#importcsv.db.accountrevisioncards.insert_one(user_revision_cards)
#return {"message":"revision card changed."}