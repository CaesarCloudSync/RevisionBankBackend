import os
import base64
import requests
class RevisionBankUtils:
    def __init__(self,importcsv) -> None:
        self.importcsv = importcsv
        self.qstash_access_token = base64.b64decode(os.environ.get("QSTASH_ACCESS_TOKEN").encode()).decode()
    def unschedule_change_cards(self,oldcard_data,current_user):
        scheduled_exists = self.importcsv.db.scheduledcards.find_one({"email":current_user})
        if scheduled_exists:
            user_scheduled_cards = list(self.importcsv.db.scheduledcards.find({"email": current_user}))[0]
            if user_scheduled_cards:
                for card in user_scheduled_cards["revisioncards"]:
                    

                    if card['revisioncardtitle'] == oldcard_data['revisioncardtitle'] and card["subject"] == oldcard_data["subject"]:
                        scheduleId = card.get("scheduleId")
                        if scheduleId:
                            del card["scheduleId"]
                        if scheduleId:
                            resp = requests.delete(f"https://qstash.upstash.io/v2/schedules/{scheduleId}",headers={"Authorization": f"Bearer {self.qstash_access_token}"})
                            user_scheduled_cards["revisioncards"].remove(card)

                self.importcsv.db.scheduledcards.replace_one(
                            {"email":current_user},user_scheduled_cards
                            )
                return True
            else:
                return True
        else:
            return True
                        
    def get_card_to_update(self,user_revision_cards,oldcard_data,current_user):
        
        edited_card = {}
        for card in user_revision_cards["revisioncards"]:   
            #print(oldcard)
            if card['revisioncardtitle'] == oldcard_data['revisioncardtitle'] and card["subject"] == oldcard_data["subject"]:
                edited_card.update(card)
                user_revision_cards["revisioncards"].remove(card)
        return user_revision_cards,edited_card
        