import pymysql
import random
import string
from pymyexporter import PyMyExporter
import logging as log
import pandas as pd
from pymysqlreplication import BinLogStreamReader
import time
from tqdm import tqdm

log.basicConfig(level=log.DEBUG)

mysql_master_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': 'test'
}

mysql_slave_config = {
    'host': 'localhost',
    'port': 3307,
    'user': 'root',
    'password': '',
    'database': 'test'
}

mysql_master2_config = {
    'host': 'localhost',
    'port': 3308,
    'user': 'root',
    'password': '',
    'database': 'test'
}

MAX_RETRIES = 10
RETRY_DELAY = 5

master_conn = None
slave_conn = None
master2_conn = None

for attempt in range(MAX_RETRIES):
    try:
        master_conn = pymysql.connect(**mysql_master_config)
        slave_conn = pymysql.connect(**mysql_slave_config)
        master2_conn = pymysql.connect(**mysql_master2_config)
    except pymysql.MySQLError as e:
        if attempt < MAX_RETRIES - 1:
            log.info(f"Connection failed. Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
        else:
            if master_conn:
                master_conn.close()
            if slave_conn:
                slave_conn.close()
            if master2_conn:
                master2_conn.close()
            raise Exception("Failed to connect to MySQL")
log.info("Connected to MySQL!")

# close unnecessary connections
slave_conn.close()

master_cursor = master_conn.cursor()
master2_cursor = master2_conn.cursor()


def execute_sql(sql):
    master_cursor.execute(sql)
    master2_cursor.execute(sql)


def create_table(num_tables, num_columns_per_table):
    for i in tqdm(range(num_tables)):
        columns = ", ".join([f"column_{j} VARCHAR(255)" for j in range(num_columns_per_table)])
        create_table_sql = f"CREATE TABLE table_{i} ({columns})"
        execute_sql(create_table_sql)


def random_string(length=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))


def insert_data(num_tables, num_columns_per_table, num_rows_per_table):
    for _ in tqdm(range(num_rows_per_table)):
        random_table = f"table_{random.randint(0, num_tables - 1)}"
        random_column = f"column_{random.randint(0, num_columns_per_table - 1)}"

        insert_sql = f"INSERT INTO {random_table} ({random_column}) VALUES ('{random_string()}')"
        execute_sql(insert_sql)
        master_conn.commit()
        master2_conn.commit()


def convert_to_dict(data):
    return {(entry["metric_name"], frozenset(entry["labels"].items())): entry["value"] for entry in data}


def diff_metrics(metrics1, metrics2):
    converted_metrics1 = convert_to_dict(metrics1)
    converted_metrics2 = convert_to_dict(metrics2)
    changed_metrics = {key: (converted_metrics1[key], converted_metrics2[key]) for key in converted_metrics1 if
                       key in converted_metrics2 and converted_metrics1[key] != converted_metrics2[key]}
    changed_summary = [
        {
            "metric_name": key[0],
            "labels": dict(key[1]),
            "metric1": values[0],
            "metric2": values[1],
            "abs(diff)": abs(values[1] - values[0]),
            "percent_diff": (values[1] - values[0]) / values[0] * 100 if values[0] != 0 else "N/A",
            "diff": values[1] - values[0]
        }
        for key, values in changed_metrics.items()
    ]
    return changed_summary


if __name__ == "__main__":
    NUM_TABLES = 10
    NUM_COLUMNS_PER_TABLE = 10
    NUM_ROWS_PER_TABLE = 10000

    master_exporter = PyMyExporter(mysql_master_config['host'], 9104)
    master2_exporter = PyMyExporter(mysql_master2_config['host'], 9105)

    log.info("Creating tables...")
    try:
        create_table(NUM_TABLES, NUM_COLUMNS_PER_TABLE)
    except Exception as e:
        log.error(e)

    log.info("Inserting data...")
    insert_data(NUM_TABLES, NUM_COLUMNS_PER_TABLE, NUM_ROWS_PER_TABLE)

    stream = BinLogStreamReader(connection_settings=mysql_master2_config, server_id=100)
    stream.close()

    log.info("Getting metrics...")
    metrics1 = master_exporter.get_metrics()
    metrics2 = master2_exporter.get_metrics()
    df_changed_summary = pd.DataFrame(diff_metrics(metrics1, metrics2))
    df_changed_summary.to_csv("diff_metrics.csv", index=False)

    log.info("Metrics saved to diff_metrics.csv")

    # close cursors and connections
    master_cursor.close()
    master2_cursor.close()
    master_conn.close()
    master2_conn.close()
