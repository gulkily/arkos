#print('Hi')
import psycopg2
con = psycopg2.connect(user="postgres",
                        password="your_password",
                        host="localhost",
                        port="5432")

# # function to create connection
# def createConnection(dbname):
#     # this executes when no database has been created
#     if dbname == 'default':
#         con = psycopg2.connect(user="postgres",
#                                password="your_password",
#                                host="localhost",
#                                port="5432")
#         # this is required for auto committing changes
#         con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
#     # this executes when database has been created
#     else:
#         con = psycopg2.connect(user="postgres",
#                                database=dbname,
#                                password="your_password",
#                                host="localhost",
#                                port="5432")
#     return con

cursor = con.cursor()


# ##CHROMA DB
# import chromadb
# chroma_client = chromadb.Client()

# # switch `create_collection` to `get_or_create_collection` to avoid creating a new collection every time
# collection = chroma_client.get_or_create_collection(name="my_collection")

# # switch `add` to `upsert` to avoid adding the same documents every time
# collection.upsert(
#     documents=[
#         "This is a document about pineapple",
#         "This is a document about oranges"
#     ],
#     ids=["id1", "id2"]
# )

# results = collection.query(
#     query_texts=["This is a query document about florida"], # Chroma will embed this for you
#     n_results=2 # how many results to return
# )

# print(results)

# function to create database and insert data
def createData(processedData):
    # creates connection to databse with some default settings
    con = createConnection('default')
    cursor = con.cursor()
    # database name and code to create table in the database
    name_Database = "gamedata"
    tableCreation = "CREATE TABLE gamewarehouse (id serial PRIMARY KEY,teams varchar(200),year integer,\
    wins integer,losses integer)"
    
    try:
        # this checks if database is available or not
        checkDatabase = "SELECT datname FROM pg_catalog.pg_database WHERE datname='gamedata';"
        cursor.execute(checkDatabase)
        result = cursor.fetchone()
        # this will create database if not available
        if not result:
            # first create database
            sqlCreateDatabase = "create database "+name_Database+";"
            cursor.execute(sqlCreateDatabase)
            cursor.destroyConnection(con)
            
            # second create table
            con = cursor.createConnection(name_Database)            
            cursor = con.cursor()
            cursor.execute(tableCreation)
            con.commit() 
            destroyConnection(con)
            
            # this is required to insert pandas dataframe directly into database
            engine = create_engine('postgresql+psycopg2://postgres:your_password@localhost:5432/gamedata')
            processedData.to_sql('gamewarehouse', engine, if_exists='append',index=False)            
            engine.dispose()
            print('Database created successfully!');           
            
    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)



destroyConnection(con)
