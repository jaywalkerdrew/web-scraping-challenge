# Dependencies
import pandas as pd
import requests
from splinter import Browser
from bs4 import BeautifulSoup as bs
import time

def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    browser = init_browser()

    # Scrape the top news headline and text
    news_url = 'https://mars.nasa.gov/news/'
    browser.visit(news_url)
    time.sleep(15)
    html = browser.html
    soup = bs(html, 'html.parser')

    # slide = soup.find('li', class_='slide')
    slide = soup.find('li', class_='slide')
    news_title = slide.find('div', class_='content_title').get_text()
    news_p = slide.find('div', class_='article_teaser_body').get_text()

    # Scrape the featured image
    image_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(image_url)
    html = browser.html
    soup = bs(html, 'html.parser')

    featured_image = soup.find(class_='main_feature')
    image_info = featured_image.find('article')
    image_url = image_info["style"].split("url('")[1].replace("');", "")

    base_image_url = 'https://www.jpl.nasa.gov'
    featured_image_url = base_image_url + image_url

    # Scrape Mars facts table
    facts_url = 'https://space-facts.com/mars/'
    browser.visit(facts_url)
    html = browser.html
    soup = bs(html, 'html.parser')

    facts_df = pd.read_html(facts_url)[0]
    facts_df.columns = ['Description','Value']
    facts_df = facts_df.set_index('Description')
    facts_html_table = facts_df.to_html()

    # Scrape hemisphere images
    hemis_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemis_url)
    html = browser.html
    soup = bs(html, 'html.parser')

    hemispheres = soup.find_all('div', class_='item')
    hemisphere_pics = []

    base_hemis_url = 'https://astrogeology.usgs.gov'

    for hemi in hemispheres:
        current_hemi_name = hemi.find('h3').text
        current_hemi_link = hemi.find('a')['href']
        current_full_hemi_url = base_hemis_url + current_hemi_link
        
        browser.visit(current_full_hemi_url)
        time.sleep(10)
        html = browser.html
        soup = bs(html, 'html.parser')
        
        hemi_image_url = soup.find('li').find('a')['href']
        
        hemi_image_dict = {}
        hemi_image_dict['title'] = current_hemi_name
        hemi_image_dict['img_url'] = hemi_image_url
        hemisphere_pics.append(hemi_image_dict)

    # Build the dictionary to be returned
    mars_data_dict = {
        'news_title': news_title,
        'news_p': news_p,
        'featured_image_url': featured_image_url,
        'facts': facts_html_table,
        'hemisphere_pics': hemisphere_pics
    }

    browser.quit()
    
    return mars_data_dict