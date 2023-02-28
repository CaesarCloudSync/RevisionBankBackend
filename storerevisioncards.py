from csv_to_db import ImportCSV
import os
importcsv = ImportCSV("RevisionBankDB")
importcsvqp = ImportCSV("RevisionBankDB",maindb= False)
"""
if __name__ == '__main__':
        try:
            edexcelpapers = list(importcsv.db.edexcelpapers.find()[:2])
            print(edexcelpapers)
            #del edexcelpapers["_id"]
            #print({"edexcelpaper":edexcelpapers}
        except Exception as e:
            print({f"error":f"{type(e)},{str(e)}"})
"""

def insert_cards(revision_cards):
    try:
        data = {"email":"amari.lawal05@gmail.com","revisioncards":revision_cards}
        email_exists = importcsv.db.accountrevisioncards.find_one({"email":"amari.lawal05@gmail.com"})
        if email_exists:  # Checks if email exists
            cards_not_exist = []
            user_revision_cards = list(importcsv.db.accountrevisioncards.find({"email": "amari.lawal05@gmail.com"}))[0] # Gets the email.
            
            #print(user_revision_cards)
            for card in data["revisioncards"]: # Checks if the revision card exists in the database.
                if card not in user_revision_cards["revisioncards"]:
                    cards_not_exist.append(card) # If not, add it to the list.
                    #cards_that_exist.append(card)
            if cards_not_exist != []:
                new_cards = cards_not_exist + user_revision_cards["revisioncards"] # adds new cards to the list.
                user_revision_cards["revisioncards"] = new_cards # Updates the list.
                del user_revision_cards["_id"]
                user_revision_cards["email"] = "amari.lawal05@gmail.com" # Sets the email to the current user.
                importcsv.db.accountrevisioncards.delete_many({"email":"amari.lawal05@gmail.com"}) # Allows data to be updated.
                importcsv.db.accountrevisioncards.insert_one(user_revision_cards) # Inserts the new data.
                print({"message":"revision cards updated"})
            elif cards_not_exist == []: # If the cards are already in the database, print(a message.
                print({"message":"No new cards"})

        elif not email_exists:
            data["email"] = "amari.lawal05@gmail.com"
            importcsv.db.accountrevisioncards.insert_one(data)

            print({"message": "revision card stored"})
    except Exception as ex:
        print(type(ex),ex)

def load_cards(dir, subject):
    chapter_revision_cards = []
    chapters = os.listdir(dir)
    for chapter in chapters:
        cards = os.listdir(f"{dir}/{chapter}")
        for card in cards:
            if card.endswith(".txt"):
                with open(f"{dir}/{chapter}/{card}", "r", encoding="utf8") as f:
                    cardjson = {"subject":f"AS Level {subject.capitalize()}","revisioncardtitle":chapter,"revisioncard":f.read()}
                    chapter_revision_cards.append(cardjson)

    return chapter_revision_cards
if __name__ == "__main__":
    physicsdir = f"C:/Users/user1/Desktop/RevisionBank/RevisionBank Scheduler/AS Level Card Sender/physicscards"
    computersciencedir = f"C:/Users/user1/Desktop/RevisionBank/RevisionBank Scheduler/AS Level Card Sender/computersciencecards"



if __name__ == "__main__":
    #revisioncards = load_cards(physicsdir,"physics")
    #insert_cards(revisioncards)
    #print(revisioncards[0])
    revisioncardscmp = load_cards(computersciencedir,"computer science")
    insert_cards(revisioncardscmp)
    #print(revisioncardscmp[0])
    #load_cards(computersciencedir,"computer science")
    
