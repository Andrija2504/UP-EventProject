import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Setup Edge options
# options = Options()
# options.use_chromium = True
# options.add_argument('--log-level=3')  # This sets the logging level to CRITICAL
# # options.add_argument("headless")  # Optional argument to run Edge in headless mode
# # options.add_argument("disable-gpu")  # Optional argument to disable GPU (useful for headless mode)

# # Path to the Edge WebDriver executable
# driver_path = 'C:\\Users\\andri\\Downloads\\edgedriver_win32\\msedgedriver.exe'

# # Initialize the Edge driver
# service = Service(driver_path)
# driver = webdriver.Edge(service=service, options=options)

# # Go to the web page
# driver.get("https://www.mojaobcina.si/aktualno/dogodki/")

# # Wait for the page to load (you can use explicit waits with WebDriverWait if necessary)
# driver.implicitly_wait(10)
# try:
#     # Now you can access the page source after JavaScript has been executed
#     WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'glavna-vsebina-clean glavna-vsebina-dogodek')))
#     html = driver.page_source
# except TimeoutException:
#     print("Timed out waiting for page to load")
#     # Handle the situation (like breaking the loop, logging, etc.)
#     # ...

url = "https://www.mojaobcina.si/aktualno/dogodki/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
response = requests.get(url, headers=headers)

linksList = []

char_map = {
    'š': 's',
    'č': 'c',
    'ć': 'c',
    'ž': 'z',
    'đ': 'd',
    'Š': 's',
    'Č': 'c',
    'Ć': 'c',
    'Ž': 'z',
    'Đ': 'd',
    'á': 'a',
    'è': 'e'
}

# Create a regular expression from the keys of the mapping
char_re = re.compile("(%s)" % "|".join(map(re.escape, char_map.keys())))

# Function to replace characters based on the above mapping
def replace_chars(match):
    return char_map[match.group(0)]

i = 2
ShouldContinue = True

while ShouldContinue and response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the event elements - you need to adjust the selector
    events = soup.find('main')  

    articles = events.find_all('article')

    if(len(articles) == 0):
        ShouldContinue = False
    for article in articles:
        # Extract details - adjust based on actual HTML structure
        h3_tag = article.find('h3')
        link = ''
        if h3_tag:
            if h3_tag.find('a'):
                link = h3_tag.find('a')['href']

        linksList.append(link)

        # print(f"Event: {name}, Date: {date}, Location: {preberiVec}")

    url = f"https://www.mojaobcina.si/aktualno/dogodki/?p={i}"
    response = requests.get(url, headers=headers)

    i = i+1

else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

print(len(linksList))
    
listPerEvent = []
input("aaa")

# Convert to a Pandas DataFrame
df = pd.DataFrame(listPerEvent, columns=['Eventname', 'Date', 'Location', 'Description', "Link"])
# Save to a CSV file
df.to_csv("VisitIzola.csv", index=False, encoding='utf-8-sig')
