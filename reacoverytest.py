
import json
from csv_to_db import ImportCSV
importcsv = ImportCSV("RevisionBankDB",maindb=0)

with open("tets.json","r") as f:
    user_revision_cards = json.load(f)
with open("input.json") as f:
    data = json.load(f)
importcsv.db.accountrevisioncards.insert_one(user_revision_cards)
def test():
    left_over_images = []
    for card in user_revision_cards["revisioncards"]:
        oldcard = {i:data[i] for i in data if i!='newrevisioncard'}
        
        oldcard["translation"] = card["translation"]    
        oldcard["revisioncardimgname"] = card["revisioncardimgname"]    
        oldcard["revisioncardimage"] = card["revisioncardimage"]     

        if card == oldcard:
            user_revision_cards["revisioncards"].remove(card)
            left_over_images.append({"revisioncardimgname":card["revisioncardimgname"],"revisioncardimage":card["revisioncardimage"] })



    #print(user_revision_cards)
    del data["revisioncard"]
    data["revisioncard"] = data["newrevisioncard"]
    del data["newrevisioncard"]
    user_revision_cards["revisioncards"].insert(0,data) # .append()

                    #importcsv.db.accountrevisioncards.delete_many({"email":current_user}