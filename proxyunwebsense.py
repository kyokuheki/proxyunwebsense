#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import urllib.parse
import argparse
import requests
import lxml.html

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(funcName)s(%(lineno)d): %(message)s")
# logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(name)s:%(funcName)s(%(filename)s:%(lineno)d): %(message)s")
logger = logging.getLogger("proxyunwebsence")
proxies = {}

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363',
    'Accept': 'text/html, application/xhtml+xml, application/xml;q=0.9, */*;q=0.8',
    'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
}

# from http.client import HTTPSConnection, RemoteDisconnected
# def conn(proxy_host, proxy_port, host, port=443, debuglevel=0):
#     c = HTTPSConnection(proxy_host, proxy_port,
#                         context=_create_unverified_context())
#     c.set_debuglevel(debuglevel)
#     c.set_tunnel(host, port)
#     return c
# def req(proxy_host, proxy_port, url):
#     _c = conn(proxy_host, proxy_port, url.netloc)
#     headers = dict(DEFAULT_HEADERS)
#     headers['Host'] = url.netloc
#     _c.request('HEAD', '{}?{}'.format(url.path, url.query), headers=headers)
#     try:
#         _r = _c.getresponse()
#     except Exception as _e:
#         logger.exception(_e)
#         raise
#     return _r


def unwebsense(url: urllib.parse.ParseResult):
    request_url = url.geturl()
    if url.scheme == 'https':
        request_url = urllib.parse.urlunparse(('http', *url[1:]))

    logger.info("stage 1")
    r = requests.get(request_url, proxies=proxies, headers=DEFAULT_HEADERS)
    h = lxml.html.fromstring((r.text))
    elements = h.xpath('//frame[@name="after_work"]')
    if len(elements) < 1:
        return None
    webblock_url = elements[0].attrib['src']
    logger.info("websense url: {}".format(webblock_url))

    logger.info("stage 2")
    r = requests.get(webblock_url, proxies=proxies, headers=DEFAULT_HEADERS)
    r.headers
    h = lxml.html.fromstring((r.text))
    elements = h.xpath('//*[@id="contents"]//input')
    data = {}
    for e in elements:
        data[e.attrib['name']] = e.attrib['value']
    elements = h.xpath('//*[@id="contents"]/form')
    path = elements[0].attrib['action']
    # method = elements[0].attrib['method']

    logger.info("stage 3")
    base_url = h.base_url if h.base_url else r.url
    url = urllib.parse.urljoin(base_url, path)
    r = requests.post(
        url,
        data=data,
        allow_redirects=False,
        proxies=proxies,
        headers=DEFAULT_HEADERS)
    r.raise_for_status()
    logger.info("POST: {} {} ".format(url, data))
    logger.info("POST: status code: {}".format(r.status_code))
    if r.status_code == requests.codes.found:
        logger.info("unwebsence: {}".format(request_url))
    return r


def is_blocked(url: urllib.parse.ParseResult):
    request_url = url.geturl()
    try:
        r = requests.get(request_url, proxies=proxies, headers=DEFAULT_HEADERS)
    except requests.exceptions.ProxyError as e:
        logger.info("response: {}".format(e))
        if '403 Blocked by Websense' in str(e) and url.scheme == 'https':
            logger.info("websense found: {}".format(request_url))
            return True
        elif "RemoteDisconnected" in str(e) and url.scheme == 'https':
            return False
        elif "503 Service Unavailable" in str(e) and url.scheme == 'https':
            return False
        else:
            logger.info("response: {}".format(e))
            logger.warning("response: {}".format(e.args[0].args[0]))
            return False
    except requests.exceptions.SSLError as e:
        logger.info("response: {}".format(e))
        if "certificate required" in str(e) and url.scheme == 'https':
            return False
    h = lxml.html.fromstring((r.text))
    logger.info("GET: status code: {}".format(r.status_code))
    return r.status_code == requests.codes.ok and h.find(
        ".//title").text == 'Blocked by Websense'


def main():
    parser = argparse.ArgumentParser(
        description='proxyunwebsence.py: Unblock proxy websence.')
    parser.add_argument(
        '--http_proxy',
        action="store",
        type=urllib.parse.urlparse,
        default=os.getenv(
            "HTTP_PROXY",
            "http://127.0.0.1:3128"),
        help="HTTP PROXY")
    parser.add_argument(
        '--https_proxy',
        action="store",
        type=urllib.parse.urlparse,
        default=os.getenv(
            "HTTPS_PROXY",
            "http://127.0.0.1:3128"),
        help="HTTPS PROXY")
    parser.add_argument(
        '-c',
        '--count',
        action="store",
        type=int,
        default=5,
        help="set the number of unwebsence.")
    parser.add_argument(
        'url',
        nargs='*',
        type=urllib.parse.urlparse,
        default=[
            urllib.parse.urlparse("https://example.com")])

    args = parser.parse_args()
    logger.info("args: {}".format(args))

    global proxies
    proxies["http"] = args.http_proxy.geturl()
    proxies["https"] = args.https_proxy.geturl()

    logger.info("url: {}".format([u.geturl() for u in args.url]))
    logger.info("proxies: {}".format(proxies))

    for url in args.url:
        if is_blocked(url) or args.count > 1:
            for i in range(args.count):
                logger.info("count: {}".format(i))
                unwebsense(url)
                print("unwebsense: {}".format(url.geturl()))
            exit(is_blocked(url))
        else:
            print("websense not found")
            exit()


if __name__ == "__main__":
    main()
