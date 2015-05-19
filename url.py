# -*- coding: utf-8 -*-
__author__ = 'zhouguobing'

from urlparse import urlparse

class Url():
    def __init__(self, seed, relativepath):
        link = seed.strip('/')+"/"+relativepath.strip('/')
        obj = urlparse(link.strip("/"))
        self.seed = "%s://%s"%(obj.scheme, obj.netloc)
        # self.seed = obj.scheme+"://"+obj.netloc+":"+obj.port
        self.link = obj.geturl()
        self.path = obj.path
        self.netloc = obj.netloc
        items = self.path.strip("/").split("/")
        self.depth = len(items)
        self.relpath = "/".join(items[0:-1])

if __name__ == "__main__":
    seeds = ["http://pycm.baidu.com:8081/"]

    urls = []
    for i in range(len(seeds)):
        u = Url(seeds[i],"/mirror/mirror/mirror/index.html")
        print u.link
        print u.netloc
        print u.path
        print u.depth
        print u.relpath
        print u.seed
        newu = Url(u.seed,u.relpath+"/"+"page1.html")
        print newu.link
