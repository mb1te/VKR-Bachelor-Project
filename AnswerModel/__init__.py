
from typing import Match
import nltk
import re
import string
from SearchClient import SearchClient

class AnswerModel:
    """Модель для выбора лучшего варианта ответа"""

    search_client = SearchClient()

    def __init__(self):
        nltk.download('stopwords')
        nltk.download('punkt')
        self.stopwords = nltk.corpus.stopwords.words('russian')

    def answer_question(self, question: str, original_choices: list[str]) -> list[str]:
        """Метод для поиска ответа на вопрос

        Args:
            question (str): вопрос
            original_choices (list[str]): варианты ответа

        Returns:
            list[str]: список выбранного варианта ответа каждым методом
        """
        question_lower = " " + question.lower()
        question_lower_trans = question_lower.translate(
            str.maketrans({key: " " for key in string.punctuation})
        )

        reverse = (
            " не " in question_lower_trans or " нет " in question_lower_trans
        )

        print(f"{reverse=}")

        choice_groups = [
            [
                choice.translate(
                    str.maketrans({key: None for key in string.punctuation})
                ),
                choice.translate(
                    str.maketrans({key: " " for key in string.punctuation})
                ),
            ]
            for choice in original_choices
        ]
        choices = sum(choice_groups, [])

        question_keywords = self.find_keywords(question)
        
        links = list(self.search_client.search(" ".join(question_keywords)))
        link_texts = list(map(lambda item: item.description, links))
        link_texts = [
            link_text.lower().translate(
                str.maketrans({key: " " for key in string.punctuation})
            )
            for link_text in link_texts
        ]

        answers = []
        for search_method in (self._method1, self._method2):
            answer = search_method(link_texts, choices, choice_groups, reverse)

            appended = False
            for ind in range(len(choice_groups)):
                if answer in choice_groups[ind]:
                    answers.append(original_choices[ind])
                    appended = True
                    break

            if not appended:
                answers.append('')

        return answers

    def _method1(self, texts: list[str], answers: list[str], answer_groups: list[list[str]], reverse: bool) -> str:
        """Метод 1: Поиск точных совпадений вариантов ответа среди текстов сниппетов из поиска

        Args:
            texts (list[str]): тексты сниппетов
            answers (list[str]): ответы
            answer_groups (list[list[str]]): группы ответов
            reverse (bool): нужно ли инвертировать значения (для вопросов с 'не')

        Returns:
            str: выбранный вариант ответа
        """
        counts = {answer: 0 for answer in answers}
        for text in texts:
            for answer in answers:
                counts[answer] += text.count(f" {answer.lower()} ")

        return self.__get_best_answer(counts, answer_groups, reverse)

    def _method2(self, texts: list[str], answers: list[str], answer_groups: list[list[str]], reverse: bool) -> str:
        """Метод 2: Поиск точных совпадений ключевых слов вариантов ответа среди текстов сниппетов из поиска

        Args:
            texts (list[str]): тексты сниппетов
            answers (list[str]): ответы
            answer_groups (list[list[str]]): группы ответов
            reverse (bool): нужно ли инвертировать значения (для вопросов с 'не')

        Returns:
            str: выбранный вариант ответа
        """
        counts = {answer: 0 for answer in answers}
        for text in texts:
            for answer in answers:
                for keyword in self.find_keywords(answer, sentences=False):
                    counts[answer] += text.count(f" {keyword.lower()} ")

        return self.__get_best_answer(counts, answer_groups, reverse)

    def find_keywords(self, text: str, sentences: bool = True) -> list[str]:
        """Поиск ключевых слов текста

        Args:
            text (str): текст
            sentences (bool, optional): нужно ли токенизировать предложения. По умолчанию True.

        Returns:
            list[str]: список ключевых слов
        """
        keyword_indices = {}

        #  токенизация предложений
        if sentences:
            sent_tokenized = nltk.tokenize.sent_tokenize(text)
            text = " ".join(
                sentence[0].lower() + sentence[1:] for sentence in sent_tokenized
            )

        text = text.translate(
            str.maketrans({key: None for key in set(string.punctuation) - {'"', "'"}})
        )

        def process_match(match: Match[str]) -> str:
            """Замена вхождения пробелами

            Args:
                match (Match[str]): вхождение

            Returns:
                str: пробелы
            """
            keyword_indices[match[1]] = match.start()
            return " " * len(match[0])

        text = re.sub('"([^"]*)"', process_match, text)

        for m in re.finditer(r"\S+", text):
            if m[0] not in self.stopwords:
                keyword_indices[m[0]] = m.start()

        keywords = list(sorted(keyword_indices, key=keyword_indices.get))
        return keywords

    @staticmethod
    def __get_best_answer(all_scores: dict, choice_groups: list[list[str]], reverse: bool = False) -> str:
        """Получение ответа на основе подсчитанного числа вхождений

        Args:
            all_scores (dict): число вхождений по каждому варианту ответа
            choice_groups (list[list[str]]): группы ответов
            reverse (bool, optional): нужно ли инвертировать значения (для вопросов с 'не')

        Returns:
            str: выбраный вариант овтета
        """

        scores = {
            choices[0]: sum(all_scores[choice] for choice in choices)
            for choices in choice_groups
        }

        print(scores)

        best_value = min(scores.values()) if reverse else max(scores.values())

        if  list(scores.values()).count(best_value) == 1:
            return min(scores, key=scores.get) if reverse else max(scores, key=scores.get)
        else:
            return ""
