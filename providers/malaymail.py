import time
import spacy
import pytextrank

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from helpers.driver import chrome_driver
from helpers.image import resize_image, save_image_from_url
from helpers.url import get_hostname
from providers.provider import Provider, ProviderData
# from rake_nltk import Rake


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
            paragraph = driver.find_elements(By.CSS_SELECTOR, '.article-body > p') #get all p in article body
            pre_author = ""
            for p in reversed(paragraph): #make a loop in reversed
                text = p.text.strip()
                if text: # check if the text has content
                    pre_author = text
                    break
            # Extract word after "—"
            if "—" in pre_author:
                author = "By " + pre_author.split("—")[-1].strip()
            else:
                author = pre_author.strip()


        articles_raw = driver.find_elements(By.CSS_SELECTOR, ".article-body p")
        articles = list(map(lambda x: x.get_attribute('outerHTML'), articles_raw))

        #Implement auto tags using TextRank & Spacy
        nlp = spacy.load("en_core_web_sm")
        articles_text = " ".join(map(lambda x: x.text, articles_raw))
        nlp.add_pipe("textrank")
        doc = nlp(articles_text)
        # Print each phrase with its rank
        for phrase in doc._.phrases[11:20]:
            print(f"{phrase.text}: {phrase.rank}")

        # Extract top 10 phrases and join them into a string
        tags = ", ".join(phrase.text for phrase in doc._.phrases[:10])

        # WE ARE NOT USING RAKE BCS THE KEYWORD IS SO LONG
        # rake = Rake()
        # articles_text = " ".join(map(lambda x: x.text, articles_raw))
        # rake.extract_keywords_from_text(articles_text)
        # tags_raw = rake.get_ranked_phrases()
        # tags_raw_score = rake.get_ranked_phrases_with_scores()
        # tags = ", ".join(tags_raw[19:26])
        # for phrase, score in tags_raw_score[19:26]:
        #     print(f"{phrase}: {score}")

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
