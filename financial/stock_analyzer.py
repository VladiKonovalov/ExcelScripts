import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import yfinance as yf
import warnings
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import re

warnings.filterwarnings('ignore')
plt.style.use('default')

class StockCompetitorAnalyzer:
    def __init__(self, alpha_vantage_api_key=None):
        """
        Initialize the Stock Competitor Analyzer
        
        Args:
            alpha_vantage_api_key (str): Alpha Vantage API key for enhanced data
        """
        self.alpha_vantage_api_key = alpha_vantage_api_key
        self.cache = {}
        
    def validate_symbol(self, symbol):
        """Validate if stock symbol exists and is actively traded"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            # Check if it's a real stock (not ETF/Index)
            return ('symbol' in info or 'shortName' in info) and info.get('quoteType', '') == 'EQUITY'
        except:
            return False
    
    def get_stock_info(self, symbol):
        """Get comprehensive stock information"""
        try:
            if symbol in self.cache:
                return self.cache[symbol]
                
            stock = yf.Ticker(symbol)
            info = stock.info
            hist = stock.history(period="1y")
            
            # Skip if not a regular stock
            if info.get('quoteType', '') not in ['EQUITY', 'ETF']:
                return None
            
            # Calculate additional metrics
            current_price = hist['Close'][-1] if len(hist) > 0 else info.get('currentPrice', 0)
            
            stock_data = {
                'symbol': symbol,
                'name': info.get('shortName', symbol),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'current_price': current_price,
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'forward_pe': info.get('forwardPE', 0),
                'price_to_book': info.get('priceToBook', 0),
                'price_to_sales': info.get('priceToSalesTrailing12Months', 0),
                'debt_to_equity': info.get('debtToEquity', 0),
                'current_ratio': info.get('currentRatio', 0),
                'quick_ratio': info.get('quickRatio', 0),
                'roe': info.get('returnOnEquity', 0),
                'roa': info.get('returnOnAssets', 0),
                'gross_margin': info.get('grossMargins', 0),
                'operating_margin': info.get('operatingMargins', 0),
                'profit_margin': info.get('profitMargins', 0),
                'revenue_growth': info.get('revenueGrowth', 0),
                'earnings_growth': info.get('earningsGrowth', 0),
                'beta': info.get('beta', 1.0),
                'dividend_yield': info.get('dividendYield', 0),
                'payout_ratio': info.get('payoutRatio', 0),
                '52_week_high': info.get('fiftyTwoWeekHigh', 0),
                '52_week_low': info.get('fiftyTwoWeekLow', 0),
                'volume': info.get('averageVolume', 0),
                'employees': info.get('fullTimeEmployees', 0)
            }
            
            # Calculate price performance
            if len(hist) > 0:
                stock_data['ytd_return'] = self.calculate_ytd_return(hist)
                stock_data['one_year_return'] = self.calculate_return(hist, 252)
                stock_data['volatility'] = hist['Close'].pct_change().std() * np.sqrt(252)
            
            self.cache[symbol] = stock_data
            return stock_data
            
        except Exception as e:
            print(f"Error getting data for {symbol}: {str(e)}")
            return None
    
    def find_industry_competitors(self, main_stock, max_competitors=5):
        """Find real competitors based on industry and sector"""
        sector = main_stock['sector']
        industry = main_stock['industry']
        market_cap = main_stock['market_cap']
        
        # Industry-based competitor lists (real stocks only)
        industry_competitors = {
            # Technology
            'Software': ['MSFT', 'ORCL', 'CRM', 'ADBE', 'NOW', 'INTU', 'VMW', 'CTXS', 'TEAM', 'ZM', 'DDOG', 'SNOW', 'PLTR', 'WDAY'],
            'Semiconductors': ['NVDA', 'AMD', 'INTC', 'QCOM', 'AVGO', 'TXN', 'ADI', 'MRVL', 'XLNX', 'LRCX', 'KLAC', 'AMAT'],
            'Consumer Electronics': ['AAPL', 'SONY', 'HPQ', 'DELL', 'LOGI', 'GRMN', 'HEAR'],
            'Internet Content': ['GOOGL', 'META', 'AMZN', 'NFLX', 'UBER', 'LYFT', 'SNAP', 'PINS', 'TWTR', 'ROKU'],
            'E-commerce': ['AMZN', 'SHOP', 'EBAY', 'ETSY', 'BABA', 'JD', 'MELI', 'SE'],
            
            # Healthcare & Pharmaceuticals  
            'Biotechnology': ['GILD', 'AMGN', 'BIIB', 'REGN', 'VRTX', 'CELG', 'ILMN', 'MRNA', 'BNTX', 'NVAX'],
            'Drug Manufacturers': ['JNJ', 'PFE', 'MRK', 'ABT', 'BMY', 'LLY', 'AZN', 'NVO', 'RHHBY', 'GSK'],
            'Medical Devices': ['MDT', 'ABT', 'TMO', 'DHR', 'SYK', 'BSX', 'EW', 'ZBH', 'ISRG', 'DXCM'],
            'Healthcare Plans': ['UNH', 'ANTM', 'AET', 'CI', 'HUM', 'CNC', 'MOH'],
            
            # Financial Services
            'Banks': ['JPM', 'BAC', 'WFC', 'C', 'USB', 'PNC', 'TFC', 'COF', 'MS', 'GS'],
            'Insurance': ['BRK-B', 'PG', 'AIG', 'MET', 'PRU', 'ALL', 'TRV', 'CB', 'AXP'],
            'Credit Services': ['V', 'MA', 'AXP', 'COF', 'DFS', 'SYF', 'PYPL', 'SQ'],
            'Investment Banking': ['GS', 'MS', 'JPM', 'BAC', 'C', 'BCS', 'DB', 'CS'],
            
            # Energy & Utilities
            'Oil & Gas': ['XOM', 'CVX', 'COP', 'EOG', 'SLB', 'HAL', 'OXY', 'KMI', 'WMB', 'EPD'],
            'Utilities': ['NEE', 'DUK', 'SO', 'D', 'EXC', 'AEP', 'XEL', 'PEG', 'ED', 'FE'],
            'Renewable Energy': ['TSLA', 'ENPH', 'SEDG', 'NEE', 'BEP', 'ICLN'],
            
            # Consumer & Retail
            'Retail': ['WMT', 'TGT', 'COST', 'HD', 'LOW', 'TJX', 'ROST', 'BBY', 'GPS', 'M'],
            'Restaurants': ['MCD', 'SBUX', 'YUM', 'QSR', 'CMG', 'DPZ', 'DRI', 'EAT'],
            'Consumer Goods': ['PG', 'UL', 'KO', 'PEP', 'CL', 'KMB', 'GIS', 'K', 'CAG', 'CPB'],
            'Apparel': ['NKE', 'ADSK', 'LULU', 'UAA', 'VFC', 'RL', 'PVH', 'URBN', 'GPS'],
            
            # Industrial & Manufacturing
            'Aerospace': ['BA', 'LMT', 'RTX', 'NOC', 'GD', 'TDG', 'LHX', 'HWM', 'TXT'],
            'Industrial Equipment': ['GE', 'CAT', 'DE', 'HON', 'MMM', 'EMR', 'ITW', 'PH', 'ROK'],
            'Automotive': ['TSLA', 'GM', 'F', 'TM', 'HMC', 'STLA', 'RIVN', 'LCID', 'NIO', 'XPEV'],
            'Transportation': ['UPS', 'FDX', 'UAL', 'DAL', 'AAL', 'LUV', 'JBLU', 'UBER', 'LYFT'],
            
            # Real Estate & REITs
            'REITs': ['AMT', 'PLD', 'CCI', 'EQIX', 'SPG', 'O', 'WELL', 'PSA', 'AVB', 'EQR'],
            
            # Media & Entertainment
            'Media': ['DIS', 'NFLX', 'PARA', 'WBD', 'ROKU', 'SPOT', 'T', 'VZ', 'TMUS'],
            'Gaming': ['ATVI', 'EA', 'TTWO', 'RBLX', 'UNITY', 'ZNGA']
        }
        
        # Sector-based fallback
        sector_competitors = {
            'Technology': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'CRM', 'ORCL', 'ADBE', 'INTC', 'AMD'],
            'Healthcare': ['JNJ', 'PFE', 'UNH', 'MRK', 'ABT', 'TMO', 'DHR', 'BMY', 'LLY', 'AMGN', 'GILD', 'MDT'],
            'Financial Services': ['JPM', 'BAC', 'BRK-B', 'V', 'MA', 'WFC', 'GS', 'MS', 'C', 'USB', 'AXP', 'COF'],
            'Consumer Cyclical': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'SBUX', 'TJX', 'LOW', 'TGT', 'GM', 'F'],
            'Consumer Defensive': ['PG', 'KO', 'PEP', 'WMT', 'COST', 'UL', 'CL', 'KMB', 'GIS', 'K'],
            'Energy': ['XOM', 'CVX', 'COP', 'EOG', 'SLB', 'HAL', 'OXY', 'KMI', 'WMB', 'MPC'],
            'Industrials': ['BA', 'CAT', 'GE', 'MMM', 'HON', 'UPS', 'LMT', 'RTX', 'DE', 'NOC'],
            'Communication Services': ['GOOGL', 'META', 'NFLX', 'DIS', 'VZ', 'T', 'TMUS', 'ROKU', 'SNAP'],
            'Utilities': ['NEE', 'DUK', 'SO', 'D', 'EXC', 'AEP', 'XEL', 'PEG', 'ED', 'FE'],
            'Real Estate': ['AMT', 'PLD', 'CCI', 'EQIX', 'SPG', 'O', 'WELL', 'PSA', 'AVB', 'EQR'],
            'Materials': ['LIN', 'APD', 'SHW', 'FCX', 'NEM', 'DD', 'DOW', 'PPG', 'ECL', 'NUE']
        }
        
        competitors = []
        main_symbol = main_stock['symbol']
        
        # First try industry-specific matches
        for key, symbols in industry_competitors.items():
            if key.lower() in industry.lower() or industry.lower() in key.lower():
                competitors.extend([s for s in symbols if s != main_symbol])
                break
        
        # If no industry match, try sector
        if not competitors and sector in sector_competitors:
            competitors.extend([s for s in sector_competitors[sector] if s != main_symbol])
        
        # If still no competitors, use similar market cap stocks from same sector
        if not competitors:
            all_sector_stocks = []
            for symbols in sector_competitors.values():
                all_sector_stocks.extend(symbols)
            competitors = [s for s in all_sector_stocks if s != main_symbol][:10]
        
        # Remove duplicates and limit
        competitors = list(dict.fromkeys(competitors))[:max_competitors]
        
        # Validate competitors are real stocks
        validated_competitors = []
        for comp in competitors:
            if self.validate_symbol(comp):
                validated_competitors.append(comp)
            if len(validated_competitors) >= max_competitors:
                break
        
        return validated_competitors
    
    def calculate_ytd_return(self, hist):
        """Calculate year-to-date return"""
        try:
            current_year_start = datetime(datetime.now().year, 1, 1)
            hist_current_year = hist[hist.index >= current_year_start]
            if len(hist_current_year) > 1:
                return (hist_current_year['Close'][-1] / hist_current_year['Close'][0] - 1) * 100
        except:
            pass
        return 0
    
    def calculate_return(self, hist, days):
        """Calculate return over specified number of days"""
        try:
            if len(hist) >= days:
                return (hist['Close'][-1] / hist['Close'][-days] - 1) * 100
        except:
            pass
        return 0
    
    def calculate_score(self, stock_data, industry_avg):
        """Calculate investment score based on multiple metrics"""
        score = 50  # Base score
        
        try:
            # Valuation scoring (lower is better for P/E, P/B)
            if stock_data['pe_ratio'] > 0 and industry_avg.get('pe_ratio', 0) > 0:
                pe_score = max(0, min(20, 20 * (industry_avg['pe_ratio'] / stock_data['pe_ratio'])))
                score += pe_score - 10
            
            # Profitability scoring
            if stock_data['roe'] and stock_data['roe'] > 0:
                roe_score = min(15, stock_data['roe'] * 100)
                score += roe_score - 7.5
            
            if stock_data['profit_margin'] and stock_data['profit_margin'] > 0:
                margin_score = min(10, stock_data['profit_margin'] * 100)
                score += margin_score - 5
            
            # Financial health scoring
            if stock_data['debt_to_equity'] and stock_data['debt_to_equity'] > 0:
                debt_score = max(-10, min(5, 5 - (stock_data['debt_to_equity'] / 100)))
                score += debt_score
            
            if stock_data['current_ratio'] and stock_data['current_ratio'] > 0:
                liquidity_score = min(5, stock_data['current_ratio'] * 2.5)
                score += liquidity_score - 2.5
            
            # Growth scoring
            if stock_data['revenue_growth'] and stock_data['revenue_growth'] > 0:
                growth_score = min(10, stock_data['revenue_growth'] * 100)
                score += growth_score - 5
            
        except Exception as e:
            print(f"Error calculating score: {e}")
        
        return max(0, min(100, score))
    
    def generate_recommendation(self, score, stock_data):
        """Generate investment recommendation based on score and metrics"""
        if score >= 70:
            recommendation = "STRONG BUY"
        elif score >= 60:
            recommendation = "BUY"
        elif score >= 40:
            recommendation = "HOLD"
        elif score >= 30:
            recommendation = "SELL"
        else:
            recommendation = "STRONG SELL"
        
        # Calculate target price (simple projection)
        current_price = stock_data['current_price']
        if score >= 60:
            target_price = current_price * (1 + (score - 50) / 100)
        else:
            target_price = current_price * (1 - (50 - score) / 100)
        
        return {
            'recommendation': recommendation,
            'score': score,
            'target_price': target_price,
            'risk_level': 'High' if stock_data.get('beta', 1) > 1.5 else 'Medium' if stock_data.get('beta', 1) > 0.8 else 'Low'
        }
    
    def analyze_stock(self, symbol, callback=None):
        """Main analysis function with callback for GUI updates"""
        try:
            if callback:
                callback(f"🔍 Validating symbol {symbol.upper()}...")
            
            # Validate symbol
            if not self.validate_symbol(symbol):
                error_msg = f"❌ Error: Invalid or non-existent stock symbol '{symbol}'"
                if callback:
                    callback(error_msg)
                return None
            
            if callback:
                callback(f"📊 Retrieving data for {symbol.upper()}...")
            
            # Get main stock data
            main_stock = self.get_stock_info(symbol.upper())
            if not main_stock:
                error_msg = f"❌ Error: Could not retrieve data for {symbol}"
                if callback:
                    callback(error_msg)
                return None
            
            if callback:
                callback(f"🏢 Company: {main_stock['name']}")
                callback(f"📈 Sector: {main_stock['sector']}")
                callback(f"🏭 Industry: {main_stock['industry']}")
                callback(f"💰 Current Price: ${main_stock['current_price']:.2f}")
                callback(f"🔍 Finding competitors...")
            
            # Find competitors using improved method
            competitors = self.find_industry_competitors(main_stock)
            if callback:
                callback(f"🎯 Competitors identified: {', '.join(competitors)}")
            
            # Get competitor data
            competitor_data = []
            for i, comp in enumerate(competitors):
                if callback:
                    callback(f"📊 Loading data for {comp} ({i+1}/{len(competitors)})...")
                comp_data = self.get_stock_info(comp)
                if comp_data:
                    competitor_data.append(comp_data)
            
            if not competitor_data:
                error_msg = "❌ Error: Could not retrieve competitor data"
                if callback:
                    callback(error_msg)
                return None
            
            if callback:
                callback("🧮 Calculating metrics and scores...")
            
            # Create comparison dataframe
            all_stocks = [main_stock] + competitor_data
            df = pd.DataFrame(all_stocks)
            
            # Calculate industry averages (only numeric columns)
            numeric_df = df.select_dtypes(include=[np.number])
            industry_avg = numeric_df.mean().to_dict()
            
            # Calculate scores and recommendations
            for stock in all_stocks:
                stock['score'] = self.calculate_score(stock, industry_avg)
                stock['recommendation_data'] = self.generate_recommendation(stock['score'], stock)
            
            # Sort stocks by score (best to worst)
            all_stocks.sort(key=lambda x: x['score'], reverse=True)
            
            if callback:
                callback("✅ Analysis complete!")
            
            return {
                'main_stock': main_stock,
                'competitors': competitor_data,
                'all_stocks': all_stocks,
                'industry_avg': industry_avg
            }
            
        except Exception as e:
            error_msg = f"❌ Error during analysis: {str(e)}"
            if callback:
                callback(error_msg)
            return None


class ModernStockAnalyzerGUI:
    def __init__(self):
        self.analyzer = StockCompetitorAnalyzer()
        self.analysis_result = None
        self.setup_gui()
    
    def setup_gui(self):
        """Setup the ultra-modern GUI with dark theme"""
        self.root = tk.Tk()
        self.root.title("🚀 Stock Competitor Analyzer Pro")
        self.root.geometry("1600x1000")
        
        # Modern dark color scheme
        self.colors = {
            'bg_primary': '#0f172a',      # Dark blue-gray
            'bg_secondary': '#1e293b',    # Lighter dark blue
            'bg_card': '#334155',         # Card background
            'accent_primary': '#3b82f6',  # Blue accent
            'accent_secondary': '#8b5cf6', # Purple accent
            'accent_success': '#10b981',   # Green
            'accent_warning': '#f59e0b',   # Orange
            'accent_danger': '#ef4444',    # Red
            'text_primary': '#f8fafc',     # Light text
            'text_secondary': '#cbd5e1',   # Secondary text
            'text_muted': '#64748b',       # Muted text
            'border': '#475569'            # Border color
        }
        
        self.root.configure(bg=self.colors['bg_primary'])
        
        # Configure modern style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure('Dark.TLabel', 
                       background=self.colors['bg_primary'], 
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 10))
        
        style.configure('Card.TLabel', 
                       background=self.colors['bg_card'], 
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 10))
        
        style.configure('Title.TLabel', 
                       background=self.colors['bg_primary'], 
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 24, 'bold'))
        
        style.configure('Subtitle.TLabel', 
                       background=self.colors['bg_primary'], 
                       foreground=self.colors['text_secondary'],
                       font=('Segoe UI', 12))
        
        style.configure('Dark.TNotebook', 
                       background=self.colors['bg_secondary'],
                       borderwidth=0)
        
        style.configure('Dark.TNotebook.Tab', 
                       background=self.colors['bg_card'],
                       foreground=self.colors['text_primary'],
                       padding=[20, 10],
                       font=('Segoe UI', 10, 'bold'))
        
        style.map('Dark.TNotebook.Tab',
                 background=[('selected', self.colors['accent_primary'])],
                 foreground=[('selected', 'white')])
        
        self.create_header()
        self.create_input_section()
        self.create_results_section()
        self.create_status_section()
        
        # Center window
        self.center_window()
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_header(self):
        """Create the modern header section"""
        header_frame = tk.Frame(self.root, bg=self.colors['bg_primary'], height=120)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Main title with gradient effect simulation
        title_container = tk.Frame(header_frame, bg=self.colors['bg_primary'])
        title_container.pack(expand=True, fill='both')
        
        title_label = tk.Label(title_container, text="🚀 Stock Analyzer Pro", 
                              font=('Segoe UI', 32, 'bold'), fg=self.colors['accent_primary'], 
                              bg=self.colors['bg_primary'])
        title_label.pack(pady=(20, 5))
        
        subtitle_label = tk.Label(title_container, 
                                 text="Advanced AI-Powered Stock Analysis & Competitor Intelligence", 
                                 font=('Segoe UI', 14), fg=self.colors['text_secondary'], 
                                 bg=self.colors['bg_primary'])
        subtitle_label.pack()
        
        # Add decorative elements
        separator = tk.Frame(header_frame, bg=self.colors['accent_primary'], height=3)
        separator.pack(fill='x', pady=(10, 0))
    
    def create_input_section(self):
        """Create the modern input section"""
        input_frame = tk.Frame(self.root, bg=self.colors['bg_secondary'], pady=25)
        input_frame.pack(fill='x', padx=30, pady=(0, 20))
        
        # Stock symbol input with modern design
        input_label = tk.Label(input_frame, text="Enter Stock Symbol", 
                              font=('Segoe UI', 16, 'bold'), 
                              bg=self.colors['bg_secondary'], 
                              fg=self.colors['text_primary'])
        input_label.pack(anchor='w', padx=20)
        
        input_container = tk.Frame(input_frame, bg=self.colors['bg_secondary'])
        input_container.pack(fill='x', pady=(15, 0), padx=20)
        
        # Modern entry with custom styling
        entry_frame = tk.Frame(input_container, bg=self.colors['bg_card'], 
                              relief='solid', bd=1, highlightthickness=2)
        entry_frame.pack(side='left', padx=(0, 15))
        
        self.symbol_var = tk.StringVar()
        self.symbol_entry = tk.Entry(entry_frame, textvariable=self.symbol_var, 
                                   font=('Segoe UI', 14), width=15, 
                                   bg=self.colors['bg_card'], 
                                   fg=self.colors['text_primary'],
                                   insertbackground=self.colors['text_primary'],
                                   relief='flat', bd=10)
        self.symbol_entry.pack(padx=10, pady=8)
        self.symbol_entry.bind('<Return>', lambda e: self.analyze_stock())
        self.symbol_entry.bind('<FocusIn>', lambda e: entry_frame.config(highlightcolor=self.colors['accent_primary']))
        self.symbol_entry.bind('<FocusOut>', lambda e: entry_frame.config(highlightcolor=self.colors['border']))
        
        # Modern gradient-style buttons
        self.analyze_button = tk.Button(input_container, text="🚀 Analyze Stock", 
                                      command=self.analyze_stock, 
                                      font=('Segoe UI', 12, 'bold'),
                                      bg=self.colors['accent_primary'], 
                                      fg='white', relief='flat', 
                                      padx=25, pady=12, cursor='hand2',
                                      activebackground='#2563eb')
        self.analyze_button.pack(side='left', padx=(0, 10))
        
        self.clear_button = tk.Button(input_container, text="🗑️ Clear", 
                                    command=self.clear_results, 
                                    font=('Segoe UI', 11),
                                    bg=self.colors['bg_card'], 
                                    fg=self.colors['text_secondary'], 
                                    relief='flat', padx=20, pady=12, cursor='hand2',
                                    activebackground=self.colors['border'])
        self.clear_button.pack(side='left')
        
        # Popular examples with modern chip design
        examples_frame = tk.Frame(input_frame, bg=self.colors['bg_secondary'])
        examples_frame.pack(fill='x', pady=(20, 0), padx=20)
        
        examples_label = tk.Label(examples_frame, text="💡 Popular Stocks:", 
                                font=('Segoe UI', 11, 'bold'), 
                                bg=self.colors['bg_secondary'], 
                                fg=self.colors['text_muted'])
        examples_label.pack(side='left', padx=(0, 15))
        
        examples = [
            ('AAPL', 'Apple'),
            ('TSLA', 'Tesla'),
            ('NVDA', 'NVIDIA'),
            ('CRM', 'Salesforce'),
            ('MSFT', 'Microsoft'),
            ('GOOGL', 'Google')
        ]
        
        for symbol, name in examples:
            chip_button = tk.Button(examples_frame, text=f"{symbol}", 
                                  command=lambda s=symbol: self.set_symbol(s),
                                  font=('Segoe UI', 9, 'bold'), 
                                  bg=self.colors['bg_card'], 
                                  fg=self.colors['text_primary'],
                                  relief='flat', padx=12, pady=6, cursor='hand2',
                                  activebackground=self.colors['accent_primary'])
            chip_button.pack(side='left', padx=(0, 8))
    
    def create_results_section(self):
        """Create the modern results section"""
        self.results_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        
        # Create modern notebook with custom styling
        self.notebook = ttk.Notebook(self.results_frame, style='Dark.TNotebook')
        
        # Overview tab with modern design
        self.overview_tab = tk.Frame(self.notebook, bg=self.colors['bg_primary'])
        self.notebook.add(self.overview_tab, text='📊 Overview & Rankings')
        
        # Metrics tab  
        self.metrics_tab = tk.Frame(self.notebook, bg=self.colors['bg_primary'])
        self.notebook.add(self.metrics_tab, text='📈 Detailed Metrics')
        
        # Charts tab
        self.charts_tab = tk.Frame(self.notebook, bg=self.colors['bg_primary'])
        self.notebook.add(self.charts_tab, text='📉 Visual Analysis')
        
        # Analysis tab
        self.analysis_tab = tk.Frame(self.notebook, bg=self.colors['bg_primary'])
        self.notebook.add(self.analysis_tab, text='🎯 AI Investment Analysis')
        
        self.notebook.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Initially hide results
        self.results_frame.pack_forget()
    
    def create_status_section(self):
        """Create the modern status section"""
        status_frame = tk.Frame(self.root, bg=self.colors['bg_secondary'], height=140)
        status_frame.pack(fill='x', side='bottom')
        status_frame.pack_propagate(False)
        
        status_header = tk.Label(status_frame, text="📋 Live Analysis Status", 
                               font=('Segoe UI', 14, 'bold'), 
                               bg=self.colors['bg_secondary'], 
                               fg=self.colors['text_primary'])
        status_header.pack(anchor='w', padx=20, pady=(15, 8))
        
        # Modern text area with custom styling
        text_frame = tk.Frame(status_frame, bg=self.colors['bg_card'], relief='solid', bd=1)
        text_frame.pack(fill='both', expand=True, padx=20, pady=(0, 15))
        
        self.status_text = scrolledtext.ScrolledText(text_frame, height=4, 
                                                   font=('Consolas', 10),
                                                   bg=self.colors['bg_card'], 
                                                   fg=self.colors['text_primary'], 
                                                   relief='flat', bd=5,
                                                   insertbackground=self.colors['text_primary'])
        self.status_text.pack(fill='both', expand=True, padx=5, pady=5)
    
    def set_symbol(self, symbol):
        """Set symbol in entry box with animation effect"""
        self.symbol_var.set(symbol)
        self.symbol_entry.focus()
        # Highlight effect
        self.symbol_entry.config(bg=self.colors['accent_primary'])
        self.root.after(200, lambda: self.symbol_entry.config(bg=self.colors['bg_card']))
    
    def update_status(self, message):
        """Update status log with timestamp and colors"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Add color coding based on message type
        if "❌" in message or "Error" in message:
            color_tag = "error"
        elif "✅" in message or "complete" in message:
            color_tag = "success"
        elif "🔍" in message or "📊" in message:
            color_tag = "info"
        else:
            color_tag = "normal"
        
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.status_text.insert(tk.END, formatted_message)
        
        # Configure color tags
        self.status_text.tag_config("error", foreground="#ef4444")
        self.status_text.tag_config("success", foreground="#10b981")
        self.status_text.tag_config("info", foreground="#3b82f6")
        self.status_text.tag_config("normal", foreground=self.colors['text_primary'])
        
        # Apply color to the last line
        line_start = self.status_text.index("end-2l")
        line_end = self.status_text.index("end-1l")
        self.status_text.tag_add(color_tag, line_start, line_end)
        
        self.status_text.see(tk.END)
        self.root.update_idletasks()
    
    def analyze_stock(self):
        """Analyze stock with modern loading animation"""
        symbol = self.symbol_var.get().strip().upper()
        if not symbol:
            messagebox.showwarning("Input Required", "Please enter a stock symbol to analyze")
            return
        
        # Modern loading state
        self.analyze_button.config(state='disabled', text='🔄 Analyzing...', 
                                 bg=self.colors['accent_warning'])
        self.clear_results()
        
        # Clear status with header
        self.status_text.delete(1.0, tk.END)
        self.update_status(f"🚀 Starting analysis for {symbol}")
        
        # Run analysis in separate thread
        thread = threading.Thread(target=self._analyze_thread, args=(symbol,))
        thread.daemon = True
        thread.start()
    
    def _analyze_thread(self, symbol):
        """Thread function for analysis"""
        try:
            result = self.analyzer.analyze_stock(symbol, callback=self.update_status)
            
            if result:
                self.analysis_result = result
                self.root.after(0, self.display_results)
            else:
                self.root.after(0, self.analysis_failed)
                
        except Exception as e:
            self.update_status(f"❌ Critical Error: {str(e)}")
            self.root.after(0, self.analysis_failed)
    
    def analysis_failed(self):
        """Handle failed analysis with better UX"""
        self.analyze_button.config(state='normal', text='🚀 Analyze Stock', 
                                 bg=self.colors['accent_primary'])
        messagebox.showerror("Analysis Failed", 
                           "Unable to complete stock analysis.\n\n"
                           "Please check:\n"
                           "• Stock symbol is valid\n"
                           "• Internet connection is stable\n"
                           "• Try again in a few moments")
    
    def display_results(self):
        """Display analysis results with modern design"""
        if not self.analysis_result:
            return
        
        # Re-enable analyze button with success state
        self.analyze_button.config(state='normal', text='✅ Analysis Complete', 
                                 bg=self.colors['accent_success'])
        self.root.after(3000, lambda: self.analyze_button.config(text='🚀 Analyze Stock', 
                                                                bg=self.colors['accent_primary']))
        
        # Show results frame with slide animation
        self.results_frame.pack(fill='both', expand=True, padx=0, pady=0)
        
        # Clear previous results
        for tab in [self.overview_tab, self.metrics_tab, self.charts_tab, self.analysis_tab]:
            for widget in tab.winfo_children():
                widget.destroy()
        
        # Populate tabs with modern design
        self.populate_overview_tab()
        self.populate_metrics_tab()
        self.populate_charts_tab()
        self.populate_analysis_tab()
    
    def populate_overview_tab(self):
        """Populate the overview tab with modern ranking design"""
        main_stock = self.analysis_result['main_stock']
        all_stocks = self.analysis_result['all_stocks']  # Already sorted by score
        
        # Create scrollable container
        canvas = tk.Canvas(self.overview_tab, bg=self.colors['bg_primary'], 
                          highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.overview_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_primary'])
        
        scrollable_frame.bind("<Configure>", 
                            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Hero section for main stock
        hero_frame = tk.Frame(scrollable_frame, bg=self.colors['accent_primary'], 
                            relief='solid', bd=2)
        hero_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        # Find main stock ranking
        main_stock_rank = next((i+1 for i, stock in enumerate(all_stocks) 
                               if stock['symbol'] == main_stock['symbol']), 1)
        
        rank_text = f"#{main_stock_rank} RANKED" if main_stock_rank <= len(all_stocks) else "ANALYZED"
        
        tk.Label(hero_frame, text=f"🎯 {rank_text} STOCK", 
                font=('Segoe UI', 14, 'bold'), fg='white', 
                bg=self.colors['accent_primary']).pack(pady=(15, 5))
        
        tk.Label(hero_frame, text=f"{main_stock['symbol']} - {main_stock['name']}", 
                font=('Segoe UI', 24, 'bold'), fg='white', 
                bg=self.colors['accent_primary']).pack(pady=(0, 5))
        
        tk.Label(hero_frame, text=f"{main_stock['sector']} • {main_stock['industry']}", 
                font=('Segoe UI', 12), fg='#e0f2fe', 
                bg=self.colors['accent_primary']).pack(pady=(0, 15))
        
        # Key metrics in hero
        hero_metrics = tk.Frame(hero_frame, bg=self.colors['accent_primary'])
        hero_metrics.pack(fill='x', padx=20, pady=(0, 20))
        
        rec_data = main_stock['recommendation_data']
        
        self.create_hero_metric(hero_metrics, "Current Price", 
                              f"${main_stock['current_price']:.2f}")
        self.create_hero_metric(hero_metrics, "Investment Score", 
                              f"{main_stock['score']:.1f}/100")
        self.create_hero_metric(hero_metrics, "Recommendation", 
                              rec_data['recommendation'])
        self.create_hero_metric(hero_metrics, "Target Price", 
                              f"${rec_data['target_price']:.2f}")
        
        # Rankings section
        rankings_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_primary'])
        rankings_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(rankings_frame, text="🏆 Complete Investment Rankings", 
                font=('Segoe UI', 20, 'bold'), 
                bg=self.colors['bg_primary'], 
                fg=self.colors['text_primary']).pack(anchor='w', pady=(0, 20))
        
        # Create ranking cards
        for i, stock in enumerate(all_stocks):
            self.create_ranking_card(rankings_frame, stock, i+1, 
                                   is_main=(stock['symbol'] == main_stock['symbol']))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_hero_metric(self, parent, title, value):
        """Create hero metric display"""
        metric_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        metric_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        tk.Label(metric_frame, text=title, font=('Segoe UI', 10, 'bold'), 
                fg=self.colors['text_muted'], bg='white').pack(pady=(12, 2))
        
        tk.Label(metric_frame, text=value, font=('Segoe UI', 14, 'bold'), 
                fg=self.colors['bg_primary'], bg='white').pack(pady=(2, 12))
    
    def create_ranking_card(self, parent, stock, rank, is_main=False):
        """Create modern ranking card"""
        # Determine rank color and medal
        if rank == 1:
            rank_color = '#ffd700'  # Gold
            medal = "🥇"
        elif rank == 2:
            rank_color = '#c0c0c0'  # Silver
            medal = "🥈"
        elif rank == 3:
            rank_color = '#cd7f32'  # Bronze
            medal = "🥉"
        else:
            rank_color = self.colors['text_muted']
            medal = f"#{rank}"
        
        # Card styling based on main stock and rank
        if is_main:
            card_bg = self.colors['accent_secondary']
            border_color = self.colors['accent_primary']
            text_color = 'white'
            star = "⭐ "
        else:
            card_bg = self.colors['bg_card']
            border_color = self.colors['border']
            text_color = self.colors['text_primary']
            star = ""
        
        card_frame = tk.Frame(parent, bg=border_color, relief='solid', bd=2)
        card_frame.pack(fill='x', pady=8)
        
        inner_frame = tk.Frame(card_frame, bg=card_bg)
        inner_frame.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Top row - Rank and Symbol
        top_row = tk.Frame(inner_frame, bg=card_bg)
        top_row.pack(fill='x', padx=20, pady=(15, 5))
        
        rank_label = tk.Label(top_row, text=f"{medal}", 
                            font=('Segoe UI', 16, 'bold'), 
                            fg=rank_color, bg=card_bg)
        rank_label.pack(side='left')
        
        symbol_label = tk.Label(top_row, text=f"{star}{stock['symbol']}", 
                              font=('Segoe UI', 18, 'bold'), 
                              fg=text_color, bg=card_bg)
        symbol_label.pack(side='left', padx=(10, 0))
        
        # Company name
        name_label = tk.Label(top_row, text=stock['name'], 
                            font=('Segoe UI', 12), 
                            fg=text_color if is_main else self.colors['text_secondary'], 
                            bg=card_bg)
        name_label.pack(side='right')
        
        # Metrics row
        metrics_row = tk.Frame(inner_frame, bg=card_bg)
        metrics_row.pack(fill='x', padx=20, pady=10)
        
        # Score with progress bar effect
        score_frame = tk.Frame(metrics_row, bg=card_bg)
        score_frame.pack(side='left')
        
        tk.Label(score_frame, text="Investment Score", 
                font=('Segoe UI', 9, 'bold'), 
                fg=text_color if is_main else self.colors['text_muted'], 
                bg=card_bg).pack(anchor='w')
        
        score_container = tk.Frame(score_frame, bg=card_bg)
        score_container.pack(fill='x', pady=(2, 0))
        
        # Score bar
        score = stock['score']
        bar_width = int(score * 2)  # Scale to 200px max
        
        if score >= 70:
            bar_color = self.colors['accent_success']
        elif score >= 50:
            bar_color = self.colors['accent_warning']
        else:
            bar_color = self.colors['accent_danger']
        
        score_bar = tk.Frame(score_container, bg=bar_color, width=bar_width, height=8)
        score_bar.pack(side='left')
        
        tk.Label(score_container, text=f"{score:.1f}/100", 
                font=('Segoe UI', 10, 'bold'), 
                fg=text_color, bg=card_bg).pack(side='left', padx=(10, 0))
        
        # Key metrics
        key_metrics = tk.Frame(metrics_row, bg=card_bg)
        key_metrics.pack(side='right')
        
        metrics_text = f"${stock['current_price']:.2f}  •  "
        if stock['pe_ratio']:
            metrics_text += f"P/E: {stock['pe_ratio']:.1f}  •  "
        if stock['roe']:
            metrics_text += f"ROE: {stock['roe']*100:.1f}%  •  "
        
        rec = stock['recommendation_data']['recommendation']
        rec_color = (self.colors['accent_success'] if 'BUY' in rec else 
                    self.colors['accent_warning'] if 'HOLD' in rec else 
                    self.colors['accent_danger'])
        
        tk.Label(key_metrics, text=metrics_text[:-3], 
                font=('Segoe UI', 10), 
                fg=text_color if is_main else self.colors['text_secondary'], 
                bg=card_bg).pack(anchor='e')
        
        # Recommendation badge
        rec_frame = tk.Frame(inner_frame, bg=card_bg)
        rec_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        rec_badge = tk.Label(rec_frame, text=rec, 
                           font=('Segoe UI', 10, 'bold'), 
                           fg='white', bg=rec_color, 
                           padx=12, pady=4)
        rec_badge.pack(side='right')
    
    def populate_metrics_tab(self):
        """Populate detailed metrics tab with modern design"""
        # Create scrollable frame
        canvas = tk.Canvas(self.metrics_tab, bg=self.colors['bg_primary'], 
                          highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.metrics_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_primary'])
        
        scrollable_frame.bind("<Configure>", 
                            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        all_stocks = self.analysis_result['all_stocks']  # Already sorted
        
        # Header
        header_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_primary'])
        header_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(header_frame, text="📈 Comprehensive Financial Analysis", 
                font=('Segoe UI', 22, 'bold'), 
                bg=self.colors['bg_primary'], 
                fg=self.colors['text_primary']).pack(anchor='w')
        
        tk.Label(header_frame, text="Detailed metrics comparison across all competitors", 
                font=('Segoe UI', 12), 
                bg=self.colors['bg_primary'], 
                fg=self.colors['text_secondary']).pack(anchor='w', pady=(5, 0))
        
        # Metrics sections with modern cards
        metrics_sections = [
            ('💰 Valuation Metrics', [
                ('Current Price ($)', 'current_price', lambda x: f"${x:.2f}" if x else "N/A"),
                ('Market Cap', 'market_cap', self.format_market_cap),
                ('P/E Ratio', 'pe_ratio', lambda x: f"{x:.2f}" if x else "N/A"),
                ('Forward P/E', 'forward_pe', lambda x: f"{x:.2f}" if x else "N/A"),
                ('Price/Book', 'price_to_book', lambda x: f"{x:.2f}" if x else "N/A"),
                ('Price/Sales', 'price_to_sales', lambda x: f"{x:.2f}" if x else "N/A")
            ]),
            ('📊 Profitability Metrics', [
                ('ROE (%)', 'roe', lambda x: f"{x*100:.2f}%" if x else "N/A"),
                ('ROA (%)', 'roa', lambda x: f"{x*100:.2f}%" if x else "N/A"),
                ('Gross Margin (%)', 'gross_margin', lambda x: f"{x*100:.2f}%" if x else "N/A"),
                ('Operating Margin (%)', 'operating_margin', lambda x: f"{x*100:.2f}%" if x else "N/A"),
                ('Profit Margin (%)', 'profit_margin', lambda x: f"{x*100:.2f}%" if x else "N/A")
            ]),
            ('🏦 Financial Health', [
                ('Debt/Equity', 'debt_to_equity', lambda x: f"{x:.2f}" if x else "N/A"),
                ('Current Ratio', 'current_ratio', lambda x: f"{x:.2f}" if x else "N/A"),
                ('Quick Ratio', 'quick_ratio', lambda x: f"{x:.2f}" if x else "N/A")
            ]),
            ('📈 Growth & Performance', [
                ('Revenue Growth (%)', 'revenue_growth', lambda x: f"{x*100:.2f}%" if x else "N/A"),
                ('Earnings Growth (%)', 'earnings_growth', lambda x: f"{x*100:.2f}%" if x else "N/A"),
                ('Beta', 'beta', lambda x: f"{x:.2f}" if x else "N/A"),
                ('YTD Return (%)', 'ytd_return', lambda x: f"{x:.2f}%" if x else "N/A")
            ])
        ]
        
        main_symbol = self.analysis_result['main_stock']['symbol']
        
        for section_title, metrics in metrics_sections:
            section_card = tk.Frame(scrollable_frame, bg=self.colors['bg_card'], 
                                  relief='solid', bd=1)
            section_card.pack(fill='x', padx=20, pady=15)
            
            # Section header
            section_header = tk.Frame(section_card, bg=self.colors['accent_primary'])
            section_header.pack(fill='x')
            
            tk.Label(section_header, text=section_title, 
                    font=('Segoe UI', 14, 'bold'), 
                    bg=self.colors['accent_primary'], 
                    fg='white').pack(pady=12, padx=20, anchor='w')
            
            # Metrics table
            table_frame = tk.Frame(section_card, bg=self.colors['bg_card'])
            table_frame.pack(fill='x', padx=20, pady=20)
            
            # Header row
            header_row = tk.Frame(table_frame, bg=self.colors['bg_secondary'])
            header_row.pack(fill='x', pady=(0, 2))
            
            tk.Label(header_row, text="Metric", font=('Segoe UI', 11, 'bold'), 
                    bg=self.colors['bg_secondary'], fg=self.colors['text_primary'],
                    width=25, anchor='w').grid(row=0, column=0, sticky='ew', padx=2, pady=8)
            
            for i, stock in enumerate(all_stocks):
                symbol_text = f"🌟 {stock['symbol']}" if stock['symbol'] == main_symbol else stock['symbol']
                
                tk.Label(header_row, text=symbol_text, font=('Segoe UI', 11, 'bold'), 
                        bg=self.colors['bg_secondary'], fg=self.colors['text_primary'],
                        width=15, anchor='center').grid(row=0, column=i+1, sticky='ew', padx=1, pady=8)
            
            # Data rows
            for row_idx, (metric_name, key, formatter) in enumerate(metrics):
                row_bg = self.colors['bg_card'] if row_idx % 2 == 0 else '#2a3441'
                
                row_frame = tk.Frame(table_frame, bg=row_bg)
                row_frame.pack(fill='x', pady=1)
                
                tk.Label(row_frame, text=metric_name, font=('Segoe UI', 10), 
                        bg=row_bg, fg=self.colors['text_primary'],
                        width=25, anchor='w').grid(row=0, column=0, sticky='ew', padx=2, pady=6)
                
                for i, stock in enumerate(all_stocks):
                    value = formatter(stock.get(key, 0))
                    
                    # Highlight best values
                    if key in ['roe', 'roa', 'gross_margin', 'operating_margin', 'profit_margin', 'revenue_growth'] and stock.get(key, 0):
                        if stock.get(key, 0) == max([s.get(key, 0) for s in all_stocks if s.get(key, 0)]):
                            text_color = self.colors['accent_success']
                        else:
                            text_color = self.colors['text_primary']
                    elif key in ['pe_ratio', 'debt_to_equity'] and stock.get(key, 0):
                        if stock.get(key, 0) == min([s.get(key, 0) for s in all_stocks if s.get(key, 0) and s.get(key, 0) > 0]):
                            text_color = self.colors['accent_success']
                        else:
                            text_color = self.colors['text_primary']
                    else:
                        text_color = self.colors['text_primary']
                    
                    tk.Label(row_frame, text=value, font=('Segoe UI', 10), 
                            bg=row_bg, fg=text_color,
                            width=15, anchor='center').grid(row=0, column=i+1, sticky='ew', padx=1, pady=6)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def populate_charts_tab(self):
        """Populate charts tab with modern visualizations"""
        try:
            all_stocks = self.analysis_result['all_stocks']
            main_symbol = self.analysis_result['main_stock']['symbol']
            
            # Create figure with dark theme
            fig = Figure(figsize=(14, 10), facecolor=self.colors['bg_primary'])
            
            # Create 2x2 subplot - fix compatibility issue
            axes = fig.subplots(2, 2)
            
            # Set face color for each subplot individually
            for ax in axes.flat:
                ax.set_facecolor(self.colors['bg_card'])
            fig.suptitle('Investment Analysis Dashboard', fontsize=16, color=self.colors['text_primary'], fontweight='bold')
            
            symbols = [stock['symbol'] for stock in all_stocks]
            colors = [self.colors['accent_danger'] if s == main_symbol else self.colors['accent_primary'] for s in symbols]
            
            # 1. Investment Scores Ranking
            ax1 = axes[0, 0]
            scores = [stock['score'] for stock in all_stocks]
            bars1 = ax1.barh(symbols, scores, color=colors, alpha=0.8)
            ax1.set_title('Investment Scores (Ranked)', fontweight='bold', color=self.colors['text_primary'])
            ax1.set_xlabel('Score (0-100)', color=self.colors['text_primary'])
            ax1.axvline(x=50, color=self.colors['text_muted'], linestyle='--', alpha=0.7, label='Neutral (50)')
            ax1.axvline(x=60, color=self.colors['accent_success'], linestyle='--', alpha=0.7, label='Buy Zone (60+)')
            
            # Add value labels
            for i, (bar, score) in enumerate(zip(bars1, scores)):
                ax1.text(score + 1, i, f'{score:.1f}', va='center', fontweight='bold', color=self.colors['text_primary'])
            
            ax1.set_facecolor(self.colors['bg_card'])
            ax1.tick_params(colors=self.colors['text_primary'])
            ax1.legend(loc='lower right')
            
            # 2. P/E Ratio Comparison
            ax2 = axes[0, 1]
            pe_ratios = [stock['pe_ratio'] if stock['pe_ratio'] and stock['pe_ratio'] > 0 else 0 for stock in all_stocks]
            bars2 = ax2.bar(symbols, pe_ratios, color=colors, alpha=0.8)
            ax2.set_title('P/E Ratio Comparison', fontweight='bold', color=self.colors['text_primary'])
            ax2.set_ylabel('P/E Ratio', color=self.colors['text_primary'])
            
            for bar in bars2:
                height = bar.get_height()
                if height > 0:
                    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                            f'{height:.1f}', ha='center', va='bottom', fontweight='bold', 
                            color=self.colors['text_primary'])
            
            ax2.set_facecolor(self.colors['bg_card'])
            ax2.tick_params(colors=self.colors['text_primary'])
            plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
            
            # 3. ROE vs Debt/Equity Scatter
            ax3 = axes[1, 0]
            roe_values = [stock['roe']*100 if stock['roe'] else 0 for stock in all_stocks]
            debt_values = [stock['debt_to_equity'] if stock['debt_to_equity'] else 0 for stock in all_stocks]
            
            scatter_colors = [self.colors['accent_danger'] if s == main_symbol else self.colors['accent_primary'] for s in symbols]
            scatter = ax3.scatter(debt_values, roe_values, c=scatter_colors, s=120, alpha=0.8, edgecolors='white', linewidth=2)
            
            # Add labels
            for i, symbol in enumerate(symbols):
                if debt_values[i] > 0 or roe_values[i] > 0:
                    ax3.annotate(symbol, (debt_values[i], roe_values[i]), 
                               xytext=(5, 5), textcoords='offset points', 
                               fontsize=9, fontweight='bold', color=self.colors['text_primary'])
            
            ax3.set_xlabel('Debt/Equity Ratio', color=self.colors['text_primary'])
            ax3.set_ylabel('ROE (%)', color=self.colors['text_primary'])
            ax3.set_title('Profitability vs Financial Leverage', fontweight='bold', color=self.colors['text_primary'])
            ax3.grid(True, alpha=0.3, color=self.colors['text_muted'])
            ax3.set_facecolor(self.colors['bg_card'])
            ax3.tick_params(colors=self.colors['text_primary'])
            
            # Add quadrant lines
            if max(debt_values) > 0 and max(roe_values) > 0:
                ax3.axhline(y=np.mean([r for r in roe_values if r > 0]), color=self.colors['text_muted'], linestyle='--', alpha=0.5)
                ax3.axvline(x=np.mean([d for d in debt_values if d > 0]), color=self.colors['text_muted'], linestyle='--', alpha=0.5)
            
            # 4. Recommendation Distribution
            ax4 = axes[1, 1]
            recommendations = [stock['recommendation_data']['recommendation'] for stock in all_stocks]
            rec_counts = {}
            rec_colors_map = {
                'STRONG BUY': self.colors['accent_success'],
                'BUY': '#16a34a',
                'HOLD': self.colors['accent_warning'], 
                'SELL': '#dc2626',
                'STRONG SELL': self.colors['accent_danger']
            }
            
            for rec in recommendations:
                rec_counts[rec] = rec_counts.get(rec, 0) + 1
            
            if rec_counts:
                wedges, texts, autotexts = ax4.pie(rec_counts.values(), 
                                                 labels=rec_counts.keys(),
                                                 colors=[rec_colors_map.get(rec, self.colors['accent_primary']) for rec in rec_counts.keys()],
                                                 autopct='%1.0f%%', startangle=90,
                                                 textprops={'color': self.colors['text_primary'], 'fontweight': 'bold'})
                
                ax4.set_title('Investment Recommendations Distribution', fontweight='bold', color=self.colors['text_primary'])
                ax4.set_facecolor(self.colors['bg_card'])
            
            # Style all axes
            for ax in axes.flat:
                ax.spines['bottom'].set_color(self.colors['border'])
                ax.spines['top'].set_color(self.colors['border'])
                ax.spines['right'].set_color(self.colors['border'])
                ax.spines['left'].set_color(self.colors['border'])
            
            plt.tight_layout()
            
            # Embed in tkinter
            canvas_widget = FigureCanvasTkAgg(fig, self.charts_tab)
            canvas_widget.draw()
            canvas_widget.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
            
        except Exception as e:
            error_frame = tk.Frame(self.charts_tab, bg=self.colors['bg_primary'])
            error_frame.pack(fill='both', expand=True)
            
            tk.Label(error_frame, text="📊 Chart Generation Error", 
                    font=('Segoe UI', 16, 'bold'), 
                    bg=self.colors['bg_primary'], 
                    fg=self.colors['accent_danger']).pack(expand=True)
            
            tk.Label(error_frame, text=f"Error: {str(e)}", 
                    font=('Segoe UI', 12), 
                    bg=self.colors['bg_primary'], 
                    fg=self.colors['text_secondary']).pack()
    
    def populate_analysis_tab(self):
        """Populate AI investment analysis tab with modern design"""
        main_stock = self.analysis_result['main_stock']
        all_stocks = self.analysis_result['all_stocks']
        rec_data = main_stock['recommendation_data']
        
        # Create scrollable frame
        canvas = tk.Canvas(self.analysis_tab, bg=self.colors['bg_primary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.analysis_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_primary'])
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # AI Analysis Header
        header_frame = tk.Frame(scrollable_frame, bg=self.colors['accent_secondary'], relief='solid', bd=2)
        header_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(header_frame, text="🤖 AI-Powered Investment Analysis", 
                font=('Segoe UI', 24, 'bold'), fg='white', 
                bg=self.colors['accent_secondary']).pack(pady=(20, 5))
        
        tk.Label(header_frame, text="Advanced algorithmic analysis with machine learning insights", 
                font=('Segoe UI', 12), fg='#e0f2fe', 
                bg=self.colors['accent_secondary']).pack(pady=(0, 20))
        
        # Investment Decision Card
        decision_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_primary'])
        decision_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Determine recommendation styling
        rec_text = rec_data['recommendation']
        if 'STRONG BUY' in rec_text:
            rec_bg = self.colors['accent_success']
            rec_icon = "🚀"
            rec_desc = "Exceptional investment opportunity with superior fundamentals"
        elif 'BUY' in rec_text:
            rec_bg = '#16a34a'
            rec_icon = "📈"
            rec_desc = "Solid investment candidate with attractive risk-reward profile"
        elif 'HOLD' in rec_text:
            rec_bg = self.colors['accent_warning']
            rec_icon = "⚖️"
            rec_desc = "Neutral outlook, consider maintaining current position"
        elif 'SELL' in rec_text:
            rec_bg = '#dc2626'
            rec_icon = "📉"
            rec_desc = "Weak fundamentals suggest reducing exposure"
        else:
            rec_bg = self.colors['accent_danger']
            rec_icon = "⚠️"
            rec_desc = "Significant risks outweigh potential rewards"
        
        # Main recommendation card
        rec_card = tk.Frame(decision_frame, bg=rec_bg, relief='solid', bd=3)
        rec_card.pack(fill='x')
        
        rec_header = tk.Frame(rec_card, bg=rec_bg)
        rec_header.pack(fill='x', pady=20)
        
        tk.Label(rec_header, text=f"{rec_icon} INVESTMENT DECISION", 
                font=('Segoe UI', 14, 'bold'), fg='white', bg=rec_bg).pack()
        
        tk.Label(rec_header, text=rec_text, 
                font=('Segoe UI', 28, 'bold'), fg='white', bg=rec_bg).pack(pady=(5, 0))
        
        tk.Label(rec_header, text=rec_desc, 
                font=('Segoe UI', 12), fg='white', bg=rec_bg).pack(pady=(5, 0))
        
        # Key metrics in recommendation card
        metrics_grid = tk.Frame(rec_card, bg=rec_bg)
        metrics_grid.pack(fill='x', padx=20, pady=(0, 20))
        
        # Create 4 metric boxes
        metrics_data = [
            ("Investment Score", f"{rec_data['score']:.1f}/100", "🎯"),
            ("Target Price", f"${rec_data['target_price']:.2f}", "💰"),
            ("Current Price", f"${main_stock['current_price']:.2f}", "📊"),
            ("Risk Level", rec_data['risk_level'], "⚡")
        ]
        
        for i, (title, value, icon) in enumerate(metrics_data):
            metric_box = tk.Frame(metrics_grid, bg='white', relief='solid', bd=1)
            metric_box.grid(row=0, column=i, sticky='ew', padx=5, pady=10)
            metrics_grid.columnconfigure(i, weight=1)
            
            tk.Label(metric_box, text=icon, font=('Segoe UI', 16), 
                    bg='white', fg=rec_bg).pack(pady=(12, 2))
            tk.Label(metric_box, text=title, font=('Segoe UI', 10, 'bold'), 
                    bg='white', fg=self.colors['text_muted']).pack()
            tk.Label(metric_box, text=value, font=('Segoe UI', 12, 'bold'), 
                    bg='white', fg=self.colors['bg_primary']).pack(pady=(2, 12))
        
        # Competitive Analysis
        competitive_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_primary'])
        competitive_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(competitive_frame, text="🏆 Competitive Position Analysis", 
                font=('Segoe UI', 18, 'bold'), 
                bg=self.colors['bg_primary'], fg=self.colors['text_primary']).pack(anchor='w', pady=(0, 15))
        
        # Calculate position
        main_stock_rank = next((i+1 for i, stock in enumerate(all_stocks) 
                               if stock['symbol'] == main_stock['symbol']), 1)
        total_stocks = len(all_stocks)
        
        position_card = tk.Frame(competitive_frame, bg=self.colors['bg_card'], relief='solid', bd=1)
        position_card.pack(fill='x', pady=(0, 15))
        
        position_text = f"Ranks #{main_stock_rank} out of {total_stocks} analyzed stocks"
        
        if main_stock_rank == 1:
            position_desc = "🥇 Leading performer in the competitive set"
            position_color = self.colors['accent_success']
        elif main_stock_rank <= 3:
            position_desc = "🥈 Strong competitive position among top performers"
            position_color = self.colors['accent_success']
        elif main_stock_rank <= total_stocks // 2:
            position_desc = "📊 Above-average performance vs competitors"
            position_color = self.colors['accent_warning']
        else:
            position_desc = "📉 Below-average performance, room for improvement"
            position_color = self.colors['accent_danger']
        
        tk.Label(position_card, text=position_text, 
                font=('Segoe UI', 14, 'bold'), 
                bg=self.colors['bg_card'], fg=position_color).pack(pady=(15, 5), padx=20)
        
        tk.Label(position_card, text=position_desc, 
                font=('Segoe UI', 12), 
                bg=self.colors['bg_card'], fg=self.colors['text_primary']).pack(pady=(0, 15), padx=20)
        
        # Strengths and Weaknesses
        analysis_container = tk.Frame(scrollable_frame, bg=self.colors['bg_primary'])
        analysis_container.pack(fill='x', padx=20, pady=20)
        
        # Calculate comparative metrics
        competitors = [s for s in all_stocks if s['symbol'] != main_stock['symbol']]
        strengths, weaknesses = self.calculate_strengths_weaknesses(main_stock, competitors)
        
        # Strengths card
        strengths_card = tk.Frame(analysis_container, bg=self.colors['accent_success'], relief='solid', bd=2)
        strengths_card.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        tk.Label(strengths_card, text="💪 Key Strengths", 
                font=('Segoe UI', 16, 'bold'), fg='white', 
                bg=self.colors['accent_success']).pack(pady=(15, 10))
        
        strengths_content = tk.Frame(strengths_card, bg='white')
        strengths_content.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        if strengths:
            for i, strength in enumerate(strengths[:4]):
                strength_item = tk.Frame(strengths_content, bg='white')
                strength_item.pack(fill='x', pady=5)
                
                tk.Label(strength_item, text=f"✓ {strength}", 
                        font=('Segoe UI', 11), bg='white', 
                        fg=self.colors['bg_primary'], wraplength=300, 
                        justify='left', anchor='w').pack(anchor='w', padx=10, pady=2)
        else:
            tk.Label(strengths_content, text="No significant strengths identified", 
                    font=('Segoe UI', 11), bg='white', 
                    fg=self.colors['text_muted']).pack(expand=True, padx=10, pady=20)
        
        # Weaknesses card
        weaknesses_card = tk.Frame(analysis_container, bg=self.colors['accent_danger'], relief='solid', bd=2)
        weaknesses_card.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        tk.Label(weaknesses_card, text="⚠️ Key Concerns", 
                font=('Segoe UI', 16, 'bold'), fg='white', 
                bg=self.colors['accent_danger']).pack(pady=(15, 10))
        
        weaknesses_content = tk.Frame(weaknesses_card, bg='white')
        weaknesses_content.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        if weaknesses:
            for i, weakness in enumerate(weaknesses[:4]):
                weakness_item = tk.Frame(weaknesses_content, bg='white')
                weakness_item.pack(fill='x', pady=5)
                
                tk.Label(weakness_item, text=f"✗ {weakness}", 
                        font=('Segoe UI', 11), bg='white', 
                        fg=self.colors['bg_primary'], wraplength=300, 
                        justify='left', anchor='w').pack(anchor='w', padx=10, pady=2)
        else:
            tk.Label(weaknesses_content, text="No significant concerns identified", 
                    font=('Segoe UI', 11), bg='white', 
                    fg=self.colors['text_muted']).pack(expand=True, padx=10, pady=20)
        
        # Investment Thesis
        thesis_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_card'], relief='solid', bd=1)
        thesis_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(thesis_frame, text="📝 AI Investment Thesis", 
                font=('Segoe UI', 18, 'bold'), 
                bg=self.colors['bg_card'], fg=self.colors['text_primary']).pack(anchor='w', padx=20, pady=(20, 10))
        
        # Generate AI-style thesis
        thesis = self.generate_investment_thesis(main_stock, rec_data, main_stock_rank, total_stocks)
        
        thesis_text = tk.Label(thesis_frame, text=thesis, 
                              font=('Segoe UI', 12), bg=self.colors['bg_card'], 
                              fg=self.colors['text_primary'], wraplength=800, 
                              justify='left', anchor='w')
        thesis_text.pack(padx=20, pady=(0, 20), anchor='w')
        
        # Risk Assessment
        risk_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_secondary'], relief='solid', bd=1)
        risk_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(risk_frame, text="⚡ Risk Assessment", 
                font=('Segoe UI', 18, 'bold'), 
                bg=self.colors['bg_secondary'], fg=self.colors['text_primary']).pack(anchor='w', padx=20, pady=(20, 10))
        
        risk_factors = self.assess_risks(main_stock, competitors)
        
        for risk in risk_factors:
            risk_item = tk.Frame(risk_frame, bg=self.colors['bg_secondary'])
            risk_item.pack(fill='x', padx=20, pady=2)
            
            tk.Label(risk_item, text=f"• {risk}", 
                    font=('Segoe UI', 11), bg=self.colors['bg_secondary'], 
                    fg=self.colors['text_primary'], wraplength=800, 
                    justify='left', anchor='w').pack(anchor='w', pady=2)
        
        if not risk_factors:
            tk.Label(risk_frame, text="• Minimal risks identified based on current analysis", 
                    font=('Segoe UI', 11), bg=self.colors['bg_secondary'], 
                    fg=self.colors['text_secondary']).pack(anchor='w', padx=20, pady=5)
        
        tk.Frame(risk_frame, height=15, bg=self.colors['bg_secondary']).pack()
        
        # Disclaimer
        disclaimer_frame = tk.Frame(scrollable_frame, bg='#2c1810', relief='solid', bd=2)
        disclaimer_frame.pack(fill='x', padx=20, pady=30)
        
        tk.Label(disclaimer_frame, text="⚠️ IMPORTANT DISCLAIMER", 
                font=('Segoe UI', 14, 'bold'), bg='#2c1810', 
                fg='#f59e0b').pack(pady=(15, 8))
        
        disclaimer_text = ("This AI analysis is for educational purposes only and should not be considered as "
                          "professional financial advice. Past performance does not guarantee future results. "
                          "Market conditions can change rapidly. Always consult with a qualified financial advisor "
                          "and conduct your own research before making investment decisions.")
        
        tk.Label(disclaimer_frame, text=disclaimer_text, 
                font=('Segoe UI', 10), bg='#2c1810', fg='#d1d5db', 
                wraplength=800, justify='center').pack(padx=20, pady=(0, 15))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def calculate_strengths_weaknesses(self, main_stock, competitors):
        """Calculate strengths and weaknesses vs competitors"""
        strengths = []
        weaknesses = []
        
        if not competitors:
            return strengths, weaknesses
        
        try:
            # Calculate averages
            avg_pe = np.mean([c['pe_ratio'] for c in competitors if c['pe_ratio'] and c['pe_ratio'] > 0])
            avg_roe = np.mean([c['roe'] for c in competitors if c['roe'] and c['roe'] > 0])
            avg_margin = np.mean([c['profit_margin'] for c in competitors if c['profit_margin'] and c['profit_margin'] > 0])
            avg_debt = np.mean([c['debt_to_equity'] for c in competitors if c['debt_to_equity'] and c['debt_to_equity'] > 0])
            
            # Valuation analysis
            if main_stock['pe_ratio'] and avg_pe and main_stock['pe_ratio'] > 0:
                if main_stock['pe_ratio'] < avg_pe * 0.85:
                    strengths.append(f"Attractive valuation with P/E of {main_stock['pe_ratio']:.1f} vs peer average of {avg_pe:.1f}")
                elif main_stock['pe_ratio'] > avg_pe * 1.25:
                    weaknesses.append(f"Premium valuation at P/E of {main_stock['pe_ratio']:.1f} vs peer average of {avg_pe:.1f}")
            
            # Profitability analysis  
            if main_stock['roe'] and avg_roe and main_stock['roe'] > 0:
                if main_stock['roe'] > avg_roe * 1.15:
                    strengths.append(f"Superior profitability with ROE of {main_stock['roe']*100:.1f}% vs peer average of {avg_roe*100:.1f}%")
                elif main_stock['roe'] < avg_roe * 0.75:
                    weaknesses.append(f"Below-average profitability with ROE of {main_stock['roe']*100:.1f}% vs peer average of {avg_roe*100:.1f}%")
            
            # Margin analysis
            if main_stock['profit_margin'] and avg_margin and main_stock['profit_margin'] > 0:
                if main_stock['profit_margin'] > avg_margin * 1.2:
                    strengths.append(f"Excellent profit margins at {main_stock['profit_margin']*100:.1f}% vs peer average of {avg_margin*100:.1f}%")
                elif main_stock['profit_margin'] < avg_margin * 0.8:
                    weaknesses.append(f"Compressed margins at {main_stock['profit_margin']*100:.1f}% vs peer average of {avg_margin*100:.1f}%")
            
            # Financial health
            if main_stock['debt_to_equity'] is not None:
                if main_stock['debt_to_equity'] < 25:
                    strengths.append(f"Strong balance sheet with low debt-to-equity ratio of {main_stock['debt_to_equity']:.1f}")
                elif main_stock['debt_to_equity'] > 100:
                    weaknesses.append(f"High financial leverage with debt-to-equity ratio of {main_stock['debt_to_equity']:.1f}")
            
            # Growth analysis
            if main_stock['revenue_growth'] and main_stock['revenue_growth'] > 0.15:
                strengths.append(f"Strong revenue growth momentum at {main_stock['revenue_growth']*100:.1f}%")
            elif main_stock['revenue_growth'] and main_stock['revenue_growth'] < -0.05:
                weaknesses.append(f"Declining revenue trend at {main_stock['revenue_growth']*100:.1f}%")
            
            # Market performance
            if main_stock.get('ytd_return'):
                if main_stock['ytd_return'] > 15:
                    strengths.append(f"Strong market performance with YTD return of +{main_stock['ytd_return']:.1f}%")
                elif main_stock['ytd_return'] < -15:
                    weaknesses.append(f"Poor market performance with YTD return of {main_stock['ytd_return']:.1f}%")
            
        except Exception as e:
            print(f"Error calculating strengths/weaknesses: {e}")
        
        return strengths, weaknesses
    
    def generate_investment_thesis(self, main_stock, rec_data, rank, total):
        """Generate AI-style investment thesis"""
        score = rec_data['score']
        
        if score >= 75:
            return (f"Our AI models identify {main_stock['symbol']} as a compelling investment opportunity, "
                   f"ranking #{rank} out of {total} analyzed securities. The company demonstrates "
                   f"exceptional fundamentals with a composite score of {score:.1f}/100, indicating "
                   f"superior risk-adjusted return potential. Key algorithmic indicators suggest "
                   f"sustainable competitive advantages and robust financial positioning.")
        
        elif score >= 60:
            return (f"{main_stock['symbol']} presents a solid investment case with our proprietary "
                   f"scoring algorithm rating it {score:.1f}/100 (rank #{rank} of {total}). "
                   f"The analysis reveals balanced fundamentals with positive momentum indicators. "
                   f"While not without risks, the overall investment profile suggests favorable "
                   f"risk-adjusted returns over the medium term.")
        
        elif score >= 40:
            return (f"Our quantitative models generate a neutral outlook for {main_stock['symbol']} "
                   f"with a composite score of {score:.1f}/100. The company ranks #{rank} among "
                   f"{total} analyzed peers, indicating average performance characteristics. "
                   f"Mixed fundamental signals suggest a wait-and-see approach may be prudent "
                   f"until clearer directional catalysts emerge.")
        
        else:
            return (f"AI analysis indicates significant headwinds for {main_stock['symbol']}, "
                   f"with our scoring models generating a concerning {score:.1f}/100 rating "
                   f"(rank #{rank} of {total}). Multiple algorithmic red flags suggest "
                   f"fundamental weaknesses that may persist. Risk management protocols "
                   f"recommend defensive positioning until material improvements are evident.")
    
    def assess_risks(self, main_stock, competitors):
        """Assess investment risks"""
        risks = []
        
        try:
            # High volatility
            if main_stock.get('beta', 1) > 1.5:
                risks.append(f"High volatility risk with beta of {main_stock['beta']:.2f}")
            
            # Valuation risk
            if main_stock['pe_ratio'] and main_stock['pe_ratio'] > 30:
                risks.append(f"Valuation risk with elevated P/E ratio of {main_stock['pe_ratio']:.1f}")
            
            # Leverage risk  
            if main_stock['debt_to_equity'] and main_stock['debt_to_equity'] > 80:
                risks.append(f"Financial leverage risk with debt-to-equity of {main_stock['debt_to_equity']:.1f}")
            
            # Profitability concerns
            if main_stock['roe'] and main_stock['roe'] < 0.05:
                risks.append(f"Low profitability with ROE of {main_stock['roe']*100:.1f}%")
            
            # Growth concerns
            if main_stock['revenue_growth'] and main_stock['revenue_growth'] < -0.1:
                risks.append(f"Revenue decline risk with growth of {main_stock['revenue_growth']*100:.1f}%")
            
            # Market performance
            if main_stock.get('ytd_return') and main_stock['ytd_return'] < -20:
                risks.append(f"Poor market momentum with YTD return of {main_stock['ytd_return']:.1f}%")
            
            # Sector-specific risks
            sector = main_stock.get('sector', '')
            if 'Technology' in sector:
                risks.append("Technology sector volatility and regulatory scrutiny")
            elif 'Energy' in sector:
                risks.append("Commodity price volatility and environmental regulations")
            elif 'Financial' in sector:
                risks.append("Interest rate sensitivity and regulatory changes")
                
        except Exception as e:
            print(f"Error assessing risks: {e}")
        
        return risks
    
    def format_market_cap(self, market_cap):
        """Format market cap in readable format"""
        if not market_cap or market_cap == 0:
            return "N/A"
        elif market_cap >= 1e12:
            return f"${market_cap/1e12:.2f}T"
        elif market_cap >= 1e9:
            return f"${market_cap/1e9:.2f}B"
        elif market_cap >= 1e6:
            return f"${market_cap/1e6:.2f}M"
        else:
            return f"${market_cap:.0f}"
    
    def clear_results(self):
        """Clear all results with animation"""
        if self.results_frame.winfo_viewable():
            self.results_frame.pack_forget()
        self.analysis_result = None
    
    def run(self):
        """Run the GUI application"""
        self.root.mainloop()


def main():
    """Main function to run the application"""
    try:
        # Check if required packages are installed
        import matplotlib.pyplot as plt
        import yfinance as yf
        import pandas as pd
        import numpy as np
        
        print("🚀 Starting Stock Competitor Analyzer Pro...")
        print("📋 All required packages are available.")
        
        # Create and run the modern GUI
        app = ModernStockAnalyzerGUI()
        app.run()
        
    except ImportError as e:
        print("❌ Missing required packages. Please install:")
        print("pip install yfinance pandas numpy matplotlib seaborn")
        print(f"\nSpecific error: {e}")
        
        # Fallback to console version
        print("\n🔄 Falling back to console version...")
        console_main()
    except Exception as e:
        print(f"❌ Error starting GUI: {e}")
        print("🔄 Falling back to console version...")
        console_main()


def console_main():
    """Console version of the application"""
    print("=" * 60)
    print("📈 STOCK COMPETITOR ANALYZER - CONSOLE VERSION")
    print("=" * 60)
    
    analyzer = StockCompetitorAnalyzer()
    
    while True:
        try:
            print("\n" + "="*50)
            symbol = input("Enter stock symbol (or 'quit' to exit): ").strip().upper()
            
            if symbol.lower() in ['quit', 'exit', 'q']:
                print("👋 Thank you for using Stock Competitor Analyzer!")
                break
            
            if not symbol:
                print("⚠️ Please enter a valid stock symbol.")
                continue
            
            print(f"\n🔍 Analyzing {symbol}...")
            result = analyzer.analyze_stock(symbol, callback=print)
            
            if result:
                main_stock = result['main_stock']
                all_stocks = result['all_stocks']  # Already sorted by score
                rec_data = main_stock['recommendation_data']
                
                # Find main stock ranking
                main_rank = next((i+1 for i, stock in enumerate(all_stocks) 
                                if stock['symbol'] == main_stock['symbol']), 1)
                
                print("\n" + "="*70)
                print("📊 INVESTMENT RANKINGS & ANALYSIS")
                print("="*70)
                print(f"📍 {main_stock['symbol']} ranks #{main_rank} out of {len(all_stocks)} analyzed stocks")
                print(f"🏢 Company: {main_stock['name']}")
                print(f"💰 Current Price: ${main_stock['current_price']:.2f}")
                print(f"🎯 Investment Score: {rec_data['score']:.1f}/100")
                print(f"📈 Recommendation: {rec_data['recommendation']}")
                print(f"🎪 Target Price: ${rec_data['target_price']:.2f}")
                print(f"⚡ Risk Level: {rec_data['risk_level']}")
                print("="*70)
                
                # Sorted comparison table
                print("\n🏆 COMPLETE RANKINGS (Best to Worst):")
                print("-" * 90)
                print(f"{'Rank':<6} {'Symbol':<8} {'Company':<20} {'Price':<10} {'P/E':<8} {'ROE':<8} {'Score':<8} {'Rec':<12}")
                print("-" * 90)
                
                for i, stock in enumerate(all_stocks):
                    rank = i + 1
                    symbol_display = f"⭐{stock['symbol']}" if stock['symbol'] == main_stock['symbol'] else stock['symbol']
                    name = stock['name'][:18] + ".." if len(stock['name']) > 20 else stock['name']
                    price = f"${stock['current_price']:.2f}" if stock['current_price'] else "N/A"
                    pe = f"{stock['pe_ratio']:.1f}" if stock['pe_ratio'] else "N/A"
                    roe = f"{stock['roe']*100:.1f}%" if stock['roe'] else "N/A"
                    score = f"{stock['score']:.1f}"
                    rec = stock['recommendation_data']['recommendation']
                    
                    # Add medal for top 3
                    if rank == 1:
                        rank_display = "🥇 1"
                    elif rank == 2:
                        rank_display = "🥈 2"
                    elif rank == 3:
                        rank_display = "🥉 3"
                    else:
                        rank_display = f"#{rank}"
                    
                    print(f"{rank_display:<6} {symbol_display:<8} {name:<20} {price:<10} {pe:<8} {roe:<8} {score:<8} {rec:<12}")
                
                print("-" * 90)
                print("⭐ = Your analyzed stock")
                print("\n💡 Higher scores indicate better investment opportunities")
                
                # Quick insights
                print(f"\n🔍 QUICK INSIGHTS:")
                if main_rank == 1:
                    print(f"🎉 {main_stock['symbol']} is the top-ranked stock in this analysis!")
                elif main_rank <= 3:
                    print(f"👍 {main_stock['symbol']} ranks in the top 3 - strong performance!")
                elif main_rank <= len(all_stocks) // 2:
                    print(f"📊 {main_stock['symbol']} shows above-average performance.")
                else:
                    print(f"⚠️ {main_stock['symbol']} ranks in the bottom half - consider alternatives.")
            
            another = input("\n🔄 Analyze another stock? (y/n): ").strip().lower()
            if another not in ['y', 'yes']:
                break
                
        except KeyboardInterrupt:
            print("\n\n👋 Exiting...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue


if __name__ == "__main__":
    main()