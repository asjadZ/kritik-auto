import time
from datetime import datetime

from requests.packages import target
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from selenium.webdriver.support.wait import WebDriverWait

from helpers.image import save_image_from_url, resize_image
from helpers.url import get_hostname

# target_post = input('Enter post url: ')
target_post = 'https://www.nst.com.my/news/nation/2024/10/1127251/strengthen-national-defence-system-light-current-geopolitical-tensions'

post_new_url = 'https://kritik.com.my/wp-admin/post-new.php'

service = Service('.\chromedriver-win64\chromedriver.exe')
driver = webdriver.Chrome(service=service)


def main():
    data = get_data()

    login()
    print('logged in')

    insert_data(data)

    input()


def login():
    driver.switch_to.new_window('tab')
    driver.switch_to.window(driver.window_handles[1])
    driver.get('https://kritik.com.my/wp-admin')
    time.sleep(1)

    user_input = driver.find_element(By.CSS_SELECTOR, '#user_login')
    pass_input = driver.find_element(By.CSS_SELECTOR, '#user_pass')
    login_btn = driver.find_element(By.CSS_SELECTOR, '#wp-submit')

    # send username and password
    user_input.send_keys(kritik_user)
    pass_input.send_keys(kritik_pass)

    login_btn.click()

    print(user_input)


def get_data():
    driver.switch_to.window(driver.window_handles[0])
    driver.get(target_post)

    time.sleep(1)

    title = driver.find_element(By.CSS_SELECTOR, ".page-title")
    try:
        author = driver.find_element(By.CSS_SELECTOR, '.article-meta > :nth-child(2) > span')
    except:
        # author has no profile picture
        author = driver.find_element(By.CSS_SELECTOR, '.article-meta > :first-child > span')

    author_a = author.find_element(By.CSS_SELECTOR, 'a')
    print(author_a)
    author_soup = BeautifulSoup(author_a.get_attribute('outerHTML'), 'html.parser')
    a = author_soup.find('a')
    a['href'] = get_hostname(target_post) + a.attrs['href']
    author = f"<p>By {str(a)}</p>"

    to_be_deleted_elems = driver.find_elements(By.CSS_SELECTOR,
                                               '[itemprop="articleBody"] .related-listing, [itemprop="articleBody"] [data-google-query-id]')

    for elem in to_be_deleted_elems:
        driver.execute_script('arguments[0].parentNode.removeChild(arguments[0])', elem)

    articles = driver.find_elements(By.CSS_SELECTOR, "[itemprop='articleBody'] p")

    # article image
    image_tag = driver.find_element(By.CSS_SELECTOR, '.field-featured-image > figure > img')
    image_url = image_tag.get_attribute('src')

    image = save_image_from_url(image_url)

    scaled_image = resize_image(image)

    print(scaled_image)

    paths = target_post.split('/')

    path = paths[-1]

    source_p = f"""
    <p>
        <strong>Source: </strong><a href="{target_post}">{path}</a>
    </p>
"""

    return {
        'title': title.text,
        'author': author,
        'articles': list(map(lambda x: x.get_attribute('outerHTML'), articles)) + ['<p></p>', source_p],
        'image': scaled_image
    }


def insert_data(data):
    driver.switch_to.window(driver.window_handles[1])
    driver.get(post_new_url)

    time.sleep(1)

    title_input = driver.find_element(By.CSS_SELECTOR, '#title')
    excerpt_input = driver.find_element(By.CSS_SELECTOR, '#excerpt')
    exerpt_string = BeautifulSoup(data['articles'][0], 'html.parser').text
    content_input = driver.find_element(By.CSS_SELECTOR, '#content')
    text_editor_btn = driver.find_element(By.CSS_SELECTOR, '#content-html')
    visual_editor_btn = driver.find_element(By.CSS_SELECTOR, '#content-tmce')

    set_image_btn = driver.find_element(By.CSS_SELECTOR, '#set-post-thumbnail')

    print(text_editor_btn.get_attribute('outerHTML'))

    print(content_input.get_attribute('outerHTML'))
    title_input.send_keys(data['title'])
    time.sleep(.5)
    excerpt_input.send_keys(exerpt_string)

    time.sleep(.5)
    # text_editor_btn.click()
    driver.execute_script("document.querySelector('#content-html').click()")

    time.sleep(.5)
    content_input.send_keys(data['author'])
    content_input.send_keys(Keys.ENTER)
    time.sleep(0.5)
    for article in data['articles']:
        content_input.send_keys(article)
        content_input.send_keys(Keys.ENTER)
        time.sleep(.1)


    visual_editor_btn.click()

    # get body
    driver.switch_to.frame(driver.find_element(By.CSS_SELECTOR, 'iframe#content_ifr'))
    content_body = driver.find_element(By.CSS_SELECTOR, '#tinymce.mce-content-body')

    driver.execute_script("""
    var range = document.createRange();
    range.selectNodeContents(arguments[0]);
    var selection = window.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
    """, content_body)

    driver.switch_to.default_content()

    color_caret_btn =  driver.find_element(By.CSS_SELECTOR, '.mce-widget.mce-btn.mce-splitbtn.mce-colorbutton > :nth-child(2)')
    color_caret_btn.click()

    black_color = driver.find_element(By.CSS_SELECTOR, '[data-mce-color="#000000"]')

    black_color.click()

    input()

    set_image_btn.click()
    time.sleep(1)

    set_featured_image_btn = driver.find_element(By.CSS_SELECTOR,
                                                 'button.media-button-select.media-button.button-primary.button-large')
    image_input = driver.find_element(By.CSS_SELECTOR, ' .moxie-shim.moxie-shim-html5 input[type="file"]')

    image_input.send_keys(data['image'])

    WebDriverWait(driver, 60).until(
        lambda d: d.find_element(By.CSS_SELECTOR,
                                 'button.media-button-select.media-button.button-primary.button-large').get_attribute(
            'disabled') is None
    )

    set_featured_image_btn.click()
    print('image setted')


if __name__ == '__main__':
    main()
