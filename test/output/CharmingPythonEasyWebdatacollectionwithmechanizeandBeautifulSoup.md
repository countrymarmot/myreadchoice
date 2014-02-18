# Charming Python: Easy Web data collection with mechanize and Beautiful Soup

## Connect with David

David is one of our most popular and prolific authors. Browse [all of David's articles and tutorials](http://www.ibm.com/developerworks/views/global/libraryview.jsp?site_id=1&contentarea_by=global&sort_by=Date&sort_order=2&start=1&end=100&topic_by=-1&product_by=-1&type_by=All%20Types&show_abstract=true&search_by=david%20mertz) on developerWorks. Check out [David's profile](https://www.ibm.com/developerworks/mydeveloperworks/profiles/user/DavidMertz) and connect with him, other authors, and fellow readers in My developerWorks.

Writing scripts to interact with Web sites is _possible_ with the basic Python modules, but you don't want to if you don't have to. The modules `urllib` and `urllib2` in Python 2.x, along with the unified `urllib.*` subpackages in Python 3.0, do a passable job of fetching resources at the ends of URLs. However, when you want to do any sort of moderately sophisticated interaction with the contents you find at a Web page, you really need the **mechanize** library (see Resources for a download link).

One of the big difficulties with automating Web scraping or other simulations of user interaction with Web sites is server use of cookies to track session progress. Obviously, cookies are part of HTTP headers and are inherently visible when `urllib` opens resources. Moreover, the standard modules `Cookie` (`http.cookie` in Python 3) and `cookielib` (`http.cookiejar` in Python 3) help in handling those headers at a higher level than raw text processing. Even so, doing this handling at this level is more cumbersome than necessary. The mechanize library takes this handling to a higher level of abstraction and lets your script—or your interactive Python shell—act very much like an actual Web browser.

Python's mechanize is inspired by Perl's `WWW:Mechanize`, which has a similar range of capabilities. Of course, as a long-time Pythonista, I find mechanize more robust, which seems to follow the general pattern of the two languages.

A close friend of mechanize is the equally excellent library **Beautiful Soup** (see Resources for a download link). This is a wonderful "sloppy parser" for the approximately valid HTML you often find in actual Web pages. You do not _need_ to use Beautiful Soup with mechanize, nor vice versa, but more often than not you will want to use the two tools together as you interact with the "actually existing Web."

## A real-life example

I have used mechanize in several programming projects. The most recent was a project to gather a list of names matching some criteria from a popular Web site. This site comes with some search facilities, but not with any official API for performing such searches. While readers might be able to guess more specifically what I was doing, I will change specifics of the code I present to avoid giving too much information on either the scraped site or my client. In general form, code very much like what I present will be common for similar tasks.

* * *

Back to top

## Tools to start with

In the process of actually developing Web scraping/analysis code, I find it invaluable to be able to peek at, poke, and prod the content of Web pages in an interactive way in order to figure out what actually occurs on related Web pages. Usually, these are sets of pages within a site that are either dynamically generated from queries (but thereby having consistent patterns) or are pre-generated following fairly rigid templates.

One valuable way of doing this interactive experimentation is to use mechanize itself within a Python shell, particularly within an enhanced shell like IPython (see Resources for a link). Doing exploration this way, you can request various linked resources, submit forms, maintain or manipulate site cookies, and so on, prior to writing your final script that performs the interaction you want in production.

However, I find that much of my experimental interaction with Web sites is better performed within an actual modern Web browser. Seeing a page conveniently rendered gives a much quicker gestalt of what is going on with a given page or form. The problem is that rendering a page alone only gives half the story, maybe less than half. Having "page source" gets you slightly further. To really understand what is behind a given Web page or a sequence of interactions with a Web server, I find more is needed.

To get at these guts, I usually use the Firebug (see Resources for a link) or Web Developer plug-ins for Firefox (or the built-in optional _Develop_ menu in recent Safari versions, but that's for a different audience). All of these tools let you do things like reveal form fields, show passwords, examine the DOM of a page, peek at or run Javascript, watch Ajax traffic, and more. Comparing the benefits and quirks of these tools is a whole other article, but do familiarize yourself with them if you do any Web-oriented programming.

Whatever specific tool you use to experiment with a Web site you intend to automate interaction with, you will probably spend many more hours figuring out what a site is actually doing than you will writing the amazingly compact mechanize code needed to perform your task.

* * *

Back to top

## The search result scraper

For the purposes of the project I mentioned above, I split my hundred-line script into two functions:

  * Retrieve all the results of interest to me
  * Pull out the information that interests me from those retrieved pages

I organized the script this way as a development convenience; when I started the task, I knew I needed to figure out how to do each of those two things. I had a sense that the information I wanted was on a general collection of pages, but I had not yet examined the specific layout of those pages.

By first retrieving a batch of pages and just saving them to disk, I could come back to the task of pulling out the information I cared about from those saved files. Of course, if your task involves using that retrieved information to formulate new interactions within the same session, you will need to use a slightly different sequence of development steps.

So, first, let's look at my `fetch()` function:

##### Listing 1. Fetching page contents
    
    
    import sys, time, os
    from mechanize import Browser
    
    LOGIN_URL = 'http://www.example.com/login'
    USERNAME = 'DavidMertz'
    PASSWORD = 'TheSpanishInquisition'
    SEARCH_URL = 'http://www.example.com/search?'
    FIXED_QUERY = 'food=spam&' 'utensil=spork&' 'date=the_future&'
    VARIABLE_QUERY = ['actor=%s' % actor for actor in
            ('Graham Chapman',
             'John Cleese',
             'Terry Gilliam',
             'Eric Idle',
             'Terry Jones',
             'Michael Palin')]
    
    def fetch():
        result_no = 0                 # Number the output files
        br = Browser()                # Create a browser
        br.open(LOGIN_URL)            # Open the login page
        br.select_form(name="login")  # Find the login form
        br['username'] = USERNAME     # Set the form values
        br['password'] = PASSWORD
        resp = br.submit()            # Submit the form
    
        # Automatic redirect sometimes fails, follow manually when needed
        if 'Redirecting' in br.title():
            resp = br.follow_link(text_regex='click here')
    
        # Loop through the searches, keeping fixed query parameters
        for actor in in VARIABLE_QUERY:
            # I like to watch what's happening in the console
            print >> sys.stderr, '***', actor
            # Lets do the actual query now
            br.open(SEARCH_URL + FIXED_QUERY + actor)
            # The query actually gives us links to the content pages we like,
            # but there are some other links on the page that we ignore
            nice_links = [l for l in br.links()
                            if 'good_path' in l.url
                            and 'credential' in l.url]
            if not nice_links:        # Maybe the relevant results are empty
                break
            for link in nice_links:
                try:
                    response = br.follow_link(link)
                    # More console reporting on title of followed link page
                    print >> sys.stderr, br.title()
                    # Increment output filenames, open and write the file
                    result_no += 1
                    out = open(result_%04d' % result_no, 'w')
                    print >> out, response.read()
                    out.close()
                # Nothing ever goes perfectly, ignore if we do not get page
                except mechanize._response.httperror_seek_wrapper:
                    print >> sys.stderr, "Response error (probably 404)"
                # Let's not hammer the site too much between fetches
                time.sleep(1)

Having done my interactive exploration of the site of interest, I find that queries I wish to perform have some fixed elements and some variable elements. I just concatenate those together into a big `GET` request and take a look at the "results" page. In turn, that list of results contains links to the resources I actually want. So, I follow those (with a couple of `try`/`except` blocks thrown in, in case something does not work along the way) and save whatever I find on those content pages.

Pretty simple, huh? Mechanize can do more than this, but this short example shows you a broad brush of its capabilities.

* * *

Back to top

## Processing the results

At this point, we are done with mechanize; all that is left is to make some sense of that big bunch of HTML files we saved during the `fetch()` loop. The batch nature of the process lets me separate these cleanly, but obviously in a different program, `fetch()` and `process()` might interact more closely. Beautiful Soup makes the post-processing even easier than the initial fetch.

For this batch task, we want to produce tabular comma-separated value (CSV) data from some bits and pieces we find on those various Web pages we fetched.

##### Listing 2. Making orderly data from odds and ends with Beautiful Soup
    
    
    from glob import glob
    from BeautifulSoup import BeautifulSoup
    
    def process():
        print "!MOVIE,DIRECTOR,KEY_GRIP,THE_MOOSE"
        for fname in glob('result_*'):
            # Put that sloppy HTML into the soup
            soup = BeautifulSoup(open(fname))
    
            # Try to find the fields we want, but default to unknown values
            try:
                movie = soup.findAll('span', {'class':'movie_title'})[1].contents[0]
            except IndexError:
                fname = "UNKNOWN"
    
            try:
                director = soup.findAll('div', {'class':'director'})[1].contents[0]
            except IndexError:
                lname = "UNKNOWN"
    
            try:
                # Maybe multiple grips listed, key one should be in there
                grips = soup.findAll('p', {'id':'grip'})[0]
                grips = " ".join(grips.split())   # Normalize extra spaces
            except IndexError:
                title = "UNKNOWN"
    
            try:
                # Hide some stuff in the HTML <meta> tags
                moose = soup.findAll('meta', {'name':'shibboleth'})[0]['content']
            except IndexError:
                moose = "UNKNOWN"
    
            print '"%s","%s","%s","%s"' % (movie, director, grips, moose)

The code here in `process()` is an impressionistic first look at Beautiful Soup. Readers should read its documentation to find more on the module details, but the general feel is well represented in this snippet. Most soup code consists of some `.findAll()` calls into a page that might be only approximately well-formed HTML. Thrown in here are some DOM-like `.parent`, `nextSibling`, and `previousSibling` attributes. These are akin to the "quirks" mode of Web browsers. What we find in the soup is not _quite_ a parse tree; it is more like a sack full of the vegetables that might go in the soup (to strain a metaphor).

* * *

Back to top

## Conclusion

Old fogies like me, and even some younger readers, will remember the great delight of scripting with TCL Expect (or with its workalikes written in Python and many other languages). Automating interaction with shells, including remote ones such as telnet, ftp, ssh, and the like, is relatively straightforward since _everything is displayed_ in the session. Web interaction is slightly more subtle in that information is divided between headers and bodies, and various dependent resources are often bundled together with `href` links, frames, Ajax, and so on. In principle, however, you _could_ just use a tool like `wget` to retrieve every byte a Web server might provide, and then run the very same style of Expect scripts as with other connection protocols.

In practice, few programmers are quite so committed to old-timey approaches as my suggested `wget` \+ Expect approach. Mechanize still has much of the same familiar and comforting feel as those nice Expect scripts, and is just as easy to write, if not easier. The `Browser()` object commands such as `.select_form()`, `.submit()`, and `.follow_link()` are really just the simplest and most obvious way of saying "look for this and send that" while bundling in all the niceness of sophisticated state and session handling that we would want in a Web automation framework.
