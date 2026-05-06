import pandas as pd
# import matplotlib.pyplot as plt
import numpy as np

fileName = '../excel/nasdaq100_with_indicators.xlsx'

# Read Excel file
PriceDF = pd.read_excel(fileName, sheet_name='Price', engine='openpyxl')
RSIDF = pd.read_excel(fileName, sheet_name='RSI', engine='openpyxl')
ROCDF = pd.read_excel(fileName, sheet_name='ROC', engine='openpyxl')

# Ensure first column is Company
PriceDF = PriceDF.set_index(PriceDF.columns[0])
RSIDF = RSIDF.set_index(RSIDF.columns[0])
ROCDF = ROCDF.set_index(ROCDF.columns[0])

# Make sure all three have same columns
common_days = RSIDF.columns.intersection(ROCDF.columns).intersection(PriceDF.columns)

RSIDF = RSIDF[common_days]
ROCDF = ROCDF[common_days]
PriceDF = PriceDF[common_days]

# Convert everything to numeric safely
RSIDF = RSIDF.apply(pd.to_numeric, errors='coerce')
ROCDF = ROCDF.apply(pd.to_numeric, errors='coerce')
PriceDF = PriceDF.apply(pd.to_numeric, errors='coerce')

results = []

# -----------------------------
# Core Logic with 3-Day Delta
# -----------------------------

for company in RSIDF.index:
    
    rsi_row = RSIDF.loc[company]
    price_row = PriceDF.loc[company]
    roc_row = ROCDF.loc[company]
    
    i = 3  # start from 3 because we need 3 previous days
    
    while i < len(common_days):
        
        day = common_days[i]
        
        rsi_value = rsi_row[day]
        price_today = price_row[day]
        price_3_days_ago = price_row[common_days[i-3]]
        roc_entry_value = roc_row[day]

        
        # Skip invalid data
        if (
            pd.isna(rsi_value) or
            pd.isna(price_today) or
            pd.isna(price_3_days_ago) or
            pd.isna(roc_entry_value)
        ):
            i += 1
            continue
        
        # Calculate 3-day delta
        delta_3 = price_today - price_3_days_ago
        
        # ---------------------------
        # ENTRY CONDITION
        # ---------------------------
        # if (
        #         45 <= rsi_value <= 60 and
        #         delta_3 > 0 
        #         and roc_entry_value < -2


        # ):

        if (
                45 <= rsi_value <= 60 and
                delta_3 > 0 
                and roc_entry_value < -2


        ):
            

            entry_day = day
            initial_price = price_today
            initial_roc = roc_entry_value
            
            trigger_day = None
            trigger_type = None
            RSI_Sell_Value = None
            
            j = i + 1
            
            # ---------------------------
            # EXIT CONDITION
            # ---------------------------
            while j < len(common_days):
                
                next_day = common_days[j]
                next_rsi = RSIDF.loc[company, next_day]
                
                if pd.isna(next_rsi):
                    j += 1
                    continue
                
                if next_rsi >= 75:
                    trigger_day = next_day
                    trigger_type = "HIGH >= 75"
                    RSI_Sell_Value = next_rsi
                    break
                
                elif next_rsi <= 35:
                    trigger_day = next_day
                    trigger_type = "LOW <= 35"
                    RSI_Sell_Value = next_rsi
                    break
                
                j += 1
            
            # If exit found
            if trigger_day:
                
                final_price = PriceDF.loc[company, trigger_day]
                roc_value = ROCDF.loc[company, trigger_day]
                profit = final_price - initial_price
                trade_return = (final_price - initial_price) / initial_price

                
                results.append([
                    company,
                    entry_day,
                    initial_price,
                    initial_roc,
                    trigger_day,
                    trigger_type,
                    RSI_Sell_Value,
                    final_price,
                    profit,
                    roc_value,
                    delta_3

                ])
                
                i = j + 1  # continue AFTER exit
            
            else:
                # Row ended without exit
                results.append([
                    company,
                    entry_day,
                    initial_price,
                    initial_roc,
                    "Row Ended",
                    "No Exit",
                    None,
                    None,
                    None,
                    None,
                    delta_3
                ])
                break
        
        else:
            i += 1

# -----------------------------
# Final Output
# -----------------------------

FinalResultDF = pd.DataFrame(results, columns=[
    "Company",
    "Entry Day",
    "Initial Price",
    "Initial ROC (<1 Filtered)",
    "Exit Day",
    "Exit Type",
    "RSI Sell Value",
    "Final Price",
    "Profit",
    "ROC Value",
    "3-Day Delta"
])

# Export to Excel
FinalResultDF.to_excel("../excel/trades_basic.xlsx", index=False)

# # Remove trades without profit
# equity_df = FinalResultDF.dropna(subset=["Profit"]).copy()

# # Create cumulative profit
# equity_df["Cumulative Profit"] = equity_df["Profit"].cumsum()

# # Running maximum of equity curve
# equity_df["Running Peak"] = equity_df["Cumulative Profit"].cummax()

# # Drawdown = current equity - peak equity
# equity_df["Drawdown"] = equity_df["Cumulative Profit"] - equity_df["Running Peak"]

# max_drawdown = equity_df["Drawdown"].min()

# print("Maximum Drawdown:", max_drawdown)


# plt.figure()
# plt.plot(equity_df["Cumulative Profit"])
# plt.title("Equity Curve")
# plt.xlabel("Trades")
# plt.ylabel("Cumulative Profit")
# plt.show()

# # Remove trades without return
# returns_df = FinalResultDF.dropna(subset=["Profit"]).copy()

# # Convert to percentage return
# returns_df["Return"] = (returns_df["Final Price"] - returns_df["Initial Price"]) / returns_df[
#     "Initial Price"]

# mean_return = returns_df["Return"].mean()
# std_return = returns_df["Return"].std()

# sharpe_ratio = mean_return / std_return

# print("\n Mean Trade Return:", mean_return)
# print("\n Std Dev of Returns:", std_return)
# print("\n Sharpe Ratio (per trade):", sharpe_ratio)

# trades_per_year = 2515
# annualized_sharpe = sharpe_ratio * np.sqrt(trades_per_year)

# print("\n Annualized Sharpe:", annualized_sharpe)
# skewness = returns_df["Return"].skew()
# kurtosis = returns_df["Return"].kurt()

# print("\n Skewness:", skewness)
# print("\n Kurtosis:", kurtosis)
# print("\n Process Completed Successfully ✅")