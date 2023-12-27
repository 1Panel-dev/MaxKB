import re
from functools import reduce
from typing import List, Set
import requests
import html2text as ht
from bs4 import BeautifulSoup
from urllib.parse import urljoin


class ForkManage:
    def __init__(self, base_url: str, selector_list: List[str]):
        self.base_url = base_url
        self.selector_list = selector_list

    def fork(self, level: int, exclude_link_url: Set[str], fork_handler):
        self.fork_child(self.base_url, self.selector_list, level, exclude_link_url, fork_handler)

    @staticmethod
    def fork_child(base_url: str, selector_list: List[str], level: int, exclude_link_url: Set[str], fork_handler):
        if level < 0:
            return
        response = Fork(base_url, selector_list).fork()
        fork_handler(base_url, response)
        for child_link in response.child_link_list:
            if not exclude_link_url.__contains__(child_link):
                exclude_link_url.add(child_link)
                ForkManage.fork_child(child_link, selector_list, level - 1, exclude_link_url, fork_handler)


class Fork:
    class Response:
        def __init__(self, html_content: str, child_link_list: List[str], status, message: str):
            self.html_content = html_content
            self.child_link_list = child_link_list
            self.status = status
            self.message = message

        @staticmethod
        def success(html_content: str, child_link_list: List[str]):
            return Fork.Response(html_content, child_link_list, 200, '')

        @staticmethod
        def error(message: str):
            return Fork.Response('', [], 500, message)

    def __init__(self, base_fork_url: str, selector_list: List[str]):
        self.base_fork_url = urljoin(base_fork_url if base_fork_url.endswith("/") else base_fork_url + '/', '.')
        self.base_fork_url = base_fork_url
        self.selector_list = selector_list

    def get_child_link_list(self, bf: BeautifulSoup):
        pattern = "^(?!(http:|https:|tel:/|#|mailto:|javascript:)).*|" + self.base_fork_url
        link_list = bf.find_all(name='a', href=re.compile(pattern))
        result = [self.parse_href(link.get('href')) for link in link_list]
        return result

    def get_content_html(self, bf: BeautifulSoup):
        if self.selector_list is None or len(self.selector_list) == 0:
            return str(bf)
        params = reduce(lambda x, y: {**x, **y},
                        [{'class_': selector.replace('.', '')} if selector.startswith('.') else {
                            'id': selector.replace("#", "") if selector.startswith("#") else {'name': selector}} for
                         selector in
                         self.selector_list], {})
        f = bf.find_all(**params)
        return "\n".join([str(row) for row in f])

    def parse_href(self, href: str):
        if href.startswith(self.base_fork_url[:-1] if self.base_fork_url.endswith('/') else self.base_fork_url):
            return href
        else:
            return urljoin(self.base_fork_url + '/' + (href if href.endswith('/') else href + '/'), ".")

    def reset_beautiful_soup(self, bf: BeautifulSoup):
        href_list = bf.find_all(href=re.compile('^(?!(http:|https:|tel:/|#|mailto:|javascript:)).*'))
        for h in href_list:
            h['href'] = urljoin(
                self.base_fork_url + '/' + (h['href'] if h['href'].endswith('/') else h['href'] + '/'),
                ".")[:-1]
        src_list = bf.find_all(src=re.compile('^(?!(http:|https:|tel:/|#|mailto:|javascript:)).*'))
        for s in src_list:
            s['src'] = urljoin(
                self.base_fork_url + '/' + (s['src'] if s['src'].endswith('/') else s['src'] + '/'),
                ".")[:-1]
        return bf

    @staticmethod
    def get_beautiful_soup(response):
        encoding = response.apparent_encoding if response.apparent_encoding is not None else 'utf-8'
        html_content = response.content.decode(encoding)
        return BeautifulSoup(html_content, "html.parser")

    def fork(self):
        try:
            response = requests.get(self.base_fork_url)
            if response.status_code != 200:
                raise Exception(response.status_code)
            bf = self.get_beautiful_soup(response)
        except Exception as e:
            return Fork.Response.error(str(e))
        bf = self.reset_beautiful_soup(bf)
        link_list = self.get_child_link_list(bf)
        content = self.get_content_html(bf)
        r = ht.html2text(content)
        return Fork.Response.success(r, link_list)


def handler(base_url, response: Fork.Response):
    print(base_url, response.status)


ForkManage('https://dataease.io/docs/v2/', ['.md-content']).fork(3, set(), handler)
