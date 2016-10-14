#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy
import csv
import sys
import logging
from scrapy.utils.log import configure_logging
# import ipdb
from w3lib.html import remove_tags
reload(sys)
sys.setdefaultencoding('utf8')


class PythonBTBugHistory(scrapy.Item):

    """Docstring for PythonBTBugHistory. """
    bug_id = scrapy.Field()
    action_date = scrapy.Field()
    action_user = scrapy.Field()
    action_desc = scrapy.Field()
    action_arg = scrapy.Field()


class PythonBTSpyder(scrapy.Spider):

    """Docstring for PythonBTSpyder. """
    # Variávies em overrride
    name = "pythonbt"
    start_urls = []
    XPATH_BASE_USER = '//*[@id="content"]/div[2]/table[3]/tr[#]/td[2]/text()'
    XPATH_BASE_DATE = '//*[@id="content"]/div[2]/table[3]/tr[#]/td[1]/text()'
    XPATH_BASE_ACTION = '//*[@id="content"]/div[2]/table[3]/tr[#]/td[3]/text()'
    XPATH_BASE_ARGS = '//*[@id="content"]/div[2]/table[3]/tr[#]/td[4]/node()'
    PYTHONBT_URL = 'https://bugs.python.org/issue'
    CSV_FILE_PATH = '../fgrm_user_crawler/inputs/pythonbt-issues.csv'
    LOAD_LIMIT = -1
    configure_logging(install_root_handler=False)
    logging.basicConfig(filename='./log/' + name + '-' + 'log.txt',
                        format='%(levelname)s: %(message)s',
                        level=logging.INFO
                        )

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
        index = 3
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
            # coletando o número o bug
            bug_id = url[start_bug_id:]
            if len(user_selector) == 1 and len(date_selector) == 1:
                bug_history_item = PythonBTBugHistory()
                user_name = user_selector.extract_first()
                event_date = date_selector.extract_first()
                event_date = str(event_date).replace('\xc2\xa0', ' ')
                action = action_selector.extract_first()
                if action == 'create':
                    bug_history_item["bug_id"] = bug_id
                    bug_history_item["action_date"] = event_date
                    bug_history_item["action_user"] = user_name
                    bug_history_item["action_desc"] = action
                    bug_history_item["action_arg"] = '-'
                    yield bug_history_item
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
                        if args:
                            bug_history_item["bug_id"] = bug_id
                            bug_history_item["action_date"] = event_date
                            bug_history_item["action_user"] = user_name
                            bug_history_item["action_desc"] = action
                            bug_history_item["action_arg"] = remove_tags(args)
                            yield bug_history_item
                    # ipdb.set_trace()
                else:
                    break
                index = index + 1
            else:
                break
        self.logger.info('Fim da recuperação para a issue {0}'.format(bug_id))
