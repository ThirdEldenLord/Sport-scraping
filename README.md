# Scraping some sports website with Selenium WebDriver and BeautifulSoup.

Right now i can't say what exactly website i am scraping and what info i get, so i just change some variables names and other things.

1. With **def login(username, password)** we login into our website.
2. **def users_list()** create a list from Excel file with users what we need.
3. Using **def pages_num(user)** we find out how many pages witn new info particular user from our list have.
4. **def one_page_scrap(user, page)** is scraping one page witn info from one user, create multiple dataframes with this info and then unite them into one dataframe.
5. With **def one_user_scrap(user)** we get new info from all pages, from one user.
6. **def all_users_scrap()** scraping info from all users in our list.
7. All **sorting** functions make a dataframes with particular information what we need.
8. Then we have two functions for creating Excel files with all and sorting information.
9. With **def result()** we get our final sorting dataframe and sum all identical information in the same columns, create a new dataframe with it and make Excel file.
10. **def main()** we use for runing our scraping script.
