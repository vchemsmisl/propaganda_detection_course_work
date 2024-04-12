from constants import (ARTICLES_PATH,
                       SCRAPPER_CONFIG_PATH,
                       PARSING_STATUS_PATH,
                       DATASET_PATH,
                       get_current_directory)
from scrapper import (Config,
                      Crawler,
                      Parser)
from preprocessor import TextPreprocessor, save_exel_dataset
import json


def collection_of_articles():
    if not PARSING_STATUS_PATH.exists():
        if not ARTICLES_PATH.exists():
            ARTICLES_PATH.mkdir(parents=True)
        configuration = Config(path_to_config=SCRAPPER_CONFIG_PATH)
        crawler = Crawler(config=configuration)
        crawler.find_articles()
        print(len(crawler.urls))
    else:
        configuration = Config(path_to_config=SCRAPPER_CONFIG_PATH)

    if not PARSING_STATUS_PATH.exists():
        with open(PARSING_STATUS_PATH, 'w', encoding='utf-8') as f:
            parsing_status_dict = {
                'urls_left': crawler.urls,
                'num_urls_parsed': 0
            }
            json.dump(parsing_status_dict, f)
    with open(PARSING_STATUS_PATH, 'r', encoding='utf-8') as f:
        parsing_status = json.load(f)

    urls = parsing_status['urls_left']
    for article_num, full_url in enumerate(urls, 1):
        parser = Parser(full_url, configuration)
        parser.parse_and_save_file(parsing_status['num_urls_parsed'] + article_num)
        with open(PARSING_STATUS_PATH, 'w', encoding='utf-8') as f:
            parsing_status_dict = {
                'urls_left': urls[article_num - 1:],
                'num_urls_parsed': parsing_status['num_urls_parsed'] + article_num
            }
            json.dump(parsing_status_dict, f)


def creation_of_corpus():
    configuration = Config(path_to_config=SCRAPPER_CONFIG_PATH)
    sentences = []
    source_tags = []
    for tag, url in enumerate(configuration.get_seed_urls()):
        current_directory = get_current_directory(url, ARTICLES_PATH)
        articles_list = list(current_directory.glob('*'))

        num_extracted = 0
        for num_art, article_link in enumerate(articles_list[num_extracted:], 1):
            preprocessor = TextPreprocessor(article_link)
            if not preprocessor.text:
                continue
            preprocessor.delete_unrelated_texts()
            sents = preprocessor.split_sentences()
            sentences.extend(sents)
            source_tags.extend([tag] * len(sents))

    save_exel_dataset(sentences, source_tags, DATASET_PATH)


if __name__ == '__main__':
    collection_of_articles()
    creation_of_corpus()

