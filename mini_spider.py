# -*- coding: utf-8 -*-
__author__ = 'zhouguobing'
import ConfigParser
import log
import logging
import threadpool
import urllib2
import time
import random

class MiniSpider():

    def __init__(self, config):
        log.init_log('./log/MiniSpider')

        cp = ConfigParser.ConfigParser()
        cp.readfp(open(config))

        self.conf_dic = dict(cp._sections)
        for key in self.conf_dic:
            self.conf_dic[key] = dict(cp._defaults, **self.conf_dic[key])
            self.conf_dic[key].pop('__name__',None)

        urllib2.socket.setdefaulttimeout(float(self.conf_dic['spider']['crawl_timeout']))
        logging.info("init")

    def run(self):
        #self.pool = Pool(processes=8)
        self.pool = threadpool.ThreadPool(int(self.conf_dic['spider']['thread_count']))
        data = [random.randint(1,10) for i in range(20)]
        requests = threadpool.makeRequests(self.crawl, ["http://www.baidu.com","http://weibo.com"], self.print_result, self.handle_exception)

        for req in requests:
            self.pool.putRequest(req)
            print "Work request #%s added." % req.requestID

        while True:
            try:
                time.sleep(int(self.conf_dic['spider']['crawl_interval']))
                self.pool.poll()
            except KeyboardInterrupt:
                print "**** Interrupted!"
                break
            except threadpool.NoResultsPending:
                print "**** No pending results."
                break

    def crawl(self, url):
        page = urllib2.urlopen(url)
        chunk = page.read()
        # print chunk
        return chunk

    # this will be called each time a result is available
    def print_result(self, request, result):
        print "**** Result from request #%s: %r" % (request.requestID, result)

    def do_something(self,data):
        time.sleep(random.randint(1,5))
        result = round(random.random() * data, 5)
        # just to show off, we throw an exception once in a while
        if result > 5:
            raise RuntimeError("Something extraordinary happened!")
        return result

    def handle_exception(self, request, exc_info):
        if not isinstance(exc_info, tuple):
            # Something is seriously wrong...
            print request
            print exc_info
            raise SystemExit
        print "**** Exception occured in request #%s: %s" % \
          (request.requestID, exc_info)

if __name__ == "__main__":
    ms = MiniSpider("spider.conf")
    ms.run()
