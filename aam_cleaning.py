
import numpy as np
import pandas as pd
from generalize_function import generalize

# read the data, file can be found in the folder 'data'
df = pd.read_excel('Survey_2019.xlsx', header=1)
# Rename the columns for ease
df = df.set_axis(['Timestamp','Age_Range','Industry','Job','Salary_annual','Currency','Location','Years_of_Experience','Extra_info','Other'], axis=1)

tempdf = df

# Find the null values in Salary_annual and their index. Then remove the null values
s = tempdf['Salary_annual']
s[pd.isna(s)]
tempdf['Salary_annual'] = tempdf.Salary_annual.dropna()
tempdf.head()
tempdf = tempdf.drop([30816,30207,17054])

# Convert the Salary_annual column to a string
tempdf['Salary_annual'] = tempdf['Salary_annual'].astype('str')
# Remove unwanted elements
tempdf['Salary_annual'] = tempdf.Salary_annual.str.replace(' ', '', regex=True)
tempdf['Salary_annual'] = tempdf.Salary_annual.str.replace(',', '', regex=True)
tempdf['Salary_annual'] = tempdf.Salary_annual.str.replace('-', '', regex=True)

#Extract the number values from Salary_annual
tempdf['clean_salary'] = tempdf.Salary_annual.str.extract("(\d+)",expand=False).astype(float)

# Drop the columns 'Extra info' and 'Others'
tempdf = tempdf.drop(['Extra_info','Other'], axis=1)
# Drop all null values
tempdf = tempdf.dropna()

# Create a mask that locates the values with 'k' next to them (such as 45k). Then multiply those values by 1000
k_val = tempdf['Salary_annual'].str.contains('[0-9]k',case=False,regex=True)
tempdf['temp_val'] = k_val
tempdf.loc[tempdf['temp_val'] == True, 'clean_salary'] *= 1000 
tempdf = tempdf.drop('temp_val', axis=1)

# Create another mask to locate values with 'm' next to them (such as 1m). Then multiply those values by 1000000
m_val = tempdf['Salary_annual'].str.contains('[0-9]m',case=False,regex=True)
tempdf[m_val]
tempdf['clean_salary'].loc[[15669,24626,5313]] *= 1000000 

# Convert the clean_salary to USD
tempdf.loc[tempdf['Currency'] == 'GBP', 'clean_salary'] *= 1.38
tempdf.loc[tempdf['Currency'] == 'CAD', 'clean_salary'] *= 0.79
tempdf.loc[tempdf['Currency'] == 'AUD/NZD', 'clean_salary'] *= 0.73
tempdf.loc[tempdf['Currency'] == 'EUR', 'clean_salary'] *= 1.18
tempdf.loc[tempdf['Currency'] == 'CHF', 'clean_salary'] *= 1.09
tempdf.loc[tempdf['Currency'] == 'JPY', 'clean_salary'] *= 0.0091
tempdf.loc[tempdf['Currency'] == 'SEK', 'clean_salary'] *= 0.12
tempdf.loc[tempdf['Currency'] == 'HKD', 'clean_salary'] *= 0.13
tempdf.loc[tempdf['Currency'] == 'ZAR', 'clean_salary'] *= 0.069

# Drop currencies with 'Other'
tempdf = tempdf.drop(tempdf.loc[tempdf['Currency'] == 'Other'].index)

z = tempdf.copy()

# Create a set with tupple pairs to begin sorting the text in the 'Industry' column
industry_patterns = [('Information','Information Technology'),('software','Information Technology'),('Web','Information Technology'),
                    ('Gover','Public'),('Public','Public'),('Librar','Public'),('Policy','Public'),('Health','Healthcare'),
                    ('Blood','Healthcare'),('Medicine','Healthcare'),('Doctor','Healthcare'),('Hospital','Healthcare'),('Education','Education'),
                    ('School','Education'),('Academia','Education'),('Teacher','Education'),('Finance','Finance'), ('Market','Finance'),
                    ('Money','Finance'),('Stock','Finance'),('Artistic','Arts'),('Perform','Arts'),('Acting','Arts'),('Science','Science'),
                    ('Bio','Science'),('Chem','Science'),('Engineer','Engineering'),('Math','Science'),('comput','Information Technology'),
                    ('technology','Information Technology'),('Media','Media'),('Judiciary','Public'),('Food','Public'),
                    ('real estate','Public'),('Guard','Public'),('Wholesale','Public'),('Shop','Public'),('Audio','Arts'),('Bank','Finance'),
                    ('Retail','Public'),('Nonprofit','Public'),('Non-profit','Public'),('Financial Services','Finance'),('Accounting','Finance'),
                    ('Advertising','Finance'),('Consult','Finance'),('Aerospace','Engineering'),('Automotive','Engineering'),
                    ('Manufacturing','Engineering'),('Energy','Engineering'),('Law','Law'),('Legal','Law'),('Insurance','Law'),('Publishing','Arts'),
                    ('Higher Ed','Education'),('Defense','Public'),('Medical','Healthcare'),('Architecture','Engineering'),('Libraries','Public'),
                    ('Non profit','Public'),('Transportation','Public'),('Entertainment','Media'),('Aviation','Public'),('Pharmaceutical','Healthcare'),
                    ('Medical','Healthcare'),('Research','Science'),('Journalism','Media'),('Construction','Public'),('Oil and Gas','Engineering'),
                    ('Communications','Public'),('Human Resources','Finance'),('Oil & Gas','Engineering'),('Utilities','Public'),
                    ('Museum','Arts'),('Sales','Finance'),('Logistics','Finance'),('Design','Arts'),('Telecom','Information Technology'),
                    ('Agriculture','Public'),('Pharma','Healthcare'),('Financial','Finance'),('Professional Services','Other'),('Semiconductor','Engineering'),
                    ('CPG','Public'),('Mining','Engineering'),('Fintech','Engineering'),('Travel','Other'),('Philanthropy','Other'),('Security','Public'),
                    ('Utility','Public'),('Fashion','Arts'),('Restaurant','Other'),('SaaS','Information Technology'),('Social Services','Public'),
                    ('Property Management','Other'),('Airline','Public'),('Grocery','Public'),('International Development','Public'),
                    ('Consumer Goods','Public'),('commerce','Finance'),('Customer','Finance'),('Internet','Information Technology'),('Service','Public'),
                    ('Fundraising','Other'),('Distribution','Finance'),('Video','Media'),('Military','Public'),('Recruit','Other'),('Consumer','Finance'),
                    ('Game','Media'),('it','Information Technology'),('Staff','Other'),('Tourism','Other'),('Music','Media'),('Electronic','Information Technology'),
                    ('tech','Information Technology'),('television','Media'),('Beauty','Finance'),('Social','Public'),('Nurs','Healthcare'),
                    ('Mortgage','Other'),('HR','Finance'),('Sports','Media'),('Supply','Finance'),('Dental','Healthcare'),('PR','Media'),
                    ('Event','Other'),('Electric','Engineering'),('Environ','Science'),('hvac','Engineering'),('Gaming','Media'),
                    ('Investment','Finance'),('Management','Finance'),('Packag','Public'),('Theatre','Arts'),('Nuclear','Engineering'),
                    ('Veter','Healthcare'),('Church','Other'),('Relig','Other'),('FMCG','Finance'),('Steel','Engineering'),
                    ('Dentist','Healthcare'),('Child','Public'),('Film','Media'),('Oil','Engineering'),('Gas','Engineering'),
                    ('Photo','Arts'),('Academ','Education'),('Urban','Public'),('Solar','Engineering'),('Industrial','Engineering'),
                    ('Ship','Public'),('Executive','Finance'),('Asso','Finance'),('Admin','Finance'),('Robot','Engineering'),('Heat','Healthcare'),
                    ('care','Healthcare'),('Archives','Public'),('Marine','Engineering'),('Pay','Finance'),('R&D','Science'),('Train','Other'),
                    ('Teach','Education'),('Econ','Finance'),('Apparel','Finance'),('Data','Information Technology'),('Truck','Other'),('Cann','Other'),
                    ('Recre','Public'),('Auto','Engineering'),('Forest','Public'),('Pow','Engineering'),('Radio','Media'),('Dev','Information Technology'),
                    ('Tax','Finance'),('NGO','Other'),('Startup','Other'),('Pet','Healthcare'),('Wine','Other'),('Ret','Other'),('Plast','Science'),
                    ('Water','Public'),('govt','Public'),('Networking','Other'),('Athletic','Media'),('DoD','Other'),('Clinic','Healthcare'),('Transp','Public'),
                    ('Wire','Information Technology'),('Material','Engineering'),('Transl','Arts'),('Tex','Arts'),('Busi','Finance'),('Atto','Law'),('News','Media'),
                    ('Recyc','Other'),('Cosmetic','Public'),('Rail','Public'),('Coff','Public'),('Optic','Healthcare'),('Anim','Media'),('Psyc','Healthcare'),('Land','Public'),
                    ('Build','Public'),('Hous','Public'),('Arts','Arts'),('Pest','Other'),('Casino','Other'),('Broad','Media'),('Clerg','Other'),
                    ('Well','Healthcare'),('Analy','Finance'),('Creat','Arts'),('Labor','Public'),('Dip','Public'),('Senior','Other'),
                    ('Regul','Finance'),('Compli','Other'),('Freight','Other'),('Art','Arts'),('Arch','Science'),('Heavy','Public'),('Hotel','Public'),
                    ('Cab','Public'),('Const','Public'),('Natur','Science'),('Space','Science'),('Resort','Public'),('Sport','Media'),('Floor','Other'),
                    ('Trade','Finance'),('VFX','Media'),('AEC','Engineering')]

# Convert the 'Industry' column to string
z['Industry'] = tempdf['Industry'].astype('string')

# Use the generalize function (check the generalize_function.py file). This will sort the column and create a new column based on sector
z['clean_industry'] = generalize(z['Industry'], industry_patterns)

# Create a list of the sectors you made in 'clean_industry' and drop the rest. 
# The dropped values are mostly industries that are difficult to fit into the current list
ind_list = ['Public','Information Technology','Finance','Healthcare','Education','Engineering','Law','Media','Arts','Science','Other']
z = z.drop(z.loc[z['clean_industry'].isin(ind_list) == False].index)

# Drop the 'Timestamp' column
z = z.drop('Timestamp',axis=1)

yr = z.copy()

# Convert 'location' column to string. Create a patterns list for locations.
yr['Location'] = z['Location'].astype('string')
location_patterns = [('USA','USA'),('New York','USA'),('Las Vegas','USA'),('UK','UK'),('TN','USA'),('Washington','USA'),('DC','USA'),('AUS','Australia'),
                    ('Sydney','Australia'),('Cali','USA'),('Chic','USA'),('Phil','USA'),('Boston','USA'),('Los Angeles','USA'),('Canada','Canada'),('United States','USA'),
                    ('London','UK'),('Toronto','Canada'),('Denver','USA'),('Texas','USA'),('Seattle','USA'),('NYC','USA'),('United Kingdom','UK'),
                    ('TX','USA'),('MN','USA'),('WA','USA'),('San Francisco','USA'),('Ohio','USA'),('Florida','USA'),('Germany','Germany'),
                    ('AZ','USA'),('Virgin','USA'),('GA','USA'),('PA','USA'),('San Diego','USA'),('Indiana','USA'),('MD','USA'),('OR','USA'),
                    ('WI','USA'),('Ireland','Ireland'),('New Zealand','New Zealand'),('Utah','USA'),('MO','USA'),('Minne','USA'),('Mary','USA'),
                    ('New Jersey','USA'),('Penn','USA'),('Ill','USA'),('VA','USA'),('OH','USA'),('UT','USA'),('Netherlands','Netherlands'),
                    ('England','UK'),('FL','USA'),('MI','USA'),('CO','USA'),('Mass','USA'),('NJ','USA'),('Atl','USA'),('CT','USA'),
                    ('Sweden','Sweden'),('Belgium','Belgium'),('Hong Kong','Hong Kong'),('Melbourne','Australia'),('Detr','USA'),
                    ('Tenn','USA'),('Dall','USA'),('Houston','USA'),('OK','USA'),('Omaha','USA'),('Pitt','USA'),('Ariz','USA'),('Ark','USA'),
                    ('kent','USA'),('SF','USA'),('Nebr','USA'),('Ontario','Canada'),('Louis','USA'),('Nebra','USA'),('Kans','USA'),('Ida','USA'),
                    ('SC','USA'),('Alberta','Canada'),(', CA','USA'),('Alaska','USA'),('Italy','Italy'),('Finalnd','Finland'),('Salt','USA'),('Alaska','USA'),
                    ('AR','USA'),('Brisbane','Australia'),('New Ham','USA'),('Rhode','USA'),('Phoenix','USA'),('Auckland','New Zealand'),('Albuq','USA'),
                    ('Boise','USA'),('Honolulu','USA'),('San Ant','USA'),('NSW','Australia'),('Sacramento','USA'),('UAE','UAE'),('Reno','USA'),('France','France'),
                    ('Frankfurt','Germany'),(', NY','USA'),('Main','USA'),('Alabama','USA'),('Upstate','USA'),('Roches','USA'),('Paris','France'),
                    ('Wales','UK'),('Scotland','UK'),('Glasgow','UK'),('Brussels','Belgium'),('Amsterdam','Netherlands'),('Raleigh','USA'),
                    ('Provid','USA'),('Durham','USA'),('Berlin','Germany'),(', MA','USA'),(', IL','USA'),(', NH','USA'),(', NY','USA')]

# Use the generalize function to sort the column and group it into a new column. This will be sorted by countries.
yr['clean_location'] = generalize(yr['Location'], location_patterns)

# Drop values which cannot fit into the existing countries list
loc_list = ['USA','Canada','UK','Australia','Germany','New Zealand','Ireland','Netherlands','Belgium','Sweden','France','Hong Kong','Italy','Finland','UAE']
yr = yr.drop(z.loc[yr['clean_location'].isin(loc_list) == False].index)

final = yr.copy()

# Drop the old columns
final = final.drop(['Industry','Location','Salary_annual','Currency'],axis=1)

# Rename the new columns with the proper names
final = final.rename(columns={'clean_industry': 'Sector', 'clean_salary': 'Annual_Salary(USD)','clean_location': 'Location'})

# Rearrange the columns
final = final.iloc[:,[0,4,1,3,2,5]]

# Export the dataframe as an excel file
final.to_excel(r'path\aam_clean_data.xlsx', index = False, header=True)
