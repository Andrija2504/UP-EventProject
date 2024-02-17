import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime
import pytz

url = "https://loske-novice.si/category/dogaja"
response = requests.get(url)

namesList = []

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
while ShouldContinue:
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the event elements - you need to adjust the selector
    events = soup.find_all('div', class_='fusion-post-content post-content') 

    if(len(events) == 0):
        break
    for event in events:
        dateStr = event.find('span', class_='updated rich-snippet-hidden').get_text()
        date = datetime.fromisoformat(dateStr)
        current_datetime_utc = datetime.now(pytz.utc)

        if(date < current_datetime_utc):
            ShouldContinue = False
            break

        h3_tag = event.find('h2')
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

        details = event.find('p', class_='fusion-single-line-meta')
        detailsText = details.get_text()

        spans = details.find_all('span')
        for span in spans:
            detailsText = detailsText + span.get_text() + " "
            spansA = span.find_all('a')
            for a in spansA:
                detailsText = detailsText + a.get_text() + " "
            
        description = event.find('div', class_='fusion-post-content-container')
        descriptionText = ''

        ps = description.find_all('p')
        for p in ps:
            descriptionText = descriptionText + p.get_text() + " "


        # Append the data to the list
        namesList.append({
            "Name": formatted_name,
            "Link": link,  # Correct the key name here
            "Details": detailsText,
            "Description": descriptionText
        })

        # print(f"Event: {name}, Date: {date}, Location: {preberiVec}")
    
    if(ShouldContinue):
        url = f"https://loske-novice.si/category/dogaja/page/{i}"
        response = requests.get(url)
        ShouldContinue = response.status_code == 200
        i = i+1


# Convert to a Pandas DataFrame
df = pd.DataFrame(namesList, columns=['Name', 'Link', 'Details', 'Description'])
# Save to a CSV file
df.to_csv("LoskeNovice.csv", index=False, encoding='utf-8-sig')