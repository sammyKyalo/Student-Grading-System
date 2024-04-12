import logging
import sqlite3
from sqlite3 import Error

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_connection():
    try:
        connection = sqlite3.connect('results.db')
        logger.info("Connected to SQLite database")
        return connection
    except Error as e:
        logger.error("Error while connecting to SQLite: %s", e)
        return None

def create_table_if_not_exists(connection, table_name, columns):
    if connection:
        cursor = connection.cursor()
        create_table_query = f"CREATE TABLE IF NOT EXISTS `{table_name}` ({columns})"
        try:
            cursor.execute(create_table_query)
            connection.commit()
            logger.info("Table %s created successfully", table_name)
        except Error as e:
            logger.error("Error creating table %s: %s", table_name, e)

def save_result_to_sql(result, School, Grade, term, exam_type):
    connection = get_connection()
    if connection is not None:
        try:
            table_name = f"{School}_{Grade}_{term}_{exam_type}".replace(" ", "_").lower()
            columns = ', '.join([f'`{column}` TEXT' for column in result.columns])
            create_table_if_not_exists(connection, table_name, columns)
            cursor = connection.cursor()
            placeholders = ', '.join(['?' for _ in result.columns])
            insert_query = f"INSERT INTO `{table_name}` VALUES ({placeholders})"
            data = [tuple(row) for row in result.values]
            cursor.executemany(insert_query, data)
            connection.commit()
            logger.info("Data saved to table %s", table_name)
        except Exception as e:
            logger.error("Error while saving data to SQLite: %s", e)
        finally:
            connection.close()
            logger.info("Connection closed")
    else:
        logger.error("Failed to save data to SQLite. No connection to SQLite database.")

def insert_data_into_table(connection, table_name, data):
    if connection:
        cursor = connection.cursor()
        placeholders = ', '.join(['?'] * len(data.columns))
        columns = ', '.join(data.columns)
        insert_query = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"
        try:
            cursor.executemany(insert_query, data.values.tolist())
            connection.commit()
            logger.info("Data inserted into table %s successfully", table_name)
        except Error as e:
            logger.error("Error while inserting data into table: %s", e)
