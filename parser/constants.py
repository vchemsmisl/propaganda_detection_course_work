from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
SCRAPPER_CONFIG_PATH = PROJECT_ROOT / 'scrapper_config.json'
PARSING_STATUS_PATH = PROJECT_ROOT / 'parsing_status.json'
CRAWLING_STATUS_PATH = PROJECT_ROOT / 'crawling_status.json'
SENTENCES_EXTRACTION_STATUS_PATH = PROJECT_ROOT / 'sentences_extraction_status.json'

ARTICLES_PATH = PROJECT_ROOT / 'articles'
DATASET_PATH = PROJECT_ROOT / 'sentences_dataset.xlsx'
CHROME_DRIVER_PATH = PROJECT_ROOT / 'chromedriver.exe'


class WrongSeedURLError(Exception):
    """
    Raised when given URL-adress is not
    present in config
    """


def get_current_directory(url: str, articles_path: Path) -> Path:
    """
    Given a link to the article and a path to the folder
    with articles, gets the path to the
    folder with articles of particular source edition
    :param url: a link to the article
    :param articles_path: a path to the folder
    with articles
    :return: the path to a particular folder
    """

    if '//iz' in url:
        return articles_path / 'Izvestiya_articles'

    elif '//rg' in url:
        return articles_path / 'RG_articles'

    elif 'mk.ru' in url:
        return articles_path / 'MK_articles'

    else:
        raise WrongSeedURLError('Entered URL isn\'t present in the "seed_urls" parameter of the config file')
