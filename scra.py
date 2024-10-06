from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import pandas as pd
import time
from urllib.parse import urljoin
from bs4.element import Tag


driver_path = 'msedgedriver.exe'
service = Service(executable_path=driver_path)
driver = webdriver.Edge(service=service)

base_url = 'https://www.corcoran.com/real-estate-agents/search/city/new-york-ny'

def scrape_broker_profile(url):
    driver.get(url)
    
    # Wait for the page to load
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'h1'))
        )
    except TimeoutException:
        print("Timed out waiting for profile page to load.")
        return {'Name': 'N/A', 'Email': 'N/A', 'Phone': 'N/A'}
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Extract Name: Try a few methods in case one fails
    name = soup.find('h1')
    name = name.find(string=True, recursive=False)  # Primary search
    if not name:  # Fallback in case the structure differs
        name = 'not found'

    # Extract Email: Multiple class lookups to handle variations
    email = soup.find('span', {'class': 'TextBase-sc-3b1caa46-0 Text__TextSmall-sc-a209283f-2 AgentText__LinkValue-sc-3fad6dff-4 fpUUIo jNEATc cRJPmn OneLinkNoTx'})
    if not email:
        email = soup.find('a', href=lambda x: x and 'mailto:' in x)  # Fallback to mailto links
        email = email['href'].replace('mailto:', '') if email else 'N/A'

    # Extract Phone: Same idea, try different approaches
    phone = soup.find('span', {'class':'TextBase-sc-3b1caa46-0 Text__TextSmall-sc-a209283f-2 AgentText__LinkValue-sc-3fad6dff-4 fpUUIo jNEATc cRJPmn'})
    if not phone:
        phone = soup.find('a', href=lambda x: x and 'tel:' in x)  # Fallback to tel links
        phone = phone['href'].replace('tel:', '') if phone else 'N/A'

    result = {
        'Name': name if name != 'N/A' else 'N/A',
        'Email': email if email != 'N/A' else 'N/A',
        'Phone': phone if phone != 'N/A' else 'N/A'
    }
    print(result)
    return result

def scrape_team_profile(url):
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    members = soup.find_all('a', {'data-e2e-id': 'agent-card-small__link'})  # Look for all team members
    team_data = []
    main_url = 'https://www.corcoran.com'
    
    for member in members:
        full_url = urljoin(main_url, member['href'])
        team_data.append(full_url)  # Collect team member profile URLs
    
    return team_data


    
def scrape_brokers_page():
    brokers = []
    team_links = set()
    # Store broker links in a list first to avoid stale element issues later
    broker_links = [link.get_attribute('href') for link in driver.find_elements(By.XPATH, "//a[contains(@class, 'VerticalAgentCard__AgentCardLink-sc-f325ad83-1')]")]
    for i in broker_links:
        print(i)
        if 'partnership' in i:
            j = broker_links.index(i)
            team_links.add(broker_links[j])
    broker_links = [x for x in broker_links if x not in team_links]
    for team_url in team_links:
        try:
            broker_links.extend(scrape_team_profile(team_url))
            time.sleep(10)
        except StaleElementReferenceException:
            print("StaleElementReferenceException encountered, skipping this team broker.")
            continue
    for profile_url in broker_links:
        try:
            brokers.append(scrape_broker_profile(profile_url))
        except StaleElementReferenceException:
            print("StaleElementReferenceException encountered, skipping this broker.")
            continue  # Skip the current broker if an issue occurs
    
    return brokers


wait = WebDriverWait(driver, 10)

def scrape_all_pages(base_url):
    driver.get(base_url)
    
    all_brokers = []
    
    for i in range(10):
        print(f'Scraping page...')
        all_brokers.extend(scrape_brokers_page())
        
        try:
            next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-e2e-id='paginator__button']")))
            next_button.click()
            
            # Wait for the page to load after clicking "Next"
            time.sleep(3)  # Ensure the page has time to load properly
            wait.until(EC.presence_of_element_located((By.XPATH, "//button[@class='Paginator__ButtonStyled-sc-1b4b15d-7 gjRFUk']")))
        except TimeoutException:
            print("No more pages to scrape or next button not found.")
            break

    return all_brokers

all_brokers_data = scrape_all_pages(base_url)
print(all_brokers_data)

df = pd.DataFrame(all_brokers_data)

def clean_html(text):
    if isinstance(text, str):  # Only process if it's an html element
        soup = BeautifulSoup(text, "html.parser")
        return soup.get_text(separator=" ")  # Extract only the text
    return text  # Return as-is if it's not an html element

# Assuming df is your DataFrame
df_cleaned = df.astype(str).applymap(clean_html)

pd.set_option('display.max_rows', None)
print(df_cleaned)
df_cleaned.to_excel('brokers_data.xlsx', index=False)
print("Data saved to brokers_data.xlsx")

driver.quit()
