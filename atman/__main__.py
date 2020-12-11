import getpass

import atman.manager
import atman.frontend

import colorama

username = input("Enter database username: ")
password = getpass.getpass(prompt="Enter database password: ")
database_name = input("Enter database name: ")

connection_parameters = {
    'host': "localhost",
    'port': 3306,
    'user': username,
    'passwd': password
}

data_source_parameters = {
    'database_name': database_name,
    'subject_table': "academic",
    'attendance_table': "attendance"
}

colorama.init(autoreset=True)

m = atman.manager.Manager(
    connection_parameters, data_source_parameters) # manager object created
m.refresh_classes()

f = atman.frontend.Frontend(m) # frontend object created

print()
print()
print("AtMan")
print("-----")
print()
print("Type 'help' for usage guide.")
print()

while f.running: # by default running = True
    try:
        f.exec()
    except KeyboardInterrupt:
        f.quit()
    except EOFError:
        f.quit()
