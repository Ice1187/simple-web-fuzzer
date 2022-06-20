#!/usr/bin/env python3
import argparse
from fuzzer import Fuzzer
from time import perf_counter
import cProfile

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
                    default=32, help='Number of concurrent processes (default: 32)')
parser.add_argument('-t', '--timeout', action='store', type=float,
                    default=10.0, help='HTTP request timeout in seconds (default: 10.0)')
http_arg_group = parser.add_argument_group('HTTP arguments')
http_arg_group.add_argument('-X', '--method', action='store', choices=['GET', 'POST'], default='GET',
                            help='HTTP method')
http_arg_group.add_argument('-b', '--cookies', action='store', nargs='+',
                            help='Cookies `"Key=Value", use `-b "Key1: Value1" "Key2: Value2" to set multiple cookies')
http_arg_group.add_argument('-d', '--data', action='store',
                            help='HTTP Post data')
http_arg_group.add_argument('-H', '--headers', action='store', nargs='+',
                            help='HTTP headers `"Key: Value"`, use `-H "Key1: Value1" "Key2: Value2" to set multiple headers')
http_arg_group.add_argument('-r', '--redirect', action='store_true',
                            help='Follow redirects, add `-r` to follow (default: false)')

if __name__ == '__main__':
    args = parser.parse_args()

    t0 = perf_counter()
    fuzzer = Fuzzer(**vars(args))
    fuzzer.fuzz()
    #cProfile.run('fuzzer.fuzz()', sort='cumtime')
