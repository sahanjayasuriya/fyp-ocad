import http.cookiejar
import time
import urllib.request
import uuid
from os import path

import requests
import bs4


class FacebookScraper:

    def __init__(self, app):
        self.storage = app.config["storage"]
        self.db = app.db
        self.m_facebook_url = "https://m.facebook.com"
        self.mbasic_facebook_url = "https://mbasic.facebook.com"
        self.login_url = "/login.php"
        self.photos_url = "/photos"
        self.authentication_url = self.m_facebook_url + self.login_url
        self.show_more_text = "show more"
        self.full_size_image_text = "view full size"

    def keep_crawling(self, all_anchors):
        result = False
        for i in all_anchors:
            if i.text.lower() == self.show_more_text:
                result = True
        return result

    def save_image(self, image_url, num):
        save_path = path.join(self.storage, 'library/')
        save_file_name = str(uuid.uuid4()) + '-' + str(num) + '.jpg'
        saved_time = int(time.time())

        if self.is_new_entry(image_url):
            urllib.request.urlretrieve(image_url, save_path + save_file_name)
            record_id = self.db.insert('INSERT INTO image_library (filename, website, url, saved) VALUES (?, ?, ?, ?)',
                                       [save_file_name, 'Facebook', image_url, saved_time])
            if record_id:
                return True
            else:
                return False
        else:
            return False

    def is_new_entry(self, image_url):
        c = self.db.select('SELECT COUNT(*) FROM image_library WHERE url = ?', [image_url])
        return c.fetchone()[0] == 0

    def crawl(self, input_url):
        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        urllib.request.install_opener(opener)

        payload = {
            'email': 'sahan.2015568@iit.ac.lk',
            'pass': 'Udara@2020',
        }
        data = urllib.parse.urlencode(payload).encode('utf-8')
        req = urllib.request.Request(self.authentication_url, data)
        resp = urllib.request.urlopen(req)
        contents = resp.read()
        print(contents)

        url = self.m_facebook_url + input_url
        photos_url = input_url + self.photos_url
        photos_url_char_length = len(photos_url)

        url_list = []
        continue_crawling = True
        while continue_crawling:
            data = requests.get(url, cookies=cj)
            soup = bs4.BeautifulSoup(data.text, 'html.parser')
            continue_crawling = self.keep_crawling(soup.find_all('a', href=True))
            for i in soup.find_all('a', href=True):
                if i['href'][0:photos_url_char_length] == photos_url:
                    if i['href'] not in url_list:
                        url_list.append(i['href'])
                if i.text.lower() == self.show_more_text:
                    url = self.mbasic_facebook_url + i['href']

        photo_list = []
        index = 0
        saved_record_count = 0
        for url in url_list:
            url = self.mbasic_facebook_url + url
            data = requests.get(url, cookies=cj)
            soup = bs4.BeautifulSoup(data.text, 'html.parser')
            for i in soup.find_all('a', href=True):

                if i.text.lower() == self.full_size_image_text:
                    if i['href'] not in photo_list:
                        photo_list.append(i['href'])
                        is_saved = self.save_image(i['href'], index)
                        index += 1
                        if is_saved:
                            saved_record_count += 1

        return saved_record_count
