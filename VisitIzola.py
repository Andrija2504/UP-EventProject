import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime, timedelta

url = "https://www.visitizola.com/dogodki"
response = requests.get(url)

links = []

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
        
        links.append('https://www.visitizola.com' + event['href'])

        # print(f"Event: {name}, Date: {date}, Location: {preberiVec}")

else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

# print(namesList)
    
dataset = []

for item in links:
    response = requests.get(item)
    # Ensure the request was successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the event elements - you need to adjust the selector
        titleInfoSection = soup.find('section', class_='clanekFotoTitle')  # title
        title = titleInfoSection.find('h1').get_text().strip()

        descriptionDiv = soup.find('div', class_='clanekVsebina')

        dateMain = descriptionDiv.find('div', class_='upper baskerville fSize40 fw400 letterSpacing01').get_text() if  descriptionDiv.find('div', class_='upper baskerville fSize40 fw400 letterSpacing01') is not None else ''
        dateMain = dateMain.strip()
        if '-' not in dateMain:
            date_obj = datetime.strptime(dateMain, "%d/%m/%y")

            # Format the datetime object to the desired format "Day, DD. Month YYYY"
            date = date_obj.strftime("%A, %d. %B %Y")
        else:
            firstDate = dateMain.split('-')[0].strip()
            secondDate = dateMain.split('-')[1].strip()

            if len(firstDate) == 2:
                firstDate = firstDate + secondDate[2:len(secondDate)]
                date_obj1 = datetime.strptime(firstDate, "%d/%m/%y")
                formatted_date1 = date_obj1.strftime("%A, %d. %B %Y")
            elif len(firstDate) == 5:
                firstDate = (firstDate + secondDate[4:len(secondDate)]) if len(secondDate.split('/')[0]) == 1 else (firstDate + secondDate[5:len(secondDate)])
                date_obj1 = datetime.strptime(firstDate, "%d/%m/%y")
                formatted_date1 = date_obj1.strftime("%A, %d. %B %Y")
            elif len(firstDate) > 5:
                date_obj1 = datetime.strptime(firstDate, "%d/%m/%y")
                formatted_date1 = date_obj1.strftime("%A, %d. %B %Y")

            date_obj2 = datetime.strptime(secondDate, "%d/%m/%y")
            formatted_date2 = date_obj2.strftime("%A, %d. %B %Y")

            date = formatted_date1 + ' - ' + formatted_date2

        location = ''
        description = ''
        startDate = ''
        endDate = ''
        link = ''
        i = 0

        
        # Find all <p> elements within this div
        paragraphs = descriptionDiv.find_all('p')

        while i < len(paragraphs):
            text = paragraphs[i].get_text()
            if 'lokacija:' in text.lower():
                location = paragraphs[i].find('span', class_='fw500').get_text() if paragraphs[i].find('span', class_='fw500') is not None else ''
            elif 'ura:' in text.lower():
                timeMain = paragraphs[i].find('span', class_='fw500').get_text() if paragraphs[i].find('span', class_='fw500') is not None else ''
                if len(timeMain) == 0:
                    time_pattern = r'\b\d{2}:\d{2}\b'
                    # Find all occurrences of the pattern in the text
                    timeValues = re.findall(time_pattern, text)
                    if len(timeValues) == 2:
                        timeMain = timeValues[0] + '-' + timeValues[1]
                    else:
                        timeMain = timeValues[0]
                if '-' in dateMain:
                    firstDate = dateMain.split('-')[0].strip()
                    secondDate = dateMain.split('-')[1].strip()

                    if len(firstDate) == 2:
                        firstDate = firstDate + secondDate[2:len(secondDate)]
                        date_obj1 = datetime.strptime(firstDate, "%d/%m/%y")
                        formatted_date1 = date_obj1.strftime("%A, %d. %B %Y")
                    elif len(firstDate) == 5:
                        firstDate = (firstDate + secondDate[4:len(secondDate)]) if len(secondDate.split('/')[0]) == 1 else (firstDate + secondDate[5:len(secondDate)])
                        date_obj1 = datetime.strptime(firstDate, "%d/%m/%y")
                        formatted_date1 = date_obj1.strftime("%A, %d. %B %Y")
                    elif len(firstDate) > 5:
                        date_obj1 = datetime.strptime(firstDate, "%d/%m/%y")
                        formatted_date1 = date_obj1.strftime("%A, %d. %B %Y")

                    date_obj2 = datetime.strptime(secondDate, "%d/%m/%y")
                    formatted_date2 = date_obj2.strftime("%A, %d. %B %Y")

                    dateForTime = formatted_date1 + ' - ' + formatted_date2
                else:
                    dateForTime = datetime.strptime(dateMain, "%d/%m/%y").strftime("%Y-%m-%d")

                if '-' not in timeMain:
                    time = datetime.strptime(timeMain, "%H:%M").strftime("%H:%M:%S")
                    startDate = dateForTime + "T" + time + "+01:00"
                else:
                    time1 = datetime.strptime(timeMain.split('-')[0].strip(), "%H:%M").strftime("%H:%M:%S")
                    time2 = datetime.strptime(timeMain.split('-')[1].strip(), "%H:%M").strftime("%H:%M:%S")

                    startDate = dateForTime + "T" + time1 + "+01:00"
                    endDate = dateForTime + "T" + time2 + "+01:00"
            elif 'več informacij' == text.lower():
                if descriptionDiv.find('a', class_='baskerville aniLink fSize30') is not None:
                    link = descriptionDiv.find('a', class_='baskerville aniLink fSize30')['href']
            else:
                description = description + paragraphs[i].get_text() + "\n"
            i = i + 1

        dataset.append({
            "Title": title, 
            "Description": description,
            "Link": link,
            "Date": date, 
            "StartDate": startDate,
            "EndDate": endDate,
            "Location": location,
        })

    else:
        print(item)
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

# Convert to a Pandas DataFrame
df = pd.DataFrame(dataset, columns=['Title', 'Description', 'Link', 'Date', 'StartDate', 'EndDate', 'Location'])
# Save to a CSV file
df.to_csv("CsvFiles/VisitIzola2.csv", index=False, encoding='utf-8-sig')
