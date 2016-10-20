#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy
from scrapy.http import FormRequest
from loginform import fill_login_form
import logging
from scrapy.utils.log import configure_logging
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class UserPythonBTItem(scrapy.Item):

    """Docstring for UserPythonBTItem. """
    project = scrapy.Field()
    username = scrapy.Field()
    github_user = scrapy.Field()
    real_name = scrapy.Field()
    user_mail = scrapy.Field()


class LoginUserPythonBtSpider(scrapy.Spider):

    name = "login-user-python-bt"
    allowed_domains = ["bugs.python.org"]
    start_urls = ['http://bugs.python.org/user']
    login_user = "vclementino"
    login_pass = "GwC7Mj4FQf8P"
    XPATH_USERNAME = "//table[@class='list']/tr[#]/td[1]/a/text()"
    XPATH_GITHUB = "//table[@class='list']/tr[#]/td[2]/text()"
    XPATH_REALNAME = "//table[@class='list']/tr[#]/td[3]/text()"
    XPATH_USERMAIL = "//table[@class='list']/tr[#]/td[4]/text()"
    configure_logging(install_root_handler=False)
    logging.basicConfig(filename='./log/' + name + '-' + 'log.txt',
                        format='%(levelname)s: %(message)s',
                        level=logging.INFO
                        )

    def parse(self, response):
        args, url, method = fill_login_form(response.url,
                                            response.body,
                                            self.login_user,
                                            self.login_pass)
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
            self.logger.info('Valid login')
            index = 2
            while True:
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
                    # self.logger.info(user_item)
                    index = index + 1
                    yield user_item
                else:
                    self.logger.info('Não foi encontrado o nome do usuário')
                    break
