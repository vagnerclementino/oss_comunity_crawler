#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy
import csv
import sys
# import ipdb
from w3lib.html import remove_tags
reload(sys)
sys.setdefaultencoding('utf8')


class PythonBTSpyder(scrapy.Spider):

    """Docstring for PythonBTSpyder. """
    # Variávies em overrride
    name = "pythonbt"
    start_urls = []

    XPATH_BASE_USER = '//*[@id="content"]/div[2]/table[3]/tr[#]/td[2]/text()'
    XPATH_BASE_DATE = '//*[@id="content"]/div[2]/table[3]/tr[#]/td[1]/text()'
    XPATH_BASE_ACTION = '//*[@id="content"]/div[2]/table[3]/tr[#]/td[3]/text()'
    # XPATH_BASE_ARGS = '//*[@id="content"]/div[2]/table[3]/tr[#]/th[4]'
    XPATH_BASE_ARGS = '//*[@id="content"]/div[2]/table[3]/tr[#]/td[4]/node()'
    PYTHONBT_URL = 'https://bugs.python.org/issue'
    CSV_FILE_PATH = '../fgrm_user_crawler/inputs/pythonbt-issues.csv'
    LOAD_LIMIT = 100

    def load_bug_id_from_csv(self):
        """TODO: Docstring for load_bug_id_from_csv.
        :returns: TODO

        """
        counter = 0
        with open(self.CSV_FILE_PATH, 'rb') as csv_file:
            pythonbt_reader = csv.reader(csv_file, delimiter=',')
            next(pythonbt_reader)
            for row in pythonbt_reader:
                if counter == self.LOAD_LIMIT:
                    return
                if len(row) >= 2:
                    counter = counter + 1
                    yield row[1]

    def load_start_urls(self):
        """TODO: Docstring for load_start_urls.
        :returns: TODO

        """
        counter = 1
        bug_list = self.load_bug_id_from_csv()
        for bug in bug_list:
            bug_url = self.PYTHONBT_URL + str(bug)
            # print("[" + str(counter) + "]" + bug_url)
            counter = counter + 1
            self.start_urls.append(bug_url)

    def start_requests(self):
        # carregando as urls
        self.load_start_urls()
        # self.start_urls.append('https://bugs.python.org/issue28380')
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # ipdb.set_trace()
        filename = './outputs/pythobt-data.csv'
        index = 3
        row = [None] * 5
        data = list()
        while True:
            xpath_user = self.XPATH_BASE_USER.replace('#', str(index), 1)
            xpath_date = self.XPATH_BASE_DATE.replace('#', str(index), 1)
            xpath_action = self.XPATH_BASE_ACTION.replace('#', str(index), 1)
            xpath_args = self.XPATH_BASE_ARGS.replace('#', str(index), 1)
            user_selector = response.xpath(xpath_user)
            date_selector = response.xpath(xpath_date)
            args_selector = response.xpath(xpath_args)
            action_selector = response.xpath(xpath_action)
            url = response.url
            # buscado a posição inicial onde começa o número do bug
            start_bug_id = url.find('issue') + len('issue')
            bug_id = url[start_bug_id:]
            if len(user_selector) == 1 and len(date_selector) == 1:
                user_name = user_selector.extract_first()
                event_date = date_selector.extract_first()
                action = action_selector.extract_first()
                row[0] = bug_id
                row[1] = event_date
                row[2] = user_name
                row[3] = action
                if action == 'create':
                    row[4] = '-'
                    data.append(list(row))
                elif len(args_selector) >= 1:
                    # extraídos os dados do seletor
                    args_data = args_selector.extract()
                    # transformando a list de argumentos em string
                    args_str = ''.join(args_data)
                    # remove carcater \n da string gerada
                    args_str = args_str.replace('\n', '')
                    # quebrando a string de argumentos em uma lista
                    args_list = args_str.split('<br>')
                    for args in args_list:
                        if args or action == 'create':
                            row[4] = remove_tags(args)
                            data.append(list(row))
                    # ipdb.set_trace()
                else:
                    break
                index = index + 1
            else:
                break
        with open(filename, 'ab') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=';')
            csv_writer.writerows(data)
            del data[:]
        self.log('Everything is gonna be alright')
