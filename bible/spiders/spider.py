import json
import scrapy

class BibleSpider(scrapy.Spider):
    # NVI: 129 ARA: 1608

    name = 'bible'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bible_id = 129
        self.base_url = f'https://events.bible.com/api/bible/'\
                        f'chapter/3.1?id={self.bible_id}&reference='
        self.start_urls = [
            f'{self.base_url}GEN.1'
        ]

    def parse(self, response):
        data = json.loads(response.body)
        text = data['content']

        html = scrapy.http.HtmlResponse(
            response.url,
            body=text,
            encoding='utf-8'
        )

        if 'verses' not in response.meta:
            verses = {}
        else:
            verses = response.meta['verses']


        book = data['reference']['human'].split(" ")
        book.pop(-1)
        book = " ".join(book)
        chapter = data['reference']['usfm'][0].split(".")[1]

        next_chapter = data['next']
        if next_chapter is not None:
            next_chapter = next_chapter['usfm'][0]

        for verse in html.css(".verse"):
            number = verse.xpath('@data-usfm').extract_first().split(".")[-1]
            text = verse.css('.content::text').extract()

            if book not in verses:
                verses[book] = {}

            if chapter not in verses[book]:
                verses[book][chapter] = {}

            if number not in verses[book][chapter]:
                verses[book][chapter][number] = ''

            text.extend([' ']) # adding space after the end of the sentence
            texto = ''.join(text)
            if len(texto.strip()) > 0:
                # excluding texts that only contains spaces
                verses[book][chapter][number] += texto

        if next_chapter is None:
            yield verses
        else:
            yield scrapy.Request(
                f"{self.base_url}{next_chapter}",
                callback=self.parse,
                meta={'verses': verses}
            )
