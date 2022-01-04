class Yukin:
    count_id = 0

    def __init__(self,name,email,form,remarks):
        Yukin.count_id +=1
        self.__user_id = Yukin.count_id
        self.__name = name
        self.__email = email
        self.__form = form
        self.__remarks = remarks

    def get_user_id(self):
        return self.__user_id
    def get_name(self):
        return self.__name
    def get_email(self):
        return self.__email
    def get_form(self):
        return self.__form
    def get_remarks(self):
        return self.__remarks

    def set_user_id(self,user_id):
        self.__user_id = user_id
    def set_name(self,name):
        self.__name = name
    def set_email(self,email):
        self.__email = email
    def set_form(self,form):
        self.__form = form
    def set_remarks(self, remarks):
        self.__remarks = remarks
