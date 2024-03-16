import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

url = "https://www.visitskofjaloka.si/si/dogodki"
response = requests.get(url)

listToPrint = []

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

# Ensure the request was successful
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the event elements - you need to adjust the selector
    event_list_day = soup.find_all('div', class_='event-list-day')  

    for days in event_list_day:

        day = days.find('div', class_='date').get_text()
        events_per_day = days.find_all('div', class_='event-list-item')

        for event in events_per_day:
            startDate = ''
            timeOfEvent = event.find('div', class_='event-time').get_text() if event.find('div', class_='event-time') is not None else ''
            if timeOfEvent and len(timeOfEvent) != 0 and timeOfEvent != '-':
                startDate = day + '---' + timeOfEvent
            
            # Extract details - adjust based on actual HTML structure
            if (event.find('h2') is not None):
                title = event.find('h2').get_text()
            else:
                continue
            details = event.find('div', class_='event-details')

            detailLocation = details.find('span', 'event-details-location').get_text() if details.find('span', 'event-details-location') is not None else ''
            detailAddress = details.find('span', 'event-details-address').get_text() if details.find('span', 'event-details-address') is not None else ''
            location = detailLocation + '\n' + detailAddress

            tip = ("Tip: " + details.find('span', 'event-details-type').get_text()) if details.find('span', 'event-details-type') is not None else ''
            
            descriptions = event.find('div', class_='event-description')
            description = ''

            ps = descriptions.find_all('p')
            for p in ps:
                description = description + p.get_text() + "\n"

            divs = descriptions.find_all('div')
            for div in divs:
                description = description + div.get_text() + "\n"

            listToPrint.append({
                "Title": title,
                "Description": description,
                "Link": None,
                "Date": day,
                "StartDate": startDate,
                "EndDate": None,
                "Location": location,
            })

            # print(f"Event: {name}, Date: {date}, Location: {preberiVec}")

else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

# Convert to a Pandas DataFrame
df = pd.DataFrame(listToPrint, columns=['Title', 'Description', 'Link', 'Date', 'StartDate', 'EndDate', 'Location'])
# Save to a CSV file
df.to_csv("CsvFiles/VisitSkofjaloka2.csv", index=False, encoding='utf-8-sig')
