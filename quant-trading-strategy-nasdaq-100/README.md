# Nasdaq-100 Trading Strategy

This project builds and backtests a systematic trading strategy using:
- RSI (14)
- ROC (9)
- 9-day Moving Average


## Project Structure

- python/ → All Python scripts  
- excel/ → Input data + outputs  
- reports/ → Strategy reports and visuals  

## Workflow

1. Download data → 01_download_data.py  
2. Add indicators in Excel  
3. Compute RSI → 03_compute_rsi.py  
4. Run strategy:
   - Basic → 04_backtest_basic.py  
   - With MA → 05_backtest_with_ma.py  
   - Parameter sweep → 06_parameter_sweep.py  

## Outputs

- trades_basic.xlsx  
- trades_with_ma.xlsx  
- parameter_sweep_results.xlsx  



Workflow
Step 1: Download Data

Run:

01_download_data.py

Output:

nasdaq100_prices_raw.xlsx


Step 2: Compute Indicators (Excel)
Open raw file
Add:
ROC (9)
9MA
Save as:
nasdaq100_with_indicators.xlsx


Step 3: Compute RSI

Run:

03_compute_rsi.py

Adds:

RSI sheet

Step 4: Run Strategies


Option A — Basic Strategy
04_backtest_basic.py

Output:

trades_basic.xlsx


Option B — With 9MA
05_backtest_with_ma.py

Output:

trades_with_ma.xlsx


Option C — Parameter Optimization
06_parameter_sweep.py

Output:

parameter_sweep_results.xlsx


