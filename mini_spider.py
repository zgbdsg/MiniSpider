# -*- coding: utf-8 -*-
__author__ = 'zhouguobing'
import ConfigParser
import log
import logging
import threadpool
import urllib2
import time
import chardet
from bs4 import BeautifulSoup

class MiniSpider():

    def __init__(self, config, seed):
        log.init_log('./log/MiniSpider')

        cp = ConfigParser.ConfigParser()
        cp.readfp(open(config))

        self.conf_dic = dict(cp._sections)
        for key in self.conf_dic:
            self.conf_dic[key] = dict(cp._defaults, **self.conf_dic[key])
            self.conf_dic[key].pop('__name__',None)

        urllib2.socket.setdefaulttimeout(float(self.conf_dic['spider']['crawl_timeout']))
        #self.seed = seed
        self.seeds = ["http://pycm.baidu.com:8081"]*1000
        self.urlpool = {}

        relativepath = '/'
        for seed in self.seeds:
            self.urlpool[seed.strip('/')+relativepath] = 1
        logging.info("init")

    def run(self):
        #self.pool = Pool(processes=8)
        self.pool = threadpool.ThreadPool(int(self.conf_dic['spider']['thread_count']))
        requests = threadpool.makeRequests(self.crawl, self.seeds, self.print_result, self.handle_exception)

        for req in requests:
            self.pool.putRequest(req)
            print "Work request #%s added." % req.requestID

        while True:
            try:
                # time.sleep(int(self.conf_dic['spider']['crawl_interval'])*10)
                self.pool.poll()
            except KeyboardInterrupt:
                print "**** Interrupted!"
                break
            except threadpool.NoResultsPending:
                print "**** No pending results."
                break

    def crawl(self, url):
        time.sleep(int(self.conf_dic['spider']['crawl_interval']))
        page = urllib2.urlopen(url)
        chunk = page.read()
        # print page.info().getparam('charset')
        # print chunk
        self.processpage(chunk)
        return True

    def processpage(self, chunk):
        encode = chardet.detect(chunk)['encoding']
        if encode in ['ascii','utf-8']:
            soup = BeautifulSoup(chunk)
            links = soup.findAll("a")
            for link in links:
                url = link.get('href').strip('/')
                if len(url.split('/')) > int(self.conf_dic['spider']['max_depth']):
                    continue

                if 'javascript:location.href' in url:
                    url = url[len("javascript:location.href")+2:-2]

                if url not in self.urlpool.keys():
                    self.urlpool[url] = 1
                    req = threadpool.WorkRequest(self.crawl,)
                    print(url)
            #print(links)
            print 1
        elif encode in ['gbk']:
            print 2

    # this will be called each time a result is available
    def print_result(self, request, result):
        print "**** Result from request #%s: %r" % (request.requestID, result)

    def handle_exception(self, request, exc_info):
        if not isinstance(exc_info, tuple):
            # Something is seriously wrong...
            print request
            print exc_info
            raise SystemExit
        print "**** Exception occured in request #%s: %s" % \
          (request.requestID, exc_info)

if __name__ == "__main__":
    ms = MiniSpider("spider.conf",None)
    ms.run()
