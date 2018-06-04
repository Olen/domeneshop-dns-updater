# -*- coding: utf-8 -*-
import requests
import yaml
from bs4 import BeautifulSoup
import re
import dns.resolver

__author__ = 'Olen'

class Domeneshop(object):
    verbose = False
    # @todo Simplify headers
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.8,nb;q=0.6",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://domeneshop.no",
        "Pragma": "no-cache",
        "Referer": "https://domeneshop.no",
        "Upgrade-Insecure-Requests": "1",
    }

    config = {}
    cookies = {}

    ip = ''

    def __init__(self, config=None, verbose=False):
        """
        Instance Domeneshop object
        """

        self.verbose = verbose

        if config == None:
            config = 'domeneshop-dns-updater/config/domains.yml'

        with open(config) as f:
            self.config = yaml.load(f)

    def login(self):
        """
        Login
        """
        data = [
            ('username', self.config['login']),
            ('password', self.config['password']),
        ]

        # Get cookie
        response = requests.get(self.config['domeneshop']['login'])
        self.cookies = dict(response.cookies)

        response = requests.post(
            self.config['domeneshop']['login'],
            data=data,
            headers=self.headers,
            cookies=self.cookies,
        );

        # Check if login was successful
        soup = BeautifulSoup(response.text, 'html.parser')

        logout = soup.findAll('a', href=re.compile('^http.*/logout'))
        if not logout:
            if self.verbose:
                print('Could not log in. Exiting.')
            # @todo Throw exception
            return False

        if self.verbose:
            print('Login successful')

        return True

    def update_record(self, id, domain, txt_record):

        """
        Update single dns record from config
        """

        host = "_acme-challenge" 
        if self.verbose:
            print('UPDATE', host + "." + domain, "IN TXT", txt_record)

        # @todo Throw exception
        if not self.cookies:
            login = self.login()
            if not login:
                return False

        url = '%s?edit=dns&advanced=1&id=%s' % (self.config['domeneshop']['admin'], id)

        response = requests.get(
            url,
            headers=self.headers,
            cookies=self.cookies,
        );

        form = self._get_form(response, host  + "." + domain)

        if not form:
            print('Problem accessing domain page.')
            return

        auth = form.find('input', {'name': 'auth'})['value']
        olddata = form.find('input', {'name': 'olddata'})['value']
        oldtype = form.find('input', {'name': 'oldtype'})['value']

        params = (
            ('id', id),
            ('edit', 'dns'),
            ('advanced', '1'),
        )

        payload = [
            ('auth', auth),
            ('advanced', '1'),
            ('id', id),
            ('edit', 'dns'),
            ('host', host),
            ('oldtype', oldtype),
            ('olddata', olddata),
            ('rrtype', 'TXT'),
            ('ttl', 300),
            ('data', '"' + txt_record + '"'),
            ('modify.x', '7'),
            ('modify.y', '6'),
        ]

        if self.verbose:
            print('Payload for update', payload)

        response = requests.post(
            url,
            params=params,
            data=payload,
            headers=self.headers,
            cookies=self.cookies,
        );
        # print(response.headers)
        # print(response.content)

        # Add check if update was successful with issuing a new request
        response = requests.get(
            url,
            headers=self.headers,
            cookies=self.cookies,
        );

        form = self._get_form(response, host  + "." + domain)

        if form:
            txt_updated = form.find('input', {'name': 'olddata'})['value']
            if txt_updated == '"' + txt_record + '"':
                print('- Updated successfully')
                return True

        print('- Whoops! Updated was not successful!')
        return False


    @staticmethod
    def _get_form(response, host):
        # Fix errors in html
        html = response.text.replace('</td>\n</td>', '</td>')

        soup = BeautifulSoup(html, 'html.parser')
        forms = soup.findAll('form')

        for form in forms:
            rrtype = form.find('input', {'name': 'rrtype'})['value']
            search = '^%s.*' % (host)
            tds = form.findAll('td', text=re.compile(search))
            if tds and rrtype == 'TXT':
                return form

        return False

