# Simple Web Fuzzer
A simple multi-process web fuzzer written in Python.

## Getting Started

### Dependencies

- Python3 (tested on Python3.9)
- [`requests`](https://requests.readthedocs.io/en/latest/) module (for multi-processing and sequential version)
- [`aiohttp`](https://docs.aiohttp.org/en/stable/) module (for async version)

### Installing

```bash
git clone git@github.com:Ice1187/simple-web-fuzzer.git
chmod +x simple-web-fuzzer/src/web-fuzzer.py
./simple-web-fuzzer/src/web-fuzzer.py --help
```

## Help

```
usage: web-fuzzer.py [-h] -u URL -w WORDLIST [-e ENCODING] [-p PROC] [-t TIMEOUT] [-X {GET,POST}] [-b COOKIES [COOKIES ...]]
                     [-d DATA] [-H HEADERS [HEADERS ...]] [-r] [-mc MC [MC ...]] [-ms MS [MS ...]] [-mw MW [MW ...]]
                     [-ml ML [ML ...]]

A simple multi-processes Web Fuzzer. Use keyword `FUZZ` in URL `-u`, post data `-d`, or header `-H` to define the fuzzing
point.

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     Target URL (required)
  -w WORDLIST, --wordlist WORDLIST
                        Wordlist file path (required)
  -e ENCODING, --encoding ENCODING
                        Encoding for the wordlist, referring to Python Codecs (default: utf-8)
  -p PROC, --proc PROC  Number of concurrent processes (default: 32)
  -t TIMEOUT, --timeout TIMEOUT
                        HTTP request timeout in seconds (default: 10.0)

HTTP arguments:
  -X {GET,POST}, --method {GET,POST}
                        HTTP method
  -b COOKIES [COOKIES ...], --cookies COOKIES [COOKIES ...]
                        Cookies `"Key=Value", use `-b "Key1: Value1" "Key2: Value2" to set multiple cookies
  -d DATA, --data DATA  HTTP Post data
  -H HEADERS [HEADERS ...], --headers HEADERS [HEADERS ...]
                        HTTP headers `"Key: Value"`, use `-H "Key1: Value1" "Key2: Value2" to set multiple headers
  -r, --redirect        Follow redirects, add `-r` to follow (default: false)

Match arguments:
  -mc MC [MC ...]       Match status codes, use `-mc 200 403 404` to match multiple codes, or use `-mc all` for all codes
                        (default: 200,204,301,302,307,401,403,405,500)
  -ms MS [MS ...]       Match the size of response content, use `-ms 200 305` to match multiple size
  -mw MW [MW ...]       Match the number of words in response, use `-mw 100 305` to match multiple number of words
  -ml ML [ML ...]       Match the number of lines in response, use `-ml 200 305` to match multiple number of lines
```

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.
