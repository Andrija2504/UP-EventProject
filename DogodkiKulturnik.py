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

    eventsPerDay = div.find_all('div', class_='day-list')
    for event in eventsPerDay:
        time = event.find('span', class_='human_date').get_text()
        detailsDiv = event.find('div', class_='labels')
        h2_tag = detailsDiv.find('h2')
        if h2_tag:  # Check if the h3 tag is found
            name = h2_tag.get_text(strip=True) #
            # Find the link within the h3 tag
            a_tag = h2_tag.find('a')
            if a_tag and 'href' in a_tag.attrs:  # Check if the a tag is found and has an href attribute
                link = a_tag['href'] #
            else:
                link = None
        
        infoDiv = event.find('div', class_='info location')
        infoDivs = infoDiv.find_all('div')
        infoText = ' '.join(div.get_text() for div in infoDivs)
        linksInInfoDiv = infoDiv.find_all('a')

        # Append the text from each link to infoText
        for linkInInfoDiv in linksInInfoDiv:
            link_text = linkInInfoDiv.get_text(strip=True)
            if link_text:  # Check if the link has text
                infoText += ' ' + link_text

        
        # Join all 'href' attributes of 'a' tags in 'linksInInforDiv' by '-'
        infoLinks = '-'.join('https://dogodki.kulturnik.si/' + a_tagInInfoDiv['href'] for a_tagInInfoDiv in linksInInfoDiv if a_tagInInfoDiv and a_tagInInfoDiv.has_attr('href'))

        # Clean the name
        formatted_name = re.sub(r'\s+', ' ', name)

        dataset.append({
            "Title": formatted_name,
            "Details": infoText,
            "InfoLinks": infoLinks,
            "LinkToPage": link,
            "Date": date
        })
        


    

# Convert to a Pandas DataFrame
df = pd.DataFrame(dataset, columns=['Title', 'Details', 'InfoLinks', 'LinkToPage', "Date"])
# Save to a CSV file
df.to_csv("DogodtkiKulturnik.csv", index=False, encoding='utf-8-sig')

# Close the browser
driver.quit()