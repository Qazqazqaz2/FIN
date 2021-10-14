import requests
import codecs
from bs4 import BeautifulSoup as BS
from random import randint


__all__ = ('work')

headers = [
    {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:47.0) Gecko/20100101 Firefox/47.0',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:53.0) Gecko/20100101 Firefox/53.0',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
    ]

def work():
    jobs = []
    hhh = []
    errors = []
    domain = 'https://www.liveworksheets.com/worksheets/en/English_as_a_Second_Language_(ESL)/Reported_questions/Reported_Speech_Interrogatives_-_Questions_ar588183pm'
    url = domain
    if url:
        resp = requests.get(url, headers=headers[randint(0, 2)])
        if resp.status_code == 200:
            soup = BS(resp.content, 'html.parser')
            print(soup)
            main_div = soup.find('div', attrs={'id': 'capa1'})
            print(main_div)
            if main_div:
                div_lst = main_div.find_all('div', attrs={'class': 'editablediv'})
                print(div_lst)
                for div in div_lst:
                    title = div['title']
                    jobs.append(title)
                    hhh = jobs
            else:
                errors.append({'url': url, 'title': "Div does not exists"})
        else:
            errors.append({'url': url, 'title': "Page do not response"})
        return hhh, jobs, errors




if __name__ == '__main__':
    jobs = work()
    print(str(jobs))
    h = codecs.open('work.txt', 'w', 'utf-8')
    h.write(str(jobs))
    h.close()
