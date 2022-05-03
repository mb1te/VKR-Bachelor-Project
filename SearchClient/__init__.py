import os
import string
from bs4 import BeautifulSoup
import requests
from html import unescape


class SearchResult:
    """Сниппет из поисковой выдачи"""
    def __init__(self, url, title, description):
        self.url = url
        self.title = title
        self.description = description

class SearchClient:
    """Клиент для поисковой системы"""
    user_agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
         AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
    system = "yandex"

    @classmethod
    def _req(cls, term: str, result_cnt: int) -> requests.Response:
        """Запрос к API SerpRiver

        Args:
            term (str): запрос
            result_cnt (int): количество сниппетов в результате

        Returns:
            requests.Response: ответ от API
        """
        resp = requests.get(
            url="https://serpriver.com/api/search.php",
            headers=cls.user_agent,
            params=dict(
                query=term,
                api_key=os.environ["API_KEY"],
                system=cls.system,
                result_cnt=result_cnt
            ),
        )
        resp.raise_for_status()
        return resp

    @classmethod
    def search(cls, term: str, num_results: int = 100) -> list[SearchResult]:
        """Получение сниппетов для поискового запроса

        Args:
            term (str): запрос
            num_results (int, optional): число сниппетов. По умолчанию 100.

        Returns:
            list[SearchResult]: список сниппетов
        """
        term_lower = term.lower()
        term_lower_trans = term_lower.translate(str.maketrans({key: "" for key in string.punctuation}))

        resp = cls._req(term_lower_trans.replace(" ", "+"), num_results)
        
        try:
            resp = resp.json()
        except Exception as e:
            return cls.search(term, num_results)

        results = []

        if 'json' not in resp.keys() or 'res' not in resp['json'].keys():
            print(f"Trying to reload search results because {resp=}")
            return cls.search(term, num_results)

        for result in resp['json']['res']:
            try:
               results.append(
                   SearchResult(
                        url=result['link'],
                        title=cls.html_to_visible_text(result['title']),
                        description=cls.html_to_visible_text(result['snippet'])
                    )
               )
            except Exception as e:
                print(f"Link not loaded because '{e}'")

        return results

    @staticmethod
    def html_to_visible_text(html: str) -> str:
        """Получение текста из html-кода

        Args:
            html (str): raw html

        Returns:
            str: текст
        """

        soup = BeautifulSoup(html, features="lxml")
        for s in soup(["style", "script", "[document]", "head", "title"]):
            s.extract()

        return unescape(soup.get_text())
