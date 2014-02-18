#!/usr/bin/env python
# encoding: utf-8

import os
import sys
from agrb import grab
from agrb import feedfinder
from agrb import feedparser
from html2text.html2text import html2text


def __save_file(path, name, content):
    if not os.path.exists(path):
        os.makedirs(path)
    invalid_chars = '<>:"/\|?* '
    valid_name = "".join(c for c in name if c not in invalid_chars)
    f = path + valid_name
    myfile = open(f, "w")
    if(type(content) == unicode):
        content = content.encode("utf-8")
    myfile.write(content)
    myfile.close()


def find(url):
    '''get article from the url, and return the markdown content.
    '''
    try:
        print url
        result = grab.get_article(url)
        print result["title"].encode("utf-8")
        print "score: " + str(result["score"])
        if(result["article"] is not None):
            html = result["article"]
            path = ("./%s/" % "output")
            name = result["title"]
            #save_file(path, name + ".html", html)
            __save_file(path, name + ".md", html2text(html))
    except Exception as e:
        print e


def finds(url):
    '''find feeds and return all markdown in feeds.
    '''
    feeds = feedfinder.feeds(url)
    if feeds is None:
        print "No feed found."
        return
    print("feeds: %s" % len(feeds))

    for feed in feeds:
        d = feedparser.parse(feed)
        map(find, [entry.link for entry in d.entries])


if __name__ == "__main__":
    args = sys.argv[1:]
    if args is not None:
        finds(args[0])
    else:
        print "need url"
