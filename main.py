import os
import time
# import os
# os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from helpers.driver import chrome_driver

from providers.provider import Provider

from dotenv import load_dotenv

from providers.nst import NST
from providers.thestar import TheStar
from providers.malaymail import MalayMail

load_dotenv()

kritik_user = os.getenv('KRITIK_USER')
kritik_pass = os.getenv('KRITIK_PASS')



category_map = {
    "Advanced Technology": "70",
    "Digital Transformation": "3291",
    "Military": "3734",
    "Science and Technology": "11",
    "Smart City": "76",
    "Technology": "6425",
    "Agriculture": "69",
    "Food Industries": "5326",
    "Food Security": "5657",
    "Arts & Literature": "56",
    "Culture and Heritage": "2885",
    "Automotive": "11988",
    "Banking and Financial": "2",
    "Budget": "3001",
    "Fintech": "3233",
    "Investment": "3000",
    "Business Services": "46",
    "Business Advisory": "3013",
    "Business Tips": "3090",
    "Corporate News": "84",
    "Customer Service": "85",
    "Productivity Tools": "77",
    "Work Life Balance": "2877",
    "Campaign": "53",
    "Consumer Products": "54",
    "Current Affairs": "47",
    "Crime": "6287",
    "Natural Disaster": "6125",
    "War": "6156",
    "Cybersecurity": "79",
    "Economics": "51",
    "Career": "6293",
    "Gig Economy": "78",
    "Editorial": "60",
    "Education": "45",
    "Energy": "12266",
    "Entertainment": "6",
    "Entrepreneurship": "64",
    "Environment": "5484",
    "Food and Beverage": "7",
    "Healthcare": "52",
    "Human Resource": "68",
    "Career Tips": "3403",
    "Coaching and Mentoring": "4992",
    "Learning and Development": "4993",
    "Workplace": "3059",
    "Humor": "71",
    "Infrastructure": "12414",
    "International Affairs": "9",
    "Investment": "72",
    "JoeGetz Critical Lens": "11703",
    "Leadership": "67",
    "Transformation": "2878",
    "Letters": "59",
    "Life Style": "4206",
    "Lifestyle": "29",
    "Opinion": "58",
    "Others": "1",
    "Personal Development": "61",
    "Politics": "10",
    "Governance": "6703",
    "Property": "12211",
    "Public Services": "27",
    "Religion": "12089",
    "Sales and Marketing": "15",
    "Advertising and Promotion": "6001",
    "Content Marketing": "2870",
    "Digital Marketing": "73",
    "Scandals": "66",
    "Fraud": "6177",
    "Scam": "6178",
    "Service Providers": "12",
    "Social Issues": "28",
    "Sports": "13",
    "Startup": "65",
    "Strategic Management": "83",
    "Tech": "4204",
    "Tourism and Hospitality": "8",
    "Transportation": "14",
    "Aviation": "8433",
    "Travel and Leisure": "16",
    "Utilities": "17",
    "Power and Energy": "3068",
    "Telecoms": "3067",
    "World": "4192",
    "Foods": "4202"
}

def main():

    print("Welcome to Kritik Long, Didn't Read(KLDR) developed by @aidilrx04 & @asjadZ")

    post = input('Enter post url(valid sites now: nst, thestar, MalayMail): ')

    provider: Provider = None

    if (post.startswith('https://www.nst.com.my/')):
        provider = NST(post)
    elif post.startswith('https://www.thestar.com.my/'):
        provider = TheStar(post)
    elif post.startswith('https://www.malaymail.com/'):
        provider = MalayMail(post)
    else:
        print("Invalid post url")
        exit(-1)

    data = provider.get_data()

    driver = chrome_driver()

    login(driver)

    insert_data(driver, data)

    input()

    driver.quit()

    pass

def login(driver):

    login_url = 'https://kritik.com.my/wp-login.php?redirect_to=https%3A%2F%2Fkritik.com.my%2Fwp-admin%2Fpost-new.php&reauth=1'

    driver.get(login_url)
    time.sleep(1)

    user_input = driver.find_element(By.CSS_SELECTOR, '#user_login')
    pass_input = driver.find_element(By.CSS_SELECTOR, '#user_pass')
    login_btn = driver.find_element(By.CSS_SELECTOR, '#wp-submit')

    # send username and password
    user_input.send_keys(kritik_user)
    pass_input.send_keys(kritik_pass)

    login_btn.click()

    pass

def insert_data(driver, data):
    # assume user already redirected to post new page
    time.sleep(2)

    title_input = driver.find_element(By.CSS_SELECTOR, '#title')
    excerpt_input = driver.find_element(By.CSS_SELECTOR, '#excerpt')
    content_input = driver.find_element(By.CSS_SELECTOR, '#content')
    visual_editor_btn = driver.find_element(By.CSS_SELECTOR, '#content-tmce')

    set_image_btn = driver.find_element(By.CSS_SELECTOR, '#set-post-thumbnail')

    print("Inserting title...")
    title_input.send_keys(data.title)
    time.sleep(.5)

    print('Inserting excerpt...')
    excerpt_input.send_keys(data.excerpt)
    time.sleep(.5)

    print('Check Category...')
    cats = data.category
    for cat in cats:
        if cat in category_map:
            checkbox = driver.find_element(By.XPATH, f'//input[@value="{category_map[cat]}"]')
            driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)  # Scroll into view
            time.sleep(0.5)  # Small delay to ensure it’s visible
            if not checkbox.is_selected():  # Avoid rechecking if already checked
                checkbox.click()

    time.sleep(.5)
    driver.execute_script("document.querySelector('#content-html').click()")

    time.sleep(.5)
    print('Inserting content...')
    content_input.send_keys(data.content)
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

    color_caret_btn = driver.find_element(By.CSS_SELECTOR,
                                          '.mce-widget.mce-btn.mce-splitbtn.mce-colorbutton > :nth-child(2)')
    color_caret_btn.click()

    black_color = driver.find_element(By.CSS_SELECTOR, '[data-mce-color="#000000"]')

    black_color.click()

    time.sleep(1)
    print("Setting tags")
    if data.tags is not None:
        tags_input = driver.find_element(By.CSS_SELECTOR, 'input#new-tag-post_tag')
        add_tags_btn = driver.find_element(By.CSS_SELECTOR, 'input.button.tagadd')

        tags_input.send_keys(data.get_tags())
        # add_tags_btn.click()
        driver.execute_script("arguments[0].click()", add_tags_btn)
    else:
        print("No tags found, skipping")

    print('Setting featured image...')
    # set_image_btn.click()
    driver.execute_script("arguments[0].click()", set_image_btn)
    time.sleep(1)

    set_featured_image_btn = driver.find_element(By.CSS_SELECTOR,
                                                 'button.media-button-select.media-button.button-primary.button-large')
    image_input = driver.find_element(By.CSS_SELECTOR, ' .moxie-shim.moxie-shim-html5 input[type="file"]')

    image_input.send_keys(data.image)

    WebDriverWait(driver, 60).until(
        lambda d: d.find_element(By.CSS_SELECTOR,
                                 'button.media-button-select.media-button.button-primary.button-large').get_attribute(
            'disabled') is None
    )

    set_featured_image_btn.click()
    print('image setted')

if __name__ == '__main__':
    main()