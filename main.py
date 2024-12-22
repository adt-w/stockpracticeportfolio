import os
import json

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import Scrollbar, messagebox

import requests
from yahooquery import Ticker
from yahooquery import Screener

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from datetime import datetime
from millify import millify

portfolio_balance = 0.0
opening_balance = 0.0
portfolio = []
portfolio_name = ""


def get_most_traded_stocks(top):
    if top == 0:
        top = 100

    s = Screener()
    data = s.get_screeners('most_actives', count=top)
    symbols = []
    for item in data['most_actives']['quotes']:
        symbols.append(item['symbol'])
    return symbols


def get_ticker(company_name):
    url = "https://query2.finance.yahoo.com/v1/finance/search"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    params = {"q": company_name, "quotes_count": 1, "country": "United States"}

    res = requests.get(url=url, params=params, headers={'User-Agent': user_agent})
    data = res.json()

    if len(data['quotes']) > 0:
        company_code = data['quotes'][0]['symbol']
    else:
        company_code = ""
    return company_code


def get_stock_info():
    clear_right_frame()
    company_name_label = tk.Label(right_frame, text="Enter Company Name:", bg='white')
    company_name_label.pack()
    company_name_entry = tk.Entry(right_frame)
    company_name_entry.pack()
    confirm_button = tk.Button(right_frame, text="Get Info",
                               command=lambda: fetch_stock_info(company_name_entry.get(), ""))
    confirm_button.pack()


def millify_float(n):
    if n != 'N/A':
        n = millify(n)
    return n


# gets information about a stock using either company name or symbol
def fetch_stock_info(company_name, symbol):
    clear_right_frame()
    try:
        if symbol == "":
            # get symbol from company name first
            symbol = get_ticker(company_name)
        if symbol != "":
            stock = Ticker(symbol)
            summary = stock.summary_detail[symbol]
            info = stock.financial_data[symbol]
            esg_score = stock.esg_scores[symbol]

            esg = 0
            esgPerformance = 0
            if isinstance(esg_score, str):
                esg = 'N/A'
                esgPerformance = 'N/A'
            else:
                esg = esg_score.get('totalEsg')
                esgPerformance = esg_score.get('esgPerformance', 'N/A')

            stock_info = {
                "Symbol": symbol,
                "Day Low": summary.get('dayLow', 'N/A'),
                "Day High": summary.get('dayHigh', 'N/A'),
                "Volume": millify_float(summary.get('volume', 'N/A')),
                "Bid Price": summary.get('bid', 'N/A'),
                "Ask Price": summary.get('ask', 'N/A'),
                "P/E Ratio": summary.get('trailingPE', 'N/A'),
                "Market Cap": millify_float(summary.get('marketCap', 'N/A')),
                "Total Cash": millify_float(info.get('totalCash', 'N/A')),
                "Total Debt": millify(info.get('totalDebt', 'N/A')),
                "Total Revenue": millify_float(info.get('totalRevenue', 'N/A')),
                "Profit Margin": info.get('profitMargins', 'N/A'),
                "Earnings Growth": info.get('earningsGrowth', 'N/A'),
                "Debt to Equity": info.get('debtToEquity', 'N/A'),
                "Return on Equity": info.get('returnOnEquity', 'N/A'),
                "totalEsg": esg,
                "esgPerformance": esgPerformance,
            }

            plot_price_history(symbol)

            tk.Label(right_frame, text=f"{'Symbol'}: {stock_info['Symbol']}", bg='white').pack(pady=1)

            info_frame = tk.Frame(right_frame)
            info_frame.pack(fill="x", expand=True, padx=100)
            info_frame.columnconfigure(0, weight=1)
            info_frame.columnconfigure(1, weight=1)
            info_frame.columnconfigure(2, weight=1)
            info_frame.columnconfigure(3, weight=1)

            tk.Label(info_frame, text=f"{'Market Cap'}: {stock_info['Market Cap']}").grid(row=0, column=0, padx=5,
                                                                                          pady=1, sticky='w')
            tk.Label(info_frame, text=f"{'Volume'}: {stock_info['Volume']}").grid(row=0, column=3, padx=5, pady=1,
                                                                                  sticky='e')

            tk.Label(info_frame, text=f"{'totalEsg'}: {stock_info['totalEsg']}").grid(row=1, column=0, padx=5, pady=1,
                                                                                      sticky='w')
            tk.Label(info_frame, text=f"{'esgPerformance'}: {stock_info['esgPerformance']}").grid(row=1, column=3,
                                                                                                  padx=5, pady=1,
                                                                                                  sticky='e')

            tk.Label(info_frame, text=f"{'P/E Ratio'}: {stock_info['P/E Ratio']}").grid(row=2, column=0, padx=5, pady=1,
                                                                                        sticky='w')
            tk.Label(info_frame, text=f"{'Total Cash'}: {stock_info['Total Cash']}").grid(row=2, column=1, padx=5,
                                                                                          pady=1, sticky='e')
            tk.Label(info_frame, text=f"{'Total Debt'}: {stock_info['Total Debt']}").grid(row=2, column=2, padx=5,
                                                                                          pady=1, sticky='w')
            tk.Label(info_frame, text=f"{'Total Revenue'}: {stock_info['Total Cash']}").grid(row=2, column=3, padx=5,
                                                                                             pady=1, sticky='e')

            tk.Label(info_frame, text=f"{'Profit Margin'}: {stock_info['Profit Margin']}").grid(row=3, column=0, padx=5,
                                                                                                pady=1, sticky='w')
            tk.Label(info_frame, text=f"{'Earnings Growth'}: {stock_info['Earnings Growth']}").grid(row=3, column=1,
                                                                                                    padx=5, pady=1,
                                                                                                    sticky='e')
            tk.Label(info_frame, text=f"{'Debt to Equity'}: {stock_info['Debt to Equity']}").grid(row=3, column=2,
                                                                                                  padx=5, pady=1,
                                                                                                  sticky='w')
            tk.Label(info_frame, text=f"{'Return on Equity'}: {stock_info['Return on Equity']}").grid(row=3, column=3,
                                                                                                      padx=5, pady=1,
                                                                                                      sticky='e')

            tk.Label(info_frame, text=f"{'Day Low'}: {stock_info['Day Low']}").grid(row=4, column=0, padx=5, pady=1,
                                                                                    sticky='w')
            tk.Label(info_frame, text=f"{'Day High'}: {stock_info['Day High']}").grid(row=4, column=1, padx=5, pady=1,
                                                                                      sticky='e')
            tk.Label(info_frame, text=f"{'Bid Price'}: {stock_info['Bid Price']}").grid(row=4, column=2, padx=5, pady=1,
                                                                                        sticky='w')
            tk.Label(info_frame, text=f"{'Ask Price'}: {stock_info['Ask Price']}").grid(row=4, column=3, padx=5, pady=1,
                                                                                        sticky='e')

            tk.Label(right_frame, text="Quantity:", bg='white').pack(pady=1)
            quantity_entry = tk.Entry(right_frame)
            quantity_entry.pack()

            btn_frame = tk.Frame(right_frame)
            btn_frame.pack(fill="x", expand=True, padx=200)
            btn_frame.columnconfigure(0, weight=1)
            btn_frame.columnconfigure(1, weight=1)

            tk.Button(btn_frame, text="Buy Stock",
                      command=lambda: buy_stock(symbol, summary.get('ask', 0), quantity_entry.get())).grid(row=0,
                                                                                                           column=0,
                                                                                                           padx=5,
                                                                                                           pady=1,
                                                                                                           sticky='w')
            tk.Button(btn_frame, text="Sell Stock",
                      command=lambda: sell_stock(symbol, summary.get('bid', 0), quantity_entry.get())).grid(row=0,
                                                                                                            column=1,
                                                                                                            padx=5,
                                                                                                            pady=1,
                                                                                                            sticky='e')


        else:
            tk.Label(right_frame, text="No results found. Please check the company name and try again.", bg='white',
                     fg='red').pack(fill=tk.BOTH, padx=10, pady=10)
    except Exception as e:
        print(e)
        tk.Label(right_frame, text="Error fetching stock information. Please check the company name and try again.",
                 bg='white', fg='red').pack(fill=tk.BOTH, padx=10, pady=10)


def plot_price_history(symbol):
    stock = Ticker(symbol)
    hist = stock.history(period='1y')

    if not hist.empty:
        fig, ax = plt.subplots(figsize=(4, 3))
        hist['close'].plot(ax=ax)

        # use smaller font sizes
        ax.set_title(f'{symbol} Price History', fontsize=10)
        ax.set_xlabel('Date', fontsize=8)
        ax.set_ylabel('Closing Price', fontsize=8)
        ax.tick_params(axis='both', which='major', labelsize=6)
        ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=right_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", expand=True)
    else:
        tk.Label(right_frame, text="No historical data available for this stock.", fg='red').pack(fill=tk.BOTH, padx=10,
                                                                                                  pady=10)


def get_float_value(input, name):
    if input == "":
        return ""
    try:
        return float(input)
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numerical value for " + name)


def get_int_value(input, name):
    if input == "":
        return 0
    try:
        return int(input)
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numerical value for " + name)

    # UI for searching stocks


def search_stocks():
    clear_right_frame()
    criteria_frame = tk.Frame(right_frame, bg='white')
    criteria_frame.pack(fill='x', padx=10, pady=10)

    tk.Label(criteria_frame, text="Top Actively Traded Stocks (default top 100): ", bg='white').grid(row=0, column=0,
                                                                                                     padx=5, pady=5,
                                                                                                     sticky='e')
    top_active_entry = tk.Entry(criteria_frame)
    top_active_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')

    tk.Label(criteria_frame, text="P/E Ratio (Max):", bg='white').grid(row=1, column=0, padx=5, pady=5, sticky='e')
    pe_entry = tk.Entry(criteria_frame)
    pe_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')

    tk.Label(criteria_frame, text="Revenue Per Share (Min):", bg='white').grid(row=2, column=0, padx=5, pady=5,
                                                                               sticky='e')
    rps_entry = tk.Entry(criteria_frame)
    rps_entry.grid(row=2, column=1, padx=5, pady=5, sticky='w')

    tk.Label(criteria_frame, text="Profit Margins (Min):", bg='white').grid(row=3, column=0, padx=5, pady=5, sticky='e')
    pm_entry = tk.Entry(criteria_frame)
    pm_entry.grid(row=3, column=1, padx=5, pady=5, sticky='w')

    tk.Label(criteria_frame, text="Earnings Growth (Min):", bg='white').grid(row=4, column=0, padx=5, pady=5,
                                                                             sticky='e')
    eg_entry = tk.Entry(criteria_frame)
    eg_entry.grid(row=4, column=1, padx=5, pady=5, sticky='w')

    tk.Label(criteria_frame, text="total ESG score (Min):", bg='white').grid(row=5, column=0, padx=5, pady=5,
                                                                             sticky='e')
    esg_entry = tk.Entry(criteria_frame)
    esg_entry.grid(row=5, column=1, padx=5, pady=5, sticky='w')

    tk.Button(criteria_frame, text="Filter Stocks", command=lambda:
    show_filtered_stocks(get_int_value(top_active_entry.get(), "Top Actively Traded Stocks"),
                         get_float_value(pe_entry.get(), "P/E ratio"),
                         get_float_value(rps_entry.get(), "Revenue per Share"),
                         get_float_value(pm_entry.get(), "Profit Margin"),
                         get_float_value(eg_entry.get(), "Earnings Growth"),
                         get_float_value(esg_entry.get(), "ESG"))).grid(row=6, column=0, columnspan=2, pady=10)


def show_filtered_stocks(top, pe, rps, pm, eg, esg):
    filtered_stocks = filter_stocks(top, pe, rps, pm, eg, esg)
    pe_msg = '= any'
    if pe != "":
        pe_msg = f"<={pe}"
    top_msg = 100
    if top != 0:
        top_msg = f"{top}"
    rps_msg = "= any"
    if rps != "":
        rps_msg = f">={rps}"
    pm_msg = "= any"
    if pm != "":
        pm_msg = f">={pm}"
    eg_msg = "= any"
    if eg != "":
        eg_msg = f">={eg}"
    esg_msg = "= any"
    if esg != "":
        esg_msg = f">={eg}"
    msg = f"Looking at top {top_msg} actively traded stocks, with P/E {pe_msg}, Revenue per share {rps_msg}, Profit Margin {pm_msg}, Earnings growth {eg_msg}, ESG {esg_msg}"
    display_filtered_stocks(msg, filtered_stocks)


def filter_stocks(top, pe_input, rps_input, pm_input, eg_input, esg_input):
    # first get a list of stocks to start with
    # here we start with most traded stocks (using a screener)
    tickers = get_most_traded_stocks(top)

    # then we get data for all those and filter based on user inputs to narrow down the stocks
    stock_data = Ticker(tickers)

    summary_details = stock_data.summary_detail
    financial_data = stock_data.financial_data
    esg_score = stock_data.esg_scores

    filtered_stocks = []
    index = 0
    for symbol in tickers:
        try:
            if isinstance(financial_data[symbol], str):
                index = index + 1
                filtered_stocks.append((index, symbol, pe, rps, pm, eg))
                continue

            pe = summary_details[symbol].get('trailingPE')
            rps = financial_data[symbol].get('revenuePerShare')
            pm = financial_data[symbol].get('profitMargins')
            eg = financial_data[symbol].get('earningsGrowth')

            try:
                if isinstance(esg_score[symbol], str):
                    esg = ''
                else:
                    esg = esg_score[symbol].get('totalEsg', '')
            except Exception as e:
                esg = ''

            matched = 0
            if pe_input == "":
                matched = 1
            elif pe is not None and pe <= pe_input:
                matched = 1

            if rps_input == "":
                matched = matched + 1
            elif rps is not None and rps >= rps_input:
                matched = matched + 1

            if pm_input == "":
                matched = matched + 1
            elif pm is not None and pm >= pm_input:
                matched = matched + 1

            if eg_input == "":
                matched = matched + 1
            elif eg is not None and eg >= eg_input:
                matched = matched + 1

            if esg_input == "":
                matched = matched + 1
            elif esg is not None and esg >= esg_input:
                matched = matched + 1

            if matched == 5:
                index = index + 1
                filtered_stocks.append((index, symbol, pe, rps, pm, eg, esg))
        except Exception as e:
            print(e)
            continue
    return filtered_stocks


def on_click_stock_table(event):
    selected_item = stock_table.focus()  # Get the selected item
    item = stock_table.item(selected_item)  # Get item details
    stock_symbol = item['values'][1]
    fetch_stock_info("", stock_symbol)


# displays the results from the search
def display_filtered_stocks(msg, filtered_stocks):
    global stock_table
    clear_right_frame()
    if not filtered_stocks:
        tk.Label(right_frame, text="No stocks found with the specified criteria.").pack(fill=tk.BOTH, padx=10, pady=10)
        return

    tk.Label(right_frame, text=msg).pack(fill=tk.BOTH, padx=10, pady=10)

    tree_frame = tk.Frame(right_frame)
    tree_frame.pack(fill=tk.BOTH, expand=True)

    columns = ("#0", "Symbol", "P/E Ratio", "Revenue per Share", "Profit Margin", "Earnings Growth", "ESG")
    stock_table = ttk.Treeview(tree_frame, columns=columns, show='headings')

    stock_table.heading("#0", text="Index")
    for col in columns:
        if col != "#0":
            stock_table.heading(col, text=col)

    column_width_percentages = {
        "#0": 5,
        "Symbol": 10,
        "P/E Ratio": 15,
        "Revenue per Share": 20,
        "Profit Margin": 20,
        "Earnings Growth": 20,
        "ESG": 10
    }

    stock_table.bind('<Configure>', lambda event: [
        stock_table.column(col, width=int(stock_table.winfo_width() * perc / 100), anchor='center')
        for col, perc in column_width_percentages.items()
    ])
    for stock in filtered_stocks:
        stock_table.insert("", "end", values=stock)

    stock_table.bind("<ButtonRelease-1>", on_click_stock_table)

    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=stock_table.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    stock_table.configure(yscrollcommand=scrollbar.set)

    stock_table.pack(fill="both", expand=True)


def on_click_summary_table(event):
    selected_item = portfolio_summary_table.focus()  # Get the selected item
    item = portfolio_summary_table.item(selected_item)  # Get item details
    stock_symbol = item['values'][0]
    fetch_stock_info("", stock_symbol)


def show_portfolio_summary():
    global portfolio_summary_table
    clear_right_frame()
    tree_frame = tk.Frame(right_frame)
    tree_frame.pack(fill=tk.BOTH, expand=True)

    portfolio_summary_table = ttk.Treeview(tree_frame, columns=(
    "Symbol", "Quantity", "Price", "Current Price", "Profit/Loss", "Date"))
    portfolio_summary_table.heading("#0", text="Index")
    portfolio_summary_table.heading("Symbol", text="Symbol")
    portfolio_summary_table.heading("Quantity", text="Quantity")
    portfolio_summary_table.heading("Price", text="Price")
    portfolio_summary_table.heading("Current Price", text="Current Price")
    portfolio_summary_table.heading("Profit/Loss", text="Profit/Loss")
    portfolio_summary_table.heading("Date", text="Date")

    # use specific widths for columns
    column_width_percentages = {
        "#0": 5,
        "Symbol": 10,
        "Quantity": 10,
        "Price": 15,
        "Current Price": 20,
        "Profit/Loss": 20,
        "Date": 20
    }

    portfolio_summary_table.bind('<Configure>', lambda event: [
        portfolio_summary_table.column(col, width=int(portfolio_summary_table.winfo_width() * perc / 100),
                                       anchor='center')
        for col, perc in column_width_percentages.items()
    ])

    portfolio_summary_table.bind("<ButtonRelease-1>", on_click_summary_table)

    scrollbar = Scrollbar(tree_frame, orient=tk.VERTICAL, command=portfolio_summary_table.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    portfolio_summary_table.config(yscrollcommand=scrollbar.set)

    total_profit_loss = 0
    for index, stock in enumerate(portfolio, start=1):
        symbol = stock["symbol"]
        quantity = stock["quantity"]
        bought_price = stock["price"]
        book_value = quantity * bought_price

        current_price = Ticker(symbol).price[symbol]['regularMarketPrice']
        current_value = current_price * quantity
        profit_loss = current_value - book_value
        total_profit_loss += profit_loss

        formatted_profitloss = f"{profit_loss:.2f}"
        portfolio_summary_table.insert("", "end", text=str(index), values=(
        symbol, quantity, stock["price"], current_price, formatted_profitloss, stock["date"]))

    portfolio_summary_table.pack(fill="both", expand=True)

    total_formatted_profitloss = f"{total_profit_loss:.2f}"
    total_label = tk.Label(right_frame, text=f"Total Profit/Loss: {total_formatted_profitloss}")
    total_label.pack(pady=10)


def go_back_home():
    clear_left_frame()
    clear_right_frame()
    initialize_home_screen()


def update_right_frame(message):
    clear_right_frame()
    tk.Label(right_frame, text=message, bg='white').pack(fill=tk.BOTH, padx=10, pady=10)


def update_footer(message):
    clear_footer()
    tk.Label(footer, text=message).pack(fill=tk.BOTH, padx=10, pady=10)


def clear_footer():
    for widget in footer.winfo_children():
        widget.destroy()


def clear_right_frame():
    for widget in right_frame.winfo_children():
        widget.destroy()


def clear_left_frame():
    for widget in left_frame.winfo_children():
        widget.destroy()


def initialize_home_screen():
    option_buttons = [
        ("Create Portfolio", create_portfolio),
        ("Load Saved Portfolio", load_portfolio)
    ]

    for text, command in option_buttons:
        tk.Button(left_frame, text=text, command=command).pack(fill=tk.BOTH, padx=5, pady=5)


def create_portfolio():
    global portfolio_name
    clear_right_frame()
    name_label = tk.Label(right_frame, text="Enter Portfolio Name:", bg='white')
    name_label.pack()
    name_entry = tk.Entry(right_frame)
    name_entry.pack()
    balance_label = tk.Label(right_frame, text="Enter Opening Balance:", bg='white').pack()
    balance_entry = tk.Entry(right_frame)
    balance_entry.pack()
    confirm_button = tk.Button(right_frame, text="Confirm",
                               command=lambda: confirm_portfolio(name_entry.get(), balance_entry.get()))
    confirm_button.pack()


def confirm_portfolio(name, balance):
    global portfolio_balance, portfolio, opening_balance, portfolio_name
    portfolio_name = name
    portfolio_balance = float(balance)
    opening_balance = float(balance)
    portfolio = []
    clear_right_frame()
    tk.Label(right_frame, text=f"Portfolio '{name}' created with opening balance {balance}", bg='white').pack(
        fill=tk.BOTH, padx=10, pady=10)
    update_footer(
        f"Portfolio '{portfolio_name}',  Opening balance {opening_balance}, Remaining balance {portfolio_balance} ")
    show_main_content()
    save_portfolio_to_file()


def load_portfolio():
    clear_right_frame()
    tk.Label(right_frame, text="Select Portfolio to Load:", bg='white').pack(fill=tk.BOTH, padx=10, pady=5)

    portfolio_files = []
    for f in os.listdir():
        if f.endswith('_portfolio.json'):
            portfolio_files.append(f)

    if portfolio_files:
        listbox = tk.Listbox(right_frame)
        for file in portfolio_files:
            listbox.insert(tk.END, file)
        listbox.pack(pady=5)

        def on_select(event):
            selected_file = listbox.get(listbox.curselection())
            load_portfolio_from_file(selected_file)

        listbox.bind('<<ListboxSelect>>', on_select)
    else:
        tk.Label(right_frame, text="No saved portfolios found.").pack(fill=tk.BOTH, padx=10, pady=10)


def save_portfolio_to_file():
    global portfolio_name, portfolio, portfolio_balance, opening_balance
    filename = f"{portfolio_name}_portfolio.json"
    with open(filename, 'w') as file:
        data = {
            "portfolio_name": portfolio_name,
            "portfolio": portfolio,
            # "portfolio_balance": portfolio_balance,
            "opening_balance": opening_balance
        }
        json.dump(data, file)


def calculate_balance(portfolio, opening_balance):
    total_spent = 0
    for stock in portfolio:
        total_spent += stock['quantity'] * stock['price']
    remaining_balance = opening_balance - total_spent
    return remaining_balance


def load_portfolio_from_file(filename):
    global portfolio_name, portfolio, portfolio_balance, opening_balance
    update_footer(f"Loading '{filename}'... ")
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            portfolio_name = data['portfolio_name']
            portfolio = data['portfolio']
            # portfolio_balance = data['portfolio_balance']
            opening_balance = data['opening_balance']
            portfolio_balance = calculate_balance(portfolio, opening_balance)
            formatted_portfolio_balance = f"{portfolio_balance:.2f}"
            update_footer(
                f"Portfolio '{portfolio_name}', Opening balance {opening_balance}, Remaining balance {formatted_portfolio_balance} ")
            show_main_content()
            show_portfolio_summary()
    except FileNotFoundError:
        update_right_frame("No saved portfolio found")
    except Exception as e:
        update_right_frame(f"Error loading portfolio: {e}")


def show_main_content():
    clear_left_frame()
    option_buttons = [
        ("Get Stock Information", get_stock_info),
        ("Portfolio Summary", show_portfolio_summary),
        ("Search Stocks", search_stocks),
        ("Go Back to Home Screen", go_back_home)
    ]

    for text, command in option_buttons:
        tk.Button(left_frame, text=text, command=command).pack(fill=tk.BOTH, padx=5, pady=5)


def buy_stock(symbol, ask_price, quantity):
    global portfolio_balance
    try:
        quantity = int(quantity)
        ask_price = float(ask_price)
        total_cost = ask_price * quantity
        if total_cost <= portfolio_balance:
            portfolio_balance -= total_cost
            book_value = ask_price * quantity
            portfolio.append({
                "symbol": symbol,
                "quantity": quantity,
                "price": ask_price,
                "book_value": book_value,
                "date": datetime.now().strftime('%Y-%m-%d')
            })
            update_right_frame(f"Bought {quantity} of {symbol} at {ask_price}. New balance: {portfolio_balance}")
            update_footer(f"Portfolio '{portfolio_name}',  Remaining balance {portfolio_balance} ")
            save_portfolio_to_file()
        else:
            update_right_frame(f"Insufficient funds to buy {quantity} of {symbol} at {ask_price}")
    except ValueError:
        update_right_frame("Invalid quantity entered")


def sell_stock(symbol, bid_price, quantity):
    global portfolio_balance
    try:
        quantity = int(quantity)
        bid_price = float(bid_price)
        total_income = bid_price * quantity
        portfolio_balance += total_income

        for stock in portfolio:
            if stock["symbol"] == symbol:
                if stock["quantity"] >= quantity:
                    stock["quantity"] -= quantity
                    if stock["quantity"] == 0:
                        portfolio.remove(stock)
                    update_right_frame(f"Sold {quantity} of {symbol} at {bid_price}. New balance: {portfolio_balance}")
                    update_footer(f"Portfolio '{portfolio_name}',  Remaining balance {portfolio_balance} ")
                    save_portfolio_to_file()
                else:
                    update_right_frame(f"Not enough quantity to sell. You have {stock['quantity']} of {symbol}")
                break
        else:
            update_right_frame(f"You don't own any shares of {symbol}")
    except ValueError:
        update_right_frame("Invalid quantity entered")


root = tk.Tk()
root.geometry('1000x700')
root.title("Practice Portfolio")

# application has header, content and footer frames
# content frame has left frame for buttons, right frame for displaying informatio
header = tk.Frame(root, bg='gray', height=5)
header.pack(fill="x")
content = tk.Frame(root, bg='white')
content.pack(fill="both", expand=True)

left_frame = tk.Frame(content)
left_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
content.columnconfigure(0, weight=1)  # Column 0 takes 20% of width
content.rowconfigure(0, weight=1)  # Row 0 takes 100% of height

right_frame = tk.Frame(content, bg='white')
right_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
content.columnconfigure(1, weight=4)  # Column 1 takes 80% of width
content.rowconfigure(0, weight=1)  # Row 0 takes 100% of height

footer = tk.Frame(root, height=50)
footer.pack(fill="x")

initialize_home_screen()

root.mainloop()
