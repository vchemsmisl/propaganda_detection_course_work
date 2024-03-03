from constants import (ARTICLES_PATH,
                       SCRAPPER_CONFIG_PATH,
                       DATASET_PATH,
                       get_current_directory)
from scrapper import (Config,
                      Crawler,
                      Parser)
from preprocessor import TextPreprocessor, save_exel_dataset

if __name__ == '__main__':
    # collection of articles
    if not ARTICLES_PATH.exists():
        ARTICLES_PATH.mkdir(parents=True)
    configuration = Config(path_to_config=SCRAPPER_CONFIG_PATH)
    crawler = Crawler(config=configuration)
    crawler.find_articles()

    for article_num, full_url in enumerate(crawler.urls, 1):
        parser = Parser(full_url, configuration)
        article = parser.parse_and_save_file(article_num)

    # creation of corpus
    # sentences = []
    # source_tags = []
    # for tag, url in enumerate(configuration.get_seed_urls()):
    #     current_directory = get_current_directory(url, ARTICLES_PATH)
    #     articles_list = list(current_directory.glob('*'))
    #
    #     for article_link in articles_list:
    #         preprocessor = TextPreprocessor(article_link)
    #         sents = preprocessor.split_sentences()
    #         sentences.extend(sents)
    #         source_tags.extend([tag] * len(sents))
    #
    # save_exel_dataset(sentences, source_tags, DATASET_PATH)
