import requests
from bs4 import BeautifulSoup
import pandas as pd

class DatasetScrapper:
    """Сбор датасета"""

    base_url = "https://baza-otvetov.ru/categories/view/1/"
    last_page = 316 #  последняя страница на сайте

    def get_page(self, page: int) -> list[tuple]:
        """Парсинг одной страницы с вопросами

        Args:
            page (int): номер страницы

        Returns:
            list[tuple]: список из вопросов в виде (вопрос, правильный ответ, ответ 2, ответ 3, ответ 4)
        """
        page_url = (page - 1) * 10
        destination_url = self.base_url

        if page_url > 0:
            destination_url += str(page_url)

        raw_html = requests.get(destination_url).text
        soup = BeautifulSoup(raw_html, features='lxml')

        table = soup.find('table', class_='q-list__table')
        
        dataset = []
        
        for row in table.find_all('tr')[1:]:
            # Не учитываем вопросы без альтернативных вариантов ответа
            if 'Ответы для викторин:' not in row.text:
                continue

            cells = row.find_all('td')

            question = row.find('a').text
            correct_answer = cells[-1].text
            other_answers = (
                row.find('div', class_='q-list__quiz-answers')
                .text
                .replace('Ответы для викторин: ', '')
                .strip()
                .split(', ')
            )

            # Оставим только вопросы с 4 вариантами ответов (это почти вся база)
            if len(other_answers) != 3:
                continue

            dataset.append((question, correct_answer, *other_answers))

        return dataset

    def save_all(self, last_page=None, filename='quiz.csv') -> None:
        """Сбор датасета из нескольких страницы

        Args:
            last_page (int, optional): последняя страница собранного датасета
            filename (str, optional): название файла с датасетом
        """
        if last_page is None:
            last_page = self.last_page

        dataset = []
        for page in range(1, last_page + 1):
            dataset += self.get_page(page)
            print(f'Proccessed {page}/{last_page}')

        df = pd.DataFrame(dataset, columns=['Вопрос', 'Ответ 1', 'Ответ 2', 'Ответ 3', 'Ответ 4'])
        df.to_csv(filename, encoding='utf-8')
