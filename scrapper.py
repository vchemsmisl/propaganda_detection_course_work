from pathlib import Path
import json
import requests
from bs4 import BeautifulSoup
import time
import random
import shutil
import lxml
from constants import get_current_directory, ARTICLES_PATH


class WrongSeedURLError(Exception):
    """
    Raised when given URL-adress is not
    present in config
    """


class Config:
    """
    Unpacks and validates configurations
    """

    def __init__(self, path_to_config: Path) -> None:
        """
        Initializes an instance of the Config class
        """
        self.path_to_config = path_to_config
        self.config = self._extract_config_content()

        self._seed_urls = self.config['seed_urls']
        self._num_articles = self.config['num_articles']
        self._headers = self.config['headers']
        self._encoding = self.config['encoding']
        self._timeout = self.config['timeout']
        self._should_verify_certificate = self.config['should_verify_certificate']
        self._headless_mode = self.config['headless_mode']

    def _extract_config_content(self) -> dict:
        """
        Returns config values
        """
        with open(self.path_to_config, 'r', encoding='utf-8') as path:
            config_dict = json.load(path)
        return config_dict

    def get_seed_urls(self) -> list[str]:
        """
        Retrieve seed urls
        """
        return self._seed_urls

    def get_num_articles(self) -> int:
        """
        Retrieve number of articles to scrape
        from each source
        """
        return self._num_articles

    def get_headers(self) -> dict[str, str]:
        """
        Retrieve headers to use during requesting
        """
        return self._headers

    def get_encoding(self) -> str:
        """
        Retrieve encoding to use during parsing
        """
        return self._encoding

    def get_timeout(self) -> int:
        """
        Retrieve number of seconds to wait for response
        """
        return self._timeout

    def get_verify_certificate(self) -> bool:
        """
        Retrieve whether to verify certificate
        """
        return self._should_verify_certificate


def make_request(url: str, config: Config) -> requests.models.Response:
    """
    Delivers a response from a request
    with given configuration
    """
    time.sleep(random.randint(1, 10))
    response = requests.get(url,
                        headers=config.get_headers(),
                        timeout=config.get_timeout())
    response.encoding = config.get_encoding()
    return response


class Crawler:
    """
    Crawler implementation
    """

    def __init__(self, config: Config) -> None:
        """
        Initializes an instance of the Crawler class
        """
        self.config = config
        self.urls = []
        self._seed_urls = self.config.get_seed_urls()

    @staticmethod
    def _extract_url(seed_url: str, article_bs: BeautifulSoup) -> str:
        """
        Finds and retrieves URL from HTML
        """
        match seed_url:
            case 'https://iz.ru/feed':
                url = 'https://iz.ru' + article_bs.get('href')
            case 'https://rg.ru/news.html':
                url = 'https://rg.ru' + article_bs.get('href')
            case 'https://russian.rt.com/news':
                url = 'https://russian.rt.com' + article_bs.get('href')
            case 'https://radiosputnik.ru/search/?query=Sputnik':
                url = article_bs.get('href')
            case _:
                raise WrongSeedURLError('Entered URL isn\'t present in '
                                        'the "seed_urls" parameter of the config file')
        if isinstance(url, str):
            return url
        return ''

    def find_articles(self) -> None:
        """
        Finds articles
        """
        num_arts = self.config.get_num_articles()
        for url in self._seed_urls:
            response = make_request(url, self.config)
            if response.status_code != 200:
                print(response.status_code)
                print('error')
                continue
            main_bs = BeautifulSoup(response.text, 'lxml')
            match url:
                case 'https://iz.ru/feed':
                    feed_lines = main_bs.find_all('a',
                            {'class': 'lenta_news__day__list__item show_views_and_comments'})[:num_arts]
                case 'https://rg.ru/news.html':
                    feed_lines_div = main_bs.find_all('div',
                                                      {'class': 'PageNewsContent_item__ZDNam'})[:num_arts]
                    feed_lines = [bs.find('a') for bs in feed_lines_div]
                case 'https://russian.rt.com/news':
                    feed_lines_div = main_bs.find_all('div',
                                {'class': 'card__heading card__heading_all-news card__heading_not-cover'})[:num_arts]
                    print(len(feed_lines_div))
                    feed_lines = [bs.find('a') for bs in feed_lines_div]

                case 'https://radiosputnik.ru/search/?query=Sputnik':
                    feed_lines = main_bs.find_all('a', {'class': 'list-item__image'})[:num_arts]
                case _:
                    raise WrongSeedURLError('Entered URL isn\'t present in '
                                            'the "seed_urls" parameter of the config file')
            for line in feed_lines:
                if link := self._extract_url(url, line):
                    if link not in self.urls:
                        self.urls.append(link)

    def get_search_urls(self) -> list:
        """
        Returns seed_urls param
        """
        return self._seed_urls


class Parser:

    def __init__(self, full_url: str, config: Config) -> None:
        """
        Initializes an instance of the Parser class
        """
        self.full_url = full_url
        self.config = config

    def _extract_text(self, article_soup: BeautifulSoup):
        if '//iz' in self.full_url:
            article = article_soup.find('div', {'itemprop': 'articleBody'})
            article_list = article.find_all('p')
        elif '//rg' in self.full_url:
            # article_p2 = article_soup.find('div', {'class': 'PageArticleContent_content__3MI5'})
            article = article_soup.find('div', {'class': ''})
            article_list = article.find_all('p')
            article_lead = article.find('div', {'class': 'PageArticleContent_lead__gvX5C'})
            article_list.insert(0, article_lead)
        elif 'russian.rt' in self.full_url:
            article = article_soup.find('div', {'class': 'article article_article-page'})
            article_list = article.find_all('p')
        elif 'radiosputnik' in self.full_url:
            article = article_soup.find('div', {'class': 'article__body js-mediator-article mia-analytics'})
            article_list = article.find_all('div', {'class': 'article__block'})
        else:
            raise WrongSeedURLError('Entered URL isn\'t present in '
                                    'the "seed_urls" parameter of the config file')
        paragraphs = [par.text for par in article_list]
        return '\n'.join(paragraphs)

    def _write_to_txt(self, text: str, article_num: int):
        curr_dir = get_current_directory(self.full_url, ARTICLES_PATH)
        if not curr_dir.exists():
            curr_dir.mkdir(parents=True)
        txt_file_link = curr_dir / f'{article_num}.txt'
        with open(txt_file_link, 'w', encoding='utf-8') as file:
            file.write(text)

    def parse_and_save_file(self, article_num: int):
        """
        Parses each article and saves
        in a .txt file in a corresponding directory
        """
        response = make_request(self.full_url, self.config)
        b_s = BeautifulSoup(response.text, 'lxml')
        text = self._extract_text(b_s)
        self._write_to_txt(text, article_num)

#
# def prepare_environment(base_path) -> None:
#     """
#     Creates folder for articles if no created
#     and removes existing folder
#     """
#     if base_path.exists():
#         shutil.rmtree(base_path)
#     base_path.mkdir(parents=True)
