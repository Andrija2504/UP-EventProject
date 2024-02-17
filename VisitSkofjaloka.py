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
            # Extract details - adjust based on actual HTML structure
            if (event.find('h2') is not None):
                title = event.find('h2').get_text()
            else:
                continue
            details = event.find('div', class_='event-details')
            detailsText = ''

            spans = details.find_all('span')
            for span in spans:
                detailsText = detailsText + span.get_text() + " "
            
            descriptions = event.find('div', class_='event-description')
            descriptionText = ''

            ps = descriptions.find_all('p')
            for p in ps:
                descriptionText = descriptionText + p.get_text() + "\n"

            divs = descriptions.find_all('div')
            for div in divs:
                descriptionText = descriptionText + div.get_text() + "\n"

            listToPrint.append({
                "Name": title,
                "Date": day,
                "Details": detailsText,
                "Description": descriptionText
            })

            # print(f"Event: {name}, Date: {date}, Location: {preberiVec}")

else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

# Ensure the request was successful
# if response.status_code == 200:
#     soup = BeautifulSoup(response.text, 'html.parser')

#     # Find the event elements - you need to adjust the selector
#     events_per_day = soup.find_all('div', class_='event-list-item')  

#     for event in events_per_day:
#         # Extract details - adjust based on actual HTML structure
#         if (event.find('h2') is not None):
#             title = event.find('h2').get_text()
#         else:
#             continue

#         details = event.find('div', class_='event-details')
#         detailsText = ''

#         spans = details.find_all('span')
#         for span in spans:
#             detailsText = detailsText + span.get_text() + " "
        
#         descriptions = event.find('div', class_='event-description')
#         descriptionText = ''

#         ps = descriptions.find_all('p')
#         for p in ps:
#             descriptionText = descriptionText + p.get_text() + "\n"

#         divs = descriptions.find_all('div')
#         for div in divs:
#             descriptionText = descriptionText + div.get_text() + "\n"

#         listToPrint.append({
#             "Name": title,
#             "Date": "1/1/1900",
#             "Details": detailsText,
#             "Description": descriptionText
#         })

#         # print(f"Event: {name}, Date: {date}, Location: {preberiVec}")

# else:
#     print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

# Convert to a Pandas DataFrame
df = pd.DataFrame(listToPrint, columns=['Name', 'Date', 'Details', 'Description'])
# Save to a CSV file
df.to_csv("VisitSkofjaloka.csv", index=False, encoding='utf-8-sig')
