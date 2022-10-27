from tabnanny import check
from tabnanny import check
from typing import final
import streamlit as st
import pandas as pd
from datetime import date

st.image('zizzl health logo 22.png')

st.title("ICHRA Affordability Calculator")

st.subheader("Upload Census Here:")
census = st.file_uploader("Upload Census:")

def calculateAge(birthDate):
    today = date.today()
    birthDate = birthDate.split("/")
    birthDate = list(map(int, birthDate))
    age = today.year - birthDate[2] - ((today.month, today.day) < (birthDate[0], birthDate[1]))
    return age

def convert_df(df):
    return df.to_csv().encode('utf-8')

if census is not None:

    choice = st.radio('Choose One', ['Age Adjusted', 'Flat'])

    percent_increase_df = pd.DataFrame()
    censusdf = pd.read_csv(census)
    Premium_Data = pd.read_csv('Premium Data.csv')
    Zip_to_County = pd.read_csv('Zip To County.csv')
    Age_Curve = pd.read_csv('Age Curve.csv')

    affordable = 0
    unaffordable = pd.DataFrame()

    bosscontribution = st.number_input('Input Employer Contribution (21/Single): ')

    if bosscontribution > 0:
        Zip_to_County = Zip_to_County.drop_duplicates(subset = ['Zip Code'], ignore_index= True)

        join = pd.merge(Zip_to_County[['Zip Code', 'county', 'State Key']], Premium_Data[['county','LCSPP']], on = 'county', how = 'inner')
        #st.write(join)
        join = pd.merge(censusdf[['First Name','Last Name', 'DOB', 'Zip Code', 'Salary']], join, on = 'Zip Code', how = 'inner')
        #st.write(join.reset_index())
        #join = join.drop_duplicates(subset=['First Name', 'Last Name', 'DOB', 'Zip Code', 'Salary', 'county', 'State Key', 'rate' ], ignore_index=True)
        #st.write(join)
        #st.write(join)
        for i in join.index:
            age = calculateAge(join['DOB'][i])
            join['State Key'][i] = join['State Key'][i]+str(age)
        
        join = pd.merge(join, Age_Curve[['State Key', 'Value']], on = 'State Key', how = 'inner')
        #st.write(join)
        #join = join.drop_duplicates(subset=['First Name', 'Last Name', 'DOB', 'Zip Code', 'Salary', 'county', 'State Key', 'rate' ], ignore_index=True)

        #st.write(join)


        join['Increase'] = " "
        


        for i in join.index:
            

            if(join['Salary'][i] < 13590):
                join['Salary'][i] = 13590


            if(choice == 'Age Adjusted'):
                employercontribution = bosscontribution * join['Value'][i]
            else:
                employercontribution = bosscontribution

            premium = round (join['LCSPP'][i] * join['Value'][i], 3)

            Employee_Contribution = premium - employercontribution
 
            Affordability_Threshold = (int(join['Salary'][i]) / 12) * 0.0961

            
            join['Increase'][i] = (premium - (Affordability_Threshold + employercontribution)) / employercontribution 


            if(Employee_Contribution <= Affordability_Threshold):
                affordable += 1

            else:
                unaffordable = unaffordable.append(join.iloc[i])

        join = join.sort_values(by = 'Increase')
        join = join.reset_index()
        #st.write(join)
        

        employercontribution = bosscontribution
    
        count = join.index[i]+1

        #st.write(count)
        final_affordability = (affordable/count) * 100


        if(final_affordability == 100):

            st.write('Your contribution is considered Affordable with ',final_affordability,'% of your employees having an affordable contribution.')

        elif(final_affordability >= 95):

            increase_index = len(join.index) - 1
            percent_increase = round(join['Increase'][increase_index], 4) 

            st.write('Your contribution is considered Affordable with ',final_affordability,'% of your employees having an affordable contribution. An increase of ', percent_increase * 100, '% is required to have an 100% affordable contribution.  This equates to a contribution of ', round(bosscontribution+(bosscontribution * percent_increase)), 'for a single, 21 year old employee.')

            st.download_button(
                label = "Download data of Unaffordable Employees",
                data = convert_df(unaffordable),
                file_name = 'DBS_FSA.csv',
                mime='text'
            )
        else:

            increase_index = round((len(join.index)) * 0.95)
            percent_increase = round(join['Increase'][increase_index], 4)

            st.write('Your contribution is considered Unaffordable with ',final_affordability,'% of your employees having an affordable contribution. An increase of ', percent_increase * 100, '% is required to have an 95% affordable contribution. This equates to a contribution of ', round(bosscontribution+(bosscontribution * percent_increase)), 'for a single, 21 year old employee.')
            st.download_button(
                label = "Download data of Unaffordable Employees",
                data = convert_df(unaffordable),
                file_name = 'unaffordable.csv',
                mime='text'
            )
