from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless') 
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(service=Service(executable_path="D:/Кирилл/Other stuff/chromedriver.exe"), options=options)

#Login into account using your username and password 
def login(username, password):
    driver.get('https://www.oddsportal.com/login/')
    time.sleep(2)
    driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
    time.sleep(2)
    driver.find_element(By.ID, 'login-username1').send_keys(username)
    driver.find_element(By.ID, 'login-password1').send_keys(password)
    driver.find_element(By.XPATH, '//*[@id="col-content"]/div[2]/div/form/div[3]/button').click()
    time.sleep(2)
    return login

#Create a list with chosen bettors from premade excel file
def bettors_list():
    df = pd.read_excel('Soccer_bettors.xlsx', sheet_name=0)
    # df = df.drop(columns=['Unnamed: 5', 'Unnamed: 6'])
    # df = df.drop(df[df['1x2 ROI'] < 0.05].index)
    our_bettors = df['Username'].to_list()
    return our_bettors

#Find how much pages with new predictions one particular bettor from our list have
def pages_num(bettor):
    # bettor = 'petersson1984'
    driver.get(f'https://www.oddsportal.com/profile/{bettor}/my-predictions/next/')
    content = driver.page_source
    soup = BeautifulSoup(content, features="html.parser")

    pages = []
    for all_pages in soup.find_all('div', attrs={'id': 'pagination'}):
        pg = all_pages.find_all('span')
        pages = [str(all_pages.get_text()).strip() for all_pages in pg
                 if str(all_pages.get_text()).strip()]
        pages = pages[2:-2]  
    
    if pages == []:
        pages = [1]
    return pages

#Collect info from one page in one bettor next predictions pages
def one_page_scrap(bettor, page):
    # bettor = 'petersson1984'
    # page = '1'
    driver.get(f'https://www.oddsportal.com/profile/{bettor}/my-predictions/next/page/{page}/')
    time.sleep(1)
    content = driver.page_source
    soup = BeautifulSoup(content, features="html.parser")
    
    #Creating a DataFrame with time
    games_time = []
    for times in soup.find_all('td', attrs={'class': 'table-time'}):
        date = times.get_text(separator = " ").strip() 
        games_time.append(date)
    
    times_df = pd.DataFrame({'Day_and_time': games_time})
    
    #Creating a DataFrame with sport, country and league
    sports = []
    for all_sports in soup.find_all('tr', attrs={'class': 'dark'}):
        sport = all_sports.find_all('a')
        row = [str(all_sports.get_text()).strip() for all_sports in sport 
               if str(all_sports.get_text()).strip()]
        sports.append(row)
    sports_df = pd.DataFrame(sports)
    sports_df = sports_df.rename(columns={0:'Sport', 1:'Country', 2:'League'})
    
    #Creating a Dataframe with teams and Bet_type
    teams = []
    for all_teams in soup.find_all('td', attrs={'class': 'table-participant'}):
        team = all_teams.find('strong')
        teams.append(team.text)

    bet_types = []
    for all_bets in soup.find_all('td', attrs={'class': 'table-participant'}):
        bet = all_bets.find('a', attrs={'class': 'number2'})
        bet_types.append(bet.text)
    teams_df = pd.DataFrame({'Teams': teams, 'Bet_type': bet_types})
    
    #Creating a DataFrame with odds
    odds = []
    for all_odds in soup.find('div', attrs={'id': 'col-content'}).find_all('tr', attrs={'class':['odd', 'even']}):
        odd = all_odds.find_all('td', attrs={'class': 'center table-odds'})
        row_2 = [str(all_odds.get_text()).strip() for all_odds in odd 
               if str(all_odds.get_text()).strip()]
        odds.append(row_2)
    odds_df = pd.DataFrame(odds)
    if len(odds_df.columns) == 2:
        odds_df[2] = np.nan
    elif len(odds_df.columns) == 1:
        odds_df[1] = np.nan
        odds_df[2] = np.nan    
    odds_df = odds_df.rename(columns = {0:'1', 1:'X', 2:'2'})
    try:
        odds_df['2'].fillna(value='-', inplace=True)   
    except:
        pass
    try:
        odds_df['X'].fillna(value='-', inplace=True)
    except:
        pass       
    odds_df = odds_df.replace(to_replace='None', value=np.nan).dropna()
    odds_df = odds_df.reset_index(drop=True)
    
    #Creating a DataFrame with predictions
    predictions = []
    for all_predictions in soup.find_all('tr', attrs={'class': 'pred-usertip'}):
        prediction = all_predictions.find_all('td')
        row_3 = [str(all_predictions.get_text()).strip() for all_predictions in prediction] 
        predictions.append(row_3)
    predictions_df = pd.DataFrame(predictions)
    if len(predictions_df.columns) == 2:
        predictions_df[2] = np.nan
    elif len(predictions_df.columns) == 1:
        predictions_df[1] = np.nan
        predictions_df[2] = np.nan 
    predictions_df = predictions_df.rename(columns = {0:'Pick_1', 1:'Pick_X', 2:'Pick_2'})
    try:
        predictions_df['Pick_X'].fillna(value='-', inplace=True)
    except:
        pass
    try:
        predictions_df['Pick_2'].fillna(value='-', inplace=True)
    except:
        pass   
    predictions_df = predictions_df.replace({'PICK':1, '':0})
    #Final DataFrame
    onepage_df = pd.concat([times_df, sports_df, teams_df, odds_df, predictions_df], axis=1)
    onepage_df.insert(0, 'Bettor', bettor)
    onepage_df.fillna(value='No_info', inplace=True)
    return onepage_df

#Collect all predictions from one bettor
def one_bettor_scrap(bettor):
    # bettor = 'petersson1984'
    onebettor_info = []
    pages = pages_num(bettor)
    for x in range(len(pages)):
        page = pages[x]
        onebettor_info.append(one_page_scrap(bettor, page))
    try:
        onebettor_df = pd.concat(onebettor_info).reset_index(drop=True)
        onebettor_df.fillna(value='No_info', inplace=True)
    except:
        onebettor_df = pd.DataFrame()       
    return onebettor_df

#Collect all predictions from all bettors from our list
def all_bettors_scrap():
    all_bettors_info = []
    bettors = bettors_list()
    for bettor in bettors:
        pred_table = one_bettor_scrap(bettor)
        if len(pred_table) > 0:
            all_bettors_info.append(pred_table)
    all_bettors_df = pd.concat(all_bettors_info).reset_index(drop=True)
    return all_bettors_df

#Sorting data by sport
def sorting_by_sport(sport):
    final_df = all_bettors_scrap()
    sorting_by_sport_df = final_df.loc[final_df['Sport'] == sport].reset_index(drop=True)
    return sorting_by_sport_df

#Sorting data by bet
def sorting_by_bet(bet):
    final_df = all_bettors_scrap()
    sorting_by_bet_df = final_df.loc[final_df['Bet_type'] == bet].reset_index(drop=True)
    return sorting_by_bet_df

#Sorting our data by particular sport and Bet_type
def sorting(sport, bet):
    final_df = all_bettors_scrap()
    sorting_df = final_df.loc[(final_df['Sport'] == sport) & (final_df['Bet_type'] == bet)].reset_index(drop=True)
    sorting_df.to_excel('Soccer_sorting_predictions.xlsx', index=False)
    return sorting_df

#Making excel file with all predictions
def all_info_excel():
    all_info = all_bettors_scrap()
    all_info.to_excel('All predictions.xlsx', index=False)
    return all_info_excel

#Making excel file with data after sorting   
def sorting_excel(sport,bet):
    sort = sorting(sport, bet)  
    sort.to_excel('Sorting predictions.xlsx', index=False)
    return sorting_excel 

#Final result
def result():
    res_df = sorting('Soccer', '1X2')
    res_df['Pick_1'] = res_df['Pick_1'].astype(float)
    res_df['Pick_X'] = res_df['Pick_X'].astype(float)
    res_df['Pick_2'] = res_df['Pick_2'].astype(float)
    result_df = res_df.pivot_table(index=['Teams'], values=['Pick_1', 'Pick_X', 'Pick_2'], aggfunc=np.sum, fill_value=0).reset_index()
    result_df['Amount_of_pred'] = result_df['Pick_1'] + result_df['Pick_X'] + result_df['Pick_2']
    result_df = result_df.sort_values(by='Amount_of_pred', ascending=False).reset_index(drop=True)
    merge_df = res_df[['Teams', 'Country', 'League', 'Day_and_time', '1', 'X', '2']].copy()
    result_df = result_df.merge(merge_df, on='Teams', how='left')
    result_df = result_df.drop_duplicates(subset=['Teams']).reset_index(drop=True)
    result_df = result_df[['Day_and_time', 'Teams', 'Country', 'League', '1', 'X', '2', 'Pick_1', 'Pick_X', 'Pick_2', 'Amount_of_pred']]
    # result_df = result_df[result_df['Day_and_time'].str.contains('To', regex=False)].reset_index(drop=True) 
    result_df.to_excel('Soccer_result.xlsx', index=False)
    return result

#Main function
def main():
    login('VermontCoders', 'Vermont')
    result()
    time.sleep(2)
    driver.close()          
    driver.quit()
    return main


main()

#For some testing 
# login('VermontCoders', 'Vermont')

# all_info_excel()
# sorting_excel('Soccer', '1X2')
# print(one_page_scrap('papmakis3', '1'))
# print(pages_num('petersson1984'))
# print(one_bettor_scrap('Fab10_MediaPronos'))
# print(all_bettors_scrap())
# print(sorting('Soccer', '1X2'))
# print(bettors_list())
# print(result())

# time.sleep(2)
# driver.close()          
# driver.quit()