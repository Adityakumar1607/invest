
import pandas as pd
import streamlit as st
import os
import ta
import mplfinance as mpf
import numpy as np
import datetime
import warnings
warnings.filterwarnings('ignore')

st.title('Stock Analysis')
st.sidebar.title("Do you want to use indicator")

# Define choices for the radio button
choices = ["Yes","No"]

# Radio button with the first choice pre-selected
action = st.sidebar.radio("Select an option:", choices, index=1)

if action == "Yes":

    def bb(country,exchange,name,initialcapital,indicator,window,type,start,end,volume,hold):
        if country== "India":
                  
            if exchange=="NSE":
                path = f"Stock/INDIA/NSE/{name}.csv"
            elif exchange=="BSE":
                path = f"Stock/INDIA/BSE/{name}.csv"
            price = " RS"
            symbol="₹ "
    
        elif country == "USA":
            path = f"Stock/US/{name}.csv"
            price=" Doller"
            symbol ="$ "
    
        elif country == "Japan":
            path = f"Stock/Japan/{name}.csv"
            price=" Yen"
            symbol="¥ "
        
        else:
            print("Select a valid country")


        if os.path.exists(path):
            data =pd.read_csv(path)

            data['Date'] = pd.to_datetime(data['Date']).dt.tz_localize(None)
            starting = pd.to_datetime(start,format='mixed')
            ending = pd.to_datetime(end,format='mixed')

            if volume.strip().lower()=="true":
                volume = True
            elif volume.strip().lower()=="false":
                volume = False
                
            if hodl.strip().lower()=="true":
                hodl = True
            elif hodl.strip().lower()=="false":
                hodl = False
                
            if starting not in data['Date'].dt.normalize().values:
                st.error("starting date is invalid")

            elif ending not in data['Date'].dt.normalize().values:
                st.error("ending date is invalid")

            elif starting<ending:
                if indicator == "Bollinger Band" :
                    data = data[(data['Date']>=starting)&(data['Date']<=ending)]
                    data['bb'] = ta.volatility.bollinger_mavg(data['Close'],window=window)
                    data['ubb'] = ta.volatility.bollinger_hband(data['Close'],window=window,window_dev=2)
                    data['lbb'] = ta.volatility.bollinger_lband(data['Close'],window=window,window_dev=2)

                    if type == "Aggressive":
                        buy = 0.95
                        sell = 1.05

                    elif type == "Moderate":
                        buy = 0.98
                        sell = 1.02

                    else:
                        buy = 1
                        sell = 1

                    capital = initialCapital
                    holding = 0
                    tradeHistory = []

                    for index, row in data.iterrows():
                        ClosePrise = row['Close']

                        if (ClosePrise<row['lbb']*buy) and capital> ClosePrise:
                            shearToBuy = capital//ClosePrise
                            capital -= shearToBuy*ClosePrise
                            holding += shearToBuy
                            tradeHistory.append((row['Date'],"Buy",ClosePrise,holding,capital))


                        elif (ClosePrise > row['ubb']*sell) and holding >0:
                            capital += holding*ClosePrise
                            tradeHistory.append((row['Date'],"Sell",ClosePrise,holding,capital))
                            holding = 0

                    portfolio = capital + (holding * data.iloc[-1]['Close'])

                    netPosition = portfolio-initialCapital
                    
                    
                    fig1,ax = mpf.plot(data.set_index('Date'),
                                        type='candle',
                                        style='charles',
                                        title='Stock Price Candlestick Chart',
                                        ylabel=f'Price {price}',
                                        volume=volume,returnfig=True)
                    
                    buy_yvalues = np.nan * np.ones(len(data))
                    sell_yvalues = np.nan * np.ones(len(data))

                    for i, date in enumerate(data['Date']):
                        for t in tradeHistory:
                            if t[0]  == date and t[1] =="Buy":
                                buy_yvalues[data['Date'] == date] = t[2]

                            if t[0] == date and t[1] == "Sell":
                                sell_yvalues[data['Date'] == date] = t[2]
                    
                    
                    buy_plot = mpf.make_addplot(buy_yvalues, scatter=True, markersize=100, marker='^', color='g', panel=0, secondary_y=False)
                    sell_plot = mpf.make_addplot(sell_yvalues, scatter=True, markersize=100, marker='v', color='r', panel=0, secondary_y=False)

                    fig2,ax=mpf.plot(data.set_index('Date'),
                            type='candle',
                            style='charles',
                            title='Bollenger Band long position on the chart',
                            ylabel=f'Price {price}',
                            volume=volume,
                            addplot=[buy_plot, sell_plot],
                            returnfig=True) 
                    st.pyplot(fig1)    

                    if hodl:
                        remcap = tradeHistory[0][4]
                        p = tradeHistory[0][2]
                        d = data.iloc[-1]['Close']
                        h = tradeHistory[0][3]
                        v = (d*h)-(p*h)
                        cap= v+remcap
                        nk=cap-initialCapital
                        return f"If you hold the stock of {name} without making any trade on the investment: {symbol}{initialCapital} you will get:{symbol} {cap:.2f} and your net position will be: {symbol}{nk:.2f}."


                    
                    else:                    
                        st.pyplot(fig2)
                        return f"The stock {name} with the initial capital: {symbol}{initialCapital} and the indicator: {indicator} the portfolio is :{symbol}{portfolio:.2f} and the net position is :{symbol}{netPosition:.2f}."

                if indicator == "RSI" :
                    data = data[(data['Date']>=starting)&(data['Date']<=ending)]
                    data['RSI'] = ta.momentum.rsi(data['Close'], window = window,)
                    
                    if type == "Aggressive":
                        buy = 30
                        sell = 80

                    elif type == "Moderate":
                        buy = 25
                        sell = 75

                    else:
                        buy = 20
                        sell = 70

                    capital = initialCapital
                    holding = 0
                    trade_history = []

                    for index, row in data.iterrows():
                        ClosePrise=row['Close']

                        if (row['RSI']<buy) and capital>ClosePrise:
                            shares_to_buy = capital // ClosePrise
                            capital -= shares_to_buy * ClosePrise
                            holding += shares_to_buy
                            trade_history.append((row['Date'], 'Buy', ClosePrise,holding,capital))
                        
                        elif(row['RSI']>sell) and holding>0:
                            capital += holding * ClosePrise
                            trade_history.append((row['Date'], 'Sell', ClosePrise,holding,capital))
                            holding = 0
                        

                    portfolio = capital + (holding * data.iloc[-1]['Close'])
                    netPosition = portfolio-initialCapital

                    data = data[(data['Date']>=starting)&(data['Date']<=ending)]
                    fig1,ax = mpf.plot(data.set_index('Date'),
                                        type='candle',
                                        style='charles',
                                        title='Stock Price Candlestick Chart',
                                        ylabel=f'Price {price}',
                                        volume=volume,returnfig=True)
                    
                    buy_yvalues = np.nan * np.ones(len(data))
                    sell_yvalues = np.nan * np.ones(len(data))

                    for i, date in enumerate(data['Date']):
                        for t in trade_history:
                            if t[0]  == date and t[1] =="Buy":
                                buy_yvalues[data['Date'] == date] = t[2]

                            if t[0] == date and t[1] == "Sell":
                                sell_yvalues[data['Date'] == date] = t[2]

                    buy_plot = mpf.make_addplot(buy_yvalues, scatter=True, markersize=100, marker='^', color='g', panel=0, secondary_y=False)
                    sell_plot = mpf.make_addplot(sell_yvalues, scatter=True, markersize=100, marker='v', color='r', panel=0, secondary_y=False)

                    fig2,ax=mpf.plot(data.set_index('Date'),
                            type='candle',
                            style='charles',
                            title='RSI long position on the chart',
                            ylabel=f'Price {price}',
                            volume=volume,
                            addplot=[buy_plot, sell_plot],
                            returnfig=True) 
                    st.pyplot(fig1)              
                    
                    if hodl:
                        remcap = tradeHistory[0][4]
                        p = tradeHistory[0][2]
                        d = data.iloc[-1]['Close']
                        h = tradeHistory[0][3]
                        v = (d*h)-(p*h)
                        cap= v+remcap
                        nk=cap-initialCapital
                        return f"If you hold the stock of {name} without making any trade on the investment: {symbol}{initialCapital} you will get:{symbol} {cap:.2f} and your net position will be: {symbol}{nk:.2f}"

        
                    
                    else:                    
                        st.pyplot(fig2)
                        return f"The stock {name} with the initial capital: {symbol}{initialCapital} and the indicator: {indicator} the portfolio is :{symbol}{portfolio:.2f} and the net position is :{symbol}{netPosition:.2f}"


                if indicator=="VWAP":
                    data = data[(data['Date']>=starting)&(data['Date']<=ending)]
                    data['VWAP'] = ta.volume.volume_weighted_average_price(data['High'],data['Low'],data['Close'],data['Volume'],window=window)
                    if type == "Aggressive":
                            buy = 0.98
                            sell = 1.04

                    elif type == "Moderate":
                        buy = 0.96
                        sell = 1.03

                    else:
                        buy = 0.95
                        sell = 1.02  


                    capital = initialCapital
                    holding = 0
                    trade_history = []

                    for index, row in data.iterrows():
                        ClosePrise=row['Close']

                        if (ClosePrise<row['VWAP']*buy) and capital>ClosePrise:
                            shares_to_buy = capital // ClosePrise
                            capital -= shares_to_buy * ClosePrise
                            holding += shares_to_buy
                            trade_history.append((row['Date'], 'Buy', ClosePrise,holding,capital))
                        
                        elif(ClosePrise>row['VWAP']*sell) and holding>0:
                            capital += holding * ClosePrise
                            trade_history.append((row['Date'], 'Sell', ClosePrise,holding,capital))
                            holding = 0
                        

                    portfolio = capital + (holding * data.iloc[-1]['Close'])
                    netPosition = portfolio-initialCapital

                    data = data[(data['Date']>=starting)&(data['Date']<=ending)]
                    fig1,ax = mpf.plot(data.set_index('Date'),
                                        type='candle',
                                        style='charles',
                                        title='Stock Price Candlestick Chart',
                                        ylabel=f'Price {price}',
                                        volume=volume,returnfig=True)
                    
                    buy_yvalues = np.nan * np.ones(len(data))
                    sell_yvalues = np.nan * np.ones(len(data))

                    for i, date in enumerate(data['Date']):
                        for t in trade_history:
                            if t[0]  == date and t[1] =="Buy":
                                buy_yvalues[data['Date'] == date] = t[2]

                            if t[0] == date and t[1] == "Sell":
                                sell_yvalues[data['Date'] == date] = t[2]

                    buy_plot = mpf.make_addplot(buy_yvalues, scatter=True, markersize=100, marker='^', color='g', panel=0, secondary_y=False)
                    sell_plot = mpf.make_addplot(sell_yvalues, scatter=True, markersize=100, marker='v', color='r', panel=0, secondary_y=False)

                    fig2,ax=mpf.plot(data.set_index('Date'),
                            type='candle',
                            style='charles',
                            title='VWAP long position on the chart',
                            ylabel=f'Price {price}',
                            volume=volume,
                            addplot=[buy_plot, sell_plot],
                            returnfig=True) 
                    st.pyplot(fig1)              

                    if hodl:
                        remcap = tradeHistory[0][4]
                        p = tradeHistory[0][2]
                        d = data.iloc[-1]['Close']
                        h = tradeHistory[0][3]
                        v = (d*h)-(p*h)
                        cap= v+remcap
                        nk=cap-initialCapital
                        return f"If you hold the stock of {name} without making any trade on the investment: {symbol}{initialCapital} you will get:{symbol} {cap:.2f} and your net position will be: {symbol}{nk:.2f}"


                    
                    else:                    
                        st.pyplot(fig2)
                        return f"The stock {name} with the initial capital: {symbol}{initialCapital} and the indicator: {indicator} the portfolio is :{symbol}{portfolio:.2f} and the net position is :{symbol}{netPosition:.2f}"

        
            elif starting>ending:
                st.error(f"{starting} date is greater then {ending} date")
            
        else:
            st.error(f"{path} didn't exist")
        
    min_date = datetime.date(2010,1,1)
    max_date = datetime.date(2024,11,11)

    st.title("Stock Analysis with Bollinger Bands")
    st.sidebar.header("Input Parameters")

    # Sidebar inputs
    country = st.sidebar.selectbox("Select the country",["India","USA","Japan"])
    if country == "India":
        
        exchange = st.sidebar.selectbox ("Sekect an exchange",["NSE","BSE"])
        if exchange == "NSE":
            stock_name = st.sidebar.selectbox("Enter stock name",['APOLLO TYRE', 'ASHOK LEYLAND', 'ATUL AUTO', 'BAJAJ AUTO', 'BOSCH', 'CEAT TYRES', 'EICHER MOTORS', 'ESCORTS MOTORS', 'EXIDE IND', 'FORCE MOTORS', 'HERO MOTO CORP', 'JK TYRE', 'Mahindra & Mahindra', 'MARUTI', 'MRF TYRES', 'SML ISUZU', 'SONA COMSTAR', 'TATA MOTORS', 'TATA POWER', 'TVS MOTORS'] )
        elif exchange == "BSE":
            stock_name = st.sidebar.selectbox("Enter stock name",['APOLLO TYRE', 'ASHOK LEYLAND', 'ATUL AUTO', 'BAJAJ AUTO', 'BOSCH', 'CEAT TYRES', 'EICHER MOTORS', 'ESCORTS MOTORS', 'EXIDE IND', 'FORCE MOTORS', 'HERO MOTO CORP', 'JK TYRE', 'Mahindra & Mahindra', 'MARUTI', 'MRF TYRES', 'SML ISUZU', 'SONA COMSTAR', 'TATA MOTORS', 'TATA POWER', 'TVS MOTORS'] )
    elif country == "USA":
        stock_name = st.sidebar.selectbox("Enter stock name",['BMW', 'Ford', 'General Motors', 'Honda', 'Lucid Motors', 'NIO', 'Rivian', 'Stellantis', 'Tesla', 'Toyota'])
        exchange = None

    else:
        stock_name = st.sidebar.selectbox("Enter stock name",['7201.T - Nissan', '7202.T - Isuzu Motors', '7203.T - Toyota', '7205.T - Hino Motors', '7211.T - Mitsubishi Motors', '7261.T - Mazda', '7267.T - Honda', '7269.T - Suzuki', '7270.T - Subaru', '8015.T - Toyota Tsusho'])
        exchange =  None


    initial_capital = st.sidebar.number_input("Enter initial capital", min_value=0, value=100000)
    indicator = st.sidebar.selectbox("Select indicator", ['Bollinger Band','RSI','VWAP'])
    window = st.sidebar.number_input("Enter window size", min_value=16,max_value=100,value =50)
    risk_type = st.sidebar.selectbox("Select risk type", ["Low","Moderate","Aggressive"])
    start_date = st.sidebar.date_input("Select start date",min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("Select end date",min_value=min_date, max_value=max_date)
    volume = st.sidebar.selectbox("Show volume?", ["True", "False"])
    hodl = st.sidebar.selectbox("Want to hodl?", ["True", "False"])

    # Trigger analysis
    if st.sidebar.button("Run Analysis"):
        result = bb(country,exchange,stock_name, initial_capital, indicator, window, risk_type, start_date, end_date, volume, hodl)
        st.write(result)   


elif action == "No":
    def portfolio(country,exchange,name, capital, starting, ending):
        if country== "India":
                  
            if exchange=="NSE":
                path = f"Stock/INDIA/NSE/{name}.csv"
            elif exchange=="BSE":
                path = f"Stock/INDIA/BSE/{name}.csv"
            price = " RS"
            symbol="₹ "
    
        elif country == "USA":
            path = f"Stock/US/{name}.csv"
            price=" Doller"
            symbol ="$ "
    
        elif country == "Japan":
            path = f"Stock/Japan/{name}.csv"
            price=" Yen"
            symbol="¥ "
        
        else:
            print("Select a valid country")

        if os.path.exists(path):
            df = pd.read_csv(path)

            # Convert the 'Date' column to datetime
            df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
            starting = pd.to_datetime(starting, format="mixed")
            ending = pd.to_datetime(ending, format="mixed")

            # Validate the date range
            if starting < ending:
                fil_df = df[(df['Date'] >= starting) & (df['Date'] <= ending)]
                
                # Check if filtered data is empty
                if fil_df.empty:
                    return f"No data available for the stock '{name}' within the selected date range ({starting} to {ending})."

                # Plot the candlestick chart
                mpf.plot(fil_df.set_index('Date'), type='candle', style='charles',
                        title='Stock Price Candlestick Chart', ylabel='Price (₹)', volume=True)

                # Calculate buy and sell prices
                buyClosePrice = fil_df.iloc[0]['Close']
                sellClosePrice = fil_df.iloc[-1]['Close']

                # Calculate the number of shares that can be bought
                if capital > buyClosePrice:
                    sharesCanBuy = capital // buyClosePrice
                    usedCapital = sharesCanBuy * buyClosePrice
                    remainingCapital = capital - usedCapital
                    portfolioValue = sharesCanBuy * sellClosePrice + remainingCapital
                    netPosition = portfolioValue - capital

                    return f"You can buy {sharesCanBuy} shares of {name} at ({symbol}{buyClosePrice:.2f}) each. Your portfolio value at the end will be ({symbol}{portfolioValue:.2f}) with a net position of ({symbol}{netPosition:.2f})."
                else:
                    return f"Your initial capital ({symbol}{capital:.2f}) is lower than the stock's opening price ({symbol}{buyClosePrice:.2f}). Unable to buy any shares."
            else:
                return f"Error: Starting date ({starting}) is greater than ending date ({ending})."
        else:
            return f"Error: File for '{name}' does not exist at the path {path}."


    min_date = datetime.date(2010, 1, 1)
    max_date = datetime.date(2024,11,11)
    st.title('Stock Analysis without Technical Indicators')

    country = st.sidebar.selectbox("Select the country",["India","USA","Japan"])
    if country == "India":
        
        exchange = st.sidebar.selectbox ("Select an exchange",["NSE","BSE"])
        if exchange == "NSE":
            stock_name = st.sidebar.selectbox("Enter stock name",['APOLLO TYRE', 'ASHOK LEYLAND', 'ATUL AUTO', 'BAJAJ AUTO', 'BOSCH', 'CEAT TYRES', 'EICHER MOTORS', 'ESCORTS MOTORS', 'EXIDE IND', 'FORCE MOTORS', 'HERO MOTO CORP', 'JK TYRE', 'Mahindra & Mahindra', 'MARUTI', 'MRF TYRES', 'SML ISUZU', 'SONA COMSTAR', 'TATA MOTORS', 'TATA POWER', 'TVS MOTORS'] )
        elif exchange == "BSE":
            stock_name = st.sidebar.selectbox("Enter stock name",['APOLLO TYRE', 'ASHOK LEYLAND', 'ATUL AUTO', 'BAJAJ AUTO', 'BOSCH', 'CEAT TYRES', 'EICHER MOTORS', 'ESCORTS MOTORS', 'EXIDE IND', 'FORCE MOTORS', 'HERO MOTO CORP', 'JK TYRE', 'Mahindra & Mahindra', 'MARUTI', 'MRF TYRES', 'SML ISUZU', 'SONA COMSTAR', 'TATA MOTORS', 'TATA POWER', 'TVS MOTORS'] )
    elif country == "USA":
        stock_name = st.sidebar.selectbox("Enter stock name",['BMW', 'Ford', 'General Motors', 'Honda', 'Lucid Motors', 'NIO', 'Rivian', 'Stellantis', 'Tesla', 'Toyota'])
        exchange = None
    
    else:
        stock_name = st.sidebar.selectbox("Enter stock name",['7201.T - Nissan', '7202.T - Isuzu Motors', '7203.T - Toyota', '7205.T - Hino Motors', '7211.T - Mitsubishi Motors', '7261.T - Mazda', '7267.T - Honda', '7269.T - Suzuki', '7270.T - Subaru', '8015.T - Toyota Tsusho'])
        exchange =  None
    
    capital = st.sidebar.number_input("Enter initial capital :", min_value=1, value=1000)
    start_date = st.sidebar.date_input("Select start date",min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("Select end date",min_value=min_date, max_value=max_date)

    # Handle button click to run the analysis
    if st.sidebar.button("Analyze Stock"):
        result = portfolio(country,exchange,stock_name, capital, start_date, end_date)
        if result:
            st.write(result)
