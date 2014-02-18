#!/usr/bin/env python
# encoding: utf-8

import os
import sys
import sys
sys.path.append("../myreadchoice")

import grab
import html2text


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
    print url
    result = grab.get_article(url)
    if "error" in result:
        print result["error"]
        return
    print result["title"].encode("utf-8")
    print "score: " + str(result["score"])
    if(result["article"] is not None):
        print type(result["article"])
        html = result["article"]
        path = ("./%s/" % "output")
        name = result["title"]
        __save_file(path, name + ".html", html)
        __save_file(path, name + ".md", html2text(html))
    else:
        print "no article found."


if __name__ == "__main__":
    args = sys.argv[1:]
    if args is not None:
        find(args[0])
    else:
        print "need url"
