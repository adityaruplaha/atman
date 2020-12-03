
import mysql.connector


class DB:
    def __init__(self, connection_parameters, database_name):
        # db_internal is the Python MySQL connector object, not an user class.
        self.db_internal = mysql.connector.connect(
            **connection_parameters,
            database=database_name
        )
        self.deltas = []

    def push(self, class_id, name, status=None):
        self.deltas.append((class_id, name, status))

    def commit(self) -> bool:
        cursor = self.db_internal.cursor()
        for class_id, name, status in self.deltas:
            try:
                sql = f"UPDATE `attendance` SET `{class_id}` = %(status)s WHERE `Name` = %(name)s"
                if status == None:
                    pass
                elif status:
                    status = 1
                else:
                    status = 0
                cursor.execute(sql, {
                    'name': name,
                    'status': status
                })
            except mysql.connector.errors.Error:
                return False
        self.db_internal.commit()
        self.deltas.clear()
        return True

    def column_names(self, table_name):
        cursor = self.db_internal.cursor()
        cursor.execute(f"SELECT * FROM `{table_name}`")
        column_names = list(cursor.column_names)
        # Result set is not being used but must must be fetched to keep Python happy.
        cursor.fetchall()
        return column_names

    def add_column(self, table_name, column_name, attributes=[]):
        cursor = self.db_internal.cursor()
        try:
            sql = f"ALTER TABLE `{table_name}` ADD `{column_name}`"
            if attributes:
                sql += ' ' + ' '.join(attributes)
            cursor.execute()
            cursor.execute(sql)
        except mysql.connector.errors.Error:
            return False

    def rollback(self):
        self.deltas.clear()
