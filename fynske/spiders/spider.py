import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import FynskeItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class FynskeSpider(scrapy.Spider):
	name = 'fynske'
	start_urls = ['https://www.fynskebank.dk/']

	def parse(self, response):
		articles = response.xpath('//div[@class="news__item"]')
		for article in articles:
			date = article.xpath('.//time/@datetime').get()
			post_links = article.xpath('.//a/@href').get()
			yield response.follow(post_links, self.parse_post,cb_kwargs=dict(date=date))

	def parse_post(self, response, date):

		title = response.xpath('//h1/text()').get()
		content = response.xpath('//p[@class="jumbo__text"]//text()').getall() + response.xpath('//div[@id="main"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=FynskeItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
