# -*- coding: utf-8 -*-
# !/usr/bin/env python
################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################

"""
This is the url module
"""
__author__ = 'zhouguobing@baidu.com'

from urlparse import urlparse
from urlparse import urljoin

class Url():
    def __init__(self, seed, relativepath):
        #link = seed.strip('/')+"/"+relativepath.strip('/')
        #obj = urlparse(link.strip("/"))
        dest = urljoin(seed.strip("/"),relativepath)
        obj = urlparse(dest)
        self.seed = "%s://%s"%(obj.scheme, obj.netloc)
        # self.seed = obj.scheme+"://"+obj.netloc+":"+obj.port
        self.link = obj.geturl()
        self.path = obj.path
        self.netloc = obj.netloc
        items = self.path.strip("/").split("/")
        self.depth = len(items)
        self.relpath = "/".join(items[0:-1])

if __name__ == "__main__":
    seeds = ["http://pycm.baidu.com:8081/page3.html"]

    urls = []
    for i in range(len(seeds)):
        u = Url(seeds[i],"")
        print u.link
        print u.netloc
        print u.path
        print u.depth
        print u.relpath
        print u.seed
        newu = Url(u.seed,u.relpath+"/"+"page1.html")
        print newu.link
