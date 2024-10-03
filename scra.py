from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import pandas as pd

driver_path = 'msedgedriver.exe'
service = Service(executable_path=driver_path)
driver = webdriver.Edge(service=service)

base_url = 'https://www.corcoran.com/real-estate-agents/search/city/new-york-ny'

def scrape_broker_profile(url):
    driver.get(url)
    
    # Wait for the main content of the broker profile to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, 'img'))  # Adjust this if needed
    )
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    name = soup.find('div', {'class':"HeaderActions__HeaderTitle-sc-acf5da2b-6 kbFkGA"}).text if soup.find('div', {'class':"HeaderActions__HeaderTitle-sc-acf5da2b-6 kbFkGA"}) else 'N/A'
    print(name)
    email = soup.find('span', {'class':'TextBase-sc-3b1caa46-0 Text__TextSmall-sc-a209283f-2 AgentText__LinkValue-sc-3fad6dff-4 fYpGIg ibxrnz epWFwx OneLinkNoTx'}).text if soup.find('span', {'class':'TextBase-sc-3b1caa46-0 Text__TextSmall-sc-a209283f-2 AgentText__LinkValue-sc-3fad6dff-4 fYpGIg ibxrnz epWFwx OneLinkNoTx'}) else 'N/A'
    print(email)
    phone = soup.find('span', {'class':'TextBase-sc-3b1caa46-0 Text__TextSmall-sc-a209283f-2 AgentText__LinkValue-sc-3fad6dff-4 fYpGIg ibxrnz epWFwx'}).text if soup.find('span', {'class':'TextBase-sc-3b1caa46-0 Text__TextSmall-sc-a209283f-2 AgentText__LinkValue-sc-3fad6dff-4 fYpGIg ibxrnz epWFwx'}) else 'N/A'
    print(phone)
    return {
        'Name': name,
        'Email': email,
        'Phone': phone
    }
    
def scrape_brokers_page():
    brokers = []
    
    # Fetch the broker links anew each time
    broker_links = driver.find_elements(By.XPATH, "//a[contains(@class, 'VerticalAgentCard__AgentCardLink-sc-f325ad83-1')]")
    
    for link in broker_links:
        try:
            # Re-fetch the link each time to avoid stale element reference
            profile_url = link.get_attribute('href')
            brokers.append(scrape_broker_profile(profile_url))
        except StaleElementReferenceException:
            print("StaleElementReferenceException encountered, re-fetching elements.")
            # Re-fetch the broker links if a stale reference occurs
            broker_links = driver.find_elements(By.XPATH, "//a[@class='VerticalAgentCard__AgentCardLink-sc-f325ad83-1 bbVogU']")
            continue  # Restart the loop to process the current link again

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
            wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'VerticalAgentCard__AgentCardLink-sc-f325ad83-1')]")))  # Wait for broker links to appear
        except TimeoutException:
            print("No more pages to scrape or next button not found.")
            break

    return all_brokers

all_brokers_data = scrape_all_pages(base_url)

df = pd.DataFrame(all_brokers_data)
df.to_excel('brokers_data.xlsx', index=False)
print("Data saved to brokers_data.xlsx")

driver.quit()
