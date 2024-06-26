import re
import pandas as pd
from pathlib import Path


class TextPreprocessor:
    """
    Text preprocessor implementation
    """

    def __init__(self, text_url) -> None:
        """
        Initializes an instance of the TextPreprocessor class
        """
        self.text = self._open_text_file(text_url)

    @staticmethod
    def _open_text_file(text_url) -> str | None:
        """
        Opens .txt file and returns its content
        :param text_url: link to article text
        :return: string with artice text
        """

        with open(text_url, 'r', encoding='utf-8') as file:
            text = file.read()
        if not text:
            return

        return text

    def delete_unrelated_texts(self) -> None:
        """
        Deletes some repeating unnecessary strings
        """

        self.text = self.text.replace(
            'Больше актуальных видео и подробностей о ситуации в Донбассе смотрите на телеканале «Известия»',
            '')
        self.text = re.sub(r'Учредитель.*«Редакция «Российской газеты»', '', self.text)

    def split_sentences(self) -> list[str]:
        """
        Splits text to sentences given a specific rule
        :return: list with sentences as strings
        """

        sent_pattern = r'((?<=[A-Za-zА-Яа-я0-9]\.\.\.)|(?<=[A-Za-zА-Яа-я0-9]' \
                       r'[A-Za-zА-Яа-я0-9\.!?][\.!?]))\s+(?=[A-ZА-Я0-9])'
        sentences = [sentence.replace('\n', '') for sentence
                     in re.split(sent_pattern, self.text) if len(sentence) > 5]

        return sentences


def save_exel_dataset(sentences: list[str],
                      source_tags: list[int],
                      path_to_dataset: Path) -> None:
    """
    Given a list of sentences,
    saves them as an Excel table
    :param sentences: list of sentences
    :param source_tags: list of int tags, marking sentences'
    source edition
    :param path_to_dataset: the path to save the dataset
    """

    data = {'Sentence': sentences, 'Source tag': source_tags}
    sent_dataframe = pd.DataFrame(data)

    sent_dataframe.to_excel(path_to_dataset,
                            sheet_name='Sentences Dataset',
                            columns=('Sentence', 'Source tag'))
