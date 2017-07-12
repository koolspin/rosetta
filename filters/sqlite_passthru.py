import json
import re
import datetime

import sqlite3

from filters.tornado_source import TornadoSource
from graph.filter_base import FilterBase
from graph.input_pin import InputPin
from graph.output_pin import OutputPin


class SqlitePassthru(FilterBase):
    """
    A filter that writes the payload to a sqlite database
    """
    CONFIG_KEY_TABLE_NAME_REGULAR_EXPRESSION = 'table_name_re'
    CONFIG_KEY_INSERT_TIMESTAMP_FLAG = 'insert_timestamp'
    CONFIG_KEY_UNIQUE_COLUMNS = 'unique_columns'
    CONFIG_KEY_DB_FILENAME = 'db_filename'

    def __init__(self, name, config_dict):
        super().__init__(name, config_dict)
        self._table_name_re = config_dict[SqlitePassthru.CONFIG_KEY_TABLE_NAME_REGULAR_EXPRESSION]
        self._insert_timestamp_flag = config_dict[SqlitePassthru.CONFIG_KEY_INSERT_TIMESTAMP_FLAG]
        self._unique_columns = config_dict.get(SqlitePassthru.CONFIG_KEY_UNIQUE_COLUMNS)
        self._db_filename = config_dict.get(SqlitePassthru.CONFIG_KEY_DB_FILENAME)
        mime_type_map = {}
        mime_type_map['application/json'] = self.recv
        ipin = InputPin('input', mime_type_map, self)
        self._add_input_pin(ipin)
        self._output_pin = OutputPin('output', False)
        self._add_output_pin(self._output_pin)

    def run(self):
        self._db_conn = sqlite3.connect(self._db_filename)

    def stop(self):
        self._db_conn.close()
        self._db_conn = None

    def recv(self, mime_type, payload, metadata_dict):
        if self._should_process_payload(metadata_dict):
            self._process_payload(payload, metadata_dict)
        # This is a passthru filter so we need to pass the payload through
        self._output_pin.send(mime_type, payload, metadata_dict)

    def _should_process_payload(self, metadata_dict):
        """
        Check if the payload should be processed by comparing the path to the table_name regular expression
        The uri path should be of the form /db/table_name - where db is used in the routing table and table name
        is used to match with the regular expression from the filter's config dictionary.


        :param metadata_dict: A metadata dictionary passed from the upstream filters
        :return: True if the payload should be processed, false if not
        """
        uri_path = metadata_dict.get(TornadoSource.METADATA_KEY_REQUEST_PATH)
        if uri_path is not None:
            path_components = uri_path.split('/')
            if len(path_components) > 2:
                self._table_name = path_components[2]
                found = re.match(self._table_name_re, self._table_name)
                return found
        return False

    def _process_payload(self, payload, metadata_dict):
        """
        Save a row to the database, creating the table first if necessary
        :param payload: The json payload to insert
        :param metadata_dict: The metadata dictionary passed from the upstream filter
        :return: True if the row was saved, false if not
        """
        pay_dict = json.loads(payload)
        self._create_table(pay_dict, self._table_name)
        ok = self._save_row(pay_dict, self._table_name)
        return ok

    def _create_table(self, payload_dict, table_name):
        """
        Create a table in the sqlite db if necessary, with the appropriate columns
        :param payload_dict: The payload dictionary to use for column names
        :param table_name: The name of the table to create
        :return: None
        """
        sql_stmt = "CREATE TABLE IF NOT EXISTS {0} (_id INTEGER PRIMARY KEY".format(table_name)
        if self._insert_timestamp_flag:
            sql_stmt += ", {0} {1}".format('rosetta_timestamp', 'TEXT')
        for key, value in payload_dict.items():
            typestr = None
            if type(value) is int:
                typestr = 'INTEGER'
            elif type(value) is float:
                typestr = 'REAL'
            elif type(value) is str:
                typestr = 'TEXT'
            if typestr is not None:
                sql_stmt += ", {0} {1}".format(key, typestr)
            if key in self._unique_columns:
                sql_stmt += " UNIQUE"
        sql_stmt += ")"
        #
        cur = self._db_conn.cursor()
        cur.execute(sql_stmt)
        self._db_conn.commit()

    def _save_row(self, payload_dict, table_name):
        """
        Save row in the database, by doing an upsert.
        :param payload_dict: The payload dictionary to use for column names and values
        :param table_name: The name of the table to insert to
        :return: True if saved, false if not
        """
        cols = []
        if self._insert_timestamp_flag:
            cols.append('rosetta_timestamp')
        for key in payload_dict.keys():
            cols.append(key)
        #
        sql_stmt = "INSERT OR REPLACE INTO {0} (".format(table_name)
        ix = 0
        for col in cols:
            if ix > 0:
                sql_stmt += ", "
            sql_stmt += col
            ix += 1
        sql_stmt += ") VALUES ("
        val_array = []
        ix = 0
        if self._insert_timestamp_flag:
            now = datetime.datetime.utcnow()
            iso = now.isoformat()
            val_array.append(iso)
            sql_stmt += "?"
            ix += 1
        for value in payload_dict.values():
            typestr = None
            if type(value) is int:
                typestr = 'INTEGER'
            elif type(value) is float:
                typestr = 'REAL'
            elif type(value) is str:
                typestr = 'TEXT'
            if typestr is not None:
                val_array.append(value)
                if ix > 0:
                    sql_stmt += ", "
                sql_stmt += "?"
                ix += 1
        sql_stmt += ")"
        #
        cur = self._db_conn.cursor()
        cur.execute(sql_stmt, val_array)
        self._db_conn.commit()
        return True
