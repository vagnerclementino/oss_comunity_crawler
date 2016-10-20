#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy
import csv
import sys
import logging
from scrapy.utils.log import configure_logging
# import ipdb
# from w3lib.html import remove_tags
reload(sys)
sys.setdefaultencoding('utf8')


class EclipseBTItem(scrapy.Item):

    """Docstring for EclipseBTItem. """
    bug_id = scrapy.Field()
    who = scrapy.Field()
    when = scrapy.Field()
    what = scrapy.Field()
    removed = scrapy.Field()
    added = scrapy.Field()


class EclipseBTScrapy(scrapy.Spider):

    """Docstring for EclipseBTScrapy. """
    # Variávies em overrride
    name = "eclipsebt"
    start_urls = []
    XPATH_BASE_ROW = '//*[@id="bugzilla-body"]/table/tr[#]/td/text()'
    PYTHONBT_URL = 'https://bugs.eclipse.org/bugs/show_activity.cgi?id='
    LOAD_LIMIT = -1
    CSV_FILE_PATH = '../fgrm_user_crawler/inputs/eclipsebt-issues.csv'
    configure_logging(install_root_handler=False)
    logging.basicConfig(filename='./log/' + name + '-' + 'log.txt',
                        format='%(levelname)s: %(message)s',
                        level=logging.INFO
                        )

    last_who = None
    last_when = None

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
                    yield row[0]

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
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # ipdb.set_trace()
        index = 2
        url = response.url
        # buscado a posição inicial onde começa o número do bug
        start_bug_id = url.find('id=') + len('id=')
        # coletando o número o bug
        bug_id = url[start_bug_id:]
        who = None
        when = None
        while True:
            # Recuperando o valor 'who' da página
            xpath_row = self.XPATH_BASE_ROW.replace('#', str(index), 1)
            row_selector = response.xpath(xpath_row)
            if len(row_selector) == 5:

                eclipse_history_item = EclipseBTItem()
                eclipse_history_item["bug_id"] = bug_id
                who = str(row_selector[0].extract()).strip()
                when = str(row_selector[1].extract()).strip()
                what = str(row_selector[2].extract()).strip()
                removed = str(row_selector[3].extract()).strip()
                added = str(row_selector[4].extract()).strip()
                eclipse_history_item['who'] = who
                eclipse_history_item['when'] = when
                eclipse_history_item['what'] = what
                eclipse_history_item['removed'] = removed
                eclipse_history_item['added'] = added
                if self.last_when is not when:
                    self.last_when = when
                if self.last_who is not who:
                    self.last_who = who
            elif len(row_selector) == 3:
                eclipse_history_item = EclipseBTItem()
                eclipse_history_item["bug_id"] = bug_id
                what = str(row_selector[0].extract()).strip()
                removed = str(row_selector[1].extract()).strip()
                added = str(row_selector[2].extract()).strip()
                eclipse_history_item['who'] = self.last_who
                eclipse_history_item['when'] = self.last_when
                eclipse_history_item['what'] = what
                eclipse_history_item['removed'] = removed
                eclipse_history_item['added'] = added
            else:
                break
            index = index + 1
            yield eclipse_history_item
        self.logger.info('Fim da recuperação para a issue {0}'.format(bug_id))
