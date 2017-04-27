'''
    What's the goal of this Chapter ?
     - See simple examples of "Policies"
     - Understand a simple "Flow" of a "Crawler"


    This chapter will also have basic examples of "HTTP Requests" and "HTML Parsing", but those will be covered
    in details on further chapters, so, don't bother trying to hard to understand what's happening right now.


    What this code does ?

    This chapter's code is a rude implementation of a "scrapper" of the "CNN" website (http://edition.cnn.com/),
    which will scrape all the links from the "Front Page" of the site, visit them, and count the number of "Image"
    tags if finds. Nothing too fancy or useful, but should be enough to ilustrate a crawler behavior.

    I hope that this fairly simple code is enough to cover most of the "policies" (selection, re-visit and politeness), so as
    how an average crawler behaves.

    There's no sofisticated code here, since the goal of this chapter is to allow you to debug and run the code, being able to
    fully grasp what's happening behind the scenes

    You can find this chapter's documentation on : https://github.com/MarcelloLins/WebCrawling101/wiki/Chapter-1-:-Anatomy-of-a-Crawler
'''

import requests
import time
from lxml import etree
import logging as log

class cnn_crawler:

    def __init__(self):
        """
        Class constructor: Initializes a few constants and attributes of the class
        """
        self.urls = ()
        self.visited_urls = set()
        self.total_links = 0
        self.total_img_tags = 0
        self.homepage_url = 'http://edition.cnn.com';

    """
    Receives an HTML page, parses and saves the links it found
    For parsing the links it simply searches for <a> tags within the HTML
    """
    def parse_links(self, html_page):
        html_tree = etree.HTML(html_page)
        links = html_tree.xpath('//a/@href')

        self.total_links = len(links)

        return links

    """
    Receives an HTML page, parses out all the <img> tags
    it finds, and returns the count
    """
    def count_img_tags(self, html_page):
        html_tree = etree.HTML(html_page)
        links = html_tree.xpath('//img')

        return len(links)

    def print_summary(self):
        log.info('Total Page Links Found: %d' % self.total_links)
        log.info('Valid Links (Selection Policy OK): %d', len(self.urls))
        log.info('Visited Links (Re-visit Policy OK): %d', len(self.visited_urls))
        log.info('Total <img> tags found on all pages: %d', self.total_img_tags)
        log.info('Average <img> tags found per page: %d', (self.total_img_tags / len(self.visited_urls)))

    """
    "Selection Policy" - Is this URL from the same domain ? (CNN)
     This is a very simple example of a logic that tells which urls are useful for this crawler to visit, and which, aren't
     In this specific case, the "Selection Policy" is basically : "Pick only the urls from this domain".
     Eg 1 : "/weather" is a valid URL, because it's a RELATIVE url. Since the full URL is http://edition.cnn.com/weather, it is a valid url, hence, it will be "picked"
     E.g 2 : "http://commercial.cnn.com" is not a valid URL, because the domain is different, hence, it will lead to a different website and should be "ignored" / "skiped"
    """
    def selection_policy(self, links):
        urls = []
        for link in links:
            if len(link) > 10 and '//' not in link and 'http' not in link:
                url = self.homepage_url + link
                urls.append(url)

        return urls

    """
    Simple implemention of a "Re-Visit Policy" that returns "true"
    to urls that were not visited yet, and "false" to
    urls that were visited already.
     
    This implementation states that no URL will be visited twice, meaning
    that this can be considered a "No-Revisit" policy
    """
    def revisit_policy(self, url):
        if url in self.visited_urls:
            return False

        self.visited_urls.add(url)
        return True

    """
    Implementation of a 'Dummy' Politeness-Policy.
    
    This simple method only 'Sleeps' for 0.5 seconds, but in a real scenario,
    you would have to see whether this time is enough to keep the target server
    from being DDOS'd be your processes.
     
    Tip: Start from a 2 seconds sleep, and tune your process as you understand
    the server's behavior.
    """
    def politeness_policy(self):
        time.sleep(0.5)

    """
    Main method responsible for executing a HTTP GET request for the home page of CNN
    and navigate to each of the links of other pages it finds there. For each link it finds it will
    do a GET request for that as well and count the number of images it finds there
    """
    def crawl(self):

        # Retrying the main retry until it works
        while True:
            # Executing request for the homepage of the site
            log.info('Executing Request for Home Page')
            http_response = requests.get(self.homepage_url)

            # Checking Response Status Code (200 Means OK)
            # If we have an OK response, we can break and continue
            if http_response.status_code == requests.codes.ok:
                break

        # Now that we have the "HTML" response, we have to start parsing the Links from this page
        # Don't bother with "how" this is done, by now, it's better for you to understand the "steps", than how they are performed
        # An in depth analysis of "HTML Parsing" will be on a future chapter
        tmp_urls = self.parse_links(http_response.text)

        # Simply Example of how to apply a "Selection Policy" to filter only what you need from your target site
        self.urls = self.selection_policy(tmp_urls)

        log.info('Found a Total of %d unique urls on the home page' % self.total_links)
        log.info('Iterating Over links and Counting <IMG> tags on each of them')

        # Iterating over found url
        for url in self.urls:
            # "Re-Visit Policy" - Should I revisit the same link ?
            # This example of "Re-Visit" policy is an implementation of "No-Revisit" policy, meaning
            # that no url will be visited more than once.
            # Since we are deciding, for each url, whether we should visit it or not, this can be considered a simple
            # "Re-Visit Policy"
            if not self.revisit_policy(url):
                log.warn('Duplicated url found. Skiping it due to revisit-policy violation: %s' % url)
            else:
                # Executing Get Request for page
                http_response = requests.get(url)
                img_tags_count = self.count_img_tags(http_response.text)

                # Incrementing total count of <img> tags
                self.total_img_tags += img_tags_count
                log.info('Found %d <img> tags on url: %s' % (img_tags_count, url))

            # Applying our statically defined politeness policy
            # Remember to respect the sites you are mining data from
            self.politeness_policy()

        self.print_summary()

# Main Function / Entry point of the code
if __name__ == "__main__":
    log.basicConfig(format='%(levelname)s:%(message)s', level=log.INFO)

    crawler = cnn_crawler()
    crawler.crawl()
