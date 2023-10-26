class CaesarCreateTables:
    def __init__(self) -> None:
        self.usersfields = ("email","password")
        self.studentsubscriptionsfields =  ("hostemail","email","password","emailsleft")
        self.revisioncardfields = ("email","sendtoemail","subject","revisioncardtitle","revisionscheduleinterval","revisioncard","revisioncardimgname","revisioncardhash")
        self.revisioncardimagefields = ("revisioncardimgname","email","filetype","revisioncardhash","revisioncardimage")
        self.scheduledcardfields = ("email","revisioncardhash","scheduleId")
        self.schedule_table = "scheduledcards"
        self.accountrevisioncards_table = "accountrevisioncards"
        self.revisioncardimage_table = "revisioncardimages"
        

    def create(self,caesarcrud):
        caesarcrud.create_table("userid",self.usersfields,
        ("varchar(255) NOT NULL","varchar(255) NOT NULL"),
        "users")
        caesarcrud.create_table("studentsubscriptionsid",self.studentsubscriptionsfields,
        ("varchar(255) NOT NULL","varchar(255) NOT NULL","varchar(255) NOT NULL","INT"),
        "studentsubscriptions")
        caesarcrud.create_table("revisioncardid",self.revisioncardfields,
        ("varchar(255) NOT NULL","varchar(255) NOT NULL","varchar(255) NOT NULL","varchar(255) NOT NULL","varchar(255) NOT NULL","TEXT NOT NULL","varchar(255)","TEXT NOT NULL"),
        "accountrevisioncards")
        caesarcrud.create_table("revisioncardimageid",self.revisioncardimagefields,
        ("varchar(255) NOT NULL","varchar(255) NOT NULL","varchar(255) NOT NULL","varchar(255) NOT NULL","MEDIUMBLOB"),
        "revisioncardimages")
        caesarcrud.create_table("schedulecardsid",self.scheduledcardfields,
        ("varchar(255) NOT NULL","TEXT NOT NULL","TEXT NOT NULL"),
        "scheduledcards")

