import datetime, readline

from attendance_manager.manager import Manager, ReturnCode
from attendance_manager.sched_class import SchedClass


class Frontend:
    def __init__(self, manager: Manager):
        self.running = True
        self.manager = manager
        self.current_class_id = None

    def quit(self):
        if self.manager.has_pending_deltas():
            choice = input(
                "Uncommitted changes present! Are you sure you want to quit? [y/N]: ").lower().strip()
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
        for class_id, name, status in self.manager.deltas():
            if status == None:
                status = "NULL"
            elif status:
                status = "PRESENT"
            else:
                status = "ABSENT"
            print(f"{name} => {class_id} [{status}]")

    def set_class(self, class_id):
        if not self.manager.classes:
            self.manager.refresh_classes()
        if class_id in self.manager.classes:
            self.current_class_id = class_id
        else:
            print("Invalid class ID. Use `newclass` to create a new class.")

    def new_class(self, class_id):
        # Check if SchedClass is well-formed.
        if not class_id == str(SchedClass(class_id)):
            print("The specified class ID doesn't seem to be in a valid format.")
        if class_id in self.manager.classes:
            print("The class with specified ID already exists.")
        else:
            rt_code = self.manager.add_class(class_id)
            if rt_code == ReturnCode.SQL_ERROR:
                print(
                    "ERR: Couldn't create class. There was an SQL error. Try again later.")
                print(
                    "     If the problem persists, check your database connection.")
            elif rt_code == ReturnCode.SUCCESS:
                print(f"Created empty class with ID '{class_id}'.")
                choice = input(
                    "Switch to newly created class? [y/N]: ").lower().strip()
                if choice == 'y':
                    self.set_class(class_id)
            else:
                # Do not cover this in flowchart/writeup.
                print("Something really unexpected happened. File a bug report. Error Code: IMP_RET-add_class")

    def save(self, filename=None):
        if not filename:
            filename = f"{self.current_class_id}_{datetime.datetime.now().isoformat()}.json"
        self.manager.save(filename)

    def load(self, filename):
        if self.manager.deltas:
            choice = input(
                "Uncommitted changes present! Are you sure you want to overwrite current state? [y/N]: ").lower().strip()
            if choice != 'y':
                return
        self.manager.load(filename)

    # SWLIMIT: This doesn't actually check the format of the CSV.
    def import_autocsv(self, filename, realname_lambda=lambda x: x):
        """
        Integrates directly with a CSV generated using this Chrome extension:
        https://chrome.google.com/webstore/detail/google-meet-attendance-co/hjjeaaibilndjeabckakaknlcbblcmbc
        """
        if not self.current_class_id:
            print("Select a class first. Use `class` to select a class by ID.")
            return
        import csv
        with open(filename) as f:
            rows = list(csv.reader(f))
            # 1st column contains the names.
            names = [row[0].strip() for row in rows]
            if len(rows[0]) == 1:
                # This is not TIME-WISE ATTENDANCE MONITORING.
                # First 4 rows are metadata. Discard.
                names = names[4:]
            elif len(rows[0]) > 1:
                # This is TIME-WISE ATTENDANCE MONITORING.
                # First 6 rows are metadata. Discard.
                names = names[6:]
            else:
                # This code will never be reached.
                print("ERR: Unknown CSV format.")
                return
            # Remove all empty entries
            while names.count(''):
                names.remove('')
            for name in names:
                name = realname_lambda(name)
                print(f"Marking '{name}' present...", end=' ')
                rt_code, matched_names = self.manager.mark(name, self.current_class_id, True)
                if rt_code == ReturnCode.MULTIPLE_MATCH:
                    subject = SchedClass(self.current_class_id).subject
                    print("DONE.")
                    print(
                        f"WARN: '{name}' matched multiple students studying '{subject}'.")
                    print(matched_names)
                elif rt_code == ReturnCode.NO_MATCH:
                    print("FAILED.")
                    subject = SchedClass(self.current_class_id).subject
                    print(
                        f"WARN: '{name}' didn't match any student studying '{subject}'.")
                elif rt_code == ReturnCode.UNDEFINED_CLASS:
                    print("FAILED.")
                    print(
                        "ERR: The current class ID doesn't exist in database.")
                else:
                    print("DONE.")
            print(f"Marking all unmarked students absent...")
            self.manager.mark('else', self.current_class_id, False)

    def mark(self, name_partial, status=None):
        # `matched_names` is returned only if `ReturnCode.MULTIPLE_MATCH` is returned.
        # Otherwise, None is returned.
        if not self.current_class_id:
            print("Select a class first. Use `class` to select a class by ID.")
            return
        rt_code, matched_names = self.manager.mark(
            name_partial, self.current_class_id, status)
        if rt_code == ReturnCode.EMPTY_INPUT:
            print("Provide a name.")
        elif rt_code == ReturnCode.MULTIPLE_MATCH:
            subject = SchedClass(self.current_class_id).subject
            print(
                f"WARN: '{name_partial}' matched multiple students studying '{subject}'.")
            print(matched_names)
        elif rt_code == ReturnCode.NO_MATCH:
            subject = SchedClass(self.current_class_id).subject
            print(
                f"WARN: '{name_partial}' didn't match any student studying '{subject}'.")
        elif rt_code == ReturnCode.UNDEFINED_CLASS:
            print(
                "ERR: The current class ID doesn't exist in database.")

    def state(self, apply_deltas=False):
        import prettytable
        if not self.current_class_id:
            print("Select a class first. Use `class` to select a class by ID.")
            return
        total = 0
        present = 0
        absent = 0
        p = prettytable.PrettyTable()
        p.field_names = ["NAME", "ATTENDANCE"]
        for name, attendance in self.manager.class_state(self.current_class_id, apply_deltas=apply_deltas):
            if attendance == None:
                attendance = ""
            elif attendance:
                attendance = "PRESENT"
                total += 1
                present += 1
            else:
                attendance = "ABSENT"
                total += 1
                absent += 1
            p.add_row([name, attendance])
            p.align["NAME"] = 'l'
            p.align["ATTENDANCE"] = 'r'
        print(p)
        if total:
            print(
                f"Present: {present}/{total} [{round(present/total*100, 2)}%]")
            print(
                f"Absent: {absent}/{total} [{round(absent/total*100, 2)}%]")

    def exec(self):
        cmd = input(f"{self.current_class_id}> ").strip()
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
        elif command == 'newclass':
            self.new_class(args_str)
        elif command == 'state':
            self.state(apply_deltas=False)
        elif command == 'newstate':
            self.state(apply_deltas=True)
        elif command == 'save':
            self.save(args_str)
        elif command == 'load':
            self.load(args_str)
        elif command == 'import-autocsv':
            import re
            # This lambda removes 'SC[section]-[roll no] ' from the name.
            self.import_autocsv(args_str, lambda name: re.sub(r'SC[\w]-[\d]+\s', '', name))
        elif command == 'null':
            self.mark(args_str, None)
        elif command == 'present':
            self.mark(args_str, True)
        elif command == 'absent':
            self.mark(args_str, False)
        else:
            print("Invalid command.")
