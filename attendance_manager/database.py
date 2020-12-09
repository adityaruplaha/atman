
import mysql.connector


class DBInterface:
    def __init__(self, connection_parameters, database_name):
        # db_internal is the Python MySQL connector object, not an user class.
        self.db_internal = mysql.connector.connect(
            **connection_parameters,
            database=database_name
        )
        self.deltas = []

    # Smart Operations

    def push(self, class_id, name, status=None):
        self.deltas.append((class_id, name, status))

    def commit(self, attendance_table_name) -> bool:
        for class_id, name, status in self.deltas:
                sql = f"UPDATE `{attendance_table_name}` SET `{class_id}` = %(status)s WHERE `Name` = %(name)s"
                if status == None:
                    pass
                elif status:
                    status = 1
                else:
                    status = 0
                is_ok = self.execute_sql(sql, {
                    'name': name,
                    'status': status
                })[0]
                if not is_ok:
                    # There was an error.
                    # SWLIMIT: Errors are discarded. Maybe shouldn't be?
                    return False
        self.db_internal.commit()
        self.deltas.clear()
        # Everything was fine. 
        return True

    def rollback(self):
        self.deltas.clear()

    # Low Level Operations
    # These should be stateless.

    def column_names(self, table_name) -> list:
        '''
        Fetch column names of given table.
        '''
        cursor = self.db_internal.cursor()
        try:
            cursor.execute(f"SELECT * FROM `{table_name}`")
            column_names = list(cursor.column_names)
            # Result set is not being used but must must be fetched to keep Python happy.
            cursor.fetchall()
            return column_names
        except mysql.connector.errors.Error:
            # SWLIMIT: Warn caller of this error?
            return []
        

    def add_column(self, table_name, column_name, attributes=[]) -> bool:
        '''
        Add a column with given name and atrributes to the given table.
        '''
        sql = f"ALTER TABLE `{table_name}` ADD `{column_name}`"
        if attributes:
            sql += ' ' + ' '.join(attributes)
        # SWLIMIT: Errors are discarded. Maybe shouldn't be?
        return self.execute_sql(sql)[0]

    def execute_sql(self, stmt, data=None) -> tuple:
        '''
        Execute any SQL statement and return a tuple:
            1. STATUS(bool): False if error occurs and True otherwise.
            2. ADDITIONAL:
                If a resultset is given by SQL, that is packed here.
                If an error is given by SQL, the error object is packed here.
                If no resultset is returned but execution didn't cause an error, `None`.
        '''
        cursor = self.db_internal.cursor()
        try:
            cursor.execute(stmt, data)
            if cursor.with_rows:
                return (True, cursor.fetchall())
            else:
                return (True,None)
        except mysql.connector.errors.Error as e:
            return (False,e)
