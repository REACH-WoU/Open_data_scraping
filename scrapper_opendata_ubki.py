import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from lxml import html
import re

#Link to hromada url
link_hromada = "https://opendatabot.ua/c/UA12020030000073022"

#Offset max number (you can take it at the end of last page link)
offset_max = 48

#Name of the final file
enterprices_file = 'enterprices_data_HromadaName.xlsx'


# Initialize Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# Setup webdriver with ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

def is_not_date(value):
    """Checks if the value is not a date in the format DD.MM.YYYY."""
    date_pattern = r"\d{2}\.\d{2}\.\d{4}"  # Format: 24.01.2025
    return not bool(re.fullmatch(date_pattern, value))

def scrape_opendatabot(website):
    """Scrapes company data from Opendatabot."""
    try:
        # Access the webpage
        driver.get(website)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//section/div[3]/div/article'))
        )

        # Parse the page source with lxml
        tree = html.fromstring(driver.page_source)
        company_elements = driver.find_elements(By.XPATH, '//article/div/div[1]/h4/a')

        data = []  # Initialize list to store company data
        for i, el in enumerate(company_elements):
            article_xpath = f'(//article)[{i + 1}]'

            # Extract EDRPOU code from the link
            edrpou_code = el.get_attribute('href').split('/')[-1]  # EDRPOU code is stored with leading zeros

            # Get company activity
            activity_xpath = f'{article_xpath}/div/p/text()'
            activity = tree.xpath(activity_xpath)
            activity_text = activity[0] if activity else None

            # Get company income and employee count
            income_xpath = f'{article_xpath}/div/div[2]/div[1]/span/text()'
            employees_xpath = f'{article_xpath}/div/div[2]/div[2]/span/text()'

            income_text = tree.xpath(income_xpath)
            employees_text = tree.xpath(employees_xpath)

            # Clean and assign values for income and employees
            income_value = income_text[0].strip() if income_text and is_not_date(income_text[0]) else None
            employees_value = employees_text[0].strip() if employees_text and is_not_date(employees_text[0]) else None

            # If income does not contain "грн", it means it's the number of employees
            if income_value and "грн" not in income_value:
                employees_value = income_value
                income_value = None

            # Append the data for the current company to the list
            data.append({
                'name': el.text,
                'edrpou_code': edrpou_code,
                'activity': activity_text,
                'income_2024': income_value,
                'number_of_employees': employees_value
            })

        return data

    except Exception as e:
        print(f"Error scraping {website}: {e}")
        return []  # Return an empty list if there is an error

if __name__ == "__main__":
    # Range of data offsets to scrape from the website
    i_all = range(0, offset_max + 12, 12)
    data_all = [scrape_opendatabot(f'{link_hromada}?offset={i}') for i in i_all]

    # Convert the list of data into a DataFrame
    data_df = pd.DataFrame(sum(data_all, []))
    print(f"Collected {len(data_df)} records from Opendatabot")

    # Ensure EDRPOU codes are in string format
    data_df["edrpou_code"] = data_df["edrpou_code"].astype(str)
    data_df.to_excel(enterprices_file, index=False)
    print(f"Saved into {enterprices_file}")

    # --- Scraping addresses from UBKI ---
    data_df["edrpou_code"] = data_df["edrpou_code"].astype(str)  # Ensure EDRPOU codes are in string format
    edrpou_codes = data_df["edrpou_code"].tolist()

    results = []
    for i in range(0, len(edrpou_codes), 50):  # Process in batches of 50 codes
        batch_codes = edrpou_codes[i:i + 50]

        for code in batch_codes:
            url = f"https://edrpou.ubki.ua/ua/{code}"
            driver.get(url)

            try:
                # Wait for the address element to be loaded using correct CSS selector
                address_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,
                                                    "#anchor_pitannya > div > div.dr_column.dr_padding_7 > div:nth-child(7) > div"))
                )
                address_text = address_element.text.split("за адресою:")[-1].strip()
            except Exception as e:
                address_text = "Not Found"
                print(f"Error retrieving address: {e}")

            # Parse the address to extract ADM4 name if available
            parsed_fragment = ""
            if " р-н," in address_text:
                try:
                    start = address_text.index(" р-н,") + len(" р-н,")
                    match = re.search(r",\s?[Вв][Уу][Лл]", address_text)
                    end = match.start() if match else None
                    parsed_fragment = address_text[start:end].strip()
                except:
                    parsed_fragment = ""

            # Append the result to the list
            results.append({
                "edrpou_code": code,
                "address": address_text,
                "ADM4_name": parsed_fragment
            })

        # Save data every 50 records processed
        results_df = pd.DataFrame(results)
        merged_df = data_df.merge(results_df, on="edrpou_code", how="left")
        merged_df.to_excel(enterprices_file, index=False)
        print(f"Processed {i + 50} records")

    # Close the browser after scraping is complete
    driver.quit()
    print(f"Done! Data has been saved into {enterprices_file}.")
