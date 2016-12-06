from pyboot.core import DictSerializable


class Page(DictSerializable):
    def __init__(self):
        self.items = []
        self.count = 0
        self.total_count = 0

        self.is_prev_page = False
        self.prev_page_start = None
        self.prev_page_count = None
        self.prev_page_url = None

        self.is_next_page = False
        self.next_page_start = None
        self.next_page_count = None
        self.next_page_url = None

    def gen_page_data(self, start: int, count: int):
        if start > 0:
            self.is_prev_page = True
            if start >= count:
                self.prev_page_start = start - count
                self.prev_page_count = count
            else:
                self.prev_page_start = 0
                self.prev_page_count = start
        else:
            self.is_prev_page = False

        if len(self.items) > count:
            self.is_next_page = True
            if start + count <= self.total_count - count:
                self.next_page_start = start + count
                self.next_page_count = count
            else:
                self.next_page_start = start + count
                self.next_page_count = self.total_count - self.next_page_start
            self.items = self.items[:-1]
        else:
            self.is_next_page = False
        self.count = len(self.items)

    def to_dict_deep(self):
        page_dict = super().to_dict_deep()
        page_dict["count"] = self.count
        page_dict["items"] = [item.to_dict_deep() for item in self.items]
        page_dict["total_count"] = self.total_count
        page_dict["is_prev"] = self.is_prev_page
        page_dict["is_next"] = self.is_next_page
        return page_dict
