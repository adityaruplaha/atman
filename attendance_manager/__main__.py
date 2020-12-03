import attendance_manager.manager
import attendance_manager.frontend

username = input("Enter database username: ")
password = input("Enter database password: ")
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

m = attendance_manager.manager.Manager(
    connection_parameters, data_source_parameters) # manager object created
m.refresh_classes()

f = attendance_manager.frontend.Frontend(m) # frontend object created

while f.running: # by default running = True
    try:
        f.exec()
    except KeyboardInterrupt:
        f.quit()
    except EOFError:
        f.quit()
