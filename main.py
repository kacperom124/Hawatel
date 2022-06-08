import mysql.connector
import logging
import requests
from decimal import Decimal
import pandas
import openpyxl

db_settings = {
    'user': 'root',
    'password': 'kacperkacper',
    'host': '127.0.0.1',
}

logging.basicConfig(filename='log.txt',
                    filemode='a',
                    format='%(asctime)s, %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)


class NBPapi:

    def __init__(self, api_url):
        self.api_url = api_url

    def request(self, url, **data):
        """Ułatwia logging requestów."""
        try:
            response = requests.get(url, **data)
        except requests.exceptions.ConnectionError:
            logging.info('Connection problem')
            raise Exception('Connection problem')
        if response.status_code != 200:
            logging.info(f'NBP api error {response.json()}')
            raise Exception(f'NBP api error {response.json()}')
        return response

    def get_rates(self):
        """ Moja zabawa z łatwą możliwośćią rozszerzenia o kolejne waluty."""
        check_rates_for = ['eur', 'usd']
        ex_rates = {}
        for currency in check_rates_for:
            response = self.request(f'{self.api_url}/exchangerates/rates/c/{currency}/today/').json()
            ex_rates[currency] = {
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
    """Komendy z pliku."""
    for command in commands:
        cursor = CONNECTION.cursor()
        cursor.execute(command)


class Product:
    """Klasa produktu. Zmiana nazwy spowoduje zaciąganie innego objektu z bazy. Więc łatwo można inne dodać."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            self.__dict__[key] = value

    def __str__(self):
        return self.ProductName

    @classmethod
    def get_all_objects(cls):
        """Zaciaga wszystko z bazy."""
        raw = f"select * from {cls.__name__}"
        cursor = CONNECTION.cursor()
        cursor.execute('use mydb;')
        cursor.execute(raw)
        columns = [column[0] for column in cursor.description]
        query_result = cursor.fetchall()
        object_list = []
        for row in query_result:
            temp_dict = {}
            for index, column in enumerate(row):
                temp_dict[columns[index]] = column
            object_list.append(cls(**temp_dict))

        return object_list

    @classmethod
    def update_foreign_currency_for_all(cls):
        products_list = cls.get_all_objects()
        bank_exchange_rates = BANK_API.get_rates()
        for product in products_list:
            product.UnitPriceEuro = product.UnitPrice * Decimal(bank_exchange_rates['eur']['buy'])
            product.UnitPriceUSD = product.UnitPrice * Decimal(bank_exchange_rates['usd']['buy'])
        return products_list


    @classmethod
    def get_pk_name(cls):
        cursor = CONNECTION.cursor()
        cursor.execute(f"SHOW KEYS FROM {cls.__name__} WHERE Key_name = 'PRIMARY'")
        result = cursor.fetchall()
        return result[0][4]


    def update(self):
        """Pseudo uniwersalny update do klas."""
        command = ''
        for index, (column, value) in enumerate(self.__dict__.items()):
            if index == 0:
                try:
                    command += f"{column} = '{str(value, 'utf-8')}'"
                except TypeError:
                    command += f"{column} = '{value}'"
            else:
                try:
                    command += f", {column} = '{str(value, 'utf-8')}'"
                except TypeError:
                    command += f", {column} = '{value}'"
        raw = f"Update `mydb`.`{self.__class__.__name__}` SET {command} where `{self.get_pk_name()}` = '{self.ProductID}';"
        logging.info(raw)
        cursor = CONNECTION.cursor()
        cursor.execute(raw)
        CONNECTION.commit()


try:
    CONNECTION = mysql.connector.connect(**db_settings)
except:
    logging.info(f'Database connection problem')
    raise Exception('Database connection problem')
BANK_API = NBPapi('http://api.nbp.pl/api')


clear = '\n' * 100
while True:
    choice = 0

    print('1. Update cen.')
    print('2. Export do excela')
    print('21432. Reset Bazy')
    try:
        choice = int(input('Podaj samą liczbe.'))
    except ValueError:
        pass
    print(clear)
    if choice == 1:
        products_list = Product.update_foreign_currency_for_all()
        for product in products_list:
            product.update()
        print('Sukces. \n')
    if choice == 2:
        df = pandas.DataFrame([o.__dict__ for o in Product.get_all_objects()])
        df.to_excel("output.xlsx")
    if choice == 21432: # żeby się komuś przypadkiem nie zresetowało.
        commands = load_commands()
        run_commands(commands)

