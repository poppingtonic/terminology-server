import os
from operator import delitem
import unittest
import requests
from simplejson import loads
from selenium import webdriver


class APIRegressionTest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.api_root_endpoint = os.getenv('API_ROOT_ENDPOINT', '')

    def test_all_endpoints(self):
        driver = self.driver
        root_api = requests.get(self.api_root_endpoint+'?format=json')
        urls_dict = loads(root_api.text)
        delitem(urls_dict, 'adjacency_list')
        urls = urls_dict.values()
        for url in urls:
            api_format_url = url.split('?')[0]
            driver.get(api_format_url)
            assert "HTTP 200 OK" in driver.page_source
            list_view_data = loads(requests.get(url).text)
            if type(list_view_data) == dict:
                if 'results' in list_view_data.keys():
                    assert type(list_view_data['results']) == list

                    try:
                        first_result = list_view_data['results'][0]
                    except IndexError:
                        pass

                    try:
                        first_result_url = first_result['url'].split('?')[0]
                        driver.get(first_result_url)
                    except KeyError:
                        pass

                    assert "HTTP 200 OK" in driver.page_source

    def tearDown(self):
        self.driver.close()


if __name__ == "__main__":
    unittest.main()
