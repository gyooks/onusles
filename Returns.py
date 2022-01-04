class Returns:
    count_id = 0

    def __init__(self,  reason, remarks):
        Returns.count_id += 1
        self.__returns_id = Returns.count_id

        self.__reason = reason
        self.__remarks = remarks

    def get_returns_id(self):
        return self.__returns_id



    def get_reason(self):
        return self.__reason

    def get_remarks(self):
        return self.__remarks

    def set_returns_id(self, returns_id):
        self.__returns_id = returns_id



    def set_reason(self, reason):
        self.__reason = reason

    def set_remarks(self, remarks):
        self.__remarks = remarks

