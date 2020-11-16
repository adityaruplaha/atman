import datetime

from attendance_manager.manager import Manager, ReturnCode
from attendance_manager.sched_class import SchedClass


class Frontend:
    def __init__(self, manager: Manager):
        self.running = True
        self.manager = manager
        self.sched_class = None

    def quit(self):
        if self.manager.has_pending_deltas():
            choice = input(
                "Uncommited changes present! Are you sure you want to quit? [y/N]: ").lower().strip()
            if choice != 'y':
                return
        self.running = False
        print("Goodbye.")

    def commit(self):
        rt_code = self.manager.commit()
        if rt_code == ReturnCode.SQL_ERROR:
            print(
                "ERR: There was an SQL error. No changes have been lost. Try again later.")
            print(
                "     If the problem persists, check your database connection and table layout.")
        elif rt_code == ReturnCode.NULL_ACTION:
            print("WARN: No changes to commit.")
        elif rt_code == ReturnCode.SUCCESS:
            print("Successfully committed changes to database.")

    def rollback(self):
        if self.manager.has_pending_deltas():
            choice = input(
                "Uncommitted changes present! Are you sure you want to rollback? THIS IS IRREVERSIBLE. [y/N]: ").lower().strip()
            if choice != 'y':
                return
        rt_code = self.manager.rollback()
        if rt_code == ReturnCode.NULL_ACTION:
            print("WARN: No changes to rollback.")
        elif rt_code == ReturnCode.SUCCESS:
            print("Successfully rolled back changes.")

    def list_deltas(self):
        print("Changes:")
        for sched_class, name, status in self.manager.deltas():
            if status == None:
                status = "NULL"
            elif status:
                status = "PRESENT"
            else:
                status = "ABSENT"
            print(f"{name} => {sched_class} [{status}]")

    def set_class(self, sched_class):
        if not self.manager.classes:
            self.manager.refresh_classes()
        if sched_class in self.manager.classes:
            self.sched_class = sched_class
        else:
            print("Invalid class.")

    def save(self, filename=None):
        if not filename:
            filename = f"{self.sched_class}_{datetime.datetime.now().isoformat()}.json"
        self.manager.save(filename)

    def load(self, filename):
        if self.manager.deltas:
            choice = input(
                "Uncommited changes present! Are you sure you want to overwrite current state? [y/N]: ").lower().strip()
            if choice != 'y':
                return
        self.manager.load(filename)

    def import_autocsv(self, filename):
        """
        Integrates directly with a CSV generated using this Chrome extension:
        https://chrome.google.com/webstore/detail/google-meet-attendance-co/hjjeaaibilndjeabckakaknlcbblcmbc
        """
        if not self.sched_class:
            print("Select a class first.")
            return
        import csv
        with open(filename) as f:
            names = [''.join(row).strip() for row in csv.reader(f)][4:]
            for name in names:
                print(f"Marking '{name}' present...")
                self.manager.mark(name, True)
            print(f"Marking all unmarked students absent...")
            self.manager.mark('else', False)

    def mark(self, name_partial, status=None):
        # `matched_names` is returned only if `ReturnCode.MULTIPLE_MATCH` is returned.
        # Otherwise, None is returned.
        if not self.sched_class:
            print("Select a class first.")
            return
        rt_code, matched_names = self.manager.mark(
            name_partial, self.sched_class, status)
        if rt_code == ReturnCode.EMPTY_INPUT:
            print("Provide a name.")
        elif rt_code == ReturnCode.MULTIPLE_MATCH:
            subject = SchedClass(self.sched_class).subject
            print(
                f"WARN: '{name_partial}' matched multiple students studying '{subject}'.")
            print(matched_names)
        elif rt_code == ReturnCode.NO_MATCH:
            subject = SchedClass(self.sched_class).subject
            print(
                f"WARN: '{name_partial}' didn't match any student studying '{subject}'.")
        elif rt_code == ReturnCode.UNDEFINED_CLASS:
            print(
                "ERR: The current scheduled class doesn't exist in database.")

    def state(self, apply_deltas=False):
        if not self.sched_class:
            print("Select a class first.")
            return
        total = 0
        present = 0
        absent = 0
        for name, attendance in self.manager.class_state(self.sched_class, apply_deltas=apply_deltas):
            if attendance == None:
                attendance = "NULL"
            elif attendance:
                attendance = "PRESENT"
                total += 1
                present += 1
            else:
                attendance = "ABSENT"
                total += 1
                absent += 1
            print(f"{name} => {attendance}")
        if total:
            print("-"*30)
            print(
                f"Present: {present}/{total} [{round(present/total*100, 2)}%]")
            print(
                f"Absent: {absent}/{total} [{round(absent/total*100, 2)}%]")

    def exec(self):
        cmd = input(f"{self.sched_class}> ").strip()
        splitted = cmd.split(' ')
        command = splitted[0].strip()
        args_str = ' '.join(splitted[1:]).strip()
        if command == 'quit':
            self.quit()
        elif command == 'commit':
            self.commit()
        elif command == 'rollback':
            self.rollback()
        elif command == 'deltas':
            self.list_deltas()
        elif command == 'class':
            self.set_class(args_str)
        elif command == 'state':
            self.state(apply_deltas=False)
        elif command == 'newstate':
            self.state(apply_deltas=True)
        elif command == 'save':
            self.save(args_str)
        elif command == 'load':
            self.load(args_str)
        elif command == 'import-autocsv':
            self.import_autocsv(args_str)
        elif command == 'null':
            self.mark(args_str, None)
        elif command == 'present':
            self.mark(args_str, True)
        elif command == 'absent':
            self.mark(args_str, False)
        else:
            print("Invalid command.")
