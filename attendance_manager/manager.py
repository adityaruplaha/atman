import datetime
import enum

from attendance_manager.database import DB
from attendance_manager.sched_class import SchedClass


class ReturnCode(enum.Enum):
    # Success
    SUCCESS = 0,
    # Errors
    FILE_NOT_FOUND = 1,
    FILE_EXISTS = 2,
    SQL_ERROR = 3,
    UNDEFINED_CLASS = 4,

    UNKNOWN_ERROR = 127,
    # Warnings
    NO_MATCH = 128,
    MULTIPLE_MATCH = 129,
    EMPTY_INPUT = 130,
    NULL_ACTION = 131,


class Manager:
    def __init__(self, connection_parameters, data_source_parameters):
        self.running = True
        self.db = DB(connection_parameters,
                     data_source_parameters['database_name'])
        self.subject_table = data_source_parameters['subject_table']
        self.attendance_table = data_source_parameters['attendance_table']
        self.loaded_name_lists = {}
        self.classes = []

    def has_pending_deltas(self) -> bool:
        return bool(self.db.deltas)

    def deltas(self) -> list:
        return self.db.deltas

    def commit(self) -> ReturnCode:
        if not self.has_pending_deltas():
            return ReturnCode.NULL_ACTION
        return ReturnCode.SUCCESS if self.db.commit() else ReturnCode.SQL_ERROR

    def rollback(self) -> ReturnCode:
        if not self.has_pending_deltas():
            return ReturnCode.NULL_ACTION
        self.db.rollback()
        return ReturnCode.SUCCESS

    def refresh_classes(self) -> None:
        cursor = self.db.db_internal.cursor()
        cursor.execute(f"SELECT * FROM `{self.attendance_table}`")
        self.classes = list(cursor.column_names)
        self.classes.remove("Name")
        # Result set is not being used but must must be fetched to keep Python happy.
        cursor.fetchall()

    def save(self, filename) -> ReturnCode:
        import json
        with open(filename, 'w') as f:
            try:
                json.dump(dict(
                    deltas=self.db.deltas,
                    timestamp=datetime.datetime.now().isoformat()
                ), f)
                return ReturnCode.SUCCESS
            except:
                return ReturnCode.UNKNOWN_ERROR

    def load(self, filename) -> tuple:
        import json
        with open(filename) as f:
            try:
                d = json.load(f)
                self.db.deltas = d['deltas']
                return (ReturnCode.SUCCESS, d['timestamp'])
            except FileNotFoundError:
                return (ReturnCode.FILE_NOT_FOUND, None)

    def mark(self, name_partial, sched_cls, status) -> tuple:
        if not name_partial:
            return (ReturnCode.EMPTY_INPUT, None)
        if sched_cls not in self.classes:
            return (ReturnCode.UNDEFINED_CLASS, None)

        name_partial = name_partial.lower()

        subject = SchedClass(sched_cls).subject
        names = self.name_list(subject)
        matched_names = []

        if name_partial == 'all':
            matched_names = names
        elif name_partial == 'else':
            matched_names = [record[0] for record in
                             self.class_state(
                                 sched_cls=sched_cls, apply_deltas=True)
                             if record[1] == None]
        else:
            matched_names = [name for name in names if (
                name.lower().startswith(name_partial))]
            if not matched_names:
                matched_names = [name for name in names if (
                    name_partial in name.lower())]

        for name in matched_names:
            self.db.push(sched_cls, name, status)

        if len(matched_names) == 0:
            return (ReturnCode.NO_MATCH, None)
        elif len(matched_names) > 1 and name_partial != 'all' and name_partial != 'else':
            return (ReturnCode.MULTIPLE_MATCH, matched_names)
        else:
            return (ReturnCode.SUCCESS, None)

    def class_state(self, sched_cls, apply_deltas=False) -> list:
        cursor = self.db.db_internal.cursor()
        subject = SchedClass(sched_cls).subject
        quoted_names = [f"'{name}'" for name in self.name_list(subject)]
        cursor.execute(
            f"SELECT Name, `{sched_cls}` FROM `{self.attendance_table}` WHERE Name IN ({','.join(quoted_names)})")
        L = []
        for name, attendance in cursor.fetchall():
            if apply_deltas:
                matched_deltas = [r for r in self.db.deltas if r[0]
                           == sched_cls and r[1] == name]
                if matched_deltas:
                    attendance = matched_deltas[-1][2]
            L.append((name, attendance))
        return L

    def name_list(self, subject) -> list:
        if subject not in self.loaded_name_lists.keys():
            cursor = self.db.db_internal.cursor()
            cursor.execute(
                f"SELECT Name FROM `{self.subject_table}` WHERE Subjects LIKE %s", (
                    '%'+subject+'%',)
            )
            self.loaded_name_lists[subject] = [row[0]
                                               for row in cursor.fetchall()]
        return self.loaded_name_lists[subject]
