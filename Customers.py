class Customers:
    count_id = 0

    def __init__(self, first_name, last_name, gender, membership, phone_number, locations, date_of_joining):
        Customers.count_id += 1
        self.__customers_id = Customers.count_id
        self.__first_name = first_name
        self.__last_name = last_name
        self.__gender = gender
        self.__membership = membership
        self.__phone_number = phone_number
        self.__locations = locations
        self.__date_of_joining = date_of_joining

    def get_customers_id(self):
        return self.__customers_id

    def get_first_name(self):
        return self.__first_name

    def get_last_name(self):
        return self.__last_name

    def get_gender(self):
        return self.__gender

    def get_membership(self):
        return self.__membership

    def get_phone_number(self):
        return self.__phone_number

    def get_locations(self):
        return self.__locations

    def get_date_of_joining(self):
        return self.__date_of_joining

    def set_customers_id(self, customers_id):
        self.__customers_id = customers_id

    def set_first_name(self, first_name):
        self.__first_name = first_name

    def set_last_name(self, last_name):
        self.__last_name = last_name

    def set_gender(self, gender):
        self.__gender = gender

    def set_membership(self, membership):
        self.__membership = membership

    def set_phone_number(self, phone_number):
        self.__phone_number = phone_number

    def set_locations(self, locations):
        self.__locations = locations

    def set_date_of_joining(self, date_of_joining):
        self.__date_of_joining = date_of_joining
