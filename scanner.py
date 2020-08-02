#!/usr/bin/env python

import requests
import re
import urlparse
from bs4 import BeautifulSoup

class Scanner:
    def __init__(self, url, ignore_links):
        self.session = requests.Session()
        self.target_url = url
        self.target_links = []
        self.links_to_ignore = ignore_links

    def extract_link_from(self, url):
        response = self.session.get(url)
        return re.findall('(?:href=")(.*?)"', response.content)

    def crawl(self, url=None):
        if url == None:
            url = self.target_url
        href_links = self.extract_link_from(url)
        for link in href_links:
            link = urlparse.urljoin(url, link)
            # Find # in href -> it is the same (sub)site
            if "#" in link:
                link = link.split("#")[0]
            # links to list
            if self.target_url in link and link not in self.target_links and link not in self.links_to_ignore:
                self.target_links.append(link)
                print(link)
                self.crawl(link)

    def extract_forms(self, url):
        response = self.session.get(url)
        parsed_html = BeautifulSoup(response.content, "html.parser")
        return parsed_html.findAll("form")

    def submit_form(self, form, value, url):
        action = form.get("action")
        post_url = urlparse.urljoin(url, action)
        method = form.get("method")

        input_list = form.findAll("input")
        post_data = {}
        for input in input_list:
            input_name = input.get("name")
            input_type = input.get("type")  # szukam type na payload
            input_value = input.get("value")
            if input_type == "text":
                input_value = value

            post_data[input_name] = input_value
        # submit form
        if method == "post":
            return self.session.post(post_url, data=post_data)
        return self.session.get(post_url, params=post_data)

    def run_scanner(self):
        for link in self.target_links:
            forms = self.extract_forms(link)
            for form in forms:
                print("[+] Testing form in " + link)
                xss_vul = self.xss_in_form(form, link)
                if xss_vul:
                    print("\n\n[***] XSS discovered in " + link + " in the following form")
                    print(form)
            if "=" in link:
                print("\n\n[+] Testing " + link)
                xss_vul = self.xss_in_link(link)
                if xss_vul:
                    print("[***] Discovered XSS in " + link)

    def xss_in_link(self, url):
        xss_script = "<sCript>alert('XSS')</scriPt>"
        url = url.replace("=", "=" + xss_script)
        response = self.session.get(url)
        return xss_script in response.content

    def xss_in_form(self, form, url):
        xss_script = "<sCript>alert('XSS')</scriPt>"
        response = self.submit_form(form, xss_script, url)
        return xss_script in response.content
