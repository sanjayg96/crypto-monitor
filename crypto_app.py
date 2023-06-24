import json

import pandas as pd
import streamlit as st

from utils.custom_functions import (
    file_download,
    get_data,
    get_insights,
    percentage_change_plot,
    price_plot,
)

with open("utils/config_constants.json", "r") as file_handle:
    config_dict = json.load(file_handle)

# Set wide page layout
st.set_page_config(layout="wide")

# Title
st.title("Crypto Price Monitor and Analysis")
st.markdown(
    """
    The crypto-currency data is retrieved in **real-time** from [CoinMarketCap](http://coinmarketcap.com) for the analysis.

"""
)

# Web scrape crypto data
df = get_data()
df = df[config_dict["select_columns"]]
df.columns = config_dict["new_col_names"]
df = df.sort_values(by="Price", ascending=False, ignore_index=True)

##################################################
# Sidebar
##################################################
side_bar = st.sidebar
side_bar.header("Data Controls")

## Sidebar - Number of coins to display
num_coin = side_bar.slider("Display Top N Coins", 1, 100, 20)
df_coins = df[:num_coin]
download_data = file_download(df_coins)

## Sidebar - Percent change timeframe
percent_timeframe = side_bar.selectbox(
    "Percent change time frame", ["1h", "24h", "7d", "30d", "60d", "90d"]
)
##################################################

most_traded, highest_ytd, steady_growth = get_insights(df)

##################################################
# Insights section
##################################################
st.markdown("### Quick insights")
expander = st.expander("View")
expander.write("##### **Five most traded by volume in the past 24 hours**")
expander.write(most_traded)
expander.write("##### **Five highest Year-to-Date (YTD) growth**")
expander.write(highest_ytd)
expander.write("##### **Steady positive growth over the past week**")
expander.write(steady_growth)
##################################################

df_change = df_coins[
    [
        "Cryptocurrency",
        "PercentChange1h",
        "PercentChange24h",
        "PercentChange7d",
        "PercentChange30d",
        "PercentChange60d",
        "PercentChange90d",
    ]
]


df_change = df_change.set_index("Cryptocurrency")
df_change["positive_PercentChange1h"] = df_change["PercentChange1h"] > 0
df_change["positive_PercentChange24h"] = df_change["PercentChange24h"] > 0
df_change["positive_PercentChange7d"] = df_change["PercentChange7d"] > 0
df_change["positive_PercentChange30d"] = df_change["PercentChange30d"] > 0
df_change["positive_PercentChange60d"] = df_change["PercentChange60d"] > 0
df_change["positive_PercentChange90d"] = df_change["PercentChange90d"] > 0


##################################################
# Percent price change plot
##################################################
st.subheader("Percentage Price Change of Cryptocurrencies")
percentage_change_plot(df_change, percent_timeframe, st)
##################################################

##################################################
# Percent price change plot
##################################################
st.subheader("Current Price of Cryptocurrencies - Top " + str(num_coin))
price_plot(df_coins, st)
##################################################


##################################################
# Crypto data
##################################################
st.subheader("Price Data of Cryptocurrencies")
st.download_button(
    label="Download data as CSV",
    data=download_data,
    file_name="crypto_price.csv",
    mime="text/csv",
)
st.write(
    "Data Dimension: "
    + str(df_coins.shape[0])
    + " rows and "
    + str(df_coins.shape[1])
    + " columns."
)
st.write("(Click on the column names to sort data)")
st.dataframe(df_coins)
##################################################
