class Order:
    count_id = 0

    def __init__(self, email, address1, address2):
        Order.count_id += 1
        self.__order_id = Order.count_id
        self.__email = email
        self.__address1 = address1
        self.__address2 = address2

    def get_order_id(self):
        return self.__order_id

    def get_email(self):
        return self.__email

    def get_address1(self):
        return self.__address1

    def get_address2(self):
        return self.__address2

    def set_order_id(self, order_id):
        self.__order_id = order_id

    def set_email(self, email):
        self.__email = email

    def set_address1(self, address1):
        self.__address1 = address1

    def set_address2(self, address2):
        self.__address2 = address2

