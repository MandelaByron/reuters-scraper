import scrapy
from inline_requests import inline_requests
import json
import re
from urllib.parse import urlencode
class NewsCrawlerSpider(scrapy.Spider):
    name = "news_crawler"
    allowed_domains = ["www.reuters.com","reuters.com",'api.scraperapi.com']
    #start_urls = ["https://reauters.com"]
    url = 'https://www.reuters.com/pf/api/v3/content/fetch/articles-by-section-alias-or-id-v1'
    base_url = 'https://www.reuters.com'
    
    run = True
    
    def clean_text(self,text):
        # Remove special characters, numbers, and extra spaces
        cleaned_text = re.sub(r'[^a-zA-Z.,\'"\s]', '', text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        return cleaned_text
    
    def start_requests(self):
        url = 'https://www.reuters.com/pf/api/v3/content/fetch/articles-by-section-alias-or-id-v1'

        headers = {
            "authority": "www.reuters.com",
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.6",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "referer": "https://www.reuters.com/sports/soccer/",
            "sec-ch-ua": "\"Not A(Brand\";v=\"99\", \"Brave\";v=\"121\", \"Chromium\";v=\"121\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-model": "",
            "sec-ch-ua-platform": "Linux",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        }

        cookies = {
            "cleared-onetrust-cookies": "Thu, 17 Feb 2022 19:17:07 GMT",
            "_gcl_au": "1.1.1136596949.1706723800",
            # Add other necessary cookies here
        }

        offset = 0
        while self.run:
            query_params = {
                "query": "{\"arc-site\":\"reuters\",\"called_from_a_component\":true,\"fetch_type\":\"collection\",\"id\":\"/sports/soccer/\",\"offset\":" + str(offset) + ",\"section_id\":\"/sports/soccer/\",\"size\":9,\"uri\":\"/sports/soccer/\",\"website\":\"reuters\"}",
                "d": "174",
                "_website": "reuters"
            }
            full_url = f"{url}?{'&'.join([f'{key}={value}' for key, value in query_params.items()])}"
            
            ar_payload = { 'api_key': '14ce6a05fd80c316f5ebf04800c0aeee', 'url': full_url } 

            scraper_url = 'https://api.scraperapi.com/?'
        
            en_full = scraper_url + urlencode(ar_payload)
          
            yield scrapy.Request(
                en_full,
                method='GET',
                headers=headers,
                callback=self.parse,
                cookies=cookies,
                #body=json.loads(query_params),
                meta={'offset': offset}
            )

            offset += 10
    @inline_requests
    def parse(self, response):
        data = json.loads(response.body)
        
        # Check if response is valid, if not, stop further requests
        if not self.is_valid_response(data):
            self.run = False
            return
        
        for article in data["result"]['articles']:
            article_url = article['canonical_url']
            article_id = article['id']
            news_page = self.base_url + article_url
            payload = { 'api_key': '14ce6a05fd80c316f5ebf04800c0aeee', 'url': news_page } 

            scraper_url = 'https://api.scraperapi.com/?'
            full = scraper_url + urlencode(payload)
            article_page_resp = yield scrapy.Request(full)
            article_page_data = article_page_resp.xpath('//div[@class="article-body__content__17Yit"]/p[contains(@class,"paragraph")]/text()').getall()
            article_body = " ".join(article_page_data)
            clean_text = self.clean_text(article_body)
            
            headline = article['basic_headline']
            description = article['description']
            publish_time = article['published_time']
            update_time = article['updated_time']
            try:
                thumbnail_url = article['thumbnail']
                thumbnail_240 = article['thumbnail']['renditions']['square']['240w']
                thumbnail_480 = article['thumbnail']['renditions']['square']['480w']
                thumbnail_960 = article['thumbnail']['renditions']['square']['960w']
                thumbnail_1080 = article['thumbnail']['renditions']['square']['1080w']
            except KeyError:
                thumbnail_url = None
                thumbnail_240 = None
                thumbnail_480 = None
                thumbnail_960 = None
                thumbnail_1080 = None
            source = "Reuters"
            items = {
                "id":article_id,
                "url": article_url,
                "article_body":clean_text,
                "base_headline":headline,
                "description":description,
                "publish_time":publish_time,
                "update_time":update_time,
                "thumbnail_url":thumbnail_url,
                "thumbnail_240":thumbnail_240,
                "thumbnail_480":thumbnail_480,
                "thumbnail_960":thumbnail_960,
                "thumbnail_1080":thumbnail_1080,
                "source":source
            }
            
            yield items
        # Process the response data here



        # Continue to the next offset
        next_offset = response.meta.get('offset') + 10
        query_params = {
            "query": "{\"arc-site\":\"reuters\",\"called_from_a_component\":true,\"fetch_type\":\"collection\",\"id\":\"/sports/soccer/\",\"offset\":" + str(next_offset) + ",\"section_id\":\"/sports/soccer/\",\"size\":9,\"uri\":\"/sports/soccer/\",\"website\":\"reuters\"}",
            "d": "168",
            "_website": "reuters"
        }
        full_url = f"{self.url}?{'&'.join([f'{key}={value}' for key, value in query_params.items()])}"
        #print(full_url)
        yield scrapy.Request(
            full_url,
            method='GET',
            headers=response.request.headers,
            callback=self.parse,
            #body=json.dumps(query_params),
            meta={'offset': next_offset}
        )

    def is_valid_response(self, data):
        # Implement your logic to check if the response is valid or invalid here
        # Return True if it's a valid response, False otherwise
        # You can check for certain keys or values in the response data to determine validity
        # For example:
        if data['result']['pagination']['size'] == 0:
            return False
        else:
            return True
        

#{"arc-site":"reuters","called_from_a_component":true,"fetch_type":"collection","id":"/sports/soccer/","offset":20,"section_id":"/sports/soccer/","size":9,"uri":"/sports/soccer/","website":"reuters"}

#{"arc-site":"reuters","called_from_a_component":true,"fetch_type":"collection","id":"/sports/soccer/","offset":200,"section_id":"/sports/soccer/","size":9,"uri":"/sports/soccer/","website":"reuters"}


