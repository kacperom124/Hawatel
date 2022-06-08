import mysql.connector

db_settings = {
    'user': 'root',
    'password': 'kacperkacper',
    'host': '127.0.0.1',
}

CONNECTION = mysql.connector.connect(**db_settings)


def load_commands():
    """Load commands from file."""

    commands = []
    temp_command = ''
    for line in open('db.txt', 'r'):
        if line == '\n':
            continue
        line = line.replace('\n', '')
        if ';' in line:
            temp_command += line
            commands.append(temp_command)
            temp_command = ''
        else:
            temp_command += line
    return commands


def run_commands(commands):
    for command in commands:
        cursor = CONNECTION.cursor()
        result = cursor.execute(command)
        print(result)


commands = load_commands()
run_commands(commands)
print(commands)

if __name__ == '__main__':
    print('hi')


