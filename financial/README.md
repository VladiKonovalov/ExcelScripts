# 🚀 Stock Competitor Analyzer Pro

A modern, AI-powered stock analysis tool that compares any stock with its competitors using real-time financial data and advanced algorithms.

![Stock Analyzer](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

## ✨ Features

### 🎯 **Intelligent Stock Analysis**
- **Real-time data** from Yahoo Finance API
- **Smart competitor detection** based on industry and sector
- **AI-powered scoring** algorithm (0-100 scale)
- **Automatic ranking** from best to worst investment opportunities

### 🎨 **Modern Dark Theme UI**
- **Professional interface** inspired by Bloomberg terminals
- **Interactive charts** and visualizations
- **Color-coded recommendations** (Buy/Hold/Sell)
- **Real-time status** updates with progress tracking

### 📊 **Comprehensive Analysis**
- **4 Analysis Tabs**: Overview, Detailed Metrics, Visual Charts, AI Analysis
- **15+ Financial Metrics**: P/E ratio, ROE, debt levels, profit margins
- **Investment Rankings** with medal system (🥇🥈🥉)
- **Risk assessment** and investment thesis generation

## 🛠️ Installation

### Prerequisites
```bash
pip install yfinance pandas numpy matplotlib seaborn tkinter
```

### Quick Start
```bash
# Clone or download the script
python stock_analyzer.py
```

## 🚀 Usage

### GUI Version (Recommended)
1. **Launch the application**
2. **Enter a stock symbol** (e.g., AAPL, TSLA, CRM, NVDA)
3. **Click "🚀 Analyze Stock"**
4. **Explore the 4 analysis tabs**:
   - 📊 **Overview & Rankings** - See how your stock ranks
   - 📈 **Detailed Metrics** - Comprehensive financial data
   - 📉 **Visual Analysis** - Professional charts
   - 🎯 **AI Investment Analysis** - Smart recommendations

### Console Version (Fallback)
If GUI fails, the app automatically switches to console mode with full functionality.

## 📈 Example Analysis

### Input: `CRM` (Salesforce)
**Competitors Found**: MSFT, ORCL, ADBE, NOW, INTU

**Sample Output**:
```
🏆 COMPLETE RANKINGS (Best to Worst):
Rank   Symbol   Company              Score    Recommendation
🥇 1   NOW      ServiceNow           76.3     STRONG BUY
🥈 2   ⭐CRM    Salesforce          71.8     BUY
🥉 3   MSFT     Microsoft           69.2     BUY
#4     ADBE     Adobe               58.4     HOLD
#5     ORCL     Oracle              52.1     HOLD
```

## 🎨 Screenshots

### Modern Dark Theme Interface
- **Hero cards** with gradient effects
- **Ranking medals** for top performers  
- **Progress bars** for investment scores
- **Interactive elements** with hover effects

### Professional Charts
- **Investment score rankings**
- **P/E ratio comparisons**
- **ROE vs Debt/Equity scatter plots**
- **Recommendation distribution**

## 🔧 Technical Details

### Data Sources
- **Yahoo Finance API** via `yfinance` library
- **Real-time stock prices** and financial metrics
- **Comprehensive industry mappings** for competitor detection

### Scoring Algorithm
- **Multi-factor analysis**: Valuation, profitability, growth, financial health
- **Peer comparison**: Relative performance vs industry averages
- **Risk adjustment**: Beta, volatility, and sector-specific factors

### Architecture
- **Modern GUI**: Tkinter with custom dark theme styling
- **Threading**: Non-blocking analysis with real-time updates  
- **Caching**: Optimized API calls and data storage
- **Error handling**: Graceful fallbacks and user feedback

## 📋 Supported Stocks

### Popular Examples
- **Tech**: AAPL, MSFT, GOOGL, NVDA, CRM, ORCL
- **Finance**: JPM, BAC, V, MA, GS
- **Healthcare**: JNJ, PFE, UNH, MRK
- **Energy**: XOM, CVX, COP
- **Consumer**: WMT, TGT, HD, MCD

**Note**: Works with any valid stock ticker symbol on major exchanges.

## ⚠️ Disclaimer

This tool is for **educational purposes only** and should not be considered professional financial advice. Always consult with qualified financial advisors and conduct your own research before making investment decisions.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your improvements
4. Submit a pull request

## 📄 License

MIT License - feel free to use and modify for personal or commercial projects.

## 🆘 Troubleshooting

### Common Issues
- **"Invalid symbol"**: Ensure ticker symbol is correct and publicly traded
- **"No competitors found"**: Tool will use sector-based alternatives
- **GUI not loading**: Automatic fallback to console mode
- **API errors**: Check internet connection and try again

### Requirements
- **Python 3.7+**
- **Internet connection** for real-time data
- **Modern display** for optimal GUI experience

---

**Happy Investing! 📈**