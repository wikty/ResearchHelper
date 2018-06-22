import os
import time
import hashlib
import socket
import json
import datetime
from io import BytesIO
from dateutil import parser as date_parser
from urllib.request import urlopen
from urllib.parse import urlparse, urlencode, urljoin
from urllib.error import URLError, HTTPError
from html import escape as html_escape
from html import unescape as html_unescape

from lxml import etree


class SpiderError(Exception):
    pass

class SpiderRequestError(SpiderError):
    pass

class SpiderRequestUnknowError(SpiderRequestError):
    pass

class SpiderRequestHTTPError(SpiderRequestError):
    pass

class SpiderRequestTimeoutError(SpiderRequestError):
    pass

class SpiderCacheError(SpiderError):
    pass

class SpiderCacheUnknowError(SpiderCacheError):
    pass

class SpiderCacheReadError(SpiderCacheError):
    pass

class SpiderCacheWriteError(SpiderCacheError):
    pass

class SpiderParseError(SpiderError):
    pass


class PaperItem(object):

    def __init__(self, url):
        self.url = url
        self.download_link = ''
        self.doi_link = ''
        self._title = ''
        self._abstract = ''
        self._highlights = []
        self._authors = []
        self._keywords = []
        self._categories = []
        self._published = datetime.datetime(1970, 1, 1) # epoch

    def filter_remove_blank(self, value):
        if isinstance(value, str):
            return [value.strip()] if value.strip() else []
        elif isinstance(value, (list, tuple)):
            return [str(v).strip() for v in value if str(v).strip()]
        else:
            return [str(value).strip()] if str(value).strip() else []

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        value = self.filter_remove_blank(value)
        self._title = '\n'.join(value)

    @title.deleter
    def title(self):
        del self._title

    @property
    def authors(self):
        return self._authors

    @authors.setter
    def authors(self, value):
        value = self.filter_remove_blank(value)
        self._authors = value

    @authors.deleter
    def authors(self):
        del self._authors

    @property
    def published(self):
        return self._published
    
    @published.setter
    def published(self, value):
        try:
            dt = date_parser.parse(str(value))
        except Exception as e:
            pass
            # self._date = str(value)
        else:
            self._published = dt

    @published.deleter
    def published(self):
        del self._published

    @property
    def categories(self):
        return self._categories

    @categories.setter
    def categories(self, value):
        value = self.filter_remove_blank(value)
        self._categories = value

    @categories.deleter
    def categories(self):
        del self._categories

    @property
    def keywords(self):
        return self._keywords
    
    @keywords.setter
    def keywords(self, value):
        value = self.filter_remove_blank(value)
        self._keywords = value

    @keywords.deleter
    def keywords(self):
        del self._keywords

    @property
    def highlights(self):
        return self._highlights
    
    @highlights.setter
    def highlights(self, value):
        value = self.filter_remove_blank(value)
        self._highlights = value

    @highlights.deleter
    def highlights(self):
        del self._highlights

    @property
    def abstract(self):
        return self._abstract
    
    @abstract.setter
    def abstract(self, value):
        value = self.filter_remove_blank(value)
        self._abstract = '\n'.join(value)

    @abstract.deleter
    def abstract(self):
        del self._abstract

    def to_dict(self):
        return {
            'url': self.url,
            'title': self.title,
            'authors': self.authors,
            'published': self.published,
            'keywords': self.keywords,
            'categories': self.categories,
            'abstract': self.abstract,
            'highlights': self.highlights,
            'download_link': self.download_link,
            'doi_link': self.doi_link
        }


class BaseSpider(object):
    name = '*'
    host = '*'
    encoding = 'utf-8'
    cache_dir = 'cache'
    cache_enabled = False
    # 0 means that cache never expire, negative means never cache
    cache_expire = 0

    @classmethod
    def host_matched(cls, url):
        try:
            netloc = urlparse(url).netloc
            return netloc.endswith(cls.host)
        except Exception as e:
            return False

    def __init__(self, url, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.url = url
        self.item = PaperItem(self.url)
        self.urlhash = hashlib.md5(self.url.encode('utf-8')).hexdigest()
        self.filename = os.path.join(self.cache_dir, self.urlhash[:3], self.urlhash)
        self.xml_parser = etree.XMLParser(
            recover=True, 
            ns_clean=True,
            encoding=self.encoding
        )
        self.html_parser = etree.HTMLParser(
            recover=True, 
            encoding=self.encoding
        )

    def get_parser_errors(self, parser='html'):
        # lists the errors and warnings of the last parser run
        if parser == 'html':
            return self.html_parser.error_log
        elif parser == 'xml':
            return self.xml_parser.error_log
        return []

    def get_cache(self):
        try:
            if ((self.cache_expire < 0)
                or (not self.cache_enabled)):
                return None

            if not os.path.isfile(self.filename):
                return None
            
            content = b''
            now = time.time()
            mtime = os.path.getmtime(self.filename)
            if (self.cache_expire == 0
                or mtime + self.cache_expire >= now):
                with open(self.filename, 'rb') as f:
                    content = f.read()
                return BytesIO(content)
            else:
                return None
        except Exception as e:
            raise SpiderCacheReadError(e)

    def put_cache(self, content):
        try:
            if not self.cache_enabled:
                return False
            dirname = os.path.dirname(self.filename)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
            with open(self.filename, 'wb') as f:
                f.write(content)
            return True
        except Exception as e:
            raise SpiderCacheWriteError(e)

    def urljoin(self, url):
        # wrapper of the urllib.parse.urljoin
        return urljoin(self.url, url)

    def request(self, data, timeout):
        buf = self.get_cache()
        if buf is not None:
            return buf

        if isinstance(data, dict):
            data = urlencode(data).encode('utf-8')
        content = b''
        with urlopen(self.url, data=data, timeout=timeout) as f:
            content = f.read()

        self.put_cache(content)

        return BytesIO(content)

    def xml_parse(self, buf):
        # http://lxml.de/parsing.html
        return etree.parse(buf, self.xml_parser)

    def html_parse(self, buf):
        # http://lxml.de/parsing.html#parsing-html
        return etree.parse(buf, self.html_parser)

    def pull(self, data=None, timeout=20):
        """Request and parse the url.
        
        :param data: if you want a POST instead of GET request, you
            should provide this argument. It's should be a hashable
            dict.
        :param timeout: request timeout.
        """
        try:
            buf = self.request(data, timeout)
        except HTTPError as e:
            raise SpiderRequestHTTPError('HTTP error, {}: {}'.format(e.code, e.reason))
        except URLError as e:
            raise SpiderRequestUnknowError('Request url error.')
        except socket.timeout as e:
            raise SpiderRequestTimeoutError('Request url timeout.')
        except SpiderCacheError as e:
            raise SpiderCacheError('There is something wrong when cache the url.')
        except Exception as e:
            raise SpiderRequestError('There is something wrong when request the url.')
        
        try:
            tree = self.html_parse(buf)
            self.parse(tree)
        except Exception as e:
            raise SpiderParseError('There is something wrong when parse the url.')

    def update_item(self, key, value):
        setattr(self.item, key, value)

    def get_item(self):
        return self.item.to_dict()

    def parse(self, tree):
        # your should parse html and store results into self.item
        pass


class IEEESpider(BaseSpider):
    name = 'ieee'
    host = 'ieee.org'

    def parse(self, tree):
        xpath = '//script[contains(text(), "global.document.metadata")]/text()'
        script = tree.xpath(xpath)
        metadata = {}
        if script:
            for line in script[0].split(';\n'):
                line = line.strip()
                # print(line[:len('global.document.metadata=')])
                if line.startswith('global.document.metadata='):
                    metadata = json.loads(line[len('global.document.metadata='):])
                    break
        title = metadata.get('title', '')
        self.update_item('title', title)
        authors = metadata.get('authors', [])
        authors = [author.get('name', '') for author in authors]
        self.update_item('authors', authors)
        abstract = metadata.get('abstract', '')
        self.update_item('abstract', abstract)
        keywords = metadata.get('keywords', [])
        keywords = list(set(word for keyword in keywords for word in keyword.get('kwd', [])))
        self.update_item('keywords', keywords)
        doi_link = metadata.get('doi', '')
        doi_link = urljoin('https://doi.org/', doi_link) if doi_link else ''
        self.update_item('doi_link', doi_link)
        download_link = metadata.get('pdfUrl', '')
        download_link = self.urljoin(download_link) if download_link else ''
        self.update_item('download_link', download_link)



class SpringerSpider(BaseSpider):
    name = 'springer'
    host = 'springer.com'

    def parse(self, tree):
        xpath = '//h1[contains(@class, "ArticleTitle")]/text()'
        self.update_item('title', tree.xpath(xpath))
        xpath = '//*[@class="authors__list"]//*[@class="authors__name"]/text()'
        authors = tree.xpath(xpath)
        authors = [html_unescape(author) for author in authors]
        self.update_item('authors', authors)
        xpath = '//*[contains(@class, "KeywordGroup")]//*[contains(@class, "Keyword")]/text()'
        keywords = tree.xpath(xpath)
        self.update_item('keywords', keywords)
        xpath = '//*[@id="article-actions"]//*[contains(@class, "download-article")]/a[1]/@href'
        download_link = tree.xpath(xpath)
        download_link = self.urljoin(download_link[0]) if download_link else ''
        self.update_item('download_link', download_link)
        xpath = '//*[@id="doi-url"]/text()'
        doi_link = tree.xpath(xpath)
        doi_link = doi_link[0] if doi_link else ''
        self.update_item('doi_link', doi_link)


class ScienceDirectSpider(BaseSpider):
    name = 'sciencedirect'
    host = 'sciencedirect.com'

    def parse(self, tree):
        xpath = '//h1[contains(@class, "Head")]/*[contains(@class, "title-text")]/text()'
        self.update_item('title', tree.xpath(xpath))
        xpath = '//*[@id="author-group"]/a/span[@class="content"]'
        authors = tree.xpath(xpath)
        value = []
        for author in authors:
            xpath = '*[contains(@class, "given-name")]/text()'
            givenname = author.xpath(xpath)
            givenname = givenname[0].strip() if givenname else ''
            xpath = '*[contains(@class, "surname")]/text()'
            surname = author.xpath(xpath)
            surname = surname[0].strip() if surname else ''
            value.append(' '.join([givenname, surname]))
        self.update_item('authors', value)
        xpath = '//*[@id="abstracts"]/*[contains(@class, "abstract")][1]//*[contains(@class, "list")]/*[contains(@class, "list-description")]//text()'
        self.update_item('highlights', tree.xpath(xpath))
        xpath = 'string(//*[@id="abstracts"]/*[contains(@class, "abstract")][2]/div)'
        self.update_item('abstract', tree.xpath(xpath))
        xpath = '//*[@class="Keywords"]//*[@class="keyword"]//text()'
        self.update_item('keywords', tree.xpath(xpath))
        xpath = '//script[@type="application/json"]/text()'
        obj = json.loads(''.join(tree.xpath(xpath)))
        date = obj.get('article', {}).get('dates', {}).get('Publication date', '')
        self.update_item('published', date)
        download_link = obj.get('article', {}).get('pdfDownload', {}).get('linkToPdf', '')
        download_link = self.urljoin(download_link) if download_link else ''
        self.update_item('download_link', download_link)
        xpath = '//*[@id="doi-link"]/a[contains(@class, "doi")]/@href'
        doi_link = tree.xpath(xpath)
        doi_link = doi_link[0] if doi_link else ''
        self.update_item('doi_link', doi_link)


class ArxivSpider(BaseSpider):
    name = 'arxiv'
    host = 'arxiv.org'

    def parse(self, tree):
        xpath = '//*[@id="abs"]//h1[contains(@class, "title")]/text()'
        self.update_item('title', tree.xpath(xpath))
        xpath = '//*[@id="abs"]//div[contains(@class, "authors")]/a/text()'
        self.update_item('authors', tree.xpath(xpath))
        xpath ='//*[@id="abs"]//div[contains(@class, "submission-history")]/b[last()]'
        date = tree.xpath(xpath)
        date = date[0].tail.split('(')[0] if date else ''
        self.update_item('published', date)
        xpath = '//*[@id="abs"]//blockquote[contains(@class, "abstract")]/text()'
        self.update_item('abstract', tree.xpath(xpath))
        xpath = '//*[@id="abs"]//div[contains(@class, "subheader")]/h1/text()'
        categories = tree.xpath(xpath)
        categories = categories[0].split('>') if categories else []
        self.update_item('categories', categories)
        xpath = '//*[@id="abs"]//div[contains(@class, "extra-services")]//a[contains(@href, "pdf")]/@href'
        download_link = tree.xpath(xpath)
        download_link = self.urljoin(download_link[0]) if download_link else ''
        self.update_item('download_link', download_link)


class SpiderFactory(object):

    spiders = [SpringerSpider, ArxivSpider, ScienceDirectSpider, IEEESpider]

    @classmethod
    def create_spider(cls, url, **kwargs):
        for spider_cls in cls.spiders:
            if spider_cls.host_matched(url):
                spider = spider_cls(url, **kwargs)
                return spider
        return None