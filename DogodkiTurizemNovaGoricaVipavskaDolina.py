import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime, timedelta

url = "https://dogodki.turizem-novagorica-vipavskadolina.si/"
response = requests.get(url)

dataset = []

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

# Define the start and end dates
start_date = datetime(2024, 2, 1)
end_date = datetime(2024, 12, 31)

# Generate the list of dates
date_list = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range((end_date - start_date).days + 1)]

for date in date_list:
    url = f"https://dogodki.turizem-novagorica-vipavskadolina.si/sl/koledar-dogodkov/{date}"
    response = requests.get(url)
    # Ensure the request was successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the event elements - you need to adjust the selector
        events = soup.find_all('div', class_='event-grid')  

        for event in events:
            # Extract details - adjust based on actual HTML structure
            location = event.find('span', class_='location').get_text() if event.find('span', class_='location') is not None else None
            date = event.find('span', class_='date').get_text() if event.find('span', class_='date') is not None else None
            time = event.find('span', class_='hour').get_text() if event.find('span', class_='hour') is not None else None
            dateTime = date + " " + time
            name = event.find('h2').get_text()
            # Remove new lines and extra spaces
            formatted_name = re.sub(r'\s+', ' ', name.strip())

            link = event.find('a')['href'] if event.find('a') is not None else None
            dataset.append({
                "Eventname": formatted_name,
                "Date": dateTime,
                "Location": location,
                "Link": link
            })

            # print(f"Event: {name}, Date: {date}, Location: {preberiVec}")

    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

# Convert to a Pandas DataFrame
df = pd.DataFrame(dataset, columns=['Eventname', 'Date', 'Location', "Link"])
# Save to a CSV file
df.to_csv("DogodkiTurizemNovaGoricaVipavskaDolina.csv", index=False, encoding='utf-8-sig')
