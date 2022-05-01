# Import Dependencies
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    # Initiate headless driver for deployment
    # Select the path and browser
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_p = mars_news(browser)
    hemisphere_image_urls= hemispheres(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_p,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres" : hemisphere_image_urls,
        "last_modified": dt.datetime.now()
        
    }
   
    # End scraping session and return data
    browser.quit()
    return data


# Mars news scrape function
def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Begin Parsing
    html = browser.html
    news_soup = soup(html, 'html.parser')
    slide_elem = news_soup.select_one('div.list_text')

    # Add try / except error handling
    try:
        # find the webpage titles
        slide_elem.find('div', class_='content_title')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()
        
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None
        
    return news_title, news_p

## Featured Image
# Scrape featured image function
def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None
    
     # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    
    return img_url

###  Get Mars Facts

# Mars facts function
def mars_facts(): 
    
    try:
    # Read the the tables in the website into a dataframe using read_html
        df = pd.read_html('https://galaxyfacts-mars.com/')[0]

    except BaseException:
        return None

    # Rename the columns and set the index
    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)

    # export the dataframe back to html
    return df.to_html(classes="table table-striped")

# Hemispheres function
def hemispheres(browser):
        # 1. Use browser to visit the URL 
    url = 'https://marshemispheres.com/'

    browser.visit(url)

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    for e in range(4):
        #create empty dictionary
        hemispheres = {}
        browser.find_by_css('a.product-item h3')[e].click()
        element = browser.find_link_by_text('Sample').first
        img_url = element['href']
        title = browser.find_by_css("h2.title").text
        hemispheres["img_url"] = img_url
        hemispheres["title"] = title
        hemisphere_image_urls.append(hemispheres)
        browser.back()

    # 4. Print the list that holds the dictionary of each image url and title.
    return hemisphere_image_urls

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())