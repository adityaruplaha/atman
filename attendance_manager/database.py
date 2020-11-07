
import mysql.connector


class DB:
    def __init__(self, connection_parameters, database_name):
        self.db_internal = mysql.connector.connect(
            **connection_parameters,
            database=database_name
        )
        self.deltas = []

    def push(self, sched_class, name, status=None):
        self.deltas.append((sched_class, name, status))

    def commit(self) -> bool:
        cursor = self.db_internal.cursor()
        for sched_class, name, status in self.deltas:
            try:
                sql = f"UPDATE `attendance` SET `{sched_class}` = %(status)s WHERE `Name` = %(name)s"
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

    def rollback(self):
        self.deltas.clear()
