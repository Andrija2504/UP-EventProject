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

url = "https://www.slovenia.info/sl/dozivetja/dogodki"
response = requests.get(url)

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

# Setup Edge options
options = Options()
options.use_chromium = True
options.add_argument('--log-level=3')  # This sets the logging level to CRITICAL
# options.add_argument("headless")  # Optional argument to run Edge in headless mode
# options.add_argument("disable-gpu")  # Optional argument to disable GPU (useful for headless mode)

# Path to the Edge WebDriver executable
driver_path = 'C:\\Users\\andri\\Downloads\\edgedriver_win32\\msedgedriver.exe'

# Initialize the Edge driver
service = Service(driver_path)
driver = webdriver.Edge(service=service, options=options)

# Go to the web page
driver.get("https://www.slovenia.info/sl/dozivetja/dogodki")

# Wait for the page to load (you can use explicit waits with WebDriverWait if necessary)
driver.implicitly_wait(10)
try:
    # Now you can access the page source after JavaScript has been executed
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'post-card')))
    html = driver.page_source
except TimeoutException:
    print("Timed out waiting for page to load")
    # Handle the situation (like breaking the loop, logging, etc.)
    # ...

# You can now parse this HTML with BeautifulSoup or perform actions with Selenium
# ...

ShouldContinue = True

while ShouldContinue:
    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Find the event elements - you need to adjust the selector
    events = soup.find_all('div', class_='post-card linkBlock item slide') 

    if(len(events) == 0):
        ShouldContinue = False
        break

    for event in events:
        h3_tag = event.find('h3')
        if h3_tag:  # Check if the h3 tag is found
            name = h3_tag.get_text(strip=True)

            # Find the link within the h3 tag
            a_tag = h3_tag.find('a')
            if a_tag and 'href' in a_tag.attrs:  # Check if the a tag is found and has an href attribute
                link = a_tag['href']
            else:
                link = None

            # Clean the name
            formatted_name = re.sub(r'\s+', ' ', name)

            # Append the data to the list
            linksList.append(link)

        # print(f"Event: {name}, Date: {date}, Location: {preberiVec}")
            
    try:
        # Go to the web page
        driver.get(f"https://www.slovenia.info/sl/dozivetja/dogodki?locale=sl&page={i}")

        # Wait for the page to load (you can use explicit waits with WebDriverWait if necessary)
        driver.implicitly_wait(10)
        # Now you can access the page source after JavaScript has been executed
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'post-card')))
        html = driver.page_source
    except TimeoutException:
        ShouldContinue = False
        print("Timed out waiting for page to load")
        # Handle the situation (like breaking the loop, logging, etc.)
        # ...
    i = i+1

dataset = []

for item in linksList:
    # Go to the web page
    driver.get(f'https://www.slovenia.info{item}')

    # Wait for the page to load (you can use explicit waits with WebDriverWait if necessary)
    driver.implicitly_wait(10)
    try:
        # Now you can access the page source after JavaScript has been executed
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'newsDetail')))
        html = driver.page_source
    except TimeoutException:
        print("Timed out waiting for page to load")
        # Handle the situation (like breaking the loop, logging, etc.)
        # ...

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Find the event elements - you need to adjust the selector
    page = soup.find('div', class_='newsDetail') 

    infoDiv = page.find('div', class_='greenBox')
    infoSpans = infoDiv.find_all('span')
    infoText = ''
    infoLink = ''
    mapLink = ''
    i = 0
    while i < len(infoSpans):
        formattedText = re.sub(r'\s+', ' ', infoSpans[i].get_text())
        if("Več informacij" in formattedText):
            a_tag = infoSpans[i].find('a')
            if a_tag and 'href' in a_tag.attrs:  # Check if the a tag is found and has an href attribute
                infoLink = a_tag['href']
            else:
                infoLink = None
        else:
            if('Kraj:' in formattedText):
                a_tag = infoSpans[i].find('a')
                if a_tag and 'href' in a_tag.attrs:  # Check if the a tag is found and has an href attribute
                    mapLink = a_tag['href']
                else:
                    mapLink = None
            infoText = infoText + " " + formattedText + "\n"
        i = i + 1

    contentDiv = page.find('div', class_='news-content')
    h1_tag = contentDiv.find('h1')
    title = ''
    if h1_tag:
        title = h1_tag.get_text()
    else:
        title = None

    summaryDiv = contentDiv.find('div', class_='summary')
    description = ''
    if summaryDiv:
        description = summaryDiv.get_text()

    summaryPs = contentDiv.find_all('p', class_=lambda x: x != 'btnBack')
    for p in summaryPs:
        description = description + " " + p.get_text()

    dataset.append({
        "Title": title,
        "Details": infoText,
        "Maplink": mapLink,
        "Description": description,
        "Link": infoLink
    })
    

# Convert to a Pandas DataFrame
df = pd.DataFrame(dataset, columns=['Title', 'Details', 'Maplink', 'Description', "Link"])
# Save to a CSV file
df.to_csv("SloveniaInfo.csv", index=False, encoding='utf-8-sig')

# Close the browser
driver.quit()