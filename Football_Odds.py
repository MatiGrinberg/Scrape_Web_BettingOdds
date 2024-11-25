from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
driver.get("https://www.oddsportal.com/results/#football")
driver.implicitly_wait(10)
page_source = driver.page_source
soup = BeautifulSoup(page_source, 'html.parser')
anchors = soup.find_all('a', href=lambda href: href and href.endswith('results/'))
hrefs = [anchor['href'] for anchor in anchors][1:]
all_rows=[]
count_link=0

for h in hrefs:
    link = f"https://www.oddsportal.com{h}"
    driver.get(link)
    count_link += 1
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'eventRow'))
        )
        new_page_source = driver.page_source
        new_soup = BeautifulSoup(new_page_source, 'html.parser')
        event_rows = new_soup.find_all('div', class_='eventRow')
        print(f"{count_link} => Scraping {h}; Found {len(event_rows)} event rows")
    except Exception as e:
        print(f"Error scraping {h}: {e}")
        event_rows = []  # If no rows are found, set an empty list to prevent crashing
    last_date = None  # This will store the last date seen
    for event_row in event_rows:
        p_elements = event_row.find_all('p')
        odds_values = [p.get_text() for p in p_elements[-3:]]
        date_element = event_row.find('div', class_='text-black-main font-main w-full truncate text-xs font-normal leading-5')
        if date_element:
            date_value = date_element.get_text().strip()
            last_date = date_value  # Update the last date seen
            odds_values.insert(0, date_value)  # Add the date to the beginning of the odds list
        elif last_date:
            odds_values.insert(0, last_date)
        gradient_green_p = event_row.find('p', class_='gradient-green')
        if gradient_green_p:
            gradient_green_value = gradient_green_p.get_text().strip()
            odds_values.append(gradient_green_value)
        all_rows.append(odds_values)


df = pd.DataFrame(all_rows, columns=['Date', 'W', 'D', 'L', 'B'])


unique_dates = sorted(df['Date'].unique())
print("Unique Date Formats in the 'Date' Column:")
print(unique_dates)

def format_date(date_str):
    if "Yesterday" in date_str:
        return (datetime.today() - pd.Timedelta(days=1)).strftime('%d %b %Y')  # Format as 'DD Mon YYYY'
    date_str = date_str.split(' -')[0].strip()
    try:
        return datetime.strptime(date_str, '%d %b %Y').strftime('%d %b %Y')
    except ValueError:
        return "Error"

df['Formatted Date'] = df['Date'].apply(format_date)
unique_dates = sorted(df['Formatted Date'].unique().tolist())
print("Unique Date Formats in the 'Date' Column:")
print(unique_dates)

print(df[df['Formatted Date']=='Error'])
df=df[df['Formatted Date']!="Error"]
print(df.shape)

df.drop('Date',axis=1,inplace=True)
df = df.sort_values(by='Formatted Date')

null_rows = df[df.isnull().any(axis=1)]
print(null_rows)
df.drop(null_rows.index,inplace=True)


# Convert all cols to number
df[['W', 'D', 'L','B']] = df[['W', 'D', 'L','B']].astype(float)
plt.figure(figsize=(14, 6))
plt.subplot(1, 3, 1)  # 1 row, 3 columns, 1st subplot
plt.hist(df['W'].dropna(), bins=20, color='green', alpha=0.7)
plt.title('Distribution of Win Payoffs')
plt.xlabel('Win Payoff')
plt.ylabel('Frequency')
plt.subplot(1, 3, 2)  # 1 row, 3 columns, 2nd subplot
plt.hist(df['D'].dropna(), bins=20, color='orange', alpha=0.7)
plt.title('Distribution of Draw Payoffs')
plt.xlabel('Draw Payoff')
plt.ylabel('Frequency')
plt.subplot(1, 3, 3)  # 1 row, 3 columns, 3rd subplot
plt.hist(df['L'].dropna(), bins=20, color='red', alpha=0.7)
plt.title('Distribution of Lose Payoffs')
plt.xlabel('Lose Payoff')
plt.ylabel('Frequency')
plt.tight_layout()
plt.show()

last_d,first_d = np.max(df['Formatted Date']), np.min(df['Formatted Date'])
threshold = 24.50  # Set your threshold value here

def calculate_wl_and_return(group):
    filtered_group = group[(group[['W', 'D', 'L']] > threshold).any(axis=1)]
    filtered_group['max_payoff'] = filtered_group[['W', 'D', 'L']].max(axis=1)
    filtered_group['W/L'] = (filtered_group['max_payoff'] == filtered_group['B']).astype(int)
    filtered_group['return'] = filtered_group.apply(
        lambda row: row['max_payoff'] - 1 if row['W/L'] == 1 else -1, axis=1
    )
    return filtered_group

result = df.groupby('Formatted Date').apply(lambda group: calculate_wl_and_return(group))
avg_ret = (
    result.groupby(level=0)['return']  
    .agg(['sum', 'count'])         
    .assign(avg=lambda x: x['sum'] / x['count'])  
)


print(os.getcwd())
small_count = avg_ret[avg_ret['count'] <= 10]
large_count = avg_ret[avg_ret['count'] > 10]

def scatter_avg_count(data, title, color):
    plt.figure(figsize=(8, 5))
    plt.scatter(data['count'], data['avg'], color=color, alpha=0.7, label='Data Points')
    avg_of_avg = data['avg'].mean()  # Calculate the average of the 'avg' column
    plt.axhline(avg_of_avg, color='gray', linestyle='--', label=f'Avg Avg: {avg_of_avg:.2f}')  # Add a horizontal line
    plt.title(title)
    plt.xlabel('Count')
    plt.ylabel('Average Return')
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{title.replace(' ', '_')}.png")  
    plt.show()

scatter_avg_count(small_count, 'Plot Count_Bets ≤ 10', 'blue')
scatter_avg_count(large_count, 'Plot Count_Bets > 10', 'orange')
scatter_avg_count(avg_ret, 'Plot Count_Bets All', 'red')





