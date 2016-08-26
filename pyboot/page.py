from pyboot.core import JSONSerializable


class Page(JSONSerializable):
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

    def to_json_dict(self, include: list = None):
        json_dict = super().to_json_dict(include)
        json_dict["count"] = self.count
        json_dict["items"] = [item.to_json_dict(include) for item in self.items]
        json_dict["total_count"] = self.total_count
        json_dict["is_prev"] = self.is_prev_page
        json_dict["is_next"] = self.is_next_page
        return json_dict

        # def gen_page_urls(self, baseurl: str, params: dict):
        #     clean_params = DictUtil.delete_null_values(params)
        #     params_str = ""
        #     for key in clean_params:
        #         params_str += "&" + key + "=" + clean_params[key]
        #
        #     if self.is_prev_page:
        #         self.prev_page_url = "%s?start=%s&count=%s%s" % (
        #             baseurl, self.prev_page_start, self.prev_page_count, params_str)
        #
        #     if self.is_next_page:
        #         self.next_page_url = "%s?start=%s&count=%s%s" % (
        #             baseurl, self.next_page_start, self.next_page_count, params_str)
