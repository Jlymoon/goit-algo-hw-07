from collections import UserDict
from datetime import datetime, timedelta


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def validate(self):
        if len(self.value) != 10 or not self.value.isdigit():
            raise ValueError("Phone number must contain 10 digits.")


class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%Y.%m.%d")
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY.MM.DD")

    def __str__(self):
        return self.value.strftime("%Y.%m.%d")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        phone_obj = Phone(phone)
        phone_obj.validate()
        self.phones.append(phone_obj)

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        self.remove_phone(old_phone)
        self.add_phone(new_phone)

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = ', '.join(str(p) for p in self.phones)
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_birthdays = []
        birthdays_dict = {}

        for record in self.data.values():
            if record.birthday:
                birthday = record.birthday.value.date()
                birthday_this_year = birthday.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(
                        year=today.year + 1)

                if birthday_this_year.weekday() == 5:
                    congratulation_date = birthday_this_year + \
                        timedelta(days=2)
                elif birthday_this_year.weekday() == 6:
                    congratulation_date = birthday_this_year + \
                        timedelta(days=1)
                else:
                    congratulation_date = birthday_this_year

                days_until_birthday = (congratulation_date - today).days

                if days_until_birthday <= 7:
                    if congratulation_date not in birthdays_dict:
                        birthdays_dict[congratulation_date] = {
                            "congratulation_date": congratulation_date, "users": [record.name.value]}
                    else:
                        birthdays_dict[congratulation_date]["users"].append(
                            record.name.value)

        for date, data in birthdays_dict.items():
            for name in data["users"]:
                days_until_birthday = (
                    data["congratulation_date"] - today).days
                upcoming_birthdays.append({"name": name, "congratulation_date": data["congratulation_date"],
                                           "days_until_birthday": days_until_birthday})

        return upcoming_birthdays


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact not found."
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Missing required arguments."
        except Exception as e:
            return f"An unexpected error occurred: {e}"
    return inner


def parse_input(user_input):
    cmd, *args = user_input.strip().split()
    return cmd.lower(), args


@input_error
def add_contact(address_book, name, *phones):
    record = address_book.find(name)
    if not record:
        record = Record(name)
        address_book.add_record(record)
        message = "Contact added."
    else:
        message = "Contact updated."
    for phone in phones:
        record.add_phone(phone)
    return message


@input_error
def change_contact(address_book, name, old_phone, new_phone):
    record = address_book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Contact updated."
    else:
        raise KeyError


@input_error
def show_phone(address_book, name):
    record = address_book.find(name)
    if record:
        return str(record)
    else:
        raise KeyError


@input_error
def show_all(address_book):
    if address_book:
        return "\n".join(str(record) for record in address_book.values())
    else:
        return "No contacts found."


@input_error
def add_birthday(address_book, name, birthday):
    record = address_book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    else:
        raise KeyError


@input_error
def show_birthday(address_book, name):
    record = address_book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday is {record.birthday}"
    else:
        raise KeyError


@input_error
def birthdays(address_book):
    upcoming = address_book.get_upcoming_birthdays()
    if upcoming:
        return "\n".join(f"{entry['name']}: {entry['congratulation_date'].strftime('%Y.%m.%d')}" for entry in upcoming)
    else:
        return "No upcoming birthdays."


def main():
    address_book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(address_book, *args))
        elif command == "change":
            if len(args) == 3:
                name, old_phone, new_phone = args
                print(change_contact(address_book, name, old_phone, new_phone))
            else:
                print("Give me name, old phone, and new phone number please.")
        elif command == "phone":
            print(show_phone(address_book, *args))
        elif command == "all":
            print(show_all(address_book))
        elif command == "add-birthday":
            if len(args) == 2:
                name, birthday = args
                print(add_birthday(address_book, name, birthday))
            else:
                print("Give me name and birthday please.")
        elif command == "show-birthday":
            print(show_birthday(address_book, *args))
        elif command == "birthdays":
            print(birthdays(address_book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
