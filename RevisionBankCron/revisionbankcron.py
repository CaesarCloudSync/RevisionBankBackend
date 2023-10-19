import datetime

class RevisionBankCron:
  # Minutes
  @staticmethod
  def minute_cron_time(datetime_string):
    minute_num = int(datetime_string.replace("MI",""))
    if minute_num < 60 and minute_num > 0:
      return f"*/{minute_num} * * * *"
    else:
      return False
# Hours
  @staticmethod
  def hour_cron_time(datetime_string):
    hour_num = int(datetime_string.replace("H",""))
    if hour_num < 24 and hour_num > 0:
      return f"{datetime.datetime.now().minute} */{hour_num} * * *"
    else:
      return False
 # Days
  @staticmethod
  def day_cron_time(datetime_string):
    day_num = int(datetime_string.replace("D",""))
    if day_num < 31 and day_num > 0:
      return f"{datetime.datetime.now().minute} {datetime.datetime.now().hour} */{day_num} * *"
    else:
      return False
    
  # Months
  @staticmethod
  def month_cron_time(datetime_string):
    month_num = int(datetime_string.replace("MO",""))
    if month_num < 12 and month_num > 0:
      return f"{datetime.datetime.now().minute} {datetime.datetime.now().hour} {datetime.datetime.now().day} */{month_num} *"
    else:
      return False
