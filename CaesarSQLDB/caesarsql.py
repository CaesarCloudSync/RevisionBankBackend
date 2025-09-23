import time
import json
import psycopg
import subprocess
from urllib.parse import urlparse
from typing import Any, Callable, Union

class CaesarSQLDetails:
    conStr = 'postgresql://postgres:SwonICiI0KhtaeHg@db.uamkdvfdvcnyggrywekf.supabase.co:5432/postgres'
    p = urlparse(conStr)

    pg_connection_dict = {
        'dbname': p.scheme,
        'user': p.username,
        'password': p.password,
        'port': p.port,
        'host': p.hostname,
        "autocommit" : True,
        "prepare_threshold":None

    }
class CaesarSQLContextManager: 
    
    async def __aenter__(self) -> None:
        self.aconn = await psycopg.AsyncConnection.connect(**CaesarSQLDetails.pg_connection_dict)
        return self
    async def run_command_generator(self,sqlcommand : str = None,arraysize:int =1000, datatuple : tuple =None,filename :str = None,verbose:int=1):
        # Executes SQL Command or takes SQL file as input.
        #if verbose == 1:
            #if self.connection.is_connected():
            #    db_Info = self.connection.get_server_info()
            #    print("Connected to MySQL Server version ", db_Info)
        if sqlcommand == None and filename == None:
            print("Please input an SQL command or SQL filename.")
        else:
            if filename != None:
               with open(filename) as f:
                   sqlcommand = f.read()
            try:
                async with self.aconn.cursor() as cursor:
                    #print(datatuple)
                    await cursor.execute(sqlcommand,datatuple)
                    if verbose == 1:
                        print("SQL command executed.")
                    while True:
                        results = await cursor.fetchmany(arraysize)
                        if not results:
                            break
                        for result in results:
                            yield result
            except Exception as poe:
                print(f"{type(poe)} - {poe}")
    async def run_command(self,sqlcommand : str = None,result_function : Callable =None,datatuple : tuple =None,filename :str = None,verbose:int=0):
        # Executes SQL Command or takes SQL file as input.
        #if verbose == 1:
            #if self.connection.is_connected():
            #    db_Info = self.connection.get_server_info()
            #    print("Connected to MySQL Server version ", db_Info)
        if sqlcommand == None and filename == None:
            print("Please input an SQL command or SQL filename.")
        else:
            if filename != None:
               with open(filename) as f:
                   sqlcommand = f.read()
            
            async with self.connection.cursor() as cursor:
                #print(datatuple)
                await cursor.execute(sqlcommand,datatuple)

                result = await cursor.fetchall()
                    
                
                if result_function != None:
                    new_result = result_function(result)
                elif result_function == None:
                    new_result = None

                #self.connection.commit()
            if verbose == 1:
                print("SQL command executed.")
                return new_result
            else:
                return new_result
    async def tuple_to_json(self,fields:tuple,result:tuple):
        if type(result[0]) == tuple:
            final_result = []
            for entry in result:
                entrydict = dict(zip(fields,entry))
                final_result.append(entrydict)
            return final_result
        elif type(result[0]) == str:
            final_result = dict(zip(fields,result))
            return final_result 
        
    async def __aexit__(self, exc_type, exc, tb):
        await self.aconn.close()
                    
class CaesarSQL:
    def __init__(self) -> None:
        # Makes SQL connection to remote server.



        self.connection = psycopg.connect(**CaesarSQLDetails.pg_connection_dict)


    def check_exists(self,result :Any):
        # Checks if an entity exists from an SQL Command.
        try:
            if len(result) == 0:
                return False
            else:
                return True
        except Exception as poe:
            return False
        
    def load_json_file(self,filename:str):
        # Loads json file
        with open(filename) as f:
            datajson = json.load(f)
        return datajson
    
    def fetch(self,result:Any):
        # Callback function that fetches data after an SQL command is run self.runcommand("SELECT * FROM names WHERE name LIKE 'bill'",self.fetch)
        return result
    
    def json_to_sql(self,datajson :Union[dict,list]):
        # Converts JSON to SQL.
        if type(datajson) == list: 
            columns = str(tuple(datajson[0].keys())).replace("'","")
            values = str(tuple(tuple(data.values())  for data in datajson))[1:-1]
            return columns,values
        elif type(datajson) == dict:
            columns = str(tuple(datajson.keys())).replace("'","")
            values = str(tuple(datajson.values())).replace("'","")
            return columns,values
        else:
            print("JSON is invalid data shape.")
            return None,None
    def executeScriptsFromFile(self,filename):
        fd = open(filename, 'r')
        sqlFile = fd.read()
        fd.close()
        sqlCommands = sqlFile.split(';')
        print(sqlCommands)
        with self.connection.cursor() as cursor:
            for command in sqlCommands:
                try:
                    if command.strip() != '':
                        print(command)
                        cursor.execute(command.replace("\n","").replace("\n",""))
                except IOError as ex:
                    print ("Command skipped: ", type(ex),ex )

    def run_command(self,sqlcommand : str = None,result_function : Callable =None,datatuple : tuple =None,filename :str = None,verbose:int=0):
        # Executes SQL Command or takes SQL file as input.
        #if verbose == 1:
            #if self.connection.is_connected():
            #    db_Info = self.connection.get_server_info()
            #    print("Connected to MySQL Server version ", db_Info)
        if sqlcommand == None and filename == None:
            print("Please input an SQL command or SQL filename.")
        else:
            if filename != None:
               with open(filename) as f:
                   sqlcommand = f.read()
            
            with self.connection.cursor() as cursor:
                #print(datatuple)
                cursor.execute(sqlcommand,datatuple)

                result = cursor.fetchall()
                    
                
                if result_function != None:
                    new_result = result_function(result)
                elif result_function == None:
                    new_result = None

                #self.connection.commit()
            if verbose == 1:
                print("SQL command executed.")
                return new_result
            else:
                return new_result


    async def run_command_generator(self,sqlcommand : str = None,arraysize:int =1000, datatuple : tuple =None,filename :str = None,verbose:int=1):
        # Executes SQL Command or takes SQL file as input.
        #if verbose == 1:
            #if self.connection.is_connected():
            #    db_Info = self.connection.get_server_info()
            #    print("Connected to MySQL Server version ", db_Info)
        if sqlcommand == None and filename == None:
            print("Please input an SQL command or SQL filename.")
        else:
            if filename != None:
               with open(filename) as f:
                   sqlcommand = f.read()
            try:
                async with self.connection.cursor() as cursor:
                    #print(datatuple)
                    await cursor.execute(sqlcommand,datatuple)
                    if verbose == 1:
                        print("SQL command executed.")
                    while True:
                        results = await cursor.fetchmany(arraysize)
                        if not results:
                            break
                        async for result in results:
                            yield result
            except Exception as poe:
                print(f"{type(poe)} - {poe}")

    def sql_to_json(self,table,sqldata :tuple):
        # Convert SQL tuple to json
        columnsinfo = self.run_command(f"DESCRIBE {table}",self.fetch)
        columns = [col[0] for col in columnsinfo]
        #print(sqldata)
        final_json = []
        for data in sqldata:
            record = {}
            for ind in range(len(data)):
                record.update({data[ind]: columns[ind]} )
            final_json.append(record)
        
        return {table:final_json}
    @staticmethod
    def convert_to_blob(filename :str):
        # Convert digital data to binary format
        with open(filename, 'rb') as file:
            blobData = file.read()
        return blobData
    @staticmethod
    def start_docker_db(verbose=1):
        # Start the docker database
        # Run the database commands - "docker exec -it mysql mysql -p"
        # https://mothishdeenadayalan.medium.com/containerizing-a-python-app-mysql-python-docker-1ce64e444ed9
        dockercommand = 'docker run --name mysql -p 3306:3306 -v mysql_volume:/var/lib/mysql/ -d -e "MYSQL_ROOT_PASSWORD=temp123" mysql'
        process = subprocess.Popen(dockercommand.split(),
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if stderr != b"" and verbose == 1:
            print(stderr)
        elif stderr == b"" and verbose == 1:
            print(stdout)
        time.sleep(2)
        return stdout,stderr






def test():
    import asyncio

    async def main():
        async with  CaesarSQLContextManager() as cex:
            async for test in  cex.run_command_generator("SELECT (email,password) FROM users;"):
                print(await cex.tuple_to_json(("email","password"),test))
                
        await asyncio.sleep(1)
        print('world')

    asyncio.run(main())
