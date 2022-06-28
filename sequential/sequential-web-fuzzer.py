#!/usr/bin/env python3
import requests as rq
from time import perf_counter
import argparse
from copy import deepcopy
from re import split

parser = argparse.ArgumentParser(description='A simple sequential Web Fuzzer.\
        Use keyword `FUZZ` in URL `-u`, post data `-d`, or header `-H` to define the fuzzing point.')
parser.add_argument('-u', '--url', action='store',
                    required=True, help='Target URL (required)')
parser.add_argument('-w', '--wordlist', action='store',
                    required=True, help='Wordlist file path (required)')
parser.add_argument('-e', '--encoding', action='store', default='utf-8',
                    help='Encoding for the wordlist, referring to Python Codecs (default: utf-8)')
parser.add_argument('-p', '--proc', action='store', type=int,
                    default=32, help='Number of concurrent processes (default: 32)')
parser.add_argument('-t', '--timeout', action='store', type=float,
                    default=10.0, help='HTTP request timeout in seconds (default: 10.0)')
http_arg_group = parser.add_argument_group('HTTP arguments')
http_arg_group.add_argument('-X', '--method', action='store', choices=['GET', 'POST'], default='GET',
                            help='HTTP method')
http_arg_group.add_argument('-b', '--cookies', action='store', nargs='+',
                            help='Cookies `"Key=Value", use `-b "Key1=Value1" "Key2=Value2" to set multiple cookies')
http_arg_group.add_argument('-d', '--data', action='store',
                            help='HTTP Post data')
http_arg_group.add_argument('-H', '--headers', action='store', nargs='+',
                            help='HTTP headers `"Key: Value"`, use `-H "Key1: Value1" "Key2: Value2" to set multiple headers')
http_arg_group.add_argument('-r', '--redirect', action='store_true',
                            help='Follow redirects, add `-r` to follow (default: false)')

keyword = 'FUZZ'
batch_size = 256
total_req = 0
success_req = 0
error_req = 0
t0 = None


def get_fuzz_func(keyword, url, data, headers):
    if keyword in url:
        return fuzz_URL
    elif data and keyword in data:
        return fuzz_data
    elif headers and any(keyword in key for key in headers.keys()):
        return fuzz_header_key
    elif headers and any(keyword in val for val in headers.values()):
        return fuzz_header_value
    else:
        raise KeyError(
            f'keyword {keyword} not found in URL, post data, and headers')


def _get_method(method, data):
    if data:
        return 'POST'
    return method


def _get_dict_headers(headers):
    if headers == None or isinstance(headers, dict):
        return headers

    ret = {}
    for h in headers:
        key, val = h.split(':', 1)
        ret[key] = val.strip()
    return ret


def _get_dict_cookies(cookies):
    if cookies == None or isinstance(cookies, dict):
        return cookies

    ret = {}
    for c in cookies:
        key, val = c.split('=', 1)
        ret[key] = val.strip()
    return ret


def _build_request(method, url, headers, data, cookies):
    method = _get_method(method, data)
    headers = _get_dict_headers(headers)
    cookies = _get_dict_cookies(cookies)
    base_req = rq.Request(
        method, url, headers, data=data, cookies=cookies)
    return base_req


def fuzz_URL(s, keyword, base_req, words, timeout, redirect):
    for i, word in enumerate(words):
        req = deepcopy(base_req)
        req.url = req.url.replace(keyword, word)
        req = req.prepare()

        res = s.send(req, timeout=timeout, allow_redirects=redirect)
        print_res(res, word)


def fuzz_data(s, keyword, base_req, words, timeout, redirect):
    for i, word in enumerate(words):
        req = deepcopy(base_req)
        req.data = req.data.replace(keyword, word)
        req = req.prepare()

        res = s.send(req, timeout=timeout, allow_redirects=redirect)
        print_res(res, word)


def fuzz_header_key(s, keyword, base_req, words, timeout, redirect):
    key_to_replace = []
    for key in base_req.headers.keys():
        if keyword in key:
            key_to_replace.append(key)
    for i, word in enumerate(words):
        req = deepcopy(base_req)
        for key in key_to_replace:
            req.headers[key.replace(keyword, word)
                        ] = req.headers.pop(key)
        req = req.prepare()
        res = s.send(req, timeout=timeout, allow_redirects=redirect)
        print_res(res, word)


def fuzz_header_value(s, keyword, base_req, words, timeout, redirect):
    for i, word in enumerate(words):
        req = deepcopy(base_req)
        for key in req.headers.keys():
            req.headers[key] = req.headers[key].replace(keyword, word)
        req = req.prepare()
        res = s.send(req, timeout=timeout, allow_redirects=redirect)
        print_res(res, word)


def print_res(r, fuzz):
    global success_req
    success_req += 1

    duration = perf_counter() - t0
    status = r.status_code
    size = len(r.content)
    word = len(split(r'[^\S\n\t]', r.text))
    line = len(r.text.split('\n'))

    print(
        f'\033[1A{fuzz: <60} [Status: {status}, Size: {size}, Word: {word}, Line: {line}]')
    print_status('\033[1B', duration)


def print_status(prefix, duration):
    rate = 0.
    if success_req != 0:
        rate = success_req / duration

    msg = prefix
    msg += f'====== Duration: {duration:.4f} sec, Rate: {rate:.4f} req/sec, Success: {success_req}, Error: {error_req}, Total: {success_req+error_req}/{total_req} ======'
    print(msg)


if __name__ == '__main__':
    args = parser.parse_args()

    session = rq.sessions.Session()

    headers = _get_dict_headers(args.headers)
    fuzz_func = get_fuzz_func(keyword, args.url, args.data, headers)
    base_req = _build_request(args.method, args.url,
                              args.headers, args.data, args.cookies)

    print('')  # allocate 1 line for printing
    t0 = perf_counter()
    words = []
    with open(args.wordlist, 'r', encoding=args.encoding) as wordlist:
        for i, word in enumerate(wordlist):
            words.append(word[:-1])  # [:-1] remove newline
            total_req += 1
            if i % batch_size == batch_size - 1:
                fuzz_func(session, keyword, base_req, words,
                          args.timeout, args.redirect)
                words = []
        fuzz_func(session, keyword, base_req,
                  words, args.timeout, args.redirect)

    session.close()
