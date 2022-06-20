from typing import List
import requests as rq
from copy import deepcopy
from re import split
from time import perf_counter
from requester import HttpRequester


class Fuzzer:
    def __init__(self, url, wordlist, proc, timeout, encoding=None, method=None, cookies=None, data=None, headers=None, redirect=None, mc=None, ms=None, mw=None, ml=None):
        self.keyword = 'FUZZ'
        self.batch_size = 256

        # required arguments
        self.url = url
        self.wordlist_path = wordlist
        self.encoding = encoding
        self.proc_num = proc
        self.timeout = timeout

        # http arguments
        self.method = method
        self.cookies = cookies
        self.data = data
        self.headers = headers
        self.redirect = redirect

        # match arguments
        self.matches = {
            'codes': ['all'] if 'all' in mc else [int(c) for c in mc],
            'size': ms if ms else [],
            'word': mw if mw else [],
            'line': ml if ml else [],
        }

        self.http_requester = HttpRequester(
            self.proc_num, self.timeout, self.redirect)

        self.fuzz_func = None
        self.base_req = None
        self.total_req = 0
        self.success_req = 0
        self.error_req = 0

    def fuzz(self):
        try:
            self._build_request()
        except Exception as e:
            raise RuntimeError('Failed to build base request') from e

        print('')  # allocate 1 line for printing
        self.t0 = perf_counter()
        words = []
        with open(self.wordlist_path, 'r', encoding=self.encoding) as wordlist:
            for i, word in enumerate(wordlist):
                words.append(word[:-1])  # [:-1] remove newline
                if i % self.batch_size == self.batch_size - 1:
                    self.fuzz_func(words)
                    words = []
                self.total_req += 1
            self.fuzz_func(words)

        self.http_requester.wait()
        self.print_status('\033[1A\r', perf_counter() - self.t0)
        return self.total_req

    def fuzz_URL(self, words: List[str]):
        for i, word in enumerate(words):
            req = deepcopy(self.base_req)
            req.url = req.url.replace(self.keyword, word)
            self.http_requester.request(
                req, word, self.callback, self.err_callback)

    def fuzz_data(self, words: List[str]):
        for i, word in enumerate(words):
            req = deepcopy(self.base_req)
            req.data = req.data.replace(self.keyword, word)
            self.http_requester.request(
                req, word, self.callback, self.err_callback)

    def fuzz_header_key(self, words):
        key_to_replace = []
        for key in self.base_req.headers.keys():
            if self.keyword in key:
                key_to_replace.append(key)
        for i, word in enumerate(words):
            req = deepcopy(self.base_req)
            for key in key_to_replace:
                req.headers[key.replace(self.keyword, word)
                            ] = req.headers.pop(key)
            self.http_requester.request(
                req, word, self.callback, self.err_callback)

    def fuzz_header_value(self, words):
        for i, word in enumerate(words):
            req = deepcopy(self.base_req)
            for key in req.headers.keys():
                req.headers[key] = req.headers[key].replace(self.keyword, word)
            self.http_requester.request(
                req, word, self.callback, self.err_callback)

    def callback(self, res: rq.Response):
        r, fuzz = res
        self.success_req += 1

        duration = perf_counter() - self.t0
        status = r.status_code
        size = len(r.content)
        word = len(split(r'[^\S\n\t]', r.text))
        line = len(r.text.split('\n'))

        if status in self.matches['codes'] or 'all' in self.matches['codes'] \
                or size in self.matches['size'] or word in self.matches['word'] or line in self.matches['line']:
            print(
                f'\033[1A{fuzz: <60} [Status: {status}, Size: {size}, Word: {word}, Line: {line}]')
            self.print_status('\033[1B', duration)

    def err_callback(self, err):
        self.error_req += 1
        print(err)

    def print_status(self, prefix, duration):
        rate = duration / self.success_req

        msg = prefix
        msg += f'====== Duration: {duration:.4f} sec, Rate: {rate:.4f} req/sec, Success: {self.success_req}, Error: {self.error_req}, Total: {self.success_req+self.error_req}/{self.total_req} ======'
        print(msg)

    def _build_request(self):
        self.method = self._get_method()
        self.headers = self._get_dict_headers()
        self.cookies = self._get_dict_cookies()
        self.base_req = rq.Request(
            self.method, self.url, self.headers, data=self.data, cookies=self.cookies)

        self.fuzz_func = self._get_fuzz_func()

    def _get_fuzz_func(self):
        if self.keyword in self.url:
            return self.fuzz_URL
        elif self.data and self.keyword in self.data:
            return self.fuzz_data
        elif self.headers and any(self.keyword in key for key in self.headers.keys()):
            return self.fuzz_header_key
        elif self.headers and any(self.keyword in val for val in self.headers.values()):
            return self.fuzz_header_value
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
            headers[key] = val.strip()
        return headers

    def _get_dict_cookies(self):
        if self.cookies == None or isinstance(self.cookies, dict):
            return self.cookies

        cookies = {}
        for c in self.cookies:
            key, val = c.split('=', 1)
            cookies[key] = val
        return cookies
