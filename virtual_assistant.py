from collections import UserDict
from datetime import datetime, timedelta, date

PHONE_LENGTH = 10
DATE_FORMAT = "%d.%m.%Y"
WEEKEND_DAYS = 5  # Saturday = 5, Sunday = 6
DAYS_IN_WEEK = 7


class Field:
    """Базовий клас для полів запису."""
    
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    """Клас для зберігання імені контакту. Обов'язкове поле."""
    pass

class Phone(Field):
    """Клас для зберігання номера телефону. Має валідацію формату (PHONE_LENGTH цифр)."""
    def __init__(self, phone_number):
        self._validate_phone(phone_number)
        super().__init__(phone_number)
    
    def _validate_phone(self, phone_number) -> None:
        """Перевіряє, що номер телефону є строкою з необхідної кількості цифр."""
        if not isinstance(phone_number, str):
            raise ValueError("Phone must be a string.")
        if not phone_number.isdigit():
            raise ValueError("Phone must contain only digits.")
        if len(phone_number) != PHONE_LENGTH:
            raise ValueError(f"Phone must be exactly {PHONE_LENGTH} digits")
        

class Birthday(Field):
    """Клас для зберігання дати народження контакту."""
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, DATE_FORMAT).date()
        except ValueError:
            raise ValueError(f"Invalid date format. Use {DATE_FORMAT}")



class Record:
    """
    Клас для зберігання інформації про контакт, 
    включаючи ім'я, список телефонів та день народження.
    """
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_raw: str) -> None:
        """
        Створює обʼєкт класу Phone та 
        додає номер телефону в список self.phones
        """
        if self.find_phone(phone_raw):
            raise ValueError("This phone is already added.")
        else:
            new_phone = Phone(phone_raw)
            self.phones.append(new_phone)
    
    def find_phone(self, phone: str) -> Phone | None:
        """Повертає об’єкт Phone або None, якщо не знайдено."""
        for phone_obj in self.phones:
            if phone_obj.value == phone:
                return phone_obj
        return None

    def remove_phone(self, phone_to_delete: str) -> bool:
        """Видаляє телефон; повертає True, якщо знайшов і видалив."""
        for index, phone in enumerate(self.phones):
            if phone.value == phone_to_delete:
                self.phones.pop(index)
                return True
        return False

    def edit_phone(self, old_phone: str, new_phone: str) -> bool:
        """
        Замінює об’єкт Phone(old_phone) на Phone(new_phone);
        повертає True, якщо заміна відбулася, False інакше.
        """
        for index, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[index] = Phone(new_phone)
                return True
        return False
    
    def add_birthday(self, birthday:str):
        """Додає день народження до контакту."""
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = "; ".join(phone.value for phone in self.phones)
        birthday = self.birthday.value.strftime(DATE_FORMAT) if self.birthday else "—"
        return f"{self.name.value}: phones=[{phones}], birthday={birthday}"




class AddressBook(UserDict):
    def add_record(self, record: Record) -> None:
        """Додає Record у словник під ключем імені контакту."""
        self.data[record.name.value] = record

    def find(self, name: str) -> Record | None:
        """Повертає Record за точним ім’ям або None, якщо не знайдено."""
        return self.data.get(name)
        
    def delete(self, name: str) -> bool:
        """
        Видаляє Record за ім’ям.
        Повертає True, якщо контакт був, і False, якщо не було такого ключа.
        """
        if name in self.data:
            del self.data[name]
            return True
        return False
    

    def get_upcoming_birthdays(self) -> list:
        """Повертає список днів народження на наступні 7 днів."""
        today = date.today()
        upcoming_birthdays = []

        for name, record in self.data.items():
            # Пропускаємо, якщо дня народження немає
            if record.birthday is None:
                continue
            # створюємо змінну birthday, яка дорівнює дню народження юзера
            birthday = record.birthday.value
            # визначаємо дату народження в цьому році
            birthday_this_year = birthday.replace(year=today.year)
            # якщо день народження пройшов, маємо розглянути наступний рік
            if birthday_this_year < today:
                birthday_this_year = birthday.replace(year=today.year + 1)  
            # виводимо різницю між датами
            days_until_birthday = (birthday_this_year - today).days
            if 0 <= days_until_birthday <= DAYS_IN_WEEK:
                # визначаємо дату привітання
                congratulation_date = birthday_this_year
                # перевірка на вихідні 
                if congratulation_date.weekday() >= WEEKEND_DAYS:  
                    # переносимо дату привітання на понеділок
                    days_to_monday = DAYS_IN_WEEK - congratulation_date.weekday()
                    congratulation_date = congratulation_date + timedelta(days=days_to_monday)
                # додаємо в список з днями народженнями
                upcoming_birthdays.append({
                    'name': name,
                    'congratulation_date': congratulation_date.strftime(DATE_FORMAT)
                })
        return upcoming_birthdays




def input_error(func):
    """
    Декоратор який обробляє помилки при вводі юзера
    """
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return f"{e}"
        except KeyError as e:
            return "key error."
        except IndexError as e:
            return "Enter the argument for the command."
    return inner



@input_error
def parse_input(user_input):
    """
    Приймає аргументи з введеного юзером рядка, розбиває їх за пробілом, 
    переводить в нижній регістр і повертає команду та аргументи, якщо є
    """
    if user_input:
        cmd, *args = user_input.split()
        cmd = cmd.strip().lower()
        return cmd, *args
    else:
        return None, None

@input_error
def add_birthday(args, book: AddressBook):
    """Додає день народження заданого контакта."""
    name, birthday, *_ = args
    record = book.find(name)
    if record is None:
        record = Record(name)
        book.add_record(record)
        record.add_birthday(birthday)
        return f"Contact '{name}' created with birthday {birthday}."
    else:
        record.add_birthday(birthday)
        return f"Birthday {birthday} added to contact '{name}'."

@input_error
def show_birthday(args, book: AddressBook):
    """Показує день народження заданого контакта."""
    name, *_ = args
    record = book.find(name)
    if record:
        if record.birthday:
            return f"Birthday of {name} is {record.birthday.value.strftime(DATE_FORMAT)}"
        else:
            return f"Error: Contact '{name}' has no birthday."
    return f"Error: Contact '{name}' not found."

@input_error
def birthdays(book: AddressBook):
    """Показує дні народження на наступні 7 днів."""
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No upcoming birthdays."
    
    result = ["Upcoming birthdays:"]
    for birthday in upcoming_birthdays:
        result.append(f"{birthday['name']}: {birthday['congratulation_date']}")
    return "\n".join(result)

@input_error
def add_contact(args, book: AddressBook):
    """
    Додає контакт з телефоном.
    Якщо не вказано телефон, то контакт створюється без телефону.
    """
    if not args:
        return "Error: Please provide at least a name."
    
    name = args[0]
    phone = args[1] if len(args) > 1 else None
    
    record = book.find(name)
    
    # Якщо контакт не існує - створюємо новий
    if record is None:
        record = Record(name)
        book.add_record(record)
        
        if phone:
            record.add_phone(phone)
            return f"Contact '{name}' created with phone {phone}."
        else:
            return f"Contact '{name}' created without phone."
    
    # Якщо контакт існує
    else:
        if phone:
            record.add_phone(phone)
            return f"Phone {phone} added to contact '{name}'."
        else:
            return f"Contact '{name}' already exists."


@input_error
def change_contact(args, book: AddressBook):
    """
    функція змінює контакт у список контактів
    """
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record is None:
        return f"Error: Contact '{name}' not found."
    
    if record.edit_phone(old_phone, new_phone):
        return "Contact updated."
    else:
        return f"Error: Phone '{old_phone}' not found."

@input_error
def show_phone(args, book: AddressBook):
    """
    функція показує телефони заданого контакта
    """
    name = args[0]
    record = book.find(name)
    if record:
        if record.phones:
            phones = [phone.value for phone in record.phones]  
            return f"Phones of {name}: {', '.join(phones)}"
        else:
            return f"Contact '{name}' has no phones."
    return f"Error: Contact '{name}' not found."

@input_error
def show_all(book: AddressBook):
    """Показує всі контакти з телефонами."""
    if not book.data:
        return "No contacts found."
    contacts_list = []
    for name, record in book.data.items():
        phones = [phone.value for phone in record.phones]
        contacts_list.append(f"{name}: {', '.join(phones)}")
    
    return "\n".join(contacts_list)


def main():
    book = AddressBook()
    
    # Словник команд з lambda функціями
    commands = {
        "add": add_contact,
        "change": change_contact,
        "phone": show_phone,
        "all": lambda args, book: show_all(book),
        "add-birthday": add_birthday,
        "show-birthday": show_birthday,
        "birthdays": lambda args, book: birthdays(book),
    }
    
    print("Welcome to the assistant bot!")
    
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)
        
        if command is None:
            print("Enter a command.")
            continue
        
        if command in ["close", "exit"]:
            print("Good bye!")
            break
        
        if command == "hello":
            print("How can I help you?")

        elif command in commands:
            print(commands[command](args, book))

        else:
            print("Invalid command.")





if __name__ == "__main__":
    main()