import pandas as pd
import mysql.connector
from mysql.connector import Error
from sqlalchemy import create_engine
from urllib.parse import quote_plus

def get_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            port="3306",
            user="root",
            password="Babygal@$",
            database="results"
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print("Error while connecting to MySQL", e)
        return None

def create_table_if_not_exists(connection, result, School, Grade, term, exam_type):
    if connection:
        cursor = connection.cursor()
        table_name = f"{School}_{Grade}_{term}_{exam_type}".replace(" ", "_").lower()  # Convert table name to lowercase
        columns = ', '.join([f'`{column}` TEXT' for column in result.columns])
        cursor.execute(f"CREATE TABLE IF NOT EXISTS `{table_name}` ({columns})")
        connection.commit()


def save_result_to_sql(result, School, Grade, term, exam_type):
    connection = get_connection()
    if connection is not None:
        try:
            password = quote_plus("Babygal@$")  # Quote the password to handle special characters
            engine = create_engine(f'mysql+mysqlconnector://root:{password}@localhost:3306/results')
            table_name = f"{School}_{Grade}_{term}_{exam_type}".replace(" ", "_")
            create_table_if_not_exists(connection, result, School, Grade, term, exam_type)
            result.to_sql(table_name, con=engine, if_exists='append', index=False)
            print(f"Data saved to table {table_name}")
        except Exception as e:
            print("Error while saving data to SQL:", e)
        finally:
            connection.close()
    else:
        print("Failed to save data to SQL. No connection to MySQL server.")

def insert_data_into_table(connection, table_name, data):
    if connection:
        cursor = connection.cursor()
        placeholders = ', '.join(['%s'] * len(data.columns))
        columns = ', '.join(data.columns)
        sql = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"
        try:
            cursor.executemany(sql, data.values.tolist())
            connection.commit()
            print("Data inserted into table successfully.")
        except Error as e:
            print("Error while inserting data into table:", e)
