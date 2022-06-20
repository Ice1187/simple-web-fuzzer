from typing import List
import requests as rq
from copy import deepcopy
from re import split
from requester import HttpRequester


class Fuzzer:
    def __init__(self, url, wordlist, proc, timeout, encoding=None, method=None, cookies=None, data=None, headers=None, redirect=None):
        self.keyword = 'FUZZ'
        self.url = url
        self.wordlist_path = wordlist
        self.encoding = encoding
        self.proc_num = proc
        self.timeout = timeout

        self.method = method
        self.cookies = cookies
        self.data = data
        self.headers = headers
        self.redirect = redirect

        self.batch_size = 256
        self.http_requester = HttpRequester(
            self.proc_num, self.timeout, self.redirect)

        self.fuzz_func = None
        self.base_req = None

    def fuzz(self):
        try:
            self._build_request()
        except Exception as e:
            raise RuntimeError('Failed to build base request') from e

        total_req = 0
        words = []
        with open(self.wordlist_path, 'r', encoding=self.encoding) as wordlist:
            for i, word in enumerate(wordlist):
                words.append(word[:-1])  # [:-1] remove newline
                if i % self.batch_size == self.batch_size - 1:
                    self.fuzz_func(words)
                    words = []
                total_req += 1
            self.fuzz_func(words)

        self.http_requester.wait()
        return total_req

    def fuzz_URL(self, words: List[str]):
        #reqs = []
        for i, word in enumerate(words):
            req = deepcopy(self.base_req)
            req.url = req.url.replace(self.keyword, word)
            # reqs.append(req)
            self.http_requester.request(req, self.callback, word)
        #self.http_requester.batch_request(reqs, self.callback, words)

    def fuzz_data(self, words: List[str]):
        #reqs = []
        for i, word in enumerate(words):
            req = deepcopy(self.base_req)
            req.data = req.data.replace(self.keyword, word)
            # reqs.append(req)
            self.http_requester.request(req, self.callback, word)
        #self.http_requester.batch_request(reqs, self.callback, words)

    def fuzz_header(self, words):
        #reqs = []
        for i, word in enumerate(words):
            req = deepcopy(self.base_req)
            for key in req.headers.keys():
                req.headers[key] = req.headers[key].replace(self.keyword, word)
            # reqs.append(req)
            self.http_requester.request(req, self.callback, word)
        #self.http_requester.batch_request(reqs, self.callback, words)

    def callback(self, res: List[rq.Response]):
        # for r, fuzz in res:
        r, fuzz = res
        status = r.status_code
        size = len(r.content)
        word = len(split(r'[^\S\n\t]', r.text))
        line = len(r.text.split('\n'))
        print(
            f'{fuzz: <32} [Status: {status}, Size: {size}, Word: {word}, Line: {line}]')

    def _build_request(self):
        self.fuzz_func = self._get_fuzz_func()
        self.method = self._get_method()
        self.headers = self._get_dict_headers()
        self.cookies = self._get_dict_cookies()

        self.base_req = rq.Request(
            self.method, self.url, self.headers, data=self.data, cookies=self.cookies)

    def _get_fuzz_func(self):
        if self.keyword in self.url:
            return self.fuzz_URL
        elif self.data and self.keyword in self.data:
            return self.fuzz_data
        elif self.header and self.keyword in self.header:
            return self.fuzz_header
        else:
            raise KeyError(
                f'keyword {self.keyword} not found in URL, post data, and headers')

    def _get_method(self):
        if self.data:
            return 'POST'
        return self.method

    def _get_dict_headers(self):
        if self.headers == None or isinstance(self.headers, dict):
            return self.headers

        headers = {}
        for h in self.headers:
            key, val = h.split(':', 1)
            headers[key] = val
        return headers

    def _get_dict_cookies(self):
        if self.cookies == None or isinstance(self.cookies, dict):
            return self.cookies

        cookies = {}
        for c in self.cookies:
            key, val = c.split('=', 1)
            cookies[key] = val
        return cookies
