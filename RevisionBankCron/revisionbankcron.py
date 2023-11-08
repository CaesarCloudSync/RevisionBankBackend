import os
import base64
import datetime
import requests
class RevisionBankCron:
  def __init__(self) -> None:
     self.qstash_access_token = base64.b64decode(os.environ.get("QSTASH_ACCESS_TOKEN").encode()).decode()
  # Minutes
    
  def minute_cron_time(self,datetime_string):
    minute_num = int(datetime_string.replace("MI",""))
    if minute_num < 60 and minute_num > 0:
      return f"*/{minute_num} * * * *"
    else:
      return False
# Hours
  
  def hour_cron_time(self,datetime_string):
    hour_num = int(datetime_string.replace("H",""))
    if hour_num < 24 and hour_num > 0:
      return f"{datetime.datetime.now().minute} */{hour_num} * * *"
    else:
      return False
 # Days
  
  def day_cron_time(self,datetime_string):
    day_num = int(datetime_string.replace("D",""))
    if day_num < 31 and day_num > 0:
      return f"{datetime.datetime.now().minute} {datetime.datetime.now().hour} */{day_num} * *"
    else:
      return False
    
  # Months
  
  def month_cron_time(self,datetime_string):
    month_num = int(datetime_string.replace("MO",""))
    if month_num < 12 and month_num > 0:
      return f"{datetime.datetime.now().minute} {datetime.datetime.now().hour} {datetime.datetime.now().day} */{month_num} *"
    else:
      return False
  def create_schedule(self,card,current_user):
        interval = str(card['revisionscheduleinterval'])

        if "MI" in interval:
            cronstr = self.minute_cron_time(interval)
        elif "H" in interval:
            cronstr = self.hour_cron_time(interval)
        elif "D" in interval:
            cronstr = self.day_cron_time(interval)
        elif "MO" in interval:
            cronstr = self.month_cron_time(interval)
        elif len(interval) <= 2:
            cronstr = f"*/{interval} * * * *"
        

        

      
        card["email"] = current_user
        resp = requests.post("https://qstash.upstash.io/v2/schedules/https://revisionbankbackendsql-aoz2m6et2a-uc.a.run.app/sendscheduledrevisioncard",json=card,headers= {"Authorization": f"Bearer {self.qstash_access_token}","Upstash-Cron":f"{cronstr}"})
        print(resp.json())
        scheduleId = resp.json()["scheduleId"]
        return scheduleId

  
