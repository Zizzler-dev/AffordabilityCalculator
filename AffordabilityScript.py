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
    today = date(2023, 1, 1)
    birthDate = birthDate.split("/")
    birthDate = list(map(int, birthDate))
    age = today.year - birthDate[2] - ((today.month, today.day) < (birthDate[0], birthDate[1]))
    return age

def convert_df(df):
    return df.to_csv().encode('utf-8')

if census is not None:

    choice = st.radio('Choose One', ['Age Adjusted', 'Flat', 'Custom'])

    percent_increase_df = pd.DataFrame()
    censusdf = pd.read_csv(census)
    Premium_Data = pd.read_csv('LCSPP_21_single.csv')
    Zip_to_County = pd.read_csv('Zip To County.csv')
    Age_Curve = pd.read_csv('Age Curve.csv')

    affordable = 0
    unaffordableCount = 0
    unaffordable = pd.DataFrame()

    #st.write(censusdf)

    bosscontribution = st.number_input('Input Employer Contribution (21/Single): ')

    if bosscontribution > 0:
        Zip_to_County = Zip_to_County.drop_duplicates(subset = ['Zip Code'], ignore_index= True)

        join = pd.merge(Zip_to_County[['Zip Code', 'FIPS', 'State Key']], Premium_Data[['FIPS','LCSPP21']], on = 'FIPS', how = 'inner')
        #st.write(join)
        join = pd.merge(censusdf[['First Name','Last Name', 'DOB', 'Zip Code', 'Salary']], join, on = 'Zip Code', how = 'inner')
        #st.write(join.reset_index())
        #join = join.drop_duplicates(subset=['First Name', 'Last Name', 'DOB', 'Zip Code', 'Salary', 'county', 'State Key', 'rate' ], ignore_index=True)
        #st.write(join)
        #st.write(join)
        for i in join.index:
            age = calculateAge(join['DOB'][i])
            join['State Key'][i] = join['State Key'][i]+str(age)
        #st.write(join)
        
        join = pd.merge(join, Age_Curve[['State Key', 'Value']], on = 'State Key', how = 'inner')
        #st.write(join)
        #join = join.drop_duplicates(subset=['First Name', 'Last Name', 'DOB', 'Zip Code', 'Salary', 'county', 'State Key', 'rate' ], ignore_index=True)

        #st.write(join)


        join['Increase'] = " "
        


        for i in join.index:
            

            if(join['Salary'][i] < 14580):
                join['Salary'][i] = 14580


            if(choice == 'Age Adjusted'):
                employercontribution = bosscontribution * join['Value'][i]
            elif(choice == 'Flat'):
                employercontribution = bosscontribution
            elif(choice == 'Custom'):
                age = calculateAge(join['DOB'][i])
                if(age <= 44):
                    employercontribution = 262
                elif(age >= 45 and age <47):
                    employercontribution = 273
                elif(age >= 47 and age <50):
                    employercontribution = 308
                elif(age == 50):
                    employercontribution = 326
                elif(age > 50 and age < 54):
                    employercontribution = 382
                elif(age == 54):
                    employercontribution = 391
                elif(age >=55 and age < 58):
                    employercontribution = 503
                elif(age >= 58 and age < 60):
                    employercontribution = 638
                elif(age >= 60 and age < 63):
                    employercontribution = 680
                elif(age >= 63 and age <65):
                    employercontribution = 700
                elif(age >= 65):
                    employercontribution = 786


            premium = round (join['LCSPP21'][i] * join['Value'][i], 3)

            Employee_Contribution = premium - employercontribution
 
            Affordability_Threshold = (int(join['Salary'][i]) / 12) * 0.0839

            
            join['Increase'][i] = (premium - (Affordability_Threshold + employercontribution)) / employercontribution 


            if(Employee_Contribution <= Affordability_Threshold):
                affordable += 1

            else:
                unaffordable = unaffordable.append(join.iloc[i])
                unaffordableCount += 1

        join = join.sort_values(by = 'Increase')
        join = join.reset_index()
        #st.write(join)
        

        employercontribution = bosscontribution
    
        count = join.index[i]+1

        #st.write(count)
        final_affordability = (affordable/count) * 100


        if(final_affordability == 100):

            st.write('Your contribution is considered Affordable with ',final_affordability,'% of your employees having an affordable contribution.')

        else:

            st.write('Your contribution is considered Unaffordable with ',final_affordability,'% of your employees having an affordable contribution. You are suceptable to a fine of $', 4460 * unaffordableCount)
            st.download_button(
                label = "Download data of Unaffordable Employees",
                data = convert_df(unaffordable),
                file_name = 'unaffordable.csv',
                mime='text'
            )
