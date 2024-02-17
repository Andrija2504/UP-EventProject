import datetime

start_dates = []
end_dates = []

for year in range(2019, 2025):  # Iterate from 2019 to 2024
    for month in range(1, 13):  # Iterate through all months
        start_dates.append(datetime.datetime(year, month, 1))
        # Handling February in leap years
        if month == 2:
            if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                end_dates.append(datetime.datetime(year, month, 29))  # Leap year February
            else:
                end_dates.append(datetime.datetime(year, month, 28))  # Non-leap year February
        elif month in [4, 6, 9, 11]:
            end_dates.append(datetime.datetime(year, month, 30))  # 30-day months
        else:
            end_dates.append(datetime.datetime(year, month, 31))  # 31-day months

print(len(start_dates))
print(len(end_dates))

