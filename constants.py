from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
SCRAPPER_CONFIG_PATH = PROJECT_ROOT / 'scrapper_config.json'
ARTICLES_PATH = PROJECT_ROOT / 'articles'
DATASET_PATH = PROJECT_ROOT / 'sentences_dataset.xlsx'


class WrongSeedURLError(Exception):
    """
    Raised when given URL-adress is not
    present in config
    """


def get_current_directory(url: str, articles_path: Path) -> Path:
    if '//iz' in url:
        return articles_path / 'Izvestiya_articles'
    elif '//rg' in url:
        return articles_path / 'RG_articles'
    elif 'russian.rt' in url:
        return articles_path / 'RT_articles'
    elif 'radiosputnik' in url:
        return articles_path / 'Sputnik_articles'
    else:
        raise WrongSeedURLError('Entered URL isn\'t present in the "seed_urls" parameter of the config file')
