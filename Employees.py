class Employees:
    count_id = 0

    def __init__(self, first_name, last_name, gender, role, phone_number, address, date_of_joining):
        Employees.count_id += 1
        self.__employees_id = Employees.count_id
        self.__first_name = first_name
        self.__last_name = last_name
        self.__gender = gender
        self.__role = role
        self.__phone_number = phone_number
        self.__address = address
        self.__date_of_joining = date_of_joining

    def get_employees_id(self):
        return self.__employees_id

    def get_first_name(self):
        return self.__first_name

    def get_last_name(self):
        return self.__last_name

    def get_gender(self):
        return self.__gender

    def get_role(self):
        return self.__role

    def get_phone_number(self):
        return self.__phone_number

    def get_address(self):
        return self.__address

    def get_date_of_joining(self):
        return self.__date_of_joining

    def set_employees_id(self, employees_id):
        self.__employees_id = employees_id

    def set_first_name(self, first_name):
        self.__first_name = first_name

    def set_last_name(self, last_name):
        self.__last_name = last_name

    def set_gender(self, gender):
        self.__gender = gender

    def set_role(self, role):
        self.__role = role

    def set_phone_number(self, phone_number):
        self.__phone_number = phone_number

    def set_address(self, address):
        self.__address = address

    def set_date_of_joining(self, date_of_joining):
        self.__date_of_joining = date_of_joining
