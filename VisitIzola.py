import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

url = "https://www.visitizola.com/dogodki"
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

# Ensure the request was successful
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the event elements - you need to adjust the selector
    events = soup.find_all('a', class_='eventsWrapp')  

    for event in events:
        # Extract details - adjust based on actual HTML structure
        date = event.find('div', class_='datum fSize70 letterSpacing007').get_text()  
        name = event.find('div', class_='imeZvrstWrapp').get_text()  
        preberiVec = event.find('div', class_='link').get_text()  

        # Remove new lines and extra spaces
        formatted_name = re.sub(r'\s+', ' ', name.strip())

        formatted_name = formatted_name.replace(', ', '')
        formatted_name = formatted_name.replace(',', '')

        # Replace special characters with space (except for alphanumeric characters and spaces)
        formatted_name = re.sub(r'[^\w\s+]', '', formatted_name)

        # Use the replace_chars function to substitute characters
        formatted_name = char_re.sub(replace_chars, formatted_name)

        # Split into words and filter out any empty strings
        words = [word for word in formatted_name.split(' ') if word]

        # Rejoin words with hyphens
        clean_title = '-'.join(words).lower()

        namesList.append(clean_title)

        # print(f"Event: {name}, Date: {date}, Location: {preberiVec}")

else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

# print(namesList)
    
listPerEvent = []

for item in namesList:
    url = "https://www.visitizola.com/dogodki/" + item
    response = requests.get(url)
    # Ensure the request was successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the event elements - you need to adjust the selector
        titleInfo = soup.find('section', class_='clanekFotoTitle')  # title
        descriptionDiv = soup.find('div', class_='clanekVsebina')
        # Find all <p> elements within this div
        paragraphs = descriptionDiv.find_all('p')

        #print(item, " sadsa ", descriptionDiv)
        #input("Ajde")

        title = titleInfo.find('h1').get_text()  

        date = descriptionDiv.find('div', class_='upper baskerville fSize40 fw400 letterSpacing01').get_text()  
        location = descriptionDiv.find('span', class_='fw500').get_text() if descriptionDiv.find('span', class_='fw500') is not None else None  
        description = ''
        i = 0
        while i < len(paragraphs):
            if i != 0:
                description = description + "\n" + paragraphs[i].get_text(strip = True)
            i = i + 1

        link = ''

        if "Več informacij" in descriptionDiv.get_text():
            if descriptionDiv.find('a', class_='baskerville aniLink fSize30') is not None:
                link = descriptionDiv.find('a', class_='baskerville aniLink fSize30')['href']

        # Remove new lines and extra spaces
        title = re.sub(r'\s+', ' ', title.strip())

        listPerEvent.append({
            "Eventname": title, 
            "Date": date, 
            "Location": location,
            "Description": description,
            "Link": link
        })

    else:
        print(item)
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

# Convert to a Pandas DataFrame
df = pd.DataFrame(listPerEvent, columns=['Eventname', 'Date', 'Location', 'Description', "Link"])
# Save to a CSV file
df.to_csv("VisitIzola.csv", index=False, encoding='utf-8-sig')
