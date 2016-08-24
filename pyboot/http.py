import logging

import requests


class HttpClient(object):
    def __init__(self, api_timeout=60):
        self.__api_timeout = api_timeout

    def set_timeout(self, timeout):
        self.__api_timeout = timeout
        return self

    def get(self, **kwargs):
        """Sends a GET request.
        :param url: URL for the new :class:`Request` object.
        :param params: (optional) Dictionary or bytes to be sent in the query string for the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        logging.debug("GET {url}".format(url=kwargs["url"]))
        r = requests.get(**kwargs)
        r.raise_for_status()
        return r

    def delete(self, **kwargs):
        """Sends a DELETE request.
        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        logging.debug("DELETE {url}".format(url=kwargs["url"]))
        r = requests.delete(**kwargs)
        r.raise_for_status()
        return r

    def post(self, **kwargs):
        """Sends a POST request.
        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
        :param json: (optional) json data to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """
        logging.debug("POST {url}".format(url=kwargs["url"]))
        r = requests.post(**kwargs)
        r.raise_for_status()
        return r

    def put(self, **kwargs):
        """Sends a PUT request.
        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        logging.debug("PUT {url}".format(url=kwargs["url"]))
        r = requests.put(**kwargs)
        r.raise_for_status()
        return r
