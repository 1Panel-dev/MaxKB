import copy
import logging
import re
import traceback
from functools import reduce
from typing import List, Set
from urllib.parse import urljoin, urlparse, ParseResult, urlsplit, urlunparse

import html2text as ht
import requests
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings()


class ChildLink:
    def __init__(self, url, tag):
        self.url = url
        self.tag = copy.deepcopy(tag)


class ForkManage:
    def __init__(self, base_url: str, selector_list: List[str]):
        self.base_url = base_url
        self.selector_list = selector_list

    def fork(self, level: int, exclude_link_url: Set[str], fork_handler):
        self.fork_child(ChildLink(self.base_url, None), self.selector_list, level, exclude_link_url, fork_handler)

    @staticmethod
    def fork_child(child_link: ChildLink, selector_list: List[str], level: int, exclude_link_url: Set[str],
                   fork_handler):
        if level < 0:
            return
        else:
            child_link.url = remove_fragment(child_link.url)
            child_url = child_link.url[:-1] if child_link.url.endswith('/') else child_link.url
        if not exclude_link_url.__contains__(child_url):
            exclude_link_url.add(child_url)
            response = Fork(child_link.url, selector_list).fork()
            fork_handler(child_link, response)
            for child_link in response.child_link_list:
                child_url = child_link.url[:-1] if child_link.url.endswith('/') else child_link.url
                if not exclude_link_url.__contains__(child_url):
                    ForkManage.fork_child(child_link, selector_list, level - 1, exclude_link_url, fork_handler)


def remove_fragment(url: str) -> str:
    parsed_url = urlparse(url)
    modified_url = ParseResult(scheme=parsed_url.scheme, netloc=parsed_url.netloc, path=parsed_url.path,
                               params=parsed_url.params, query=parsed_url.query, fragment=None)
    return urlunparse(modified_url)


class Fork:
    class Response:
        def __init__(self, content: str, child_link_list: List[ChildLink], status, message: str):
            self.content = content
            self.child_link_list = child_link_list
            self.status = status
            self.message = message

        @staticmethod
        def success(html_content: str, child_link_list: List[ChildLink]):
            return Fork.Response(html_content, child_link_list, 200, '')

        @staticmethod
        def error(message: str):
            return Fork.Response('', [], 500, message)

    def __init__(self, base_fork_url: str, selector_list: List[str]):
        base_fork_url = remove_fragment(base_fork_url)
        self.base_fork_url = urljoin(base_fork_url if base_fork_url.endswith("/") else base_fork_url + '/', '.')
        parsed = urlsplit(base_fork_url)
        query = parsed.query
        self.base_fork_url = self.base_fork_url[:-1]
        if query is not None and len(query) > 0:
            self.base_fork_url = self.base_fork_url + '?' + query
        self.selector_list = [selector for selector in selector_list if selector is not None and len(selector) > 0]
        self.urlparse = urlparse(self.base_fork_url)
        self.base_url = ParseResult(scheme=self.urlparse.scheme, netloc=self.urlparse.netloc, path='', params='',
                                    query='',
                                    fragment='').geturl()

    def get_child_link_list(self, bf: BeautifulSoup):
        pattern = "^((?!(http:|https:|tel:/|#|mailto:|javascript:))|" + self.base_fork_url + "|/).*"
        link_list = bf.find_all(name='a', href=re.compile(pattern))
        result = [ChildLink(link.get('href'), link) if link.get('href').startswith(self.base_url) else ChildLink(
            self.base_url + link.get('href'), link) for link in link_list]
        result = [row for row in result if row.url.startswith(self.base_fork_url)]
        return result

    def get_content_html(self, bf: BeautifulSoup):
        if self.selector_list is None or len(self.selector_list) == 0:
            return str(bf)
        params = reduce(lambda x, y: {**x, **y},
                        [{'class_': selector.replace('.', '')} if selector.startswith('.') else
                         {'id': selector.replace("#", "")} if selector.startswith("#") else {'name': selector} for
                         selector in
                         self.selector_list], {})
        f = bf.find_all(**params)
        return "\n".join([str(row) for row in f])

    @staticmethod
    def reset_url(tag, field, base_fork_url):
        field_value: str = tag[field]
        if field_value.startswith("/"):
            result = urlparse(base_fork_url)
            result_url = ParseResult(scheme=result.scheme, netloc=result.netloc, path=field_value, params='', query='',
                                     fragment='').geturl()
        else:
            result_url = urljoin(
                base_fork_url + '/' + (field_value if field_value.endswith('/') else field_value + '/'),
                ".")
        result_url = result_url[:-1] if result_url.endswith('/') else result_url
        tag[field] = result_url

    def reset_beautiful_soup(self, bf: BeautifulSoup):
        reset_config_list = [
            {
                'field': 'href',
            },
            {
                'field': 'src',
            }
        ]
        for reset_config in reset_config_list:
            field = reset_config.get('field')
            tag_list = bf.find_all(**{field: re.compile('^(?!(http:|https:|tel:/|#|mailto:|javascript:)).*')})
            for tag in tag_list:
                self.reset_url(tag, field, self.base_fork_url)
        return bf

    @staticmethod
    def get_beautiful_soup(response):
        encoding = response.encoding if response.encoding is not None and response.encoding != 'ISO-8859-1' else response.apparent_encoding
        html_content = response.content.decode(encoding)
        beautiful_soup = BeautifulSoup(html_content, "html.parser")
        meta_list = beautiful_soup.find_all('meta')
        charset_list = [meta.attrs.get('charset') for meta in meta_list if
                        meta.attrs is not None and 'charset' in meta.attrs]
        if len(charset_list) > 0:
            charset = charset_list[0]
            if charset != encoding:
                html_content = response.content.decode(charset)
                return BeautifulSoup(html_content, "html.parser")
        return beautiful_soup

    def fork(self):
        try:

            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
            }

            logging.getLogger("max_kb").info(f'fork:{self.base_fork_url}')
            response = requests.get(self.base_fork_url, verify=False, headers=headers)
            if response.status_code != 200:
                logging.getLogger("max_kb").error(f"url: {self.base_fork_url} code:{response.status_code}")
                return Fork.Response.error(f"url: {self.base_fork_url} code:{response.status_code}")
            bf = self.get_beautiful_soup(response)
        except Exception as e:
            logging.getLogger("max_kb_error").error(f'{str(e)}:{traceback.format_exc()}')
            return Fork.Response.error(str(e))
        bf = self.reset_beautiful_soup(bf)
        link_list = self.get_child_link_list(bf)
        content = self.get_content_html(bf)
        r = ht.html2text(content)
        return Fork.Response.success(r, link_list)


def handler(base_url, response: Fork.Response):
    print(base_url.url, base_url.tag.text if base_url.tag else None, response.content)

# ForkManage('https://bbs.fit2cloud.com/c/de/6', ['.md-content']).fork(3, set(), handler)
