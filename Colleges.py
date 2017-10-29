# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 12:33:29 2017

@author: Maria
"""
# The sorse of data: https://collegescorecard.ed.gov/data/

# Importing the libraries
import pandas as pd
import re
import math
import matplotlib.pyplot as plt

# Downloading the datasets
zipcodes = pd.read_csv('zipcodes.csv') # http://federalgovernmentzipcodes.us/

def read_DF(file_name):
    path = 'CollegeScorecard_Raw_Data/' + file_name
    data = pd.read_csv(path, low_memory=False)
    return data

# Dropping unnecessary columns
def drop_columns(data):
    col_names = list(data.columns)
    for col in col_names:
        family_income = re.compile('.*INC.*')
        male = re.compile('.*MALE.*')
        female = re.compile('.*FEMALE.*')
        if family_income.findall(col) or male.findall(col) or female.findall(col):
            data = data.drop([col], axis='columns')
    return data
        

# =============================================================================
#              Creating a map with universities in the target area
# =============================================================================

# Downloading data
data = read_DF('MERGED2015_16_PP.csv')
data = drop_columns(data)

# Transforming data
for row in range(7593):
    name = data['INSTNM'][row]
    if name.find("'") != -1:
        name = name.replace("'", "`")
        data['INSTNM'][row] = name

# Transforming numeric data for universities.js file
def data_transform(fild):
    if math.isnan(fild):
        return ('No data')
    else:
        return(str(fild))
        
# Finding the target area
zipcode = input('Input your ZIP code here: ')
for row in range(81831):
    if str(zipcodes['Zipcode'][row]) == zipcode:
        x_0 = zipcodes['Long'][row]
        y_0 = zipcodes['Lat'][row]
        break
mile_radius = float(input('Input the maximum distance from your location (mi): '))
radius = mile_radius / 60  # Converting the radius from miles to degreeses

# Creating the subset of the main dataframe
outcomes = pd.DataFrame(columns = 
                      ['INSTNM', 'LATITUDE', 'LONGITUDE', 'INSTURL', 'COSTT4_A'])
for row in range(len(data)):
    if ((data['LONGITUDE'][row] - x_0)**2 + (data['LATITUDE'][row] - y_0)**2) <= (radius ** 2):        
        new_data = data.loc[row,['INSTNM', 'LATITUDE', 'LONGITUDE', 'INSTURL', 'COSTT4_A']]
        outcomes = outcomes.append(new_data)
outcomes = outcomes.reset_index(drop=True)

# Creating a universities.js file with required information
list_of_colleges = open('universities.js', 'w')
list_of_colleges.write("myData = [\n")

for row in range(len(outcomes)):
    item = "[" + str(outcomes['LATITUDE'][row]) + "," + str(outcomes['LONGITUDE'][row]) + ", '"
    item += str("Name: " + str(outcomes['INSTNM'][row]) + "\\n") 
    item += str("URL:  " + str(outcomes['INSTURL'][row]) + "\\n")
    item += str("Cost: " + data_transform(outcomes['COSTT4_A'][row]) + "'], \n")
    list_of_colleges.write(item)

list_of_colleges.write("\n];\n")
list_of_colleges.close()

        
# =============================================================================
#              Doing an exploratory data analysis of costs
# =============================================================================

# Counting the average cost for the single year 
def count_cost(data, param):
    costs = pd.Series()
    i = 0
    for state in states:
        cost = data[data['STABBR'] == state][param].mean()
        costs = costs.set_value(i, cost)
        i += 1
    return costs

# Counting the average cost for N years
def avg_counting(data, N):
    avg_costs = pd.Series()
    for state in range(50):
        average = 0
        for i in range(N):
            average += data[str(2015 - i)][state]
        avg_costs = avg_costs.set_value(state, (average / N))
    return avg_costs
    
# Creating DataFrames containing information about costs 
states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO',	'CT',	'DE', 'FL', 'GA', 'HI', 
          'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 
          'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 
          'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 
          'VT', 'VA', 'WA', 'WV', 'WI', 'WY']

program_year = pd.DataFrame(states, columns = ['State'])
academic_year = pd.DataFrame(states, columns = ['State'])

for year in range(2009, 2016):
    file_name = 'MERGED' + str(year) + '_' + str(year - 2000 + 1) + '_PP.csv'
    data = read_DF(file_name)
    data = drop_columns(data)
    means_program = count_cost(data, 'COSTT4_P')
    means_academic = count_cost(data, 'COSTT4_A')
    program_year[str(year)] = means_program
    academic_year[str(year)] = means_academic

# Counting the average cost for the last N years
while True:
    years = int(input('Enter the number of years: '))
    if years > 7:
        print('Sorry, the dataset does not containg data prior 2009.')
    else:
        break

# Creating the DataFrame with average costs for N years
average_costs = pd.DataFrame(states, columns = ['State'])
average_costs['Program'] = avg_counting(program_year, years)
average_costs['Academic'] = avg_counting(academic_year, years)

# Drowing the barchart
title = 'The annual costs of attendences for the last ' + str(years) + ' years'
barchart = plt.figure(figsize = (10, 20))
plt.title(title, fontsize = 14)

plt.barh([x*3 - 0.5 for x in range(50)], 
         [average_costs['Program'][row] for row in range(50)],
         color = 'red', label = 'Annual cost per program year', zorder = 2)
plt.barh([x*3 + 0.5 for x in range(50)], 
         [average_costs['Academic'][row] for row in range(50)],
         color = 'blue', label = 'Annual cost per academic year', zorder = 2)

plt.xlabel('Annual costs, USD')
plt.ylabel('States')
plt.yticks([x*3 for x in range(50)], states)
plt.legend(loc=4)
plt.grid(c='#E0E0E0')

plt.savefig('plot.jpg')
barchart.show()
