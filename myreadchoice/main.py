#!/usr/bin/env python
# encoding: utf-8

"""`main` top level module."""
#TODO add layout.html, 404.html and about.html reder from layout.html.
#TODO add url validation check.

from flask import Flask, render_template, request
import json
app = Flask(__name__)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

import grab
from html2text import html2text
#from markdown2 import markdown


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/mdcontent')
def mdcontent():
    url = request.args.get("url", "", type=str)
    response = {"text": "not valid url",
                "url": url,
                "score": 0}
    if(url != ""):
        result = grab.get_article(url)
        if(result["article"] is not None):
            html = result["article"]
            html = html2text(html)
        else:
            html = ""
        score = result["score"]
        response.update({"text": html, "score": score})
    return json.dumps(response)


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


if __name__ == "__main__":
    app.run(debug=True)
