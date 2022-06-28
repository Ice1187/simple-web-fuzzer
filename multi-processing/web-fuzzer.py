#!/usr/bin/env python3
import argparse
from fuzzer import Fuzzer

parser = argparse.ArgumentParser(
    description='A simple multi-processes Web Fuzzer.\
        Use keyword `FUZZ` in URL `-u`, post data `-d`, or header `-H` to define the fuzzing point.')
parser.add_argument('-u', '--url', action='store',
                    required=True, help='Target URL (required)')
parser.add_argument('-w', '--wordlist', action='store',
                    required=True, help='Wordlist file path (required)')
parser.add_argument('-e', '--encoding', action='store', default='utf-8',
                    help='Encoding for the wordlist, referring to Python Codecs (default: utf-8)')
parser.add_argument('-p', '--proc', action='store', type=int,
                    default=100, help='Number of concurrent processes (default: 32)')
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
match_arg_group = parser.add_argument_group('Match arguments')
match_arg_group.add_argument('-mc', action='store', nargs='+', default=[200, 204, 301, 302, 307, 401, 403, 405, 500],
                             help='Match status codes, use `-mc 200 403 404` to match multiple codes, or use `-mc all` for all codes (default: 200,204,301,302,307,401,403,405,500)')
match_arg_group.add_argument('-ms', action='store', nargs='+', type=int,
                             help='Match the size of response content, use `-ms 200 305` to match multiple size')
match_arg_group.add_argument('-mw', action='store', nargs='+', type=int,
                             help='Match the number of words in response, use `-mw 100 305` to match multiple number of words')
match_arg_group.add_argument('-ml', action='store', nargs='+', type=int,
                             help='Match the number of lines in response, use `-ml 200 305` to match multiple number of lines')

if __name__ == '__main__':
    args = parser.parse_args()

    fuzzer = Fuzzer(**vars(args))
    fuzzer.fuzz()
