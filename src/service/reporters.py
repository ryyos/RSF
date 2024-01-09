import os
import requests

from APIRetrys import ApiRetry
from pyquery import PyQuery
from time import time
from datetime import datetime
from icecream import ic
from tqdm import tqdm

from src.utils.parser import Parser
from src.utils.fileIO import File
from src.utils.logs import logger
from src.utils.corrector import vname

requests = ApiRetry(show_logs=False, retry_interval=10)
class Reporters:
    def __init__(self) -> None:

        self.__parser = Parser()
        self.__file = File()

        self.API = 'https://rsf.org/en/country/'
        self.MAIN_DOMAIN = 'rsf.org'

        ...


    def __extract_data(self, url: str) -> dict:
        response = requests.get(url)
        html = PyQuery(response.text)

        contents = []
        for index, content in enumerate(html.find('div.field.field--name-field-contenu-editorial.field--type-entity-reference-revisions.field--label-hidden.field__items > div')):

            if index % 2 == 0:
                contents.append(
                    {
                        "sub_title": PyQuery(content).text()
                    }
                )
            else:
                contents[len(contents)-1].update({
                    "sub_description":PyQuery(content).text()
                    })


        article = {
            "region": html.find('div.text-wrapper > a').text(),
            "descriptions": html.find('div.clearfix.text-formatted.field.field--name-field-chapo.field--type-text-long.field--label-hidden.field__item p').text(),
            "contents": contents,
            "datas": {
                PyQuery(year).attr('class'): {
                    "year": int(PyQuery(self.__parser.ex(html=html, selector='div.popin-classement.preview-pays  > div > div:first-child')[index]).text().split(' ')[-1]),
                    "score_global": float(self.__parser.ex(html=year, selector='div.score.current').text().split(' : ')[-1]),
                    "rank_global": self.__parser.ex(html=year, selector='div.position').text(),
                    "indicators" : [{
                        "title": self.__parser.ex(html=indicator, selector='div.indicateur-title').text(),
                        "rank": int(self.__parser.ex(html=indicator, selector='div.indicateur-rank').text()),
                        "score": float(self.__parser.ex(html=indicator, selector='div.indicateur-score').text())
                    }for indicator in html.find('div.indicateurs-wrapper > div')] 
                } for index, year in enumerate(html.find('div.popin-classement.preview-pays  > div'))
            }
            
        }

        return article
        ...


    def main(self, url: str):
        response = requests.get(url)
        html = PyQuery(response.text)
        
        countrys = html.find(selector='div.country-list > div')

        for country in tqdm(countrys,
                            ascii=True, 
                            smoothing=0.1,
                            desc=f'YEAR: {int(url.split("=")[-1])}',
                            total=len(countrys)):

            results = {
                "crawling_time": str(datetime.now()),
                "crawling_time_epoch": int(time()),
                "domain": self.MAIN_DOMAIN,
                "url": url,
                "country": PyQuery(country).attr('data-pays-name'),
                "year": int(url.split('=')[-1]),
                "article": self.__extract_data(url=self.API+PyQuery(country).attr('data-pays-name'))
            }


            self.__file.write_json(
                path=f'data/{vname(results["country"])}_{results["year"]}.json', 
                content=results)
        ...

