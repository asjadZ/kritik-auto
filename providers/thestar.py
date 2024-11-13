import re
from webbrowser import Error

import requests
from bs4 import BeautifulSoup

from helpers.image import save_image_from_url, resize_image
from helpers.url import get_hostname
from providers.provider import Provider, ProviderData


class TheStar(Provider):
    def __init__(self, url):
        super().__init__(url)

        self.fetch_data()

    def fetch_data(self):

        r = requests.get(self.url)
        s = BeautifulSoup(r.content, 'html.parser')


        title = s.select_one('.headline > h1').text.strip()
        author = f'<p>By <a href="{get_hostname(self.url)}">The Star</a></p>'

        to_removed_elems = s.select("#story-body > .sasStoryRectPos, #story-body > .inlineAd")
        for elem in to_removed_elems:
            if elem.decomposed:
                continue
            elem.decompose()

        articles = s.select('#story-body > p')

        paths = self.url.split('/')
        sources = f'<p><strong>Source: </strong><a href="{self.url}">{paths[-1]}</a></p>'

        article_string = '\n'.join(map(lambda x: str(x), articles))
        contents = \
f"""{author}
{article_string}
&nbsp;
{sources}
"""

        image_base = 'https://apicms.thestar.com.my/'
        image_path_regex = r'"image_path":"(.*)","media_type"'
        image_script = s.select_one('.story-image > script').text

        path_match = re.search(image_path_regex, image_script)

        if path_match:
            image_path = path_match.group(1).replace('\\', '')
        else:
            raise Error("Failed to get article image, please do this article manually.!")

        image_src = image_base + image_path
        saved_image = save_image_from_url(image_src)
        resized_image = resize_image(saved_image)

        tags = s.select('p.tags > a')
        tag_texts = ','.join(map(lambda tag: tag.text, tags))


        self.data = ProviderData(
            title=title,
            excerpt=articles[0].text,
            content=contents,
            image=resized_image,
            tags=tag_texts
        )

if __name__ == "__main__":
    TheStar("https://www.thestar.com.my/news/nation/2024/11/13/pm-anwar-arrives-in-peru-for-official-visit-apec-leaders-week")
