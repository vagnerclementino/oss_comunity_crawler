#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy
from scrapy.http import FormRequest
from loginform import fill_login_form
import logging
from scrapy.utils.log import configure_logging
import sys
import requests
import json
import oss_crawler_config as cfg
# import ipdb as pdb
reload(sys)
sys.setdefaultencoding('utf8')


class UserPythonBTItem(scrapy.Item):

    """Docstring for UserPythonBTItem. """
    project = scrapy.Field()
    username = scrapy.Field()
    github_user = scrapy.Field()
    real_name = scrapy.Field()
    user_mail = scrapy.Field()
    github_mail = scrapy.Field()


class LoginUserPythonBtSpider(scrapy.Spider):

    name = "login-user-python-bt"
    is_logged = False
    allowed_domains = ["bugs.python.org"]
    start_urls = ['http://bugs.python.org/user']
    BASE_URL = 'http://bugs.python.org/'
    XPATH_USERNAME = "//table[@class='list']/tr[#]/td[1]/a/text()"
    XPATH_GITHUB = "//table[@class='list']/tr[#]/td[2]/text()"
    XPATH_REALNAME = "//table[@class='list']/tr[#]/td[3]/text()"
    XPATH_USERMAIL = "//table[@class='list']/tr[#]/td[4]/text()"
    XPATH_NEXT_PAGE = "//table[@class='list']/tr[52]/th/table/tr/th[3]/a/@href"
    configure_logging(install_root_handler=False)
    logging.basicConfig(filename='./log/' + name + '-' + 'log.txt',
                        format='%(levelname)s: %(message)s',
                        level=logging.INFO
                        )

    def get_email_by_github(self, github_user):
        """TODO: Docstring for get_email_by_github.

        :github_user: TODO
        :returns: TODO

        """
        GITHUB_API_BASE = 'https://api.github.com/users/'
        headers = {'Authorization': 'token %s' % cfg.github['oauth_token']}

        user_url = GITHUB_API_BASE + github_user
        r = requests.get(user_url, headers=headers)
        if r.ok:
            item = json.loads(r.text)
            return item["email"]
        else:
            return None

    def parse(self, response):
        self.logger.info('O usuário esta logado: ' + str(self.is_logged))
        if not self.is_logged:
            args, url, method = fill_login_form(response.url,
                                                response.body,
                                                cfg.pythonbt['username'],
                                                cfg.pythonbt['password'])
            return FormRequest(url,
                               method=method,
                               formdata=args,
                               callback=self.after_login,
                               dont_filter=False)

    def after_login(self, response):
        if "Invalid login" in response.body:
            self.logger.error("Invalid login")
            return
        else:
            self.is_logged = True
            self.logger.info('Valid login')
            index = 2
            while True:
                self.logger.info("Esperando 1 segundos")
                # delays for 5 seconds
                # time.sleep(1)
                # Recuperando o nome do usuário
                xpath_base = self.XPATH_USERNAME
                xpath = xpath_base.replace('#', str(index), 1)
                user_name_sel = response.xpath(xpath)
                # Recuperando o nome de usuário do github
                xpath_base = self.XPATH_GITHUB
                xpath = xpath_base.replace('#', str(index), 1)
                user_github_sel = response.xpath(xpath)
                # Recuperando o nome real do usuário
                xpath_base = self.XPATH_REALNAME
                xpath = xpath_base.replace('#', str(index), 1)
                user_realname = response.xpath(xpath)
                # Recuperando o e-mail do usuário
                xpath_base = self.XPATH_USERMAIL
                xpath = xpath_base.replace('#', str(index), 1)
                user_mail_sel = response.xpath(xpath)
                # Criando uma instância de um item de usuário
                user_item = UserPythonBTItem()
                if (len(user_name_sel) >= 1):
                    user_item['project'] = 'Python'
                    user_item['username'] = user_name_sel.extract_first()
                    user_item['github_user'] = user_github_sel.extract_first()
                    user_item['real_name'] = user_realname.extract_first()
                    user_item['user_mail'] = user_mail_sel.extract_first()
                    if str(user_item['github_user']) != str('\xa0'):
                        email = self.get_email_by_github(
                                    user_item['github_user']
                                )
                        user_item['github_mail'] = email
                    # self.logger.info(user_item)
                    index = index + 1
                    yield user_item
                else:
                    self.logger.info('Não foi encontrado o nome do usuário')
                    break
            next_page = response.xpath(self.XPATH_NEXT_PAGE).extract_first()
            if next_page:
                next_page_url = self.BASE_URL + next_page
                request = scrapy.Request(url=next_page_url,
                                         callback=self.after_login)
                yield request
            else:
                self.logger.info("Não foi encontrada a próxima página")
