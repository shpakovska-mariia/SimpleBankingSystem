import random
import string
import math
import sqlite3


def get_luhn(n):
    l = list(n)
    l = [int(i) for i in l]
    l = [l[i] * 2 if i % 2 == 0 else l[i] for i in range(len(l))]
    l = [i - 9 if i > 9 else i for i in l]
    s = sum(l)
    div = int(math.ceil(s / 10.0)) * 10
    return str(div - s)


class Card:
    current = None

    def __init__(self, id=None, number=None, pin=None, balance=None):
        if number and pin:
            self.id = id
            self.number = number
            self.pin = pin
            self.balance = balance
        else:
            self.id = 0
            self.number = '400000'
            self.number += ''.join([random.choice(string.digits) for _ in range(9)])
            self.number += get_luhn(self.number)
            self.pin = ''.join([random.choice(string.digits) for _ in range(4)])
            self.balance = 0
            cur.execute(
                f'''INSERT INTO card(number, pin) 
                VALUES ({self.number}, {self.pin});'''
            )
            conn.commit()

    def change_balance(self, amount):
        self.balance += amount
        cur.execute(f'''UPDATE card SET balance = {self.balance}
        WHERE id = {self.id};''')
        conn.commit()


def menu():
    if Card.current:
        print('''
1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit''')
        options = [leave, balance, add_income, do_transfer, close, logout]
    else:
        print('''
1. Create an account
2. Log into account
0. Exit''')
        options = [leave, create, login]
    return options[int(input())]


def add_income():
    Card.current.change_balance(int(input()))
    print('Income was added!')


def do_transfer():
    print('Transfer')
    nb = input('Enter card number:\n')
    if nb == Card.current.number:
        print("You can't transfer money to the same account!")
    elif get_luhn(nb[:-1]) != nb[-1]:
        print("Probably you made a mistake in the card number. Please try again!")
    else:
        cur.execute(f'SELECT * FROM card WHERE number={nb};')
        found = cur.fetchone()
        if not found:
            print('Such a card does not exist.')
        else:
            card = Card(found[0], found[1], found[2], found[3])
            amount = int(input('Enter how much money you want to transfer:\n'))
            if amount > Card.current.balance:
                print('Not enough money!')
            else:
                Card.current.change_balance(amount * -1)
                card.change_balance(amount)
                print('Success!')


def close():
    cur.execute(f'DELETE FROM card WHERE id = {Card.current.id};')
    conn.commit()
    print('The account has been closed!')
    Card.current = None


def logout():
    Card.current = None
    print('You have successfully logged out!')


def leave():
    print('Bye!')
    exit()


def create():
    new_card = Card()
    print(f'''Your card has been created
Your card number:
{new_card.number}
Your card PIN:
{new_card.pin}''')
    return new_card


def balance():
    print(f'Balance: {Card.current.balance}')


def login():
    number = input('Enter your card number:\n')
    pin = input('Enter your PIN:\n')
    cur.execute(
        f''' SELECT 
                * 
            FROM 
                card 
            WHERE 
                number={number} AND pin={pin};'''
    )
    result = cur.fetchone()
    if result:
        print('You have successfully logged in!')
        Card.current = Card(result[0], result[1], result[2], result[3])
        return
    print('Wrong card number or PIN!')


if __name__ == '__main__':
    conn = sqlite3.connect('card.s3db')
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS card(
        id INTEGER PRIMARY KEY,
        number TEXT,
        pin TEXT,
        balance INTEGER DEFAULT 0)''')
    conn.commit()
    while True:
        menu()()
