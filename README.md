#   🚀 Binance Futures Order Bot

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Binance API](https://img.shields.io/badge/API-Binance%20Futures-yellow)
![Status](https://img.shields.io/badge/Mode-Dry%20Run%20%7C%20Live-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

### 🧠 A CLI-based trading bot for Binance USDT-M Futures  

Supports Market, Limit, and Advanced Order Types like Stop-Limit, OCO, TWAP, and Grid strategies.
Built with Python, Binance Futures API, and structured logging for transparency and debugging.


## 📂 Project Structure

[your_name]_binance_bot/
│
├── src/
│   ├── market_orders.py         # Market order logic
│   ├── limit_orders.py          # Limit order logic
│   ├── advanced/
│   │   ├── stop_limit.py        # Stop-Limit order logic
│   │   ├── oco.py               # One-Cancels-the-Other logic
│   │   ├── twap.py              # TWAP (Time-Weighted Average Price) strategy
│   │   └── grid_strategy.py     # Grid trading strategy
│
├── bot.log                      # Centralized structured log file
├── report.pdf                   # Screenshots, explanations, and analysis
└── README.md                    # Setup instructions, usage guide

⚙️ Features

Core Orders

Market Orders – Instant execution at the best available price
Limit Orders – Execute only when the target price is reached

Advanced Orders (Bonus Features)

Stop-Limit Orders – Trigger a limit order once a stop price is hit
OCO (One-Cancels-the-Other) – Place take-profit and stop-loss orders simultaneously
TWAP Strategy – Split large orders into smaller chunks over time
Grid Strategy – Automate buy-low/sell-high orders within a price range

🧠 Validation & Logging

Input validation for symbols, quantities, and price thresholds
Detailed logs for all actions (executions, errors, and dry-run events)
Example log entry:

2025-10-05 12:35:09,995 | WARNING | __main__ | API key/secret not found in environment; running dry-run only
2025-10-05 12:35:09,996 | INFO | __main__ | Placing market order: BTCUSDT BUY 0.001
2025-10-05 12:35:09,997 | INFO | __main__ | Dry-run mode: not sending order to Binance

🧰 Setup Instructions
1️⃣ Prerequisites

Python 3.8 or higher
Binance account (optional if running in dry-run mode)
Install required libraries:
pip install python-binance pandas python-dotenv

2️⃣ Environment Variables (Optional for Live Mode)

Create a .env file in the project root:

BINANCE_API_KEY=your_binance_api_key_here
BINANCE_API_SECRET=your_binance_api_secret_here

If not provided, the bot automatically runs in Dry-Run Mode.

3️⃣ Add Python Path

Before running, set the PYTHONPATH (needed if not using Git):

Windows PowerShell
$env:PYTHONPATH = (Get-Item -Path ".\src").FullName

Linux/macOS
export PYTHONPATH=$(pwd)/src

🏃 Usage

All scripts can be executed directly from the CLI.

📈 Market Order
python src/market_orders.py BTCUSDT BUY 0.001

💰 Limit Order
python src/limit_orders.py BTCUSDT SELL 0.001 71000

🛑 Stop-Limit Order
python src/advanced/stop_limit.py --symbol BTCUSDT --side SELL --qty 0.001 --stop 62000 --limit 61900 --dry-run

⚖️ OCO Order
python src/advanced/oco.py --symbol BTCUSDT --side BUY --qty 0.001 --tp 70000 --sl 60000 --dry-run

🕒 TWAP Strategy
python src/advanced/twap.py --symbol BTCUSDT --side BUY --total 0.01 --chunks 5 --duration 60 --dry-run

🧱 Grid Strategy
python src/advanced/grid_strategy.py --symbol BTCUSDT --side BUY --lower 60000 --upper 70000 --grids 4 --qty 0.001 --dry-run

Add --dry-run to simulate orders without connecting to Binance.

🧾 Logging

All actions are logged to bot.log and console output.
You can view details about each simulated or live order there.
Example:

2025-10-05 12:35:09,997 | INFO | __main__ | Result: {'status': 'DRY_RUN', 'symbol': 'BTCUSDT', 'side': 'BUY', 'qty': '0.001'}

🏁 Notes

No real orders are placed without valid API keys.
Always use Dry-Run Mode first to test safely.
Code is modular — easily extendable with new strategies or indicators.