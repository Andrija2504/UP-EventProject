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
from selenium.webdriver.common.action_chains import ActionChains

url = "https://dogodki.kulturnik.si/"
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
driver.get("https://dogodki.kulturnik.si/")

# Wait for the page to load (you can use explicit waits with WebDriverWait if necessary)

# Assume 'container_id' is the ID of the div that contains the button you want to click
container_id = 'eventsUpcoming'  # Replace with the actual ID of the div

# Initialize an item count to track the number of items loaded
item_count = 0

# Loop to click the 'Load More' link repeatedly
while True:
    try:
        # Find the div by its ID
        container = driver.find_element(By.ID, container_id)

        # Within this container, find the 'Load More' button
        load_more_button = WebDriverWait(container, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'continue'))
        )

        # Click the 'Load More' button
        load_more_button.click()

        # After clicking, you may want to wait for a new set of items to be loaded
        # Here we wait for the number of items to increase
        WebDriverWait(driver, 10).until(
            lambda d: len(d.find_elements(By.CLASS_NAME, 'day-list-wrapper')) > item_count
        )
        
        # Update the item count with the new count
        item_count = len(driver.find_elements(By.CLASS_NAME, 'day-list-wrapper'))
    except TimeoutException:
        # If the 'Load More' link isn't found, exit the loop
        print("No more 'Load More' links to be clicked, or loading took too much time.")
        break


html = driver.page_source
# You can now parse this HTML with BeautifulSoup or perform actions with Selenium
# ...

ShouldContinue = True

# Parse the page source with BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

# Find the event elements - you need to adjust the selector
upcomingEvents = soup.find('section', id='eventsUpcoming')

divs = upcomingEvents.find_all('div', class_='day-list-wrapper')

dataset = []    
for div in divs:
    date = div.find('h2').get_text(strip = True) #

    allEventDays = div.find_all('div', class_='day-list')
    for event in allEventDays:
        time = event.find('span', class_='human_date').get_text() if event.find('span', class_='human_date') is not None else ''  # time of event
        eventsPerDay = event.select('article.item.vevent')

        for eventInDay in eventsPerDay:
            detailsDiv = eventInDay.find('div', class_='labels')
            h2_tag = detailsDiv.find('h2') 
            links = ''

            if h2_tag:  # Check if the h3 tag is fou    2nd
                name = h2_tag.get_text(strip=True) # name of event
                # Find the link within the h3 tag
                a_tag = h2_tag.find('a')
                nameLink = ''
                if a_tag and 'href' in a_tag.attrs:  # Check if the a tag is found and has an href attribute
                    nameLink = a_tag['href'] # link to a page
                else:
                    nameLink = ''
            
            links = links + nameLink + "\n"
            
            infolocationDiv = eventInDay.find('div', class_='info location')
            aLinks = infolocationDiv.find_all('a')
            locationInfo = ''
            for a in aLinks:
                locationInfo = locationInfo + a.get_text() + '\n'
                if a.has_attr('href'):
                    links = links + 'https://dogodki.kulturnik.si/' + a['href'] + "\n"
            
            links = links.strip()
            locationInfo = locationInfo.strip()

            hiddenDiv = infolocationDiv.find('div', class_='hidden')
            startDate = hiddenDiv.find('time', class_='dtstart').get_text() if hiddenDiv.find('time', class_='dtstart') is not None else ''
            endDate = hiddenDiv.find('time', class_='dtend').get_text() if hiddenDiv.find('time', class_='dtend') is not None else ''

            # Clean the name
            formatted_name = re.sub(r'\s+', ' ', name)

            dataset.append({
                "Title": formatted_name,
                "Description": '',
                "Link": links,
                "Date": date,
                "StartDate": startDate,
                "EndDate": endDate,
                "Location": locationInfo
            })

# Convert to a Pandas DataFrame
df = pd.DataFrame(dataset, columns=['Title', 'Description', 'Link', 'Date', 'StartDate', 'EndDate', 'Location'])
# Save to a CSV file
df.to_csv("CsvFiles/DogodtkiKulturnik2.csv", index=False, encoding='utf-8-sig')

# Close the browser
driver.quit()