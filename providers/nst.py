import time

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from helpers.driver import chrome_driver
from helpers.image import resize_image, save_image_from_url
from helpers.url import get_hostname
from providers.provider import Provider, ProviderData


class NST(Provider):
    def __init__(self, url):
        super().__init__(url)

        self.fetch_data()

    def fetch_data(self):

        driver = chrome_driver()

        driver.get(self.url)

        # wait for page load
        time.sleep(2)

        title = driver.find_element(By.CSS_SELECTOR, ".page-title").text
        try:
            author = driver.find_element(By.CSS_SELECTOR, '.article-meta > :nth-child(2) > span')
        except:
            # author has no profile picture
            author = driver.find_element(By.CSS_SELECTOR, '.article-meta > :first-child > span')

        author_a = author.find_element(By.CSS_SELECTOR, 'a')
        a_soup = BeautifulSoup(author_a.get_attribute('outerHTML'), 'html.parser')
        a = a_soup.find('a')
        a['href'] = get_hostname(self.url) + a.attrs['href']
        author = f"<p>By {str(a)}</p>"

        to_be_deleted_elems = driver.find_elements(By.CSS_SELECTOR,
                                                   '[itemprop="articleBody"] .related-listing, [itemprop="articleBody"] [data-google-query-id]')

        for elem in to_be_deleted_elems:
            driver.execute_script('arguments[0].parentNode.removeChild(arguments[0])', elem)

        articles = driver.find_elements(By.CSS_SELECTOR, "[itemprop='articleBody'] p, [itemprop='articleBody'] figure img")
        articles = list(map(lambda x: x.get_attribute('outerHTML'), articles))

        # article image
        image_tag = driver.find_element(By.CSS_SELECTOR, '.field-featured-image > figure > img')
        image_url = image_tag.get_attribute('src')
        image = save_image_from_url(image_url)
        scaled_image = resize_image(image)

        paths = self.url.split('/')
        path = paths[-1]
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

        tags = driver.find_elements(By.CSS_SELECTOR, '.article-content > .keywords > span')
        tags = ', '.join(map(lambda x: x.text, tags))

        self.data = ProviderData(
            title=title,
            content=content,
            image=scaled_image,
            excerpt=excerpt,
            tags=tags
        )


if __name__ == '__main__':
    url = 'https://www.nst.com.my/news/crime-courts/2024/10/1127538/two-myanmar-nationals-among-three-charged-murder-unemployed-man'

    provider = NST(url)

    pass
