import logging
import pandas as pd
import mysql.connector
from mysql.connector import Error
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            logger.info("Connected to MySQL database")
            return connection
    except Error as e:
        logger.error("Error while connecting to MySQL: %s", e)
        return None

def create_table_if_not_exists(connection, result, School, Grade, term, exam_type):
    if connection:
        cursor = connection.cursor()
        table_name = f"{School}_{Grade}_{term}_{exam_type}".replace(" ", "_").lower()  # Convert table name to lowercase
        columns = ', '.join([f'`{column}` TEXT' for column in result.columns])
        cursor.execute(f"CREATE TABLE IF NOT EXISTS `{table_name}` ({columns})")
        connection.commit()
        logger.info("Table %s created successfully", table_name)


def save_result_to_sql(result, School, Grade, term, exam_type):
    connection = get_connection()
    if connection is not None:
        try:
            password = quote_plus("Babygal@$")
            engine = create_engine(f'mysql+mysqlconnector://root:{password}@localhost:3306/results')
            table_name = f"{School}_{Grade}_{term}_{exam_type}".replace(" ", "_")
            create_table_if_not_exists(connection, result, School, Grade, term, exam_type)
            result.to_sql(table_name, con=engine, if_exists='append', index=False)
            logger.info("Data saved to table %s", table_name)
        except Exception as e:
            logger.error("Error while saving data to SQL: %s", e)
        finally:
            connection.close()
            logger.info("Connection closed")
    else:
        logger.error("Failed to save data to SQL. No connection to MySQL server.")

def insert_data_into_table(connection, table_name, data):
    if connection:
        cursor = connection.cursor()
        placeholders = ', '.join(['%s'] * len(data.columns))
        columns = ', '.join(data.columns)
        sql = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"
        try:
            cursor.executemany(sql, data.values.tolist())
            connection.commit()
            logger.info("Data inserted into table %s successfully", table_name)
        except Error as e:
            logger.error("Error while inserting data into table: %s", e)
