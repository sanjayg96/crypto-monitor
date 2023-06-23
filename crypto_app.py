import json

import pandas as pd
import streamlit as st

from utils.custom_functions import (
    file_download,
    get_data,
    percentage_change_plot,
    price_plot,
)

with open("utils/config_constants.json", "r") as file_handle:
    config_dict = json.load(file_handle)

st.set_page_config(layout="wide")

# Title
st.title("Crypto Price Monitor and Analysis")
st.markdown(
    """
    The crypto-currency data is retrieved in **real-time** from [CoinMarketCap](http://coinmarketcap.com) for the analysis.

"""
)

st.markdown("### Quick insights")
expander = st.expander("View")
expander.markdown(
    """
WIP

"""
)


# Divide the page into 3 columns
# col1 would be the sidebar for data controls accepting user inputs
# col2 and col3 would contain the main contents
col1 = st.sidebar
# col2, col3 = st.columns((2, 1))

df = get_data()
df = df[config_dict["select_columns"]]
df.columns = config_dict["new_col_names"]
df = df.sort_values(by="Price", ascending=False, ignore_index=True)

col1.header("Data Controls")

## Sidebar - Cryptocurrency selections
# sorted_coin = sorted(df["Symbol"])
# selected_coin = col1.multiselect("Cryptocurrency", sorted_coin, sorted_coin)

# df_selected_coin = df[(df["Symbol"].isin(selected_coin))]  # Filtering data

## Sidebar - Number of coins to display
num_coin = col1.slider("Display Top N Coins", 1, 100, 20)
df_coins = df[:num_coin]
download_data = file_download(df_coins)

## Sidebar - Percent change timeframe
percent_timeframe = col1.selectbox(
    "Percent change time frame", ["1h", "24h", "7d", "30d", "60d", "90d"]
)

## Sidebar - Sorting values
# sort_values = col1.selectbox("Sort values?", ["Yes", "No"])

# ---------------------------------#
# Preparing data for Bar plot of % Price change
df_change = pd.concat(
    [
        df_coins.Cryptocurrency,
        df_coins.PercentChange1h,
        df_coins.PercentChange24h,
        df_coins.PercentChange7d,
        df_coins.PercentChange30d,
        df_coins.PercentChange60d,
        df_coins.PercentChange90d,
    ],
    axis=1,
)
df_change = df_change.set_index("Cryptocurrency")
df_change["positive_PercentChange1h"] = df_change["PercentChange1h"] > 0
df_change["positive_PercentChange24h"] = df_change["PercentChange24h"] > 0
df_change["positive_PercentChange7d"] = df_change["PercentChange7d"] > 0
df_change["positive_PercentChange30d"] = df_change["PercentChange30d"] > 0
df_change["positive_PercentChange60d"] = df_change["PercentChange60d"] > 0
df_change["positive_PercentChange90d"] = df_change["PercentChange90d"] > 0

st.subheader("Percentage Price Change of Cryptocurrencies")
percentage_change_plot(df_change, percent_timeframe, st)

st.subheader("Current Price of Cryptocurrencies - Top " + str(num_coin))
price_plot(df_coins, st)


# Display the dataframe
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
