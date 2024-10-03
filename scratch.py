from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import pandas as pd
import time
import requests


driver_path = 'msedgedriver.exe'
service = Service(executable_path=driver_path)
driver = webdriver.Edge(service=service)

base_url = 'https://www.corcoran.com/real-estate-agents/search/city/new-york-ny'


def scrape_broker_profile(url):
    driver.get(url)
    
    # Wait for the main content of the broker profile to load
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'img'))  # Adjust this if needed
        )
    except TimeoutException:
        print("Timed out waiting for profile page to load.")
        return {'Name': 'N/A', 'Email': 'N/A', 'Phone': 'N/A'}
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Adjust these if class names have changed
    if 'partnership' in url:
        team_member_elements = soup.find_all('div', {'class': 'AgentCardSmall__AgentCardWrapper-sc-81035ab3-0'})
        team_data=[]
        for i in team_member_elements:
            member = i.find('a', {'data-e2e-id': 'agent-card-small__link'})
            if member and member.has_attr('href'):
                yield from scrape_broker_profile(member['href'])
    
    else:
        name = soup.find('h1', {'class': "Heading__H1-sc-ca6db03b-0 MainTitle__AgentName-sc-7dd2fa10-0 bbMiVA kHGacy OneLinkNoTx"}) or 'N/A'
        email = soup.find('span', {'class': 'TextBase-sc-3b1caa46-0 Text__TextSmall-sc-a209283f-2 AgentText__LinkValue-sc-3fad6dff-4 fYpGIg ibxrnz epWFwx OneLinkNoTx'}) or 'N/A'
        phone = soup.find('span', {'class': 'TextBase-sc-3b1caa46-0 Text__TextSmall-sc-a209283f-2 AgentText__LinkValue-sc-3fad6dff-4 fYpGIg ibxrnz epWFwx'}) or 'N/A'

        return {
            'Name': name.find(text=True, recursive=False).strip() if name != 'N/A' else 'N/A',
            'Email': email.text if email != 'N/A' else 'N/A',
            'Phone': phone.text if phone != 'N/A' else 'N/A'
        }
    
def scrape_brokers_page():
    brokers = []
    
    # Store broker links in a list first to avoid stale element issues later
    broker_links = [link.get_attribute('href') for link in driver.find_elements(By.XPATH, "//a[contains(@class, 'VerticalAgentCard__AgentCardLink-sc-f325ad83-1')]")]
    
    for profile_url in broker_links:
        try:
            brokers.append(scrape_broker_profile(profile_url))
            
            # After scraping, navigate back to the brokers page
            driver.back()  # This will take the driver back to the previous page
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'VerticalAgentCard__AgentCardLink-sc-f325ad83-1')]"))
            )  # Wait for broker links to reappear before scraping the next one
            
        except StaleElementReferenceException:
            print("StaleElementReferenceException encountered, skipping this broker.")
            continue  # Skip the current broker if an issue occurs

    return brokers


wait = WebDriverWait(driver, 10)

def scrape_all_pages(base_url):
    driver.get(base_url)
    
    all_brokers = []
    
    while True:
        print(f'Scraping page...')
        all_brokers.extend(scrape_brokers_page())
        
        try:
            next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@class='Paginator__ButtonStyled-sc-1b4b15d-7 gjRFUk']")))
            next_button.click()
            
            # Wait for the page to load after clicking "Next"
            time.sleep(3)  # Ensure the page has time to load properly
            wait.until(EC.presence_of_element_located((By.XPATH, "//button[@class='Paginator__ButtonStyled-sc-1b4b15d-7 gjRFUk']")))
        except TimeoutException:
            print("No more pages to scrape or next button not found.")
            break

    return all_brokers

all_brokers_data = scrape_all_pages(base_url)

df = pd.DataFrame(all_brokers_data)
df.to_excel('brokers_data.xlsx', index=False)
print("Data saved to brokers_data.xlsx")

driver.quit()
