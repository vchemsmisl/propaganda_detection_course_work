import re
import pandas as pd
from pathlib import Path


class TextPreprocessor:

    def __init__(self, text_url):
        self.text = self._open_text_file(text_url)

    @staticmethod
    def _open_text_file(text_url):
        with open(text_url, 'r', encoding='utf-8') as file:
            text = file.read()
        if not text:
            return
        return text

    def delete_unrelated_texts(self):
        self.text = self.text.replace(
            'Больше актуальных видео и подробностей о ситуации в Донбассе смотрите на телеканале «Известия»',
            '')
        self.text = re.sub(r'Учредитель.*«Редакция «Российской газеты»', '', self.text)

    def split_sentences(self):
        sent_pattern = r'((?<=[A-Za-zА-Яа-я0-9]\.\.\.)|(?<=[A-Za-zА-Яа-я0-9]' \
                       r'[A-Za-zА-Яа-я0-9\.!?][\.!?]))\s+(?=[A-ZА-Я0-9])'
        sentences = [sentence.replace('\n', '') for sentence
                     in re.split(sent_pattern, self.text) if len(sentence) > 5]
        return sentences


def save_exel_dataset(sentences: list[str],
                      source_tags: list[int],
                      path_to_dataset: Path) -> None:
    data = {'Sentence': sentences, 'Source tag': source_tags}
    sent_dataframe = pd.DataFrame(data)
    sent_dataframe.to_excel(path_to_dataset,
                            sheet_name='Sentences Dataset',
                            columns=('Sentence', 'Source tag'))
