class Donate:
    count_id = 0

    def __init__(self, first_name, last_name, email, check_one, specifications):
        Donate.count_id +=1
        self.__donate_id = Donate.count_id
        self.__first_name = first_name
        self.__last_name = last_name
        self.__email = email
        self.__check_one = check_one
        self.__specifications = specifications

    def get_donate_id(self):
        return self.__donate_id
    def get_first_name(self):
        return self.__first_name
    def get_last_name(self):
        return self.__last_name
    def get_email(self):
        return self.__email
    def get_check_one(self):
        return self.__check_one
    def get_specifications(self):
        return self.__specifications

    def set_donate_id(self, donate_id):
        self.__donate_id = donate_id
    def set_first_name(self, first_name):
        self.__first_name = first_name
    def set_last_name(self, last_name):
        self.__last_name = last_name
    def set_email(self,email):
        self.__email = email
    def set_check_one(self,check_one):
        self.__check_one = check_one
    def set_specifications(self, specifications):
        self.__specifications = specifications
