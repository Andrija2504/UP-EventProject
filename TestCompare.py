from fuzzywuzzy import fuzz, process
import pandas as pd

# Example DataFrames (replace with your actual DataFrames)
path = "CsvFiles/SloveniaInfo.csv"
df1 = pd.read_csv("CsvFiles/DogodtkiKulturnik.csv")
current = df1

while(path != "exit"):

    df2 = pd.read_csv(path)

    # This will hold the rows from df2 that are not duplicates
    unique_rows = []

    # Iterate over each row in df2
    for index2, row2 in df2.iterrows():
        is_duplicate = False
        
        # Compare with each row in df1
        for index1, row1 in current.iterrows():
            # Calculate the similarity using fuzzy matching
            similarity = fuzz.ratio(row1['Title'], row2['Title'])
            
            if similarity > 90:
                is_duplicate = True
                break
                
        if not is_duplicate:
            unique_rows.append(row2)

    # Create a new DataFrame with the unique rows from df2
    df2_unique = pd.DataFrame(unique_rows)

    # Combine df1 with the unique rows from df2
    combined_df = pd.concat([current, df2_unique], ignore_index=True)
    current = pd.concat([current, df2_unique], ignore_index=True)

    path = input("Unesite path")


combined_df.to_csv("CsvFiles/Combined.csv", index=False, encoding='utf-8-sig')

# Now `filtered_df1` contains the events with similar names from both datasets
