
import json
from csv_to_db import ImportCSV
importcsv = ImportCSV("RevisionBankDB",maindb=0)

with open("tets.json","r") as f:
    data = json.load(f)

importcsv.db.accountrevisioncards.insert_one(data)