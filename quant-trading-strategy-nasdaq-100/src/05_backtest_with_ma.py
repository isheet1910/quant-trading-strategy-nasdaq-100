import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

fileName = '../excel/nasdaq100_with_indicators.xlsx'

# -----------------------------
# 1. LOAD DATA
# -----------------------------
PriceDF = pd.read_excel(fileName, sheet_name='Price', engine='openpyxl')
RSIDF = pd.read_excel(fileName, sheet_name='RSI', engine='openpyxl')
ROCDF = pd.read_excel(fileName, sheet_name='ROC', engine='openpyxl')
MA9DF = pd.read_excel(fileName, sheet_name='9MA', engine='openpyxl')   # NEW

# -----------------------------
# 2. SET INDEX
# -----------------------------
PriceDF = PriceDF.set_index(PriceDF.columns[0])
RSIDF = RSIDF.set_index(RSIDF.columns[0])
ROCDF = ROCDF.set_index(ROCDF.columns[0])
MA9DF = MA9DF.set_index(MA9DF.columns[0])   # NEW

# -----------------------------
# 3. ALIGN COLUMNS
# -----------------------------
common_days = RSIDF.columns.intersection(ROCDF.columns)\
                             .intersection(PriceDF.columns)\
                             .intersection(MA9DF.columns)   # NEW

RSIDF = RSIDF[common_days]
ROCDF = ROCDF[common_days]
PriceDF = PriceDF[common_days]
MA9DF = MA9DF[common_days]   # NEW

# -----------------------------
# 4. NUMERIC CLEANING
# -----------------------------
RSIDF = RSIDF.apply(pd.to_numeric, errors='coerce')
ROCDF = ROCDF.apply(pd.to_numeric, errors='coerce')
PriceDF = PriceDF.apply(pd.to_numeric, errors='coerce')
MA9DF = MA9DF.apply(pd.to_numeric, errors='coerce')   # NEW

results = []

# -----------------------------
# CORE LOGIC
# -----------------------------
for company in RSIDF.index:
    
    rsi_row = RSIDF.loc[company]
    price_row = PriceDF.loc[company]
    roc_row = ROCDF.loc[company]
    ma9_row = MA9DF.loc[company]   # NEW
    
    i = 3
    
    while i < len(common_days):
        
        day = common_days[i]
        
        rsi_value = rsi_row[day]
        price_today = price_row[day]
        price_3_days_ago = price_row[common_days[i-3]]
        roc_entry_value = roc_row[day]
        ma9_value = ma9_row[day]   # NEW

        # -----------------------------
        # DATA VALIDATION
        # -----------------------------
        if (
            pd.isna(rsi_value) or
            pd.isna(price_today) or
            pd.isna(price_3_days_ago) or
            pd.isna(roc_entry_value) or
            pd.isna(ma9_value)   # NEW
        ):
            i += 1
            continue
        
        delta_3 = price_today - price_3_days_ago
        
        # -----------------------------
        # ENTRY CONDITION (UPDATED)
        # -----------------------------
        if (
            45 <= rsi_value <= 60 and
            delta_3 > 0 and
            roc_entry_value < -1 and
            price_today > 0.9 *ma9_value    
        ):
            
            entry_day = day
            initial_price = price_today
            initial_roc = roc_entry_value
            
            trigger_day = None
            trigger_type = None
            RSI_Sell_Value = None
            
            j = i + 1
            
            # -----------------------------
            # EXIT CONDITION
            # -----------------------------
            while j < len(common_days):
                
                next_day = common_days[j]
                next_rsi = RSIDF.loc[company, next_day]
                
                if pd.isna(next_rsi):
                    j += 1
                    continue
                
                if next_rsi >= 60:
                    trigger_day = next_day
                    trigger_type = "HIGH >= 60"
                    RSI_Sell_Value = next_rsi
                    break
                
                elif next_rsi <= 35:
                    trigger_day = next_day
                    trigger_type = "LOW <= 35"
                    RSI_Sell_Value = next_rsi
                    break
                
                j += 1
            
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
                
                i = j + 1
            
            else:
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
# FINAL OUTPUT
# -----------------------------
FinalResultDF = pd.DataFrame(results, columns=[
    "Company",
    "Entry Day",
    "Initial Price",
    "Initial ROC",
    "Exit Day",
    "Exit Type",
    "RSI Sell Value",
    "Final Price",
    "Profit",
    "ROC Value",
    "3-Day Delta"
])

# -----------------------------
# WIN RATE + SUMMARY METRICS
# -----------------------------
valid_profits = FinalResultDF["Profit"].dropna()

total_trades = len(valid_profits)
winning_trades = (valid_profits > 0).sum()
total_profit = valid_profits.sum()

win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0

# -----------------------------
# EXTRACT PARAMETERS FROM LOGIC
# -----------------------------
ROC_param = -1           # from: roc_entry_value < -3
MA_param = 0.9           # from: price_today > 1.1 * ma9_value
RSI_LOW = 35            # from exit condition
RSI_HIGH = 60            # from exit condition

# -----------------------------
# EMPTY ROW FOR SPACING
# -----------------------------
empty_row = pd.DataFrame([{}])

# -----------------------------
# SUMMARY ROW
# -----------------------------
summary_row = pd.DataFrame([{
    "Company": "SUMMARY",
    "ROC": ROC_param,
    "9MA": MA_param,
    "RSI LOW": RSI_LOW,
    "RSI HIGH": RSI_HIGH,
    "Profit": total_profit,
    "Number of Trades": total_trades,
    "Win Rate (%)": win_rate
}])

# -----------------------------
# APPEND TO FINAL DF
# -----------------------------
FinalResultDF = pd.concat([FinalResultDF, empty_row, summary_row], ignore_index=True)

# -----------------------------
# SAVE FILE
# -----------------------------
FinalResultDF.to_excel("../excel/trades_with_ma.xlsx", index=False)

print("Done —  added successfully.")

# Remove trades without profit
equity_df = FinalResultDF.dropna(subset=["Profit"]).copy()

# Create cumulative profit
equity_df["Cumulative Profit"] = equity_df["Profit"].cumsum()

# Running maximum of equity curve
equity_df["Running Peak"] = equity_df["Cumulative Profit"].cummax()

# Drawdown = current equity - peak equity
equity_df["Drawdown"] = equity_df["Cumulative Profit"] - equity_df["Running Peak"]

max_drawdown = equity_df["Drawdown"].min()

print("Maximum Drawdown:", max_drawdown)


plt.figure()
plt.plot(equity_df["Cumulative Profit"])
plt.title("Equity Curve")
plt.xlabel("Trades")
plt.ylabel("Cumulative Profit")
plt.show()

# Remove trades without return
returns_df = FinalResultDF.dropna(subset=["Profit"]).copy()

# Convert to percentage return
returns_df["Return"] = (returns_df["Final Price"] - returns_df["Initial Price"]) / returns_df[
    "Initial Price"]

mean_return = returns_df["Return"].mean()
std_return = returns_df["Return"].std()

sharpe_ratio = mean_return / std_return

print("\n Mean Trade Return:", mean_return)
print("\n Std Dev of Returns:", std_return)
print("\n Sharpe Ratio (per trade):", sharpe_ratio)

trades_per_year = 2515
annualized_sharpe = sharpe_ratio * np.sqrt(trades_per_year)

print("\n Annualized Sharpe:", annualized_sharpe)
skewness = returns_df["Return"].skew()
kurtosis = returns_df["Return"].kurt()

print("\n Skewness:", skewness)
print("\n Kurtosis:", kurtosis)
print("\n Process Completed Successfully ✅")