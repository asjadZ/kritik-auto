import time

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from helpers.driver import chrome_driver
from helpers.image import resize_image, save_image_from_url
from helpers.url import get_hostname
from providers.provider import Provider, ProviderData


class MalayMail(Provider):
    def __init__(self, url):
        super().__init__(url)

        self.fetch_data()

    def fetch_data(self):

        driver = chrome_driver()
        driver.get(self.url)

        # wait for page load
        time.sleep(2)

        title = driver.find_element(By.CSS_SELECTOR, "h1.article-title").text

        try:
            author = driver.find_element(By.CSS_SELECTOR, '.article-byline').text
        except:
            # If not found, fall back to the last 3rd <p> in .article-body
            pre_author = driver.find_element(By.CSS_SELECTOR, '.article-body > p:nth-last-of-type(1)').text
            # Extract word after "—"
            if "—" in pre_author:
                author = "By " + pre_author.split("—")[-1].strip()
            else:
                author = pre_author.strip()


        articles = driver.find_elements(By.CSS_SELECTOR, ".article-body p")
        articles = list(map(lambda x: x.get_attribute('outerHTML'), articles))

        # article image

        image_url = None
        try:
            # image_tag = driver.find_element(By.CSS_SELECTOR, 'layout-ratio > picture > img')
            # image_url = image_tag.get_attribute('src')
            image_tag = driver.find_element(By.CSS_SELECTOR, '.article-image-gallery .layout-ratio picture img')
            image_url = image_tag.get_attribute('src')
        except:
            print("No image found or failed to locate image.")

        image = save_image_from_url(image_url)
        scaled_image = resize_image(image)

        paths = self.url.split('/')
        path = paths[-2]
        source_p = \
            f"""
<p>
    <strong>Source: </strong><a href="{self.url}">{path}</a>
</p>
"""
        articles_string = '\n'.join(articles)
        content = \
            f"""<p>
{author}
</p>
{articles_string}
&nbsp;
{source_p}
"""
        excerpt = BeautifulSoup(articles[0], 'html.parser').text
        tags = ""

        self.data = ProviderData(
            title=title,
            content=content,
            image=scaled_image,
            excerpt=excerpt,
            tags=tags
        )


if __name__ == '__main__':
    url = 'https://www.malaymail.com/news/malaysia/2025/02/10/sell-your-ramadan-bazaar-licence-lose-it-immediately-warns-pm/166130'

    provider = MalayMail(url)

    # Accessing the scraped data
    data = provider.get_data()
    print(f"Title: {data.get_title()}")
    print(f"Excerpt: {data.get_excerpt()}")
    print(f"Content: {data.get_content()}")
    print(f"Image: {data.get_image()}")
    print(f"Tags: {data.get_tags()}")
