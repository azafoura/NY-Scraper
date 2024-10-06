
# Real Estate Broker Scraper

This project is a web scraping tool designed to extract real estate agent profiles (both individual brokers and teams) from the Corcoran real estate website. The script uses **Selenium** and **BeautifulSoup** to automate browser interactions and parse the HTML to collect broker information, saving it into an Excel file.

## Features
- Scrapes individual brokers and teams.
- Handles automatic pagination until all brokers are scraped.
- Extracts broker names, emails, and phone numbers.
- Cleans and formats phone numbers for consistency.
- Saves data in an Excel file (`clean_brokers_data.xlsx`).

## Technologies Used
- **Python 3.10+**
- **Selenium** for browser automation.
- **BeautifulSoup** for HTML parsing.
- **Pandas** for data manipulation and Excel output.
- **Microsoft Edge WebDriver** (ensure it's compatible with your browser version).

## Requirements
1. **Microsoft Edge** (or modify to use another browser).
2. **Edge WebDriver**.
3. **Python** and the following libraries:
    - `selenium`
    - `bs4` (BeautifulSoup)
    - `pandas`
    - `openpyxl`

Install the dependencies using:
```bash
pip install -r requirements.txt
```

## Setup
1. **Clone the repository**:
    ```bash
    git clone https://github.com/azafoura/NY-Scraper.git
    cd NY-Scraper
    ```

2. **Download and set up Edge WebDriver**:
    - Download the WebDriver from [here](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/).
    - Place `msedgedriver.exe` in the project folder or ensure it's in your system path.

3. **Run the scraper**:
    ```bash
    python Broker_scraper.py
    ```

4. **Check the Excel output**:
    - The scraped data will be saved in `clean_brokers_data.xlsx`.

## Usage
- **Broker Information**: Scrapes the broker's name, email, and phone number.
- **Team Handling**: Detects team profiles and scrapes individual team members.
- **Pagination**: Automatically clicks the next button until no more pages remain.
- **Phone Formatting**: Cleans phone numbers to ensure they are in a standardized format (removes country code if unnecessary).

## Customizing the Base URL for Different Regions

To scrape brokers from regions other than New York City, follow these steps:

1. Visit [Corcoran Real Estate Agents Search](https://www.corcoran.com/real-estate-agents/search).
2. Search for the desired region by entering the city or area in the search bar.
3. Once the search results are displayed, copy the URL from the address bar.
4. Update the `base_url` variable in the script with the copied link:

   ```python
   base_url = '<copied-link>'


## Output
- The final output is an Excel file, `clean_brokers_data.xlsx`, which contains cleaned and de-duplicated broker data.

## WebDriver Notice
Ensure that `msedgedriver.exe` is included in the project.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

