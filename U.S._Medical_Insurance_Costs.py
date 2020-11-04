#!/usr/bin/env python
# coding: utf-8

# # U.S. Medical Insurance Costs
# 
# In this project, I will be importing and analyzing data from a given CSV file of medical insurance data. 
# I will use the Pandas module to create and manipulate a dataframe from the CSV.

# In[1]:


import pandas as pd
import numpy as np


# Upon data inspection, the attributes of the columns are:
# * age is an int
# * sex is 'male' or 'female'
# * bmi is a float
# * children is an int
# * smoker is 'yes' or 'no'
# * region has 4 options: (north/south)(east/west)
# * charges is a float, and not rounded to an even cent
#     
# The next step is to import the csv as a dataframe and make sure that it loaded in as intended by using the '.head()' method.

# In[2]:


imported = pd.read_csv('insurance.csv')
print(imported.head(10))


# Now that we have the data imported into a usable format, we can start thinking about what type of things we would like to know.
# Some insights we can gain from this data are:
# * The average age of the patients
# * A percentage of male vs female
# * If there is a correlation between number of children and BMI
# * If there is a correlation between smoking and BMI
# * Differences in charges for the different regions
# * What are the most significant drivers of cost
# 
# To do this, we will create a MedicalData class as a subclass of pandas.DataFrame that has methods to accomplish these tasks.

# In[3]:


class MedicalData(pd.DataFrame):
    def average_age(self):
#         Aquire the mean through parent class method and then prints a formatted string with the average age.
        avg = self.age.mean()
        print(f'The average age of all patients in the dataset is {avg:.2f}.\n')
        
    def male_female(self):
#         Divide the data into two new dataframes, one for each gender represented
        male_df = self[self.sex == 'male']
        female_df = self[self.sex == 'female']
        
#         Calculate and print the percentages of representation
        num_m = male_df.sex.count()
        num_f = female_df.sex.count()
        percent_m = num_m / (num_m + num_f) * 100
        percent_f = 100 - percent_m
        
        print(f'The dataset is divided into {percent_m:.1f}% male patients'
              f' and {percent_f:.1f}% female patients.\n')
        
#         Create another dataframe showing average statistics among men and women and prints formatted tables
        male_avgs = male_df.mean()
        female_avgs = female_df.mean()
        
        print('Average age, BMI, number of children, and insurance charges by sex:\n')
        print(f'Male:\n'
              f'Age: {male_avgs.age:.2f}\n'
              f'BMI: {male_avgs.bmi:.2f}\n'
              f'Number of Children: {male_avgs.children:.2f}\n'
              f'Insurance Charges: ${male_avgs.charges:.2f}\n')
        print(f'Female:\n'
              f'Age: {female_avgs.age:.2f}\n'
              f'BMI: {female_avgs.bmi:.2f}\n'
              f'Number of Children: {female_avgs.children:.2f}\n'
              f'Insurance Charges: ${female_avgs.charges:.2f}\n')
    
    
    def children_to_bmi(self):
#         Create a dataframe of the average BMI grouped by the number of children the patient has
        c_to_bmi = self.groupby('children').bmi.mean().reset_index()
        
#         Round the BMI averages to 2 places and reformat the columns for better readability, and then print
        c_to_bmi.bmi = c_to_bmi.bmi.apply(lambda x: round(x, 2))
        c_to_bmi.columns = ['No. of Children', 'Average BMI']
        
        print(c_to_bmi.to_string(index=False), end='\n\n')
        
    
    def cost_by_region(self):
#         Create a dataframe of averge cost organized by region
        c_by_reg = self.groupby('region').charges.mean().reset_index()
        
#         Reformat column names and print 
        c_by_reg.charges = c_by_reg.charges.apply(lambda x: ''.join(['$',str(round(x, 2))]))
        c_by_reg.region = c_by_reg.region.apply(lambda x: x.title())
        c_by_reg.columns = ['Region', 'Average Charges']
        
        print(c_by_reg.to_string(index=False), end='\n\n')
        
    def make_percentage(self, percent):
        return ''.join([str(percent), '%'])
        
    def age_groups(self, age):
#         A helper function to group patients by age
        if age < 25:
            group = '18 - 24'
        elif age < 35:
            group = '25 - 34'
        elif age < 45:
            group = '35 - 44'
        elif age < 55:
            group = '45 - 54'
        else:
            group = '55+'
        
        return group
        
    def age_above_median(self):
#         Add a column with age group using helper function and create new dataframe grouped by age group
#           and if the charges are above the median
        self['age_group'] = self.age.apply(self.age_groups)
        age_as_factor = self.groupby(['age_group', 'above_median']).age.count().reset_index(name='count')
#         Create pivot table, convert raw counts to percentages, and change column names for readability
        age_pivot = age_as_factor.pivot(columns='above_median', index='age_group', values='count').reset_index().fillna(0)
        age_pivot[False] = round(age_pivot[False] / (age_pivot[False] + age_pivot[True]) * 100, 1)
        age_pivot[True] = round(100 - age_pivot[False], 1)
        age_pivot[False] = age_pivot[False].apply(self.make_percentage)
        age_pivot[True] = age_pivot[True].apply(self.make_percentage)
        age_pivot.columns = ['Age Group', ' Below Median', ' Above Median' ]
        
        print(age_pivot.to_string(index=False), end='\n\n')
        
    def sex_above_median(self):
#         Create new dataframe grouped by sex and if the charges are above the median
        sex_as_factor = self.groupby(['sex', 'above_median']).age.count().reset_index(name='count')
#         Create pivot table, convert raw counts to percentages, and change column names for readability
        sex_pivot = sex_as_factor.pivot(columns='above_median', index='sex', values='count').reset_index().fillna(0)
        sex_pivot[False] = round(sex_pivot[False] / (sex_pivot[False] + sex_pivot[True]) * 100, 1)
        sex_pivot[True] = round(100 - sex_pivot[False], 1)
        sex_pivot[False] = sex_pivot[False].apply(self.make_percentage)
        sex_pivot[True] = sex_pivot[True].apply(self.make_percentage)
        sex_pivot['sex'] = sex_pivot['sex'].apply(lambda x: x.title())
        sex_pivot.columns = ['Sex', ' Below Median', ' Above Median' ]
        
        print(sex_pivot.to_string(index=False), end='\n\n')
        
    def bmi_groups(self, bmi):
#         A helper function to group patients by BMI
        if bmi < 18.5:
            group = 'Underweight'
        elif bmi < 25:
            group = 'Healthy'
        elif bmi < 30:
            group = 'Overweight'
        else:
            group = 'Obese'
        
        return group
        
    def bmi_above_median(self):
#         Add a column with bmi group using helper function and create new dataframe grouped by bmi group
#           and if the charges are above the median
        self['bmi_group'] = self.bmi.apply(self.bmi_groups)
        bmi_as_factor = self.groupby(['bmi_group', 'above_median']).bmi.count().reset_index(name='count')
#         Create pivot table, convert raw counts to percentages, and change column names for readability
        bmi_pivot = bmi_as_factor.pivot(columns='above_median', index='bmi_group', values='count').reset_index().fillna(0)
        bmi_pivot[False] = round(bmi_pivot[False] / (bmi_pivot[False] + bmi_pivot[True]) * 100, 1)
        bmi_pivot[True] = round(100 - bmi_pivot[False], 1)
        bmi_pivot[False] = bmi_pivot[False].apply(self.make_percentage)
        bmi_pivot[True] = bmi_pivot[True].apply(self.make_percentage)
        bmi_pivot.columns = ['Weight Status', ' Below Median', ' Above Median' ]
        
        print(bmi_pivot.to_string(index=False), end='\n\n')
        
    def children_above_median(self):
#         Create new dataframe grouped by number of children and if the charges are above the median
        children_as_factor = self.groupby(['children', 'above_median']).children.count().reset_index(name='count')
#         Create pivot table, convert raw counts to percentages, and change column names for readability
        children_pivot = children_as_factor.pivot(columns='above_median', index='children', values='count').                                                  reset_index().fillna(0)
        children_pivot[False] = round(children_pivot[False] / (children_pivot[False] + children_pivot[True]) * 100, 1)
        children_pivot[True] = round(100 - children_pivot[False], 1)
        children_pivot[False] = children_pivot[False].apply(self.make_percentage)
        children_pivot[True] = children_pivot[True].apply(self.make_percentage)
        children_pivot.columns = ['Number of Children', ' Below Median', ' Above Median' ]
        
        print(children_pivot.to_string(index=False), end='\n\n')
        
    def smoke_above_median(self):
#         Create new dataframe grouped by smoking status and if the charges are above the median
        smoke_as_factor = self.groupby(['smoker', 'above_median']).smoker.count().reset_index(name='count')
#         Create pivot table, convert raw counts to percentages, and change column names for readability
        smoke_pivot = smoke_as_factor.pivot(columns='above_median', index='smoker', values='count').reset_index().fillna(0)
        smoke_pivot[False] = round(smoke_pivot[False] / (smoke_pivot[False] + smoke_pivot[True]) * 100, 1)
        smoke_pivot[True] = round(100 - smoke_pivot[False], 1)
        smoke_pivot[False] = smoke_pivot[False].apply(self.make_percentage)
        smoke_pivot[True] = smoke_pivot[True].apply(self.make_percentage)
        smoke_pivot['smoker'] = smoke_pivot['smoker'].apply(lambda x: 'Smoker' if x == 'yes' else 'Non-Smoker')
        smoke_pivot.columns = ['', ' Below Median', ' Above Median' ]
        
        print(smoke_pivot.to_string(index=False), end='\n\n')
        
    def cost_factors(self):
#         Calculate median charges and add a column to the data that shows if it is over or below the median
        median_cost = self.charges.median()
        print(f'The median of charges over the whole dataset is ${median_cost:.2f}.\n')
        self['above_median'] = self.charges.apply(lambda x: x > median_cost)
#         Run all the functions that compare individual statistics to whether the charges were above the median
        self.age_above_median()
        self.sex_above_median()
        self.bmi_above_median()
        self.children_above_median()
        self.smoke_above_median()
        


# Now that we have built our class and all class methods, we can try them out. First, we will have to store the data 
# imported from the CSV file into an instance of our new class

# In[4]:


med_data = MedicalData(data=imported)


# Our first task is to simply see what the average age of the patients in the data is.

# In[5]:


med_data.average_age()


# Next, we can split the data by sex to see if we can spot any trends deoending on if the patient is male or female.
# 
# It seems that the data is pretty smiliar between males and females, with the one exception being that males pay about $1400 more on average.

# In[6]:


med_data.male_female()


# I was curious to see if the number of children had any correlation to BMI, as lifestyles can be very different for people with children 
# than those without, but the differences are not significant.

# In[7]:


med_data.children_to_bmi()


# Here we can see that there is a slight difference in the charges depending on the region the patient is from, but this may also be
# related to other factors such as age and likelihood to be a smoker in different regions.

# In[8]:


med_data.cost_by_region()


# This function runs several aggregates to compare how different factors affect whether a patient paid more or less than the median.
# The biggest factor by far is smoking status. Every single smoker in the data paid over the median, while only 1/3 of the non-smokers did.
# Another large factor is age, where the percentage of patients paying over median drastically rises after 45, with everyone over 55 paying
# above median. Sex and number of children did not seem to have any significant impact that can be inferred from this data.
# The same can be said of BMI with the exception of if the patient is obese, in which case there was a slight increase of patients over the median.

# In[9]:


med_data.cost_factors()

