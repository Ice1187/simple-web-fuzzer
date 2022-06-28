from typing import Callable, List
import requests as rq
import multiprocessing as mp
from time import perf_counter


class _HttpRequest:
    def __init__(self, req: rq.Request, timeout: float, word: str, redirect):
        self.req = req.prepare()
        self.timeout = timeout
        self.word = word
        self.redirect = redirect

    def request(self):
        with rq.sessions.Session() as session:
            res = session.send(self.req, timeout=self.timeout,
                               allow_redirects=self.redirect)
        return res, self.word


class HttpRequester:
    def __init__(self, worker_num, timeout, redirect) -> None:
        self.pool = mp.Pool(processes=worker_num)
        self.results = []
        self.timeout = timeout
        self.redirect = redirect

    def request(self, r: rq.Request, word: str, callback: Callable[[rq.Response], None], err_callback):
        req = _HttpRequest(r, self.timeout, word, self.redirect)
        self.pool.apply_async(
            req.request, (), callback=callback, error_callback=err_callback)

    def batch_request(self, rs: List[rq.Request], words: List[str], callback: Callable[[List[rq.Response]], None], err_callback):
        reqs = [_HttpRequest(rs[i], self.timeout, words[i], self.redirect)
                for i in range(len(rs))]
        self.pool.map_async(_HttpRequest.request, reqs,
                            callback=callback, error_callback=err_callback)

    def wait(self):
        self.pool.close()
        self.pool.join()


def default_callback(res):
    for r, word in res:
        print(f'{word}, {r.status_code}')


if __name__ == '__main__':
    url = 'https://ice1187.github.io'
    requester = HttpRequester(worker_num=16, timeout=10.)

    t0 = perf_counter()
    rs = []
    for _ in range(100):
        r = rq.Request(method='GET', url=url)
        rs.append(r)
    requester.batch_request(rs, default_callback, [i for i in range(100)])
    requester.get_results()
    print(f'Elapsed time: {perf_counter() - t0:.4f}')
