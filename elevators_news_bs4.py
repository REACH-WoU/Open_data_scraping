import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd

# Create a folder for images
image_folder = "image_folder_name"
os.makedirs(image_folder, exist_ok=True)

#Chose the category of news from list:
"""
Зерно - zerno, 
Сільгосптехніка - selhoztehnika,
Елеватори - elevatory,
Тваринництво - zhivotnovodstvo,
Компанії - kompanii,
Агрономія - agronomiya,
Транспорт - transport,
Світ - mir,
Загальні - ukraina
"""
category = "category_name"

# Base URL format with page number
base_url = f"https://tripoli.land/ua/news/{category}?category_slug={category}&page={{}}"

#Base url for all news for news categories
#base_url = f"https://tripoli.land/ua/news?page={{}}"

#Last page number
last_page = 100

#Name of output
file_name = "file_name.xlsx"


# Headers to prevent blocking
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

# Function to get the HTML content of a page
def get_soup(url):
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return BeautifulSoup(response.text, "html.parser")
    else:
        print(f"[WARNING] Failed to fetch {url} (Status code: {response.status_code})")
        return None


news_links = set()  # Use a set to store unique news links

# Collect news links from pages (range should be on one number bigger than last page number)
for page in range(1, last_page + 1):
    current_url = base_url.format(page)
    print(f"Fetching page: {current_url}")

    soup = get_soup(current_url)
    if not soup:
        continue

    # Find news article links
    article_elements = soup.select("article a")
    for element in article_elements:
        href = element.get("href")
        if href:
            full_link = urljoin(base_url, href)
            news_links.add(full_link)  # Set automatically removes duplicates

print(f"Found {len(news_links)} unique news articles.")

# Collect data from each unique news article
news_data = []
for news_id, link in enumerate(news_links, start=1):  # Assign unique IDs sequentially
    print(f"Processing [{news_id}]: {link}")
    soup = get_soup(link)
    if not soup:
        continue

    try:
        # Extract title
        title_element = soup.select_one("body > content > div.container.maincontent > h1")
        title = title_element.text.strip() if title_element else "No Title"

        # Extract publication date
        date_element = soup.select_one("body > content > div.container.maincontent > div.big-date")
        date = date_element.text.strip().replace("Опубліковано ", "") if date_element else "No Date"

        # Extract news text
        text_elements = soup.select("body > content > div.container.maincontent > div.row.news-content p")
        text = "\n".join(p.text.strip() for p in text_elements) if text_elements else "No Content"

        # Download and save image
        image_filename = None
        image_element = soup.select_one(
            "body > content > div.container.maincontent > div.row.tiding-image-center > img")
        if image_element and "src" in image_element.attrs:
            image_url = urljoin(link, image_element["src"])
            print(f"  [INFO] Image URL: {image_url}")

            response = requests.get(image_url, headers=HEADERS, stream=True)
            if response.status_code == 200:
                image_filename = f"{news_id}.jpg"  # Save image as ID.jpg
                image_path = os.path.join(image_folder, image_filename)

                with open(image_path, "wb") as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)
                print(f"  [IMAGE SAVED] {image_filename}")
            else:
                print(f"  [WARNING] Image could not be downloaded. HTTP Status: {response.status_code}")

    except Exception as e:
        print(f"  [ERROR] Error processing {link}: {e}")
        continue

    # Save the news data
    news_data.append({
        "ID": news_id,
        "Title": title,
        "Publication Date": date,
        "Text": text,
        "Image File": image_filename if image_filename else "No Image",
        "Link": link
    })

# Save data to Excel file
df = pd.DataFrame(news_data)
df.to_excel(file_name, index=False)

print(f"✅ Data saved to file {file_name}")
