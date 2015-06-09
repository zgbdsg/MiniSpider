# -*- coding: utf-8 -*-
# !/usr/bin/env python
################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################

"""
This is the main module
"""
__author__ = 'zhouguobing@baidu.com'
import ConfigParser
import logging
import urllib2
import time
import re
from StringIO import StringIO
import gzip

import chardet
from bs4 import BeautifulSoup

import url
from util import threadpool, log


class MiniSpider():
    def __init__(self, config, seed):
        log.init_log('./log/MiniSpider')

        cp = ConfigParser.ConfigParser()
        cp.readfp(open(config))

        self.conf_dic = dict(cp._sections)
        for key in self.conf_dic:
            self.conf_dic[key] = dict(cp._defaults, **self.conf_dic[key])
            self.conf_dic[key].pop('__name__', None)

        urllib2.socket.setdefaulttimeout(float(self.conf_dic['spider']['crawl_timeout']))
        self.seeds = ["http://pycm.baidu.com:8081/page3.html"]
        # self.seeds = ["http://www.sina.com.cn/"]

        self.urls = []
        self.urlpool = {}
        for i in range(len(self.seeds)):
            u = url.Url(self.seeds[i], "")
            self.urls.append(u)
            self.urlpool[u.link] = 1

        logging.info("init")

    def run(self):
        # self.pool = Pool(processes=8)
        self.pool = threadpool.ThreadPool(int(self.conf_dic['spider']['thread_count']))
        requests = threadpool.makeRequests(self.crawl, self.urls, self.print_result, self.handle_exception)

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

        try:
            page = urllib2.urlopen(url.link)
            if page.info().get('Content-Encoding') == 'gzip':
                buf = StringIO(page.read())
                f = gzip.GzipFile(fileobj=buf)
                chunk = f.read()
            else:
                chunk = page.read()
            # print page.info()
            # print chunk
            result = re.match(self.conf_dic['spider']['target_url'], url.link)
            if not result == None:
                self.savepage(url, chunk)

            if page.info()['Content-Type'] in ["text/html"]:
                self.processpage(chunk, url)

        except urllib2.HTTPError, e:
            print e.code
        except urllib2.URLError, e:
            print e.reason
        else:
            print "pass"

        return url.link

    def processpage(self, chunk, purl):
        encode = chardet.detect(chunk)['encoding']
        # print encode
        if encode in ['ascii', 'utf-8']:
            pass
        elif encode in ['GBK']:
            chunk.decode('gbk', 'ignore').encode('utf-8')
        elif encode in ['GB2312']:
            # print "GB2312"
            chunk.decode('GB2312', 'ignore').encode('utf-8')
        elif encode in ['GB18030']:
            chunk.decode('GB18030', 'ignore').encode('utf-8')

        soup = BeautifulSoup(chunk)
        self.extractlink(soup, purl)

    def extractlink(self, soup, purl):
        hrefs = []
        links1 = soup.findAll("a")
        for link in links1:
            href = link.get('href')
            if href:
                href = href.strip("/")
            # if 'javascript:location.href' in href:
            #     href = href[len("javascript:location.href")+2:-2]
            hrefs.append(href)

        links2 = soup.find_all("img")
        for link in links2:
            href = link.get('src')
            if href:
                hrefs.append(href)

        for href in hrefs:
            # u = url.Url(purl.seed,purl.relpath+"/"+href)
            u = url.Url(purl.link, href)
            if u.depth > int(self.conf_dic['spider']['max_depth']):
                continue
            if u.link not in self.urlpool:
                self.urlpool[u.link] = 1
                req = threadpool.WorkRequest(self.crawl, [u], callback=self.print_result,
                                             exc_callback=self.handle_exception)
                # print(newurl)
                self.pool.putRequest(req)
                print "new url  %s added." % u.link

    def savepage(self, url, chuck):
        name = urllib2.quote(url.link)
        result, number = re.subn(re.compile('["\\/*?<>|]'), "", name)
        f = open("output/" + result, "wb")
        f.write(chuck)
        f.flush()
        f.close()

    def extractrule(self, tag):
        return tag.has_attr('href') or tag.has_attr('src')

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
    ms = MiniSpider("spider.conf", None)
    ms.run()
