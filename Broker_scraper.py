from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
import time
from urllib.parse import urljoin
from selenium.webdriver.common.action_chains import ActionChains

# Path to the Edge WebDriver executable
driver_path = 'Drivers\msedgedriver.exe'
service = Service(executable_path=driver_path)

# Initialize the Edge WebDriver
driver = webdriver.Edge(service=service)

# Base URL for scraping real estate agents in New York City
base_url = 'https://www.corcoran.com/real-estate-agents/search/city/new-york-ny'

# Function to scrape individual broker profile information
def scrape_broker_profile(url):
    driver.get(url)  # Navigate to the broker profile URL

    # Wait for the page to load and the main header (h1) to be present
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'h1'))
        )
    except TimeoutException:
        print("Timed out waiting for profile page to load.")
        return {'Name': 'N/A', 'Email': 'N/A', 'Phone': 'N/A'}
    
    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Extract broker name
    name = soup.find('h1')
    name = name.find(string=True, recursive=False)
    if not name:
        name = 'not found'  # Fallback if name not found

    # Extract email address
    email = soup.find('span', {'class': 'TextBase-sc-3b1caa46-0 Text__TextSmall-sc-a209283f-2 AgentText__LinkValue-sc-3fad6dff-4 fpUUIo jNEATc cRJPmn OneLinkNoTx'})
    if not email:
        email = soup.find('a', href=lambda x: x and 'mailto:' in x)
        email = email['href'].replace('mailto:', '') if email else 'N/A'

    # Extract phone number
    phone = soup.find('span', {'class':'TextBase-sc-3b1caa46-0 Text__TextSmall-sc-a209283f-2 AgentText__LinkValue-sc-3fad6dff-4 fpUUIo jNEATc cRJPmn'})
    if not phone:
        phone = soup.find('a', href=lambda x: x and 'tel:' in x)
        phone = phone['href'].replace('tel:', '') if phone else 'N/A'

    # Store the results in a dictionary
    result = {
        'Name': name if name != 'N/A' else 'N/A',
        'Email': email if email != 'N/A' else 'N/A',
        'Phone': phone if phone != 'N/A' else 'N/A'
    }
    print(result)  # Print the result for debugging
    return result  # Return the extracted data

# Function to scrape team profiles
def scrape_team_profile(url):
    driver.get(url)  # Navigate to the team profile URL
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Find all team members' links
    members = soup.find_all('a', {'data-e2e-id': 'agent-card-small__link'})
    team_data = []
    main_url = 'https://www.corcoran.com'
    
    # Collect each team member's full profile URL
    for member in members:
        full_url = urljoin(main_url, member['href'])
        team_data.append(full_url) 
    
    return team_data  # Return list of team member URLs

# Function to scrape broker links from a single page
def scrape_brokers_page():
    team_links = set()  # Set to store team links
    # Get broker links using XPath
    broker_links = [link.get_attribute('href') for link in driver.find_elements(By.XPATH, "//a[contains(@class, 'VerticalAgentCard__AgentCardLink-sc-f325ad83-1')]")]
    
    for i in broker_links:
        print(i)  # Print each broker link
        if 'partnership' in i:
            j = broker_links.index(i)  # Get index of partnership link
            team_links.add(broker_links[j])  # Add to team links
    
    # Remove team links from broker links
    broker_links = [x for x in broker_links if x not in team_links]
    
    return broker_links, team_links  # Return individual and team links

# Initialize WebDriverWait instance
wait = WebDriverWait(driver, 10)

# Function to scrape all pages
def scrape_all_pages(base_url):
    driver.get(base_url)  # Navigate to the base URL
    
    all_brokers_links = []  # List to store all broker links
    all_brokers_data = []   # List to store all broker data
    team_links = set()      # Set to store team links

    while True:
        print(f'Scraping page...')  # Indicate progress
        indiv_out, team_out = scrape_brokers_page()  # Scrape broker and team links
        team_links.update(team_out)  # Update team links
        all_brokers_links.extend(indiv_out)  # Extend broker links
        
        # Click on the next button to go to the next page
        try:
            next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-e2e-id='paginator__button']")))
            action = ActionChains(driver)
            action.move_to_element(next_button).click().perform()  # Click the next button
            
            # Wait for the page to load after clicking "Next"
            time.sleep(3)  # Ensure the page has time to load properly
            wait.until(EC.presence_of_element_located((By.XPATH, "//button[@class='Paginator__ButtonStyled-sc-1b4b15d-7 gjRFUk']")))
        except TimeoutException:
            print("No more pages to scrape or next button not found.")
            break  # Exit loop if no more pages

    # Scrape profiles for each team link
    for i in team_links:
        all_brokers_links.extend(scrape_team_profile(i))
        
    # Scrape profiles for each individual broker link
    for i in all_brokers_links:
        all_brokers_data.append(scrape_broker_profile(i))

    return all_brokers_data  # Return all collected broker data

# Start scraping all pages and collect data
data = scrape_all_pages(base_url)
print(data)  # Print the collected data

# Create a DataFrame from the collected data
df = pd.DataFrame(data)

# Function to clean HTML tags from text
def clean_html(text):
    if isinstance(text, str):
        soup = BeautifulSoup(text, "html.parser")
        return soup.get_text(separator=" ")  # Return cleaned text
    return text  # Return as-is if not a string

# Clean the DataFrame
df_cleaned = df.astype(str).applymap(clean_html)

import re

# Function to clean phone numbers
def clean_phone(phone):
    cleaned_phone = re.sub(r'\D', '', phone)  # Remove non-digit characters
    if len(cleaned_phone) == 10: 
        return cleaned_phone  # Return if valid length
    elif len(cleaned_phone) == 11 and cleaned_phone.startswith('1'): 
        return cleaned_phone[1:]  # Remove leading 1
    elif len(cleaned_phone) == 12 and cleaned_phone.startswith('+1'): 
        return cleaned_phone[2:]  # Remove leading +1
    else:
        return None  # Return None if invalid format

# Apply phone cleaning function to the DataFrame
df_cleaned['Phone'] = df_cleaned['Phone'].apply(clean_phone)

# Remove duplicate entries from the DataFrame
df_cleaned.drop_duplicates(inplace=True)

# Save the cleaned DataFrame to an Excel file
df_cleaned.to_excel('Data\clean_brokers_data.xlsx', index=False)

# Quit the WebDriver session
driver.quit()
