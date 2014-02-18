#!/usr/bin/env python
# encoding: utf-8
"""This module is used to grab the article div from a blog url.
"""
#TODO change urllib2 to request
#TODO lxml instead of bs4 ??
#TODO language detect

import urllib2
from bs4 import BeautifulSoup as BS
from bs4 import Comment
import re
from urlparse import urljoin


RAW1 = r"""^((blog|post|hentry|entry|article)|(blog|post|hentry|entry|article)[-|_](content|text|body))$"""
RAW2 = r"""(comment|meta|footer|footnote)"""
REGEX_POST = re.compile(RAW1,  re.IGNORECASE)
REGEX_COMM = re.compile(RAW2,  re.IGNORECASE)
REGEX_URL = re.compile(r'^(?:http|ftp)s?://'
                       r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
                       r'localhost|'
                       r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
                       r'(?::\d+)?'
                       r'(?:/?|[/?]\S+)$', re.IGNORECASE)
REGEX_LAZYPIC = re.compile(r"(?:ajax|load(?:ing)?)[a-zA-Z]?.gif")


def validURL(url):
    match = REGEX_URL.search(url)
    if match:
        return True
    else:
        return False


def urlopen(url):
    '''open url with urllib2 and return the html content
    '''
    opener = urllib2.build_opener()

    content = ""
    opener.addheaders = [('User-agent',
                          'Mozilla/5.0 (Windows NT 6.1; rv:18.0) \
                          Gecko/20100101 Firefox/18.0')]
    content = opener.open(str(url), data=None, timeout=10).read()
    if content is None or content == "":
        raise Exception("no content.")
    return content


def cleanHTML(soup, url):
    # remove br
    for tag in soup.findAll("br"):
        tag.extract()

    # remove script
    script_tags = soup.findAll("script")
    for tag in script_tags:
        tag.extract()

    # remove comments
    comments = soup.findAll(text=lambda text: isinstance(text, Comment))
    [comment.extract() for comment in comments]

    # join the relative url
    for a in soup.findAll("a"):
        if "href" in a:
            link = urljoin(url, a["href"])
            a["href"] = link
    for img in soup.findAll("img"):
        img_link = None
        if "src" in img.attrs:
            if(not REGEX_LAZYPIC.search(img["src"])):
                img_link = img["src"]
        for key in img.attrs.keys():
            if re.match(r"data-(?:\w)+", key):
                # lazy loader of picture
                img_link = img[key]
        if img_link:
            link = urljoin(url, img_link)
            img["src"] = link
        else:
            img.extract()

    return soup


def get_score(div):
    s = 0

    # check div name
    if(div.name == "article"):
        s += 100    # html5 tag <article>, perfect
    elif(div.name == "div"):
        s += 0
    else:
        s -= 50

    # check div class
    if("class" in div.attrs):
        for c in div["class"]:
            match = REGEX_POST.search(c)
            match2 = REGEX_COMM.search(c)
            if match:
                s += 25
            elif match2:
                s -= 50
            else:
                s -= 10

    if("id" in div.attrs):
        c = div["id"]
        match = REGEX_POST.search(c)
        match2 = REGEX_COMM.search(c)
        if match:
            s += 25
        elif match2:
            s -= 50
        else:
            s -= 10

    for head in div.findAll("h2", "h3"):
        s += 1

    # check text number, 5 character for 1 point
    for p in div.findAll("p"):
        text = p.get_text()
        if(len(text) > 15):
            s += (len(text) - text.count(u" ")) / 5
        else:
            s += 0

    # check code number, 10 character for 1 point
    for pre in div.findAll("pre"):
        text = pre.get_text()
        s += (len(pre.get_text()) - text.count(u" "))

    return s


def get_article(url):
    result = {"url": url}
    if(not validURL(url)):
        result.update({"error": "url is not valid"})
        return result
    html = urlopen(url)
    soup = cleanHTML(BS(html), url)

    # put into <article>
    atl = BS("<article></article>").article
    # get title and append to h1
    head = BS("<h1></h1>").h1
    head.string = soup.title.string
    result.update({"title": soup.title.string})

    atlist = []
    for p in soup.findAll("p"):
        tag = p.parent
        if(tag not in atlist):
            atlist.append(tag)
    #atlist = [p.parent for p in soup.findAll("p")]
    scored = {}
    for tag in atlist:
        scored.update({tag: get_score(tag)})

    # get the highest score
    final_score = 0
    content = ""
    for t, s in scored.items():
        if(s >= final_score):
            final_score = s
            content = t
    if(final_score == 0):
        # all score < 0
        result.update({"error": "nothing valualbe is not found"})
        return result

    ## remove div in content
    #for div in content.findAll("div"):
    #    divs = get_score(div)
    #    if(divs < 20):
    #        div.extract()

    # if article found, return article
    if(content.name == "article"):
        atl = content
    else:
        # if no h1 found, put the title as h1
        if(content.find("h1") is None):
            # if previous_sibling is head, append
            pre1 = content.findPreviousSibling("h1")
            pre2 = content.findPreviousSibling("h2")
            if(pre1):
                atl.append(pre1)
            elif(pre2):
                atl.append(pre2)
            else:
                atl.append(head)
        atl.append(content)
    atl = unicode(atl)

    result.update({"article": atl})
    result.update({"score": final_score})
    return result


if __name__ == "__main__":
    with open('./output/1.htm') as f:
        content = f.read()
    s, a = get_article(content)
    print s
    print a
