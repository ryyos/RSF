import os
import requests

from pyquery import PyQuery
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter

from src import Reporters
from src import logger

class Main:
    def __init__(self) -> None:

        self.API = 'https://rsf.org/en/index?year='
        self.__executor = ThreadPoolExecutor(max_workers=10)
        ...

    def ex(self):
        response = requests.get('https://rsf.org/en/index?year=2023')
        html = PyQuery(response.text)

        for year in html.find('select[name="year"] > option'):
            reporter = Reporters()
            self.__executor.submit(reporter.main, self.API+PyQuery(year).attr('value'))
        ...

        self.__executor.shutdown(wait=True)

if __name__ == '__main__':
    if not os.path.exists('data'): os.mkdir('data')
    start = perf_counter()

    logger.info('Scraping Start..')

    main = Main()
    main.ex()

    logger.info('Scraping completed')
    logger.info(f'total scraping time: {perf_counter() - start}')

