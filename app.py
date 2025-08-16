"""
Main Streamlit application for CryptoGap+
"""
import streamlit as st
import pandas as pd
import time
import plotly.graph_objects as go
from datetime import datetime

from utils.arbitrage_calculator import ArbitrageCalculator
from models.llm_analyzer import LLMAnalyzer
from data.binance_fetcher import BinanceFetcher
from data.kraken_fetcher import KrakenFetcher
from config.config import TOP_CRYPTOS, MARKETS, REFRESH_RATE

# Initialize components
arbitrage_calculator = ArbitrageCalculator()
llm_analyzer = LLMAnalyzer()
binance_fetcher = BinanceFetcher()
kraken_fetcher = KrakenFetcher()

# Page configuration
st.set_page_config(
    page_title="CryptoGap+ | Crypto Arbitrage Tool",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* General styles */
    .main-header {
        font-size: 2.5rem;
        color: #2196F3;
        margin-bottom: 0.5rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        font-weight: bold;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .header-image {
        height: 45px;
        width: 80px;
        object-fit: cover;
        border-radius: 8px;
        vertical-align: middle;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #FFFFFF;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    
    /* Card styles */
    .card {
        background-color: #1E1E1E;
        color: #E0E0E0;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
        border: 1px solid #333;
    }
    
    /* Profit/Loss indicators */
    .profit {
        color: #00E676;
        font-weight: bold;
        background-color: rgba(0, 230, 118, 0.1);
        padding: 2px 6px;
        border-radius: 4px;
    }
    .loss {
        color: #FF1744;
        font-weight: bold;
        background-color: rgba(255, 23, 68, 0.1);
        padding: 2px 6px;
        border-radius: 4px;
    }
    .info {
        color: #2196F3;
        font-weight: bold;
        background-color: rgba(33, 150, 243, 0.1);
        padding: 2px 6px;
        border-radius: 4px;
    }
    
    /* Highlight box */
    .highlight {
        background-color: #2C2C2C;
        color: #E0E0E0;
        padding: 15px;
        border-left: 5px solid #FFC107;
        margin-bottom: 15px;
        border-radius: 0 10px 10px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Table styles */
    .dataframe {
        background-color: #1E1E1E !important;
        color: #E0E0E0 !important;
    }
    .dataframe th {
        background-color: #2C2C2C !important;
        color: #2196F3 !important;
    }
    .dataframe td {
        background-color: #1E1E1E !important;
        color: #E0E0E0 !important;
    }
    
    /* Metric styles */
    [data-testid="stMetricValue"] {
        color: #2196F3 !important;
    }
    [data-testid="stMetricDelta"] {
        color: #00E676 !important;
    }
    
    /* LLM Analysis section */
    .llm-analysis {
        background-color: #2C2C2C;
        color: #E0E0E0;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #424242;
        margin: 15px 0;
    }
    .llm-analysis h3 {
        color: #2196F3;
        margin-bottom: 15px;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #1E1E1E;
    }
    ::-webkit-scrollbar-thumb {
        background: #424242;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
</style>
""", unsafe_allow_html=True)

# App title
st.markdown('<div class="main-header"><img src="https://variety.com/wp-content/uploads/2021/12/Bitcoin-Cryptocurrency-Placeholder.jpg?w=1000&h=563&crop=1" class="header-image" alt="CryptoGap+ Logo">CryptoGap+</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Advanced Crypto Arbitrage & Analysis Tool</div>', unsafe_allow_html=True)

# Sidebar
st.sidebar.title("Controls & Settings")

# Refresh button
if st.sidebar.button("Refresh Data"):
    st.experimental_rerun()

# Coin selection for detailed analysis
st.sidebar.markdown("## Detailed Coin Analysis")
selected_coin = st.sidebar.selectbox("Select Coin", TOP_CRYPTOS)
selected_market = st.sidebar.selectbox("Select Market", MARKETS)

# Trade simulator
st.sidebar.markdown("## Trade Simulator")
trade_amount = st.sidebar.number_input("Investment Amount (USDT)", min_value=10.0, max_value=10000.0, value=100.0, step=10.0)
buy_exchange = st.sidebar.radio("Buy Exchange", ["Binance", "Kraken"])
sell_exchange = "Kraken" if buy_exchange == "Binance" else "Binance"

# Main content area - using tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Arbitrage Opportunities", "Live Prices", "Low-Price Gainers", "Detailed Analysis", "Advanced Analytics"])

with tab1:
    st.markdown("## Arbitrage Opportunities")
    
    with st.spinner("Calculating arbitrage opportunities..."):
        # Get arbitrage opportunities
        opportunities_df = arbitrage_calculator.calculate_arbitrage_opportunities()
        
        if not opportunities_df.empty:
            # Display opportunities table
            st.dataframe(
                opportunities_df[['Symbol', 'Market', 'Buy_Exchange', 'Sell_Exchange', 
                                 'Buy_Price', 'Sell_Price', 'Price_Diff_Pct']]
                .style.format({
                    'Buy_Price': '${:.6f}',
                    'Sell_Price': '${:.6f}',
                    'Price_Diff_Pct': '{:.2f}%'
                }).map(lambda x: f'color: {"#00E676" if x > 0 else "#FF1744"}' if isinstance(x, float) else '', subset=['Price_Diff_Pct'])
            )
            
            # Get the best opportunity
            best_opportunity = opportunities_df.iloc[0].to_dict()
            
            # LLM analysis of the best opportunity
            st.markdown("### LLM Analysis of Best Opportunity")
            with st.spinner("Generating analysis..."):
                analysis = llm_analyzer.analyze_arbitrage_opportunity(best_opportunity)
                st.markdown(f'<div class="llm-analysis">{analysis}</div>', unsafe_allow_html=True)
            
            # Last seen opportunity tracker
            st.markdown("### Last Seen Opportunity")
            last_opportunity = arbitrage_calculator.get_last_opportunity()
            if last_opportunity:
                timestamp = last_opportunity.get('Timestamp', time.time())
                formatted_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                price_diff = last_opportunity.get('Price_Diff_Pct', 0)
                diff_color = '#00E676' if price_diff > 0 else '#FF1744'
                
                st.markdown(f"""
                <div class="highlight">
                Last seen: {formatted_time}<br>
                Symbol: {last_opportunity.get('Symbol')}/{last_opportunity.get('Market')}<br>
                Buy on {last_opportunity.get('Buy_Exchange')} at ${last_opportunity.get('Buy_Price', 0):.6f}<br>
                Sell on {last_opportunity.get('Sell_Exchange')} at ${last_opportunity.get('Sell_Price', 0):.6f}<br>
                Price Difference: <span style="color: {diff_color}">{price_diff:.2f}%</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No profitable arbitrage opportunities found at the moment. Try refreshing later.")

with tab2:
    st.markdown("## Live Prices")
    
    with st.spinner("Fetching live prices..."):
        # Get prices from both exchanges
        binance_prices, kraken_prices = arbitrage_calculator.fetch_all_prices()
        
        if not binance_prices.empty and not kraken_prices.empty:
            # Merge dataframes
            merged_df = pd.merge(
                binance_prices, 
                kraken_prices, 
                on='Symbol', 
                suffixes=('_binance', '_kraken')
            )
            
            # Display prices
            for market in MARKETS:
                st.markdown(f"### {market} Market")
                
                market_df = merged_df[['Symbol', f'{market}_price_binance', f'{market}_price_kraken']].copy()
                market_df = market_df.dropna()
                
                if not market_df.empty:
                    # Calculate price difference
                    market_df['Price_Diff_Pct'] = (
                        (market_df[f'{market}_price_binance'] - market_df[f'{market}_price_kraken']).abs() / 
                        market_df[[f'{market}_price_binance', f'{market}_price_kraken']].min(axis=1) * 100
                    )
                    
                    # Rename columns for display
                    market_df = market_df.rename(columns={
                        f'{market}_price_binance': 'Binance Price',
                        f'{market}_price_kraken': 'Kraken Price'
                    })
                    
                    # Display table with colored price differences
                    st.dataframe(
                        market_df.style.format({
                            'Binance Price': '${:.6f}',
                            'Kraken Price': '${:.6f}',
                            'Price_Diff_Pct': '{:.2f}%'
                        }).map(lambda x: f'color: {"#00E676" if x > 0 else "#FF1744"}' if isinstance(x, float) else '', subset=['Price_Diff_Pct'])
                    )
                else:
                    st.info(f"No data available for {market} market.")
            
            # Add price trend visualization
            if not merged_df.empty:
                st.markdown("### 📈 Price Trend Analysis")
                
                # Select top cryptocurrencies for trend analysis
                top_cryptos = merged_df.head(10)  # Top 10 by market cap
                
                # Create trend chart
                fig_trend = go.Figure()
                
                for _, crypto in top_cryptos.iterrows():
                    if 'USDT_price_binance' in crypto and 'USDT_price_kraken' in crypto:
                        if pd.notna(crypto['USDT_price_binance']) and pd.notna(crypto['USDT_price_kraken']):
                            fig_trend.add_trace(go.Scatter(
                                x=[crypto['USDT_price_binance'], crypto['USDT_price_kraken']],
                                y=['Binance', 'Kraken'],
                                mode='lines+markers',
                                name=crypto['Symbol'],
                                line=dict(width=2),
                                marker=dict(size=8)
                            ))
                
                fig_trend.update_layout(
                    title="Price Comparison Across Exchanges (Top 10 Cryptocurrencies)",
                    xaxis_title="Price (USDT)",
                    yaxis_title="Exchange",
                    height=500,
                    showlegend=True
                )
                
                st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.error("Failed to fetch prices from one or both exchanges.")

with tab3:
    st.markdown("## Low-Price Gainers")
    
    with st.spinner("Identifying low-price gainers..."):
        # Get low-price gainers
        gainers_df = arbitrage_calculator.get_low_price_gainers()
        
        if not gainers_df.empty:
            # Display gainers table with colored price differences
            st.dataframe(
                gainers_df.style.format({
                    'Binance_Price': '${:.6f}',
                    'Kraken_Price': '${:.6f}',
                    'Price_Diff_Pct': '{:.2f}%',
                    'Avg_Price': '${:.6f}'
                }).map(lambda x: f'color: {"#00E676" if x > 0 else "#FF1744"}' if isinstance(x, float) else '', subset=['Price_Diff_Pct'])
            )
            
            # Get the top gainer
            top_gainer = gainers_df.iloc[0].to_dict()
            
            # LLM analysis of the top gainer
            st.markdown("### LLM Analysis of Top Low-Price Gainer")
            with st.spinner("Generating analysis..."):
                analysis = llm_analyzer.analyze_low_price_gainer(top_gainer)
                st.markdown(f'<div class="card">{analysis}</div>', unsafe_allow_html=True)
        else:
            st.info("No low-price gainers found at the moment. Try refreshing later.")

with tab4:
    st.markdown(f"## Detailed Analysis: {selected_coin}/{selected_market}")
    
    with st.spinner(f"Fetching detailed data for {selected_coin}..."):
        # Get detailed coin info from both exchanges
        binance_info = binance_fetcher.get_detailed_coin_info(selected_coin, selected_market)
        kraken_info = kraken_fetcher.get_detailed_coin_info(selected_coin, selected_market)
        
        if binance_info and 'stats' in binance_info:
            # Display basic stats
            binance_stats = binance_info['stats']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Current Price", 
                    f"${float(binance_stats.get('last_price', 0)):.6f}", 
                    f"{float(binance_stats.get('price_change_percent', 0)):.2f}%"
                )
            
            with col2:
                st.metric(
                    "24h High", 
                    f"${float(binance_stats.get('high_price', 0)):.6f}"
                )
            
            with col3:
                st.metric(
                    "24h Low", 
                    f"${float(binance_stats.get('low_price', 0)):.6f}"
                )
            
            col4, col5, col6 = st.columns(3)
            
            with col4:
                st.metric(
                    "24h Volume", 
                    f"{float(binance_stats.get('volume', 0)):.2f} {selected_coin}"
                )
            
            with col5:
                st.metric(
                    "24h Quote Volume", 
                    f"${float(binance_stats.get('quote_volume', 0)):.2f}"
                )
            
            with col6:
                st.metric(
                    "Trade Count", 
                    f"{int(binance_stats.get('count', 0))}"
                )
            
            # Create enhanced price charts
            st.markdown("### 📊 Price Charts & Analysis")
            
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                # Candlestick chart
                if 'open_price' in binance_stats and 'high_price' in binance_stats and 'low_price' in binance_stats and 'last_price' in binance_stats:
                    fig_candlestick = go.Figure(data=[go.Candlestick(
                        x=['Open', 'High', 'Low', 'Close'],
                        open=[float(binance_stats['open_price'])] * 4,
                        high=[float(binance_stats['high_price'])] * 4,
                        low=[float(binance_stats['low_price'])] * 4,
                        close=[float(binance_stats['last_price'])] * 4
                    )])
                    
                    fig_candlestick.update_layout(
                        title=f"{selected_coin}/{selected_market} 24h Price Range",
                        xaxis_title="Price Points",
                        yaxis_title="Price",
                        height=350
                    )
                    
                    st.plotly_chart(fig_candlestick, use_container_width=True)
            
            with col_chart2:
                # Volume analysis chart
                if 'volume' in binance_stats and 'quote_volume' in binance_stats:
                    fig_volume = go.Figure()
                    
                    # Volume bars
                    fig_volume.add_trace(go.Bar(
                        x=['Volume', 'Quote Volume'],
                        y=[float(binance_stats['volume']), float(binance_stats['quote_volume'])],
                        name='Volume',
                        marker_color=['#00E676', '#2196F3']
                    ))
                    
                    fig_volume.update_layout(
                        title=f"{selected_coin} Volume Analysis",
                        xaxis_title="Volume Type",
                        yaxis_title="Amount",
                        height=350
                    )
                    
                    st.plotly_chart(fig_volume, use_container_width=True)
            
            # Price comparison across exchanges
            st.markdown("### 🔄 Cross-Exchange Price Comparison")
            
            if kraken_info and 'stats' in kraken_info and kraken_info['stats']:
                kraken_stats = kraken_info['stats']
                
                # Create comparison chart
                fig_comparison = go.Figure()
                
                # Price comparison
                if 'last_price' in binance_stats and 'last_price' in kraken_stats:
                    fig_comparison.add_trace(go.Bar(
                        x=['Binance', 'Kraken'],
                        y=[float(binance_stats['last_price']), float(kraken_stats['last_price'])],
                        name='Current Price',
                        marker_color=['#2196F3', '#FF9800']
                    ))
                    
                    fig_comparison.update_layout(
                        title=f"{selected_coin}/{selected_market} Price Comparison",
                        xaxis_title="Exchange",
                        yaxis_title="Price (USDT)",
                        height=400
                    )
                    
                    st.plotly_chart(fig_comparison, use_container_width=True)
                
                # Price difference indicator
                if 'last_price' in binance_stats and 'last_price' in kraken_stats:
                    binance_price = float(binance_stats['last_price'])
                    kraken_price = float(kraken_stats['last_price'])
                    price_diff = ((binance_price - kraken_price) / min(binance_price, kraken_price)) * 100
                    
                    st.markdown(f"""
                    <div class="highlight">
                    <h4>Price Difference Analysis</h4>
                    <p><strong>Binance Price:</strong> ${binance_price:.6f}</p>
                    <p><strong>Kraken Price:</strong> ${kraken_price:.6f}</p>
                    <p><strong>Difference:</strong> <span style="color: {'#00E676' if abs(price_diff) < 1 else '#FF9800' if abs(price_diff) < 2 else '#FF1744'}">{price_diff:.3f}%</span></p>
                    <p><strong>Arbitrage Potential:</strong> {'🟢 Low' if abs(price_diff) < 1 else '🟡 Medium' if abs(price_diff) < 2 else '🔴 High'}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # LLM analysis
            st.markdown("### LLM Analysis")
            with st.spinner("Generating analysis..."):
                analysis = llm_analyzer.generate_coin_analysis(selected_coin, binance_info)
                st.markdown(f'<div class="card">{analysis}</div>', unsafe_allow_html=True)
            
            # Trade simulator results
            st.markdown("### Trade Simulator Results")
            with st.spinner("Calculating trade simulation..."):
                trade_result = arbitrage_calculator.calculate_trade_profit(
                    selected_coin, selected_market, trade_amount, buy_exchange, sell_exchange
                )
                
                if trade_result:
                    profit = trade_result.get('profit', 0)
                    profit_class = "profit" if profit > 0 else "loss"
                    
                    st.markdown(f"""
                    <div class="card">
                        <h4>Trade Simulation: {selected_coin}/{selected_market}</h4>
                        <p>Investment: ${trade_amount:.2f}</p>
                        <p>Buy on {buy_exchange} at ${trade_result.get('buy_price', 0):.6f}</p>
                        <p>Sell on {sell_exchange} at ${trade_result.get('sell_price', 0):.6f}</p>
                        <p>Crypto amount: {trade_result.get('crypto_amount', 0):.6f} {selected_coin}</p>
                        <p>Final amount: ${trade_result.get('final_amount', 0):.2f}</p>
                        <p>Profit: <span class="{profit_class}">${profit:.2f} (<span style="color: {'#00E676' if profit > 0 else '#FF1744'}">{trade_result.get('profit_percentage', 0):.2f}%</span>)</span></p>
                        <p>Recommendation: <span class="info">{
                            "Consider this trade" if profit > 0 else "Avoid this trade"
                        }</span></p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("Failed to calculate trade simulation.")
        else:
            st.error(f"Failed to fetch detailed information for {selected_coin}/{selected_market}.")

with tab5:
    st.markdown("## Advanced Analytics & Visualizations")
    
    # Market Overview Dashboard
    st.markdown("### 📊 Market Overview Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Total cryptocurrencies tracked
        total_cryptos = len(TOP_CRYPTOS)
        st.metric("Total Cryptos Tracked", total_cryptos)
    
    with col2:
        # Total markets
        total_markets = len(MARKETS)
        st.metric("Total Markets", total_markets)
    
    with col3:
        # Exchange status
        binance_status = "🟢 Active" if binance_fetcher.client else "🔴 Restricted"
        st.metric("Binance Status", binance_status)
    
    with col4:
        # Last update
        st.metric("Last Update", datetime.now().strftime("%H:%M:%S"))
    
    # Price Distribution Analysis
    st.markdown("### 📈 Price Distribution Analysis")
    
    try:
        # Get current prices for analysis
        binance_prices, kraken_prices = arbitrage_calculator.fetch_all_prices()
        
        if not binance_prices.empty and not kraken_prices.empty:
            # Merge data for analysis
            merged_prices = pd.merge(
                binance_prices, 
                kraken_prices, 
                on='Symbol', 
                suffixes=('_binance', '_kraken')
            )
            
            # Calculate price differences
            for market in MARKETS:
                if f'{market}_price_binance' in merged_prices.columns and f'{market}_price_kraken' in merged_prices.columns:
                    merged_prices[f'{market}_diff'] = (
                        (merged_prices[f'{market}_price_binance'] - merged_prices[f'{market}_price_kraken']).abs() / 
                        merged_prices[[f'{market}_price_binance', f'{market}_price_kraken']].min(axis=1) * 100
                    )
            
            # Create price distribution histogram
            if 'USDT_price_binance' in merged_prices.columns:
                fig_dist = go.Figure()
                
                # Binance price distribution
                fig_dist.add_trace(go.Histogram(
                    x=merged_prices['USDT_price_binance'].dropna(),
                    name='Binance Prices',
                    nbinsx=20,
                    opacity=0.7,
                    marker_color='#2196F3'
                ))
                
                # Kraken price distribution
                if 'USDT_price_kraken' in merged_prices.columns:
                    fig_dist.add_trace(go.Histogram(
                        x=merged_prices['USDT_price_kraken'].dropna(),
                        name='Kraken Prices',
                        nbinsx=20,
                        opacity=0.7,
                        marker_color='#FF9800'
                    ))
                
                fig_dist.update_layout(
                    title=f"Price Distribution - USDT Market",
                    xaxis_title="Price (USDT)",
                    yaxis_title="Frequency",
                    barmode='overlay',
                    height=400
                )
                
                st.plotly_chart(fig_dist, use_container_width=True)
            
            # Price difference heatmap
            st.markdown("### 🔥 Price Difference Heatmap")
            
            # Prepare data for heatmap
            heatmap_data = []
            symbols = []
            
            for market in MARKETS:
                if f'{market}_diff' in merged_prices.columns:
                    market_data = merged_prices[['Symbol', f'{market}_diff']].dropna()
                    if not market_data.empty:
                        heatmap_data.append(market_data[f'{market}_diff'].values)
                        symbols.extend(market_data['Symbol'].values)
            
            if heatmap_data:
                # Create heatmap
                fig_heatmap = go.Figure(data=go.Heatmap(
                    z=heatmap_data,
                    x=merged_prices['Symbol'].unique()[:len(heatmap_data[0])],
                    y=MARKETS[:len(heatmap_data)],
                    colorscale='RdYlGn_r',
                    zmid=0,
                    text=[[f"{val:.2f}%" for val in row] for row in heatmap_data],
                    texttemplate="%{text}",
                    textfont={"size": 10},
                    hoverongaps=False
                ))
                
                fig_heatmap.update_layout(
                    title="Price Difference Heatmap Across Exchanges & Markets",
                    xaxis_title="Cryptocurrency",
                    yaxis_title="Market",
                    height=500
                )
                
                st.plotly_chart(fig_heatmap, use_container_width=True)
            
            # Volatility Analysis
            st.markdown("### 📊 Volatility Analysis")
            
            # Calculate price volatility (standard deviation of price differences)
            volatility_data = []
            for market in MARKETS:
                if f'{market}_diff' in merged_prices.columns:
                    market_volatility = merged_prices[f'{market}_diff'].std()
                    volatility_data.append({
                        'Market': market,
                        'Volatility': market_volatility
                    })
            
            if volatility_data:
                volatility_df = pd.DataFrame(volatility_data)
                
                # Volatility bar chart
                fig_volatility = go.Figure(data=go.Bar(
                    x=volatility_df['Market'],
                    y=volatility_df['Volatility'],
                    marker_color='#9C27B0',
                    text=[f"{val:.2f}%" for val in volatility_df['Volatility']],
                    textposition='auto'
                ))
                
                fig_volatility.update_layout(
                    title="Market Volatility (Price Difference Standard Deviation)",
                    xaxis_title="Market",
                    yaxis_title="Volatility (%)",
                    height=400
                )
                
                st.plotly_chart(fig_volatility, use_container_width=True)
            
            # Top Opportunities Timeline
            st.markdown("### ⏰ Top Opportunities Timeline")
            
            # Simulate some historical data for demonstration
            import numpy as np
            
            # Generate sample timeline data
            dates = pd.date_range(start='2025-08-01', end='2025-08-16', freq='D')
            opportunities_data = []
            
            for date in dates:
                # Simulate daily best opportunity
                best_diff = np.random.uniform(0.5, 3.0)
                opportunities_data.append({
                    'Date': date,
                    'Best_Opportunity': best_diff,
                    'Symbol': np.random.choice(['BTC', 'ETH', 'ADA', 'DOT', 'LINK'])
                })
            
            opportunities_df = pd.DataFrame(opportunities_data)
            
            # Create timeline chart
            fig_timeline = go.Figure()
            
            fig_timeline.add_trace(go.Scatter(
                x=opportunities_df['Date'],
                y=opportunities_df['Best_Opportunity'],
                mode='lines+markers',
                name='Best Daily Opportunity',
                line=dict(color='#00E676', width=3),
                marker=dict(size=8, color='#00E676')
            ))
            
            fig_timeline.update_layout(
                title="Daily Best Arbitrage Opportunities (Simulated Data)",
                xaxis_title="Date",
                yaxis_title="Price Difference (%)",
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_timeline, use_container_width=True)
            
            # Market Correlation Matrix
            st.markdown("### 🔗 Market Correlation Analysis")
            
            # Calculate correlation between different markets
            correlation_data = []
            for i, market1 in enumerate(MARKETS):
                for j, market2 in enumerate(MARKETS):
                    if i < j:  # Avoid duplicate pairs
                        if f'{market1}_price_binance' in merged_prices.columns and f'{market2}_price_binance' in merged_prices.columns:
                            corr = merged_prices[f'{market1}_price_binance'].corr(merged_prices[f'{market2}_price_binance'])
                            correlation_data.append({
                                'Market1': market1,
                                'Market2': market2,
                                'Correlation': corr
                            })
            
            if correlation_data:
                corr_df = pd.DataFrame(correlation_data)
                
                # Create correlation heatmap
                fig_corr = go.Figure(data=go.Heatmap(
                    z=[[corr_df.loc[(corr_df['Market1'] == m1) & (corr_df['Market2'] == m2), 'Correlation'].iloc[0] 
                        if len(corr_df.loc[(corr_df['Market1'] == m1) & (corr_df['Market2'] == m2)]) > 0 else 0
                        for m2 in MARKETS] for m1 in MARKETS],
                    x=MARKETS,
                    y=MARKETS,
                    colorbar=dict(title="Correlation"),
                    colorscale='RdBu',
                    zmid=0,
                    text=[[f"{val:.3f}" if val != 0 else "" for val in row] for row in 
                          [[corr_df.loc[(corr_df['Market1'] == m1) & (corr_df['Market2'] == m2), 'Correlation'].iloc[0] 
                            if len(corr_df.loc[(corr_df['Market1'] == m1) & (corr_df['Market2'] == m2)]) > 0 else 0
                            for m2 in MARKETS] for m1 in MARKETS]],
                    texttemplate="%{text}",
                    textfont={"size": 12},
                    hoverongaps=False
                ))
                
                fig_corr.update_layout(
                    title="Market Price Correlation Matrix",
                    height=500
                )
                
                st.plotly_chart(fig_corr, use_container_width=True)
        
        else:
            st.warning("Unable to fetch price data for advanced analytics. Please check your API connections.")
            
    except Exception as e:
        st.error(f"Error generating advanced analytics: {str(e)}")
        st.info("This might be due to API rate limits or connection issues.")

# Footer
st.markdown("---")
st.markdown("CryptoGap+ | Advanced Crypto Arbitrage & Analysis Tool")
st.markdown(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")