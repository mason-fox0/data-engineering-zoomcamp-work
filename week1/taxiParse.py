import sys
import os
from dotenv import load_dotenv
import numpy as np
import polars as pl
import sqlalchemy as sqa

def main():
    #envs 
    POSTGRES_USER = "postgres"
    POSTGRES_HOST = "localhost"
    POSTGRES_PORT = "5432"
    POSTGRES_DB   = "NYC_Taxi"
    env_file_name = "./docker_password.env"
    load_dotenv(env_file_name)
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"


    if len(sys.argv) != 3: #file name is first arg, expecting another for filename
        raise Exception("Unexpected command line argument. Usage: python taxiParse.py (init OR modify OR addtable) myfilepath")
    else:
        action = str(sys.argv[1])

        eng = sqa.create_engine(DATABASE_URL, connect_args={"connect_timeout": 10})
        pq_file_path = str(sys.argv[2])
        col, dat = process_parquet(pq_file_path)

        if action == "init":
            table = add_table(eng, "Rides", col)
        elif action == "modify":
            table = modify_table(eng, "Rides")
        elif action == "addtable":
            table_name = str(input("Enter table name: "))
            table = add_table(eng, table_name, col) 
        else:
            raise Exception("Invalid Action. Must be init OR modify OR addtable. Usage: python taxiParse.py [init OR modify OR addtable] myfilepath")
        
        insert_data(eng, table, dat, batch_size= min(50000, len(dat)) )

def add_table(engine, table_name, columns):
    metadata = sqa.MetaData()
    table = sqa.Table(table_name, metadata, *columns)
    metadata.create_all(engine)

    return table

def modify_table(engine, table_name):
    metadata = sqa.MetaData()
    table = sqa.Table(table_name, metadata, autoload_with=engine)

    return table

def process_parquet(pq_file_path):
    df = pl.read_parquet(pq_file_path)
    
    #map parquet schema to sql types
    columns = []
    for name, pq_dtype in df.schema.items():
        if pq_dtype == pl.Int64 or pq_dtype == pl.Int32:
            sql_type = sqa.Integer
        elif pq_dtype == pl.Float64:
            sql_type = sqa.Float
        elif pq_dtype == pl.Utf8:
            sql_type = sqa.String
        elif pq_dtype == pl.Boolean:
            sql_type = sqa.Boolean
        elif pq_dtype == pl.Date:
            sql_type = sqa.Date
        elif pq_dtype == pl.Datetime:
            sql_type = sqa.DateTime
        else:
            print(f"Warning: Unexpected dataframe datatype in column {name} of type {pq_dtype}")
            sql_type = sqa.String

        columns.append(sqa.Column(name, sql_type))


    data = df.to_dicts()

    return columns, data

def insert_data(engine, table, data, batch_size):
    data_size = len(data)
    print(data_size)
    
    with engine.begin() as connection:
        for start in range(0, data_size, batch_size):
            end = start + batch_size
            batch = data[start:end] #apparently this is safe even if size(data) < batch_size

            connection.execute(table.insert(), batch)
            print(f"Batch inserted successfully, through record number {end}")

    print("Done")

if __name__ == "__main__":
    main()
