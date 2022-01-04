class Product:
    count_id = 0

    def __init__(self, product_name, product_cost, stock):
        Product.count_id += 1
        self.__product_id = Product.count_id
        self.__product_name = product_name
        self.__product_cost = product_cost
        self.__stock = stock

    def get_product_id(self):
        return self.__product_id

    def get_product_name(self):
        return self.__product_name

    def get_product_cost(self):
        return self.__product_cost

    def get_stock(self):
        return self.__stock

    def set_product_id(self, product_id):
        self.__product_id = product_id

    def set_product_name(self, product_name):
        self.__product_name = product_name

    def set_product_cost(self, product_cost):
        self.__product_cost = product_cost

    def set_stock(self, stock):
        self.__stock = stock



