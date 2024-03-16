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
start_date = datetime(2024, 3, 11)
end_date = datetime(2024, 12, 31)

# Generate the list of dates
date_list = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range((end_date - start_date).days + 1)]
links = []
for date in date_list:
    url = f"https://dogodki.turizem-novagorica-vipavskadolina.si/sl/koledar-dogodkov/{date}"
    response = requests.get(url)
    # Ensure the request was successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the event elements - you need to adjust the selector
        events = soup.find_all('div', class_='event-grid')  

        for event in events:
            link = event.find('a')['href'] if event.find('a') is not None else None
            links.append('https://dogodki.turizem-novagorica-vipavskadolina.si' + link)

            # print(f"Event: {name}, Date: {date}, Location: {preberiVec}")

    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

for link in links:
    response = requests.get(link)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # extract the name
        name = soup.find('h1').get_text()

        detailsSection = soup.find('section', class_='container no-padding main-content')

        detailsDiv = detailsSection.find('div', class_='meta-data')
        # Extract details - adjust based on actual HTML structure
        location = detailsDiv.find('span', class_='location').get_text() if detailsDiv.find('span', class_='location') is not None else ''
        dateMain = detailsDiv.find('span', class_='date').get_text() if detailsDiv.find('span', class_='date') is not None else ''
        timeMain = detailsDiv.find('span', class_='hour').get_text() if detailsDiv.find('span', class_='hour') is not None else None
        
        dateMain = dateMain.strip()
        timeMain = timeMain.strip() if timeMain is not None else None

        date = ''
        startDate = ''
        endDate = ''

        if '-' not in dateMain:
            date_obj = datetime.strptime(dateMain, "%d.%m.%Y")

            # Format the datetime object to the desired format "Day, DD. Month YYYY"
            date = date_obj.strftime("%A, %d. %B %Y")
        else:
            date_obj1 = datetime.strptime(dateMain.split('-')[0].strip(), "%d.%m.%Y")
            formatted_date1 = date_obj1.strftime("%A, %d. %B %Y")
            date_obj2 = datetime.strptime(dateMain.split('-')[1].strip(), "%d.%m.%Y")
            formatted_date2 = date_obj2.strftime("%A, %d. %B %Y")

            date = formatted_date1 + ' - ' + formatted_date2

        if timeMain is not None and len(timeMain) > 0:
            if '-' not in timeMain:
                # Convert the original date string to the desired date format
                formatted_date = datetime.strptime(dateMain, "%d.%m.%Y").strftime("%Y-%m-%d")

                # Convert the original time string to the desired time format (with seconds)
                formatted_time = datetime.strptime(timeMain.strip(), "%H:%M").strftime("%H:%M:%S")

                startDate = formatted_date + "T" + formatted_time + "+01:00"
            else:
                
                # Convert the original date string to the desired date format
                formatted_date = datetime.strptime(dateMain, "%d.%m.%Y").strftime("%Y-%m-%d")

                # Convert the original time string to the desired time format (with seconds)
                formatted_time1 = datetime.strptime(timeMain.split('-')[0].strip(), "%H:%M").strftime("%H:%M:%S")
                formatted_time2 = datetime.strptime(timeMain.split('-')[1].strip(), "%H:%M").strftime("%H:%M:%S")

                startDate = formatted_date + "T" + formatted_time1 + "+01:00"
                endDate = formatted_date + "T" + formatted_time2 + "+01:00"

        description = detailsSection.find('p').get_text() if detailsSection.find('p') is not None else ''
        # Convert the original date string to a datetime object
        
        # Remove new lines and extra spaces
        name.strip()

        dataset.append({
                "Title": name,
                "Description": description,
                "Link": link,
                "Date": date,
                "StartDate": startDate,
                "EndDate": endDate,
                "Location": location
        })
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

# Convert to a Pandas DataFrame
df = pd.DataFrame(dataset, columns=['Title', 'Description', 'Link', 'Date', 'StartDate', 'EndDate', 'Location'])
# Save to a CSV file
df.to_csv("CsvFiles/DogodkiTurizemNovaGoricaVipavskaDolina2.csv", index=False, encoding='utf-8-sig')
