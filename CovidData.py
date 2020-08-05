#CovidData
import requests
import pandas as pd
from datetime import date
import yagmail
from tabulate import tabulate
from StateAbbrevDict import us_state_abbrev
from EmailPassword import password

#datetime needed to grab only today from historic file
date_today = date.today()
date_today = int(date_today.strftime("%Y%m%d"))

#get state populations
census_URL = "https://api.census.gov/data/2019/pep/population?get=NAME,POP&for=STATE:*" 
census_get = requests.get(url = census_URL).json()
census_df = pd.DataFrame(data=census_get) #to df
census_df.columns = census_df.iloc[0] #make first row to header
census_df = census_df[1:] #make first row to header pt 2
census_df['state'] = census_df['NAME'].map(us_state_abbrev) #append abbreviation to df


#get historic data csv, count rows for today, create new dF for today's data, append state population
historic_state_data = pd.read_csv('https://covidtracking.com/api/v1/states/daily.csv')
daily_state_bool = historic_state_data.apply(lambda x: True if x['date'] == date_today else False , axis=1)
daily_state_count_rows = len(daily_state_bool[daily_state_bool == True].index)
today_state_data = historic_state_data[:daily_state_count_rows]
today_state_data = pd.merge(today_state_data, census_df, on='state', how='inner') #join dfs to add population
today_state_data['POP'] = today_state_data['POP'].astype(int) #convert POP to int
today_state_data.rename(columns={'NAME': 'State', 'positiveIncrease': 'NewCases', 'deathIncrease': 'NewDeaths'}, inplace=True)


#top 5 biggest case increase per capita
biggest_percapita_case_increase = today_state_data
biggest_percapita_case_increase['CasePerCapita'] = biggest_percapita_case_increase.NewCases / biggest_percapita_case_increase.POP #creates calculated column of cases/population
biggest_percapita_case_increase.sort_values('CasePerCapita', ascending=False, inplace=True) #sort by case per capita
biggest_percapita_case_increase = biggest_percapita_case_increase[:5] #top 5
biggest_percapita_case_increase = biggest_percapita_case_increase[['State','NewCases']] #reduce df
biggest_percapita_case_increase = tabulate(biggest_percapita_case_increase, headers = "keys", tablefmt="html", numalign="right", showindex=False) #tabulate formatting 

#top 5 biggest case increase
biggest_positive_case_increase = today_state_data.sort_values('NewCases', ascending=False)
biggest_positive_case_increase = biggest_positive_case_increase[:5]
biggest_positive_case_increase = biggest_positive_case_increase[['State','NewCases']] #reduce df to columns needed
biggest_positive_case_increase = tabulate(biggest_positive_case_increase, headers = "keys", tablefmt="html", numalign="right", showindex=False) #tabulate formatting 

#top 5 biggest death increase per capita
biggest_percapita_death_increase = today_state_data
biggest_percapita_death_increase['DeathPerCapita'] = biggest_percapita_death_increase.NewDeaths / biggest_percapita_death_increase.POP #creates calculated column of deaths/population
biggest_percapita_death_increase.sort_values('DeathPerCapita', ascending=False, inplace=True) #sort by death per capita
biggest_percapita_death_increase = biggest_percapita_death_increase[:5] #top 5
biggest_percapita_death_increase = biggest_percapita_death_increase[['State','NewDeaths']] #reduce df
biggest_percapita_death_increase = tabulate(biggest_percapita_death_increase, headers = "keys", tablefmt="html", numalign="right", showindex=False) #tabulate formatting 


# #top 5 biggest death increase
biggest_death_increase = today_state_data.sort_values('NewDeaths', ascending=False)
biggest_death_increase = biggest_death_increase[:5]
biggest_death_increase = biggest_death_increase[['State','NewDeaths']] #reduce df to columns needed
biggest_death_increase = tabulate(biggest_death_increase, headers = "keys", tablefmt="html", numalign="right", showindex=False) #tabulate formatting 



# email it out
yag = yagmail.SMTP("glen.cupples.dev@gmail.com",password)
contents = [
	"Biggest per capita case increase:"+
	biggest_percapita_case_increase,
	"Biggest case increase:"+
    biggest_positive_case_increase,
    "Biggest per capita death increase:"+
    biggest_percapita_death_increase,
    "Biggest death increase:"+
    biggest_death_increase
]
yag.send('glen.cupples@gmail.com', 'Daily US Covid Update', contents)
