#!/usr/bin/env python

import scanner

#have to change for your app
target_url = "app_url_login"
links_to_ignore = ["list_of_links",]
data_dict = {"username": "admin", "password": "password", "Login": "submit"}

vuln_scanner = scanner.Scanner(target_url, links_to_ignore)
vuln_scanner.session.post("app_url_login", data=data_dict)

vuln_scanner.crawl()
vuln_scanner.run_scanner()
