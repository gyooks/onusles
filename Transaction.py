class Transaction:
    count_id = 0

    def __init__(self, products, total_cost, order_status):
        Transaction.count_id += 1
        self.__order_id = Transaction.count_id
        self.__products = products
        self.__total_cost = total_cost
        self.__order_status = order_status

    def get_order_id(self):
        return self.__order_id

    def get_products(self):
        return self.__products

    def get_total_cost(self):
        return self.__total_cost

    def get_order_status(self):
        return self.__order_status

    def set_order_id(self, order_id):
        self.__order_id = order_id

    def set_products(self, products):
        self.__products = products

    def set_total_cost(self, total_cost):
        self.__total_cost = total_cost

    def set_order_status(self, order_status):
        self.__order_status = order_status

