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
    driver.get('(our website)')
    time.sleep(2)
    driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
    time.sleep(2)
    driver.find_element(By.ID, 'login-username1').send_keys(username)
    driver.find_element(By.ID, 'login-password1').send_keys(password)
    driver.find_element(By.XPATH, '//*[@id="col-content"]/div[2]/div/form/div[3]/button').click()
    time.sleep(2)
    return login

#Create a list with chosen users from premade excel file
def bettors_list():
    df = pd.read_excel('our_file.xlsx', sheet_name=0)
    our_users = df['Username'].to_list()
    return our_users

#Find how much pages with new information one particular user from our list have
def pages_num(user):
    driver.get(f'https://www.(website).com/profile/{user}/.../.../')
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

#Collect info from one page in one user next info
def one_page_scrap(user, page):
    driver.get(f'https://www.(website).com/profile/{user}/.../.../.../{page}/')
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
    
    #Creating a Dataframe with teams and info
    teams = []
    for all_teams in soup.find_all('td', attrs={'class': 'table-participant'}):
        team = all_teams.find('strong')
        teams.append(team.text)

    info_types = []
    for all_info in soup.find_all('td', attrs={'class': 'table-participant'}):
        info = all_info.find('a', attrs={'class': 'number2'})
        info_types.append(info.text)
    teams_df = pd.DataFrame({'Teams': teams, 'info_type': info_types})
    
    #Creating a DataFrame with info_2
    infos_2 = []
    for all_info_2 in soup.find('div', attrs={'id': 'col-content'}).find_all('tr', attrs={'class':['odd', 'even']}):
        info_2 = all_info_2.find_all('td', attrs={'class': 'center table-odds'})
        row_2 = [str(all_info_2.get_text()).strip() for all_info_2 in info_2 
               if str(all_info_2.get_text()).strip()]
        infos_2.append(row_2)
    info_2_df = pd.DataFrame(infos_2)
    if len(info_2_df.columns) == 2:
        info_2_df[2] = np.nan
    elif len(odds_df.columns) == 1:
        info_2_df[1] = np.nan
        info_2_df[2] = np.nan    
    info_2_df = info_2_df.rename(columns = {0:'a', 1:'b', 2:'c'})
    try:
        info_2_df['c'].fillna(value='-', inplace=True)   
    except:
        pass
    try:
        info_2_df['b'].fillna(value='-', inplace=True)
    except:
        pass       
    info_2_df = info_2_df.replace(to_replace='None', value=np.nan).dropna()
    info_2_df = info_2_df.reset_index(drop=True)
    
    #Creating a DataFrame with info_3
    infos_3 = []
    for all_info_3 in soup.find_all('tr', attrs={'class': 'pred-usertip'}):
        info_3 = all_info_3.find_all('td')
        row_3 = [str(all_info_3.get_text()).strip() for all_info_3 in info_3] 
        infos_3.append(row_3)
    info_3_df = pd.DataFrame(infos_3)
    if len(info_3_df.columns) == 2:
        info_3_df[2] = np.nan
    elif len(info_3_df.columns) == 1:
        info_3_df[1] = np.nan
        info_3_df[2] = np.nan 
    info_3_df = info_3_df.rename(columns = {0:'a', 1:'b', 2:'c'})
    try:
        info_3_df['b'].fillna(value='-', inplace=True)
    except:
        pass
    try:
        info_3_df['c'].fillna(value='-', inplace=True)
    except:
        pass   
    info_3_df = info_3_df.replace({'abc':1, '':0})
    #Final DataFrame
    onepage_df = pd.concat([times_df, sports_df, teams_df, info_2_df, info_3_df], axis=1)
    onepage_df.insert(0, 'User', user)
    onepage_df.fillna(value='No_info', inplace=True)
    return onepage_df

#Collect all new info from one user
def one_user_scrap(user):
    oneuser_info = []
    pages = pages_num(user)
    for x in range(len(pages)):
        page = pages[x]
        oneuser_info.append(one_page_scrap(user, page))
    try:
        oneuser_df = pd.concat(oneuser_info).reset_index(drop=True)
        oneuser_df.fillna(value='No_info', inplace=True)
    except:
        oneuser_df = pd.DataFrame()       
    return oneuser_df

#Collect all info from all users from our list
def all_users_scrap():
    all_users_info = []
    users = users_list()
    for user in users:
        info_table = one_user_scrap(user)
        if len(info_table) > 0:
            all_users_info.append(info_table)
    all_users_df = pd.concat(all_users_info).reset_index(drop=True)
    return all_users_df

#Sorting data by sport
def sorting_by_sport(sport):
    final_df = all_users_scrap()
    sorting_by_sport_df = final_df.loc[final_df['Sport'] == sport].reset_index(drop=True)
    return sorting_by_sport_df

#Sorting data by info type
def sorting_by_info(info):
    final_df = all_users_scrap()
    sorting_by_info_df = final_df.loc[final_df['Info_type'] == info].reset_index(drop=True)
    return sorting_by_info_df

#Sorting our data by particular sport and info type
def sorting(sport, info):
    final_df = all_users_scrap()
    sorting_df = final_df.loc[(final_df['Sport'] == sport) & (final_df['Info_type'] == info)].reset_index(drop=True)
    sorting_df.to_excel('sorting_info.xlsx', index=False)
    return sorting_df

#Making excel file with all new info
def all_info_excel():
    all_info = all_users_scrap()
    all_info.to_excel('All_info.xlsx', index=False)
    return all_info_excel

#Making excel file with data after sorting   
def sorting_excel(sport, info):
    sort = sorting(sport, info)  
    sort.to_excel('Sorting.xlsx', index=False)
    return sorting_excel 

#Final result
def result():
    res_df = sorting('Sport', 'info')
    res_df['a'] = res_df['a'].astype(float)
    res_df['b'] = res_df['b'].astype(float)
    res_df['c'] = res_df['c'].astype(float)
    result_df = res_df.pivot_table(index=['Teams'], values=['a', 'b', 'c'], aggfunc=np.sum, fill_value=0).reset_index()
    result_df['Amount_of_info'] = result_df['a'] + result_df['b'] + result_df['c']
    result_df = result_df.sort_values(by='Amount_of_info', ascending=False).reset_index(drop=True)
    merge_df = res_df[['Teams', 'Country', 'League', 'Day_and_time', 'a', 'b', 'c']].copy()
    result_df = result_df.merge(merge_df, on='Teams', how='left')
    result_df = result_df.drop_duplicates(subset=['Teams']).reset_index(drop=True)
    result_df = result_df[['Day_and_time', 'Teams', 'Country', 'League', 'a', 'b', 'c', 'a', 'b', 'c', 'Amount_of_info']]
    result_df.to_excel('result.xlsx', index=False)
    return result

#Main function
def main():
    login('login', 'password')
    result()
    time.sleep(2)
    driver.close()          
    driver.quit()
    return main


main()
