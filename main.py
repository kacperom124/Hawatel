import mysql.connector

import requests

db_settings = {
    'user': 'root',
    'password': 'kacperkacper',
    'host': '127.0.0.1',
}

CONNECTION = mysql.connector.connect(**db_settings)


class NBPapi:

    def __init__(self, api_url):
        self.api_url = api_url

    def USD__exchange_rate__(self):
        return requests.get(f'{self.api_url}/exchangerates/rates/c/usd/today/').json()

    def EUR__exchange_rate__(self):
        return requests.get(f'{self.api_url}/exchangerates/rates/c/eur/today/').json()

    def get_rates(self):
        """ Moja zabawa z łatwą możliwośćią rozszerzenia o kolejne waluty."""
        functions = [name for name in dir(self) if '__exchange_rate__' in name]
        ex_rates = {}
        for function in functions:
            response = getattr(self, function)()
            ex_rates[function.replace('__exchange_rate__', '')] = {
                'buy': response['rates'][0]['ask'],
                'sell': response['rates'][0]['bid']
            }
        return ex_rates


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





bank_api = NBPapi('http://api.nbp.pl/api')
bank_exchange_rates = bank_api.get_rates()


# commands = load_commands()
# run_commands(commands)
# print(commands)

if __name__ == '__main__':
    print('hi')


