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
    connection_parameters, data_source_parameters)
m.refresh_classes()

f = attendance_manager.frontend.Frontend(m)

while f.running:
    try:
        f.exec()
    except KeyboardInterrupt:
        f.quit()
