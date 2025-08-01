# bitcoin-income-suite-v2

## Project Overview
Bitcoin Income Suite V2 is a suite of tools to help people produce income from investments (ETFs, dividends, intelligent leverage) that sweep into Bitcoin over time. This strategy highlights Bitcoin's power as an income generator, focusing on Bitcoin, ETFs, Dividends, allocations, and discipline to efficiently create wealth through time. The suite educates on Bitcoin's outperformance (>50% historical CAGR, fixed 21M supply) against fiat debasement (2.7% CPI + ~6.5% M2 growth), driving time reclamation and delayed gratification via DGI (70% increase target).

## Dependency Map
| Tool | Dependencies (Imports From) | Provides To (Exports) |
|------|-----------------------------|------------------------|
| Income Sweep Simulator | Common (sweep logic, Bitcoin projection, inflation rate); Options Recommender (real-time premiums) | TRE (sim results for time projections); DCA (sweep forecasts) |
| Options Premium Recommender | Common (leverage calcs, real-time stock/Bitcoin APIs, asset comparisons) | Income Sweep Simulator (premiums); TRE (amplified time reclamation) |
| BTC Flywheel for Beginners | Common (basics, Bitcoin metrics); DCA Tracker | TRE (intro time concepts) |
| DCA Tracker | Common (DGI, sats conversion, Bitcoin growth); Optional real-time Bitcoin price | TRE (consistency data); Income Sweep Simulator (funded sweeps) |
| Opportunity Cost Calculator | Common (hours calcs, inflation, comparisons); DCA | TRE ("stolen hours" for erosion sims) |
| Time Reclamation Engine (Hub) | All tools (imports sims/premiums/forecasts, Bitcoin/inflation funcs) | Suite-wide (DGI scores, time metrics, societal aggregates) |

## Setup Instructions
1. Clone the repo: `git clone https://github.com/johnquinby79/bitcoin-income-suite-v2.git`  
2. Install dependencies: `pip install -r requirements.txt`  
3. Run a tool: `streamlit run hub/tre.py` (for TRE)  
4. For APIs: Add keys to .env (e.g., ALPHA_VANTAGE_API_KEY=yourkey) and load with os.environ.  
5. Test: Run backtesting or AI nudges from `common.py` in a REPL.  

## Bitcoin Mission  
Empower users to reclaim time from debasement by sweeping income to Bitcoin, with TRE visualizing "hours saved" and DGI tracking shifts for financial freedom.
