from collections import defaultdict
import re

crush_dict = defaultdict(set)

US_PHONE_NUMBER_REGEX = re.compile(r'[2-9]{1}[0-9]{2}[2-9]{1}[0-9]{6}')

def is_valid_number(number):
    return bool(US_PHONE_NUMBER_REGEX.fullmatch(number))

def get_number():
    number = input('Please enter a valid US phone number: ')
    while not is_valid_number(number):
        number = input('Please enter a valid US phone number: ')
    return number

def add_crush(crusher, crush):
    if crush == crusher:
        return
    crush_dict[crusher].add(crush)
    if crusher in crush_dict[crush]:
        alert_crushes(crusher, crush)

def delete_all(crusher):
    crush_dict[crusher].clear()

def delete_crush(crusher, crush):
    crush_dict[crusher].discard(crush)

def list_crushes(crusher):
    for crush in crush_dict[crusher]:
        print(crush)

def alert_crushes(a, b):
    print(f"{a} and {b} have a crush on each other")

def process_request(crusher):
    command = input("Please input a command like SWITCH, ADD, DELETE, DELETE ALL, or LIST: ")
    if command == 'SWITCH':
        new_number = get_number()
        return new_number

    elif command == 'ADD':
        crush = get_number()
        add_crush(crusher, crush)

    elif command == 'DELETE':
        crush = get_number()
        delete_crush(crusher, crush)

    elif command == 'DELETE ALL':
        delete_all(crusher)

    elif command == 'LIST':
        list_crushes(crusher)

    else:
        print(f"I'm sorry, but {command} is not a valid command")

    return crusher


def main():
    number = get_number()
    while True:
        number = process_request(number)
        print(crush_dict)

if __name__ == "__main__":
    main()