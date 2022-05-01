from bs4 import BeautifulSoup
from requests import get


class SearchResult:
    def __init__(self, url, title, description):
        self.url = url
        self.title = title
        self.description = description

class SearchClient:
    user_agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
         AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

    @classmethod
    def _req(cls, term, results, start):
        resp = get(
            url="https://www.google.com/search",
            headers=cls.user_agent,
            params=dict(
                q = term,
                num = results + 2,
                hl = "ru",
                start = start,
            ),
        )
        resp.raise_for_status()
        return resp

    @classmethod
    def search(term, num_results=10):
        escaped_term = term.replace(' ', '+')
        
        start = 0
        while start < num_results:
            resp = _req(escaped_term, num_results-start, start,)

            soup = BeautifulSoup(resp.text, 'html.parser')
            result_block = soup.find_all('div', attrs={'class': 'g'})
            for result in result_block:
                link = result.find('a', href=True)
                title = result.find('h3')
                description_box = result.find('div', {'style': '-webkit-line-clamp:2'})
                if description_box:
                    description = description_box.find('span')
                    if link and title and description:
                        start += 1
                        yield SearchResult(link['href'], title.text, description.text)
