import os
import base64
import requests
from RevisionBankCron.revisionbankcron import RevisionBankCron
from CaesarSQLDB.caesarcrud import CaesarCRUD
from CaesarSQLDB.caesar_create_tables import CaesarCreateTables
class RevisionBankSQLOps:
    def __init__(self,caesarcrud : CaesarCRUD,caesarcreatetables : CaesarCreateTables) -> None:
        self.caesarcrud = caesarcrud
        self.caesarcreatetables = caesarcreatetables
        self.qstash_access_token = base64.b64decode(os.environ.get("QSTASH_ACCESS_TOKEN").encode()).decode()
    def store_revisoncard(self,revisioncard,revisioncardhash,current_user,table):
        revisioncardvalues = (current_user,revisioncard["sendtoemail"],revisioncard["subject"],revisioncard["revisioncardtitle"],revisioncard["revisionscheduleinterval"],revisioncard["revisioncard"],revisioncardhash)
        res = self.caesarcrud.post_data(("email","sendtoemail","subject","revisioncardtitle","revisionscheduleinterval","revisioncard","revisioncardhash"),
                                revisioncardvalues,table)
        return res
    def store_revisoncard_image(self,current_user,revisioncardimgname,revisioncardimage,revisioncardhash):
        filetype,revisioncardimage = revisioncardimage.split(",", 1)[0] + ",",revisioncardimage.split(",", 1)[1]
                           

        tableblob = "revisioncardimages"

        resblob = self.caesarcrud.post_data(("revisioncardimgname","email","filetype","revisioncardhash"),
                    (revisioncardimgname,current_user,filetype,revisioncardhash),tableblob)
        resblob = self.caesarcrud.update_blob("revisioncardimage",revisioncardimage,tableblob,f"revisioncardhash = '{revisioncardhash}' AND revisioncardimgname = '{revisioncardimgname}'")
        return resblob    
    def update_revisoncard_image(self,revisioncardimgname,revisioncardimage,revisioncardhash,oldrevisioncardimgname):
        tableblob = "revisioncardimages"
        condition = f"revisioncardhash = '{revisioncardhash}' AND revisioncardimgname = '{oldrevisioncardimgname}'"
        filetype,revisioncardimage = revisioncardimage.split(",", 1)[0] + ",",revisioncardimage.split(",", 1)[1]
                           

        tableblob = "revisioncardimages"

        resblob = self.caesarcrud.update_blob("revisioncardimage",
            revisioncardimage,tableblob,condition=condition)
        resblob = self.caesarcrud.update_data(("revisioncardimgname","filetype"),
                    (revisioncardimgname,filetype),tableblob,condition=condition)
    

        return resblob    
    
    def unschedule_card_qstash(self,condition):
        card = self.caesarcrud.get_data(("scheduleId",),self.caesarcreatetables.schedule_table,condition=condition)[0]
        scheduleId = card.get("scheduleId")
        if scheduleId:
            resp = requests.delete(f"https://qstash.upstash.io/v2/schedules/{scheduleId}",headers={"Authorization": f"Bearer {self.qstash_access_token}"})
            self.caesarcrud.delete_data(self.caesarcreatetables.schedule_table,condition=condition)
    