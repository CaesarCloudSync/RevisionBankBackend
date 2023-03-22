
from csv_to_db import ImportCSV
importcsv = ImportCSV("RevisionBankDB",maindb=0)

print(list(importcsv.db.oplog.rs.find()))