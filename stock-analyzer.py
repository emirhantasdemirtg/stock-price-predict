import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.linear_model import LinearRegression
import tkinter as tk

# Define the function to retrieve the stock data and perform analysis
def analyze_stock():
    # Get the ticker symbol from the user input
    tickerSymbol = ticker_entry.get()

    # Get data on this ticker
    tickerData = yf.Ticker(tickerSymbol)

    # Get the historical prices for this ticker
    tickerDf = tickerData.history(period='1d', start='2010-1-1', end='2021-12-31')

    # Perform fundamental analysis
    revenue = tickerDf['Close'].resample('Y').mean().pct_change().dropna()
    earnings = tickerDf['Volume'].resample('Y').mean().pct_change().dropna()
    profit_margin = (tickerDf['Close'] - tickerDf['Open']) / tickerDf['Close']
    debt_ratio = tickerDf['Volume'].rolling(window=30).mean() / tickerDf['Close']

    # Perform technical analysis
    tickerDf['MA50'] = tickerDf['Close'].rolling(window=50).mean()
    tickerDf['MA200'] = tickerDf['Close'].rolling(window=200).mean()
    tickerDf['MA50-200'] = tickerDf['MA50'] - tickerDf['MA200']
    tickerDf['Returns'] = np.log(tickerDf['Close'] / tickerDf['Close'].shift(1))
    tickerDf['Volatility'] = tickerDf['Returns'].rolling(window=252).std() * np.sqrt(252)
    tickerDf['Volume_MA'] = tickerDf['Volume'].rolling(window=30).mean()
    tickerDf['OBV'] = np.where(tickerDf['Close'] > tickerDf['Open'], tickerDf['Volume'], -tickerDf['Volume']).cumsum()

    # Use scikit-learn to perform linear regression on the historical prices
    X = tickerDf.index.values.reshape(-1, 1)
    y = tickerDf['Close'].values.reshape(-1, 1)
    model = LinearRegression()
    model.fit(X, y)

    # Calculate the potential profit or loss based on the user's investment
    investment = float(investment_entry.get())
    shares = investment / tickerDf['Close'].iloc[-1]
    future_price = model.predict([[len(tickerDf) + 1]])[0][0]
    future_value = shares * future_price
    profit_loss = future_value - investment

    # Display a message indicating whether the investment is risky or not
    if profit_loss < 0:
        risk_message = 'This investment is risky.'
    else:
        risk_message = 'This investment is not risky.'

    # Display the potential profit or loss and risk message to the user
    result_label.config(text=f'Potential Profit/Loss: {profit_loss:.2f} USD\n{risk_message}')

    # Display the analysis results to the user
    fundamental_label.config(text=f'Revenue Growth: {revenue.iloc[-1]:.2f}\nEarnings Growth: {earnings.iloc[-1]:.2f}\nProfit Margin: {profit_margin.iloc[-1]:.2f}\nDebt Ratio: {debt_ratio.iloc[-1]:.2f}')
    technical_label.config(text=f'Moving Average 50: {tickerDf["MA50"].iloc[-1]:.2f}\nMoving Average 200: {tickerDf["MA200"].iloc[-1]:.2f}\nMA50-200: {tickerDf["MA50-200"].iloc[-1]:.2f}\nVolatility: {tickerDf["Volatility"].iloc[-1]:.2f}\nVolume MA: {tickerDf["Volume_MA"].iloc[-1]:.2f}\nOn-Balance Volume: {tickerDf["OBV"].iloc[-1]:.2f}')


# Create the window
window = tk.Tk() 
window.title('Stock Analysis')

# Add a label for the ticker symbol entry
ticker_label = tk.Label(window, text='Enter the stock ticker symbol:')
ticker_label.pack()

# Add an entry field for the ticker symbol
ticker_entry = tk.Entry(window)
ticker_entry.pack()

# Add a label for the investment entry
investment_label = tk.Label(window, text='Enter the amount of your investment (in USD):')
investment_label.pack()

# Add an entry field for the investment amount
investment_entry = tk.Entry(window)
investment_entry.pack()

# Add a button to analyze the stock
analyze_button = tk.Button(window, text='Analyze', command=analyze_stock)
analyze_button.pack()

# Add a label to display the potential profit or loss and risk message
result_label = tk.Label(window, text='')
result_label.pack()

# Add a label to display the fundamental analysis results
fundamental_label = tk.Label(window, text='')
fundamental_label.pack()

# Add a label to display the technical analysis results
technical_label = tk.Label(window, text='')
technical_label.pack()

# Start the main event loop for the window
window.mainloop()