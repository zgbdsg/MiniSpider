# -*- coding: utf-8 -*-
__author__ = 'zhouguobing'
import ConfigParser
import log
import logging
from multiprocessing import Pool

class MiniSpider():

    def __init__(self, config):
        log.init_log('./log/MiniSpider')

        cp = ConfigParser.ConfigParser()
        cp.readfp(open(config))

        self.conf_dic = dict(cp._sections)
        for key in self.conf_dic:
            self.conf_dic[key] = dict(cp._defaults, **self.conf_dic[key])
            self.conf_dic[key].pop('__name__',None)

        logging.info("init")

    def run(self):
        self.pool = Pool(processes=8)

if __name__ == "__main__":
    ms = MiniSpider("spider.conf")
