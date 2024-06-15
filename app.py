import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

data = pd.read_csv('D:\My Com\Python & DA Projects\Streamlit_WebApp\startup_funding.csv')

#Some Data cleaning steps 
data.drop(columns=['Remarks'],inplace=True)
data.set_index('Sr No',inplace=True)
data.rename(columns = {'Date dd/mm/yyyy':'date',
                       'Startup Name':'Startup',
                       'City  Location':'City',
                       'Industry Vertical':'Vertical',
                       'SubVertical':'Subvertical',
                       'Investors Name':'Investors',
                       'InvestmentnType':'Round',
                       'Amount in USD':'Amount'},inplace=True)

#Formatting the Amount in dataframe
data['Amount'] = np.where((data['Amount'].isin(['Undisclosed','undisclosed','Unknown','unknown'])),0,data['Amount'])
data['Amount'] = data['Amount'].str.replace(',','')

data['Amount'].fillna(0,inplace = True)
data['Amount'] = data['Amount'].astype(str).replace('14342000+','14342000')
data['Amount'] = data['Amount'].str.replace('016200000','16200000')
data['Amount'] = data['Amount'].str.replace('0N/A','0')
data['Amount'] = data['Amount'].str.replace('\\\\xc2\\\\xa020000000','20000000')
data['Amount'] = data['Amount'].str.replace('\\\\xc2\\\\xa16200000','16200000')
data['Amount'] = data['Amount'].str.replace('\\\\xc2\\\\xa0','0')
data['Amount'] = data['Amount'].astype(float)


#Converting the Amount as Float data types, to Convert into INR(In Coror values)
data['Amount'] = data['Amount'].astype(float)
data['Amount'] = data['Amount'].apply(lambda x: x* 84/10000000)

#date time conversion from string to datetime, we provided errors='coerce, which will neglect the unsupported date format in column
data['date'] = data['date'].str.replace('05/072018','05/07/2018')
data['date'] = data['date'].str.replace('01/07/015','01/07/2015')
data['date'] = pd.to_datetime(data['date'],format='mixed',errors='coerce')
data['Year'] = round(data['date'].dt.year,0)
data['Month'] = round(data['date'].dt.month)
data.dropna(subset=['date','Startup','Vertical','City','Investors','Round','Amount'],inplace=True)

#Web App creation start
st.set_page_config(layout='wide',page_title='Start-up Investment')
st.sidebar.title("Startup Funding Analysis")
option = st.sidebar.selectbox("Select any analysis.",['Overall','Startup','Investors'])

#function to load investor analysis
def investor_loader(investor):
    st.subheader(investor)
    #show the recent five investment details.
    st.subheader("Most recent Investments.")
    most_recent_investment = data[data['Investors'].str.contains(investor,case=False,na=False)].head()[['date','Startup','Vertical','Round','Amount']]
    st.dataframe(most_recent_investment.reset_index(drop=True))

    #highest investment in particular startup by investors
    col1, col2,col3= st.columns(3,gap='small')
    with col1:
        st.subheader('Biggest Investmets.')
        new_invest_df = data[data['Investors'].str.contains(investor,na=False,case=False)]
        investment_df = new_invest_df.groupby(by='Startup')['Amount'].sum().sort_values(ascending=False).reset_index().head(6)
        st.dataframe(investment_df)
    with col2:
        #plot bar chart of investment
        st.subheader('Investment Chart.')
        fig, ax = plt.subplots()
        ax.bar(investment_df['Startup'],investment_df['Amount'],width=0.4)
        st.pyplot(fig,ax.set_xlabel('Start-up Names'),ax.set_ylabel('In Coror(Rs)'))
    with col3:
        st.subheader('Top Invsted Sectors.')
        vertical_df = data[data['Investors'].str.contains(investor,na=False)].groupby(by='Vertical')['Amount'].sum().sort_values(ascending=False).reset_index()
        fig1,ax1 = plt.subplots()
        ax1.pie(vertical_df['Amount'].head(),labels=vertical_df['Vertical'].head(),radius=1.5,autopct='%0.01f%%')
        st.pyplot(fig1)
    #plot a graph for YOY Investment
    col4,col5,_ = st.columns(3,gap='small')
    with col4:
        st.subheader('YoY Investment.')
        YoY_invest_df = data[data['Investors'].str.contains(investor,na=False,case=False)].groupby(by='Year')['Amount'].sum().reset_index().sort_values(by='Year')
        st.dataframe(YoY_invest_df.head())
    with col5:
        st.subheader('YoY Invest Chart.')
        fig2,ax2 = plt.subplots()
        ax2.plot(YoY_invest_df['Year'],YoY_invest_df['Amount'])
        st.pyplot(fig2,ax2.set_xlabel('Year'),ax2.set_ylabel('Amount (in Coror Rs)'))

def Startup_loader(startup):
    st.title(startup)

def load_overall_analysis():
    total_funded_amount = round(data['Amount'].sum())
    col1,col2,col3,col4 = st.columns(4,gap='small')
    with col1:
        st.metric('Total Funded Amount',str(total_funded_amount)+' Cr')
    with col2:
        startup_details = data.groupby(by='Startup')['Amount'].sum().sort_values(ascending=False).head(1)
        startup_name = startup_details.index[0]
        amount_invested = startup_details.values[0]
        st.metric('Highest Funding by individual Statup ',str(round(amount_invested))+' Cr')
    with col3:
        avg_funded_amount = round(data['Amount'].mean())
        st.metric('Averege Funded',str(avg_funded_amount)+' Cr')
    with col4:
        all_funded_startup = data[data['Amount'] > 0]['Startup'].nunique()
        st.metric('Funded Startup counts.',str(all_funded_startup))
    
    #checking investment periodically
    MoM_invest_df = data.groupby(by=['Year','Month'])['Amount'].sum().reset_index()
    MoM_invest_df['Period'] = MoM_invest_df['Month'].astype(str) + '-' + MoM_invest_df['Year'].astype(str)

    #startup count in each period getting funded
    funded_startup_count = data.groupby(by=['Year','Month'])['Startup'].count().reset_index()
    funded_startup_count['Period'] = funded_startup_count['Month'].astype(str) + '-' + funded_startup_count['Year'].astype(str)
    funded_startup_count.rename(columns={'Startup':'Startup_count'},inplace=True)

    col1,col2 = st.columns(2,gap='small')
    with col1:
        st.subheader('MoM Investment amount.')
        fig3,ax3 = plt.subplots()
        ax3.plot(MoM_invest_df['Period'],MoM_invest_df['Amount'])
        ticks = list(MoM_invest_df['Period'])
        plt.xticks([ticks[i] for i in range(len(ticks)) if i % 5 == 0], rotation=45)
        st.pyplot(fig3,ax3.set_xlabel('Period'),ax3.set_ylabel('Amount (in Coror Rs)'))
    with col2:
        st.subheader('Funded Startup count periodically.')
        fig4,ax4 = plt.subplots()
        ax4.plot(funded_startup_count['Period'],funded_startup_count['Startup_count'])
        ticks = list(funded_startup_count['Period'])
        plt.xticks([ticks[i] for i in range(len(ticks)) if i % 5 == 0], rotation=45)
        st.pyplot(fig4,ax4.set_xlabel('Period'),ax4.set_ylabel('Count of startups.'))
    
    
if option == "Overall":
    st.title("Overall Analysis")
    btn0 = st.sidebar.button('Check Overall Analysis')
    if btn0:
        load_overall_analysis()


elif option == "Startup":
    st.title('Startup Analysis')
    selected_startup = st.sidebar.selectbox("Select any one startup.",sorted(data['Startup'].unique().tolist()))
    btn = st.sidebar.button("Find Startup Details")

    if btn:
        Startup_loader(selected_startup)
else:
    st.title("Invstor Analysis")
    selected_investor = st.sidebar.selectbox("Select Investor name.",sorted(set(data['Investors'].apply(lambda x:x.split(',')).sum())))
    btn2 = st.sidebar.button('Find Investor details')

    if btn2:
        investor_loader(selected_investor)

