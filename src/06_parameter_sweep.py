import pandas as pd
import numpy as np
import itertools
import matplotlib.pyplot as plt

fileName = '../excel/nasdaq100_with_indicators.xlsx'

# -----------------------------
# CORE BACKTEST FUNCTION
# -----------------------------
def run_strategy(ROC_param, MA_param, RSI_LOW, RSI_HIGH):

    # LOAD DATA
    PriceDF = pd.read_excel(fileName, sheet_name='Price', engine='openpyxl')
    RSIDF = pd.read_excel(fileName, sheet_name='RSI', engine='openpyxl')
    ROCDF = pd.read_excel(fileName, sheet_name='ROC', engine='openpyxl')
    MA9DF = pd.read_excel(fileName, sheet_name='9MA', engine='openpyxl')

    # SET INDEX
    PriceDF = PriceDF.set_index(PriceDF.columns[0])
    RSIDF = RSIDF.set_index(RSIDF.columns[0])
    ROCDF = ROCDF.set_index(ROCDF.columns[0])
    MA9DF = MA9DF.set_index(MA9DF.columns[0])

    # ALIGN
    common_days = RSIDF.columns.intersection(ROCDF.columns)\
                                 .intersection(PriceDF.columns)\
                                 .intersection(MA9DF.columns)

    RSIDF = RSIDF[common_days].apply(pd.to_numeric, errors='coerce')
    ROCDF = ROCDF[common_days].apply(pd.to_numeric, errors='coerce')
    PriceDF = PriceDF[common_days].apply(pd.to_numeric, errors='coerce')
    MA9DF = MA9DF[common_days].apply(pd.to_numeric, errors='coerce')

    results = []

    # -----------------------------
    # CORE LOGIC (UNCHANGED)
    # -----------------------------
    for company in RSIDF.index:

        rsi_row = RSIDF.loc[company]
        price_row = PriceDF.loc[company]
        roc_row = ROCDF.loc[company]
        ma9_row = MA9DF.loc[company]

        i = 3

        while i < len(common_days):

            day = common_days[i]

            rsi_value = rsi_row[day]
            price_today = price_row[day]
            price_3_days_ago = price_row[common_days[i-3]]
            roc_entry_value = roc_row[day]
            ma9_value = ma9_row[day]

            if (
                pd.isna(rsi_value) or
                pd.isna(price_today) or
                pd.isna(price_3_days_ago) or
                pd.isna(roc_entry_value) or
                pd.isna(ma9_value)
            ):
                i += 1
                continue

            delta_3 = price_today - price_3_days_ago

            # ENTRY CONDITION (PARAMETERIZED)
            if (
                45 <= rsi_value <= 60 and
                delta_3 > 0 and
                roc_entry_value < ROC_param and
                price_today > MA_param * ma9_value
            ):

                initial_price = price_today
                j = i + 1

                while j < len(common_days):

                    next_day = common_days[j]
                    next_rsi = RSIDF.loc[company, next_day]

                    if pd.isna(next_rsi):
                        j += 1
                        continue

                    if next_rsi >= RSI_HIGH or next_rsi <= RSI_LOW:
                        final_price = PriceDF.loc[company, next_day]
                        profit = final_price - initial_price

                        results.append(profit)
                        break

                    j += 1

                i = j + 1
            else:
                i += 1

    # -----------------------------
    # SUMMARY METRICS
    # -----------------------------
    profits = pd.Series(results).dropna()

    total_trades = len(profits)
    winning_trades = (profits > 0).sum()
    total_profit = profits.sum()
    win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0

    return {
        "ROC": ROC_param,
        "9MA": MA_param,
        "RSI LOW": RSI_LOW,
        "RSI HIGH": RSI_HIGH,
        "Total Profit": total_profit,
        "Number of Trades": total_trades,
        "Win Rate (%)": win_rate
    }


# -----------------------------
# PARAMETER SWEEP FUNCTION
# -----------------------------
def run_parameter_sweep():

    ROC_values = [0, -1, -2, -3, -4]
    MA_values = [0.9, 1.05, 1.1, 1.2, 1.25]
    RSI_LOW_values = [30, 35, 40, 45]
    RSI_HIGH_values = [55, 60 , 65, 70, 75]

    all_results = []

    # Generate all combinations
    for ROC_param, MA_param, RSI_LOW, RSI_HIGH in itertools.product(
        ROC_values, MA_values, RSI_LOW_values, RSI_HIGH_values
    ):
        print(f"Running: ROC={ROC_param}, MA={MA_param}, RSI_LOW={RSI_LOW}, RSI_HIGH={RSI_HIGH}")

        result = run_strategy(ROC_param, MA_param, RSI_LOW, RSI_HIGH)
        all_results.append(result)

    # Convert to DataFrame
    final_df = pd.DataFrame(all_results)

    # Save output
    final_df.to_excel("../excel/parameter_sweep_results.xlsx", index=False)

    print("Parameter sweep complete. File saved.")


# -----------------------------
# RUN
# -----------------------------
run_parameter_sweep()

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