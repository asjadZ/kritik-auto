import time
import spacy
import pytextrank
# import os
# os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from helpers.driver import chrome_driver
from helpers.image import resize_image, save_image_from_url
from helpers.url import get_hostname
from providers.provider import Provider, ProviderData
from transformers import pipeline
from rake_nltk import Rake

# CATEGORY_LIST = [
#     "Advanced Technology", "Digital Transformation", "Agriculture", "Food Industries", "Food Security",
#     "Arts & Literature", "Culture and Heritage", "Automotive", "Banking and Financial", "Budget",
#     "Fintech", "Investment", "Business Services", "Business Advisory", "Business Tips", "Corporate News",
#     "Customer Service", "Productivity Tools", "Work Life Balance", "Campaign", "Consumer Products",
#     "Current Affairs", "Crime", "Natural Disaster", "War", "Cybersecurity", "Economics", "Career",
#     "Gig Economy", "Editorial", "Education", "Energy", "Entertainment", "Entrepreneurship", "Environment",
#     "Food and Beverage", "Healthcare", "Human Resource", "Career Tips", "Coaching and Mentoring",
#     "Learning and Development", "Workplace", "Humor", "Infrastructure", "International Affairs",
#     "Investment", "JoeGetz Critical Lens", "Leadership", "Transformation", "Letters", "Life Style",
#     "Lifestyle", "Opinion", "Others", "Personal Development", "Politics", "Governance", "Property",
#     "Public Services", "Religion", "Sales and Marketing", "Advertising and Promotion", "Content Marketing",
#     "Digital Marketing", "Scandals", "Fraud", "Scam", "Service Providers", "Social Issues", "Sports",
#     "Startup", "Strategic Management", "Tech", "Tourism and Hospitality", "Transportation", "Aviation",
#     "Travel and Leisure", "Utilities", "Power and Energy", "Telecoms", "World", "Foods", "Games",
#     "Travel", "Military", "Science and Technology", "Smart City", "Technology"
# ]

# category_map = {
#     "Advanced Technology": "70",
#     "Digital Transformation": "3291",
#     "Military": "3734",
#     "Science and Technology": "11",
#     "Smart City": "76",
#     "Technology": "6425",
#     "Agriculture": "69",
#     "Food Industries": "5326",
#     "Food Security": "5657",
#     "Arts & Literature": "56",
#     "Culture and Heritage": "2885",
#     "Automotive": "11988",
#     "Banking and Financial": "2",
#     "Budget": "3001",
#     "Fintech": "3233",
#     "Investment": "3000",
#     "Business Services": "46",
#     "Business Advisory": "3013",
#     "Business Tips": "3090",
#     "Corporate News": "84",
#     "Customer Service": "85",
#     "Productivity Tools": "77",
#     "Work Life Balance": "2877",
#     "Campaign": "53",
#     "Consumer Products": "54",
#     "Current Affairs": "47",
#     "Crime": "6287",
#     "Natural Disaster": "6125",
#     "War": "6156",
#     "Cybersecurity": "79",
#     "Economics": "51",
#     "Career": "6293",
#     "Gig Economy": "78",
#     "Editorial": "60",
#     "Education": "45",
#     "Energy": "12266",
#     "Entertainment": "6",
#     "Entrepreneurship": "64",
#     "Environment": "5484",
#     "Food and Beverage": "7",
#     "Healthcare": "52",
#     "Human Resource": "68",
#     "Career Tips": "3403",
#     "Coaching and Mentoring": "4992",
#     "Learning and Development": "4993",
#     "Workplace": "3059",
#     "Humor": "71",
#     "Infrastructure": "12414",
#     "International Affairs": "9",
#     "Investment": "72",
#     "JoeGetz Critical Lens": "11703",
#     "Leadership": "67",
#     "Transformation": "2878",
#     "Letters": "59",
#     "Life Style": "4206",
#     "Lifestyle": "29",
#     "Opinion": "58",
#     "Others": "1",
#     "Personal Development": "61",
#     "Politics": "10",
#     "Governance": "6703",
#     "Property": "12211",
#     "Public Services": "27",
#     "Religion": "12089",
#     "Sales and Marketing": "15",
#     "Advertising and Promotion": "6001",
#     "Content Marketing": "2870",
#     "Digital Marketing": "73",
#     "Scandals": "66",
#     "Fraud": "6177",
#     "Scam": "6178",
#     "Service Providers": "12",
#     "Social Issues": "28",
#     "Sports": "13",
#     "Startup": "65",
#     "Strategic Management": "83",
#     "Tech": "4204",
#     "Tourism and Hospitality": "8",
#     "Transportation": "14",
#     "Aviation": "8433",
#     "Travel and Leisure": "16",
#     "Utilities": "17",
#     "Power and Energy": "3068",
#     "Telecoms": "3067",
#     "World": "4192",
#     "Foods": "4202"
# }

# def detect_category(content):
#     classifier = pipeline("zero-shot-classification",model="facebook/bart-large-mnli")
#     result = classifier(content,CATEGORY_LIST, multi_label=True)
#     top_categories = result["labels"][:2]
#     # return  top_categories
#     return ", ".join(top_categories)

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
            # If not found, find in the paragraph
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

        articles_text = " ".join(map(lambda x: x.text, articles_raw))

        #SET CATEGORY
        # category = detect_category(articles_text)
        # print(f"Category : {category}")

        #Implement auto tags using TextRank & Spacy
        nlp = spacy.load("en_core_web_sm")
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
            tags=tags,
            # category=category,
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
