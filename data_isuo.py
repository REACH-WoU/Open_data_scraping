import pandas as pd
import requests
from bs4 import BeautifulSoup
import os

oblast = "ДОН Дніпропетровської ОДА"
hromada = "Царичанська СТГ"
file_name = "test_edu_data_general.xlsx"


# Define the URL of the main page
url = "https://isuo.org/"  # Replace with the actual main page URL

# Send a GET request to fetch the HTML content
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    html_content = response.text
    print("Page fetched successfully!")
else:
    print(f"Failed to fetch the page. Status code: {response.status_code}")

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Find the link with the specific text
oblast_link = soup.find('a', string=oblast)

# Check if the link was found
if oblast_link:
    oblast_href = oblast_link.get('href')
    print(f"Found the link to {oblast}: {oblast_href}")
else:
    print("Link not found.")

# Construct the full URL
oblast_url = f"https:{oblast_href}"  # Assuming the link is relative, prepend "https:"

# Fetch the page for oblast
oblast_response = requests.get(oblast_url)

# Check if the request was successful
if oblast_response.status_code == 200:
    oblast_content = oblast_response.text
    print(f"Navigated to the {oblast} page successfully!")
else:
    print(f"Failed to navigate to the page. Status code: {oblast_response.status_code}")

# Parse the content of the oblast page
oblast_soup = BeautifulSoup(oblast_content, 'html.parser')

# Find the link to the specific hromada
hromada_link = oblast_soup.find('a', string=hromada)

# Check if the link was found
if hromada_link:
    hromada_href = hromada_link.get('href')
    print(f"Found the link to {hromada}: {hromada_href}")
else:
    print("Hromada link not found.")


# Correct the URL with double slashes after https:
hromada_url = f"https://isuo.org{hromada_href}"


# Fetch the page for hromada
hromada_response = requests.get(hromada_url)

# Check if the request was successful
if hromada_response.status_code == 200:
    drohobych_content = hromada_response.text
    print(f"Navigated to the {hromada} page successfully!")
else:
    print(f"Failed to navigate to the page. Status code: {hromada_response.status_code}")

# Send a GET request to fetch the HTML content
response = requests.get(hromada_url)

# Check if the request was successful
if response.status_code == 200:
    print("Page fetched successfully!")
    hromada_content = response.text
else:
    print(f"Failed to fetch the page. Status code: {response.status_code}")

# Parse the HTML content
soup = BeautifulSoup(hromada_content, 'html.parser')

# Define a dictionary to hold the extracted data
details = {}

# Extract all rows from the table
rows = soup.find_all('tr')

for row in rows:
    th = row.find('th')
    td = row.find('td')
    if th and td:
        key = th.get_text(strip=True).replace(':', '')
        value = td.get_text(strip=True)
        details[key] = value

# Print the extracted details
for k, v in details.items():
    print(f"{k}: {v}")

# Transform the dictionary to list of lists
data_list = [[k, v] for k, v in details.items()]

# Create a DataFrame from the list of lists
df = pd.DataFrame(data_list, columns=['Field', 'Value'])

## Export the DataFrame to an Excel file

df.to_excel(file_name, index=False)
print(f"Data exported to {file_name} successfully!")

# Fetch the Hromada page
response = requests.get(hromada_url)

# Check if the request was successful
if response.status_code == 200:
    print("Hromada page fetched successfully!")
    hromada_content = response.text
else:
    print(f"Failed to fetch the hromada page. Status code: {response.status_code}")

def get_urls(url):
    """
    Function to extract all  URLs from the given page.
    """
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []

        # Locate the table containing the list of schools/kindergartens
        table = soup.find('table', class_='zebra-stripe list')
        rows = table.find_all('tr')[1:]  # Skip the header row

        for row in rows:
            cols = row.find_all('td')
            if len(cols) > 1:
                a_tag = cols[1].find('a')
                if a_tag and a_tag['href']:
                    links.append(a_tag['href'])

        return links
    else:
        print(f"Failed to fetch the page. Status code: {response.status_code}")
        return []


def get_data(relative_url, base_url):
    """
    Function to extract data from a specific page.
    """
    full_url = f"{base_url}{relative_url}"  # Correct URL concatenation
    response = requests.get(full_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        details = {}

        # Extract data from the table rows
        rows = soup.find_all('tr')
        for row in rows:
            th = row.find('th')
            td = row.find('td')
            if th and td:
                key = th.get_text(strip=True).replace(':', '')
                value = td.get_text(strip=True)
                details[key] = value

        # Перевірка, чи працює заклад
        working_status = is_working(soup)
        details['Працює/Не працює'] = working_status

        return details
    else:
        print(f"Failed to fetch the page: {full_url}. Status code: {response.status_code}")
        return {}


def is_working(soup):
    # Шукаємо текст в елементі h3
    working_status_element = soup.select_one('#main-content > h3')

    if working_status_element:
        # Перевіряємо, чи містить текст "не працює"
        if 'не працює' in working_status_element.get_text().lower():
            return "Не працює"
        else:
            return "Працює"
    else:
        # Якщо елемент не знайдено, повертаємо "Не вказано"
        return "Не вказано"


def save_to_excel(data, filename, sheet_name):
    """
    Function to save the extracted data into an existing Excel file by adding a new sheet.

    Parameters:
    - data: The list of dictionaries containing data to save.
    - filename: The Excel file where data should be saved.
    - sheet_name: The name of the sheet where data should be written.
    """
    df = pd.DataFrame(data)

    # Check if the file exists
    file_exists = os.path.exists(filename)

    try:
        # Use ExcelWriter with openpyxl engine
        with pd.ExcelWriter(filename, engine='openpyxl', mode='a' if file_exists else 'w') as writer:
            if file_exists:
                # If the file exists, load the workbook
                print(f"Appending to the existing file: {filename}")
                # Get the existing sheet names
                existing_sheets = writer.book.sheetnames

                # Check if the sheet already exists
                if sheet_name in existing_sheets:
                    print(f"Sheet '{sheet_name}' already exists. Overwriting data in this sheet.")

                    # Remove the existing sheet to overwrite
                    idx = writer.book.sheetnames.index(sheet_name)
                    writer.book.remove(writer.book.worksheets[idx])

            # Write the dataframe to the specified sheet
            df.to_excel(writer, sheet_name=sheet_name, index=False)

        print(f"Data successfully saved to '{filename}' in sheet '{sheet_name}'.")

    except Exception as e:
        print(f"An unexpected error occurred while saving to Excel: {e}")

# Parse the HTML content of the Hromada page
soup = BeautifulSoup(hromada_content, 'html.parser')

# Locate the "ЗЗСО (школи)" link
schools_tab = soup.find('a', string='ЗЗСО (школи)')
if schools_tab:
    schools_href = schools_tab.get('href').strip()
    # Ensure the href does not start with a leading slash if base_url ends with a slash
    if schools_href.startswith('/'):
        schools_href = schools_href[1:]
    schools_url = f"{oblast_url}/{schools_href}"
    print(f"Schools page URL: {schools_url}")
else:
    print("Schools link not found!")

# Send a GET request to fetch the HTML content of the schools page
schools_response = requests.get(schools_url)

# Check if the request was successful
if schools_response.status_code == 200:
    print("Schools page fetched successfully!")
    schools_content = schools_response.text

    # Get school URLs from the schools page
    school_urls = get_urls(schools_url)

    # Fetch and store data for each school
    school_data_list = []
    for school_url in school_urls:
        data = get_data(school_url, oblast_url)
        if data:
            school_data_list.append(data)

    # Save schools data to Excel
    save_to_excel(school_data_list, filename=file_name, sheet_name="Schools")
else:
    print(f"Failed to fetch the schools page. Status code: {schools_response.status_code}")

# Locate the "ЗДО (дошкілля)" link
kindergartens_tab = soup.find('a', string='ЗДО (дошкілля)')
if kindergartens_tab:
    kindergartens_href = kindergartens_tab.get('href').strip()
    # Ensure the href does not start with a leading slash if base_url ends with a slash
    if kindergartens_href.startswith('/'):
        kindergartens_href = kindergartens_href[1:]
    kindergartens_url = f"{oblast_url}/{kindergartens_href}"
    print(f"Kindergartens page URL: {kindergartens_url}")
else:
    print("Kindergartens link not found!")

# Send a GET request to fetch the HTML content of the kindergartens page
kindergartens_response = requests.get(kindergartens_url)

# Check if the request was successful
if kindergartens_response.status_code == 200:
    print("Kindergartens page fetched successfully!")
    kindergartens_content = kindergartens_response.text

    # Get kindergarten URLs from the kindergartens page
    kindergartens_urls = get_urls(kindergartens_url)

    # Fetch and store data for each kindergarten
    kindergartens_data_list = []
    for kindergarten_url in kindergartens_urls:
        data = get_data(kindergarten_url, oblast_url)
        if data:
            kindergartens_data_list.append(data)

    # Save kindergartens data to Excel
    save_to_excel(kindergartens_data_list, filename=file_name, sheet_name="Kindergartens")
else:
    print(f"Failed to fetch the kindergartens page. Status code: {kindergartens_response.status_code}")

# Locate the "ЗПО(позашкілля)" link
out_schools_tab = soup.find('a', string='ЗПО(позашкілля)')
if out_schools_tab:
    out_schools_href = out_schools_tab.get('href').strip()
    # Ensure the href does not start with a leading slash if base_url ends with a slash
    if out_schools_href.startswith('/'):
        out_schools_href = out_schools_href[1:]
    out_schools_url = f"{oblast_url}/{out_schools_href}"
    print(f"Out of school institutions page URL: {out_schools_url}")

    # Send a GET request to fetch the HTML content of the out-of-school institutions page
    out_schools_response = requests.get(out_schools_url)

    # Check if the request was successful
    if out_schools_response.status_code == 200:
        print("Out of school institutions page fetched successfully!")
        out_schools_content = out_schools_response.text

        # Get URLs from the out-of-school institutions page
        out_schools_urls = get_urls(out_schools_url)

        # Fetch and store data for each institution
        out_schools_data_list = []
        for url in out_schools_urls:
            data = get_data(url, oblast_url)
            if data:
                out_schools_data_list.append(data)

        # Save out-of-school institutions data to Excel
        save_to_excel(out_schools_data_list, filename=file_name, sheet_name="Out of school institutions")
    else:
        print(f"Failed to fetch the out-of-school institutions page. Status code: {out_schools_response.status_code}")
else:
    print("Out of school institutions link not found!")
# Inclusive centers data
# ---------------------------

# Locate the "ІРЦ" link
inclusive_tab = soup.find('a', string='ІРЦ')
if inclusive_tab:
    inclusive_href = inclusive_tab.get('href').strip()
    # Ensure the href does not start with a leading slash if base_url ends with a slash
    if inclusive_href.startswith('/'):
        inclusive_href = inclusive_href[1:]
    inclusive_url = f"{oblast_url}/{inclusive_href}"
    print(f"Inclusive centers page URL: {inclusive_url}")

    # Send a GET request to fetch the HTML content of the inclusive centers page
    inclusive_response = requests.get(inclusive_url)

    # Check if the request was successful
    if inclusive_response.status_code == 200:
        print("Inclusive centers page fetched successfully!")
        inclusive_content = inclusive_response.text

        # Get inclusive centers URLs from the inclusive centers page
        inclusive_urls = get_urls(inclusive_url)

        # Fetch and store data for each inclusive center
        inclusive_data_list = []
        for url in inclusive_urls:
            data = get_data(url, oblast_url)
            if data:
                inclusive_data_list.append(data)

        # Save inclusive centers data to Excel
        save_to_excel(inclusive_data_list, filename=file_name, sheet_name="Inclusive centers")

    else:
        print(f"Failed to fetch the inclusive centers page. Status code: {inclusive_response.status_code}")
else:
    print("Inclusive centers link not found!")

