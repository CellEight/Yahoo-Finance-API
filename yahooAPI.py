import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt

class YahooStock():
    def __init__(self):
        self.base_url='https://in.finance.yahoo.com/quote/'
        self.price_tag = "span"
        self.price_class = 'Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)'
        self.detail_tags = ['td','span']
        self.detail_classes = ['Ta(end) Fw(600) Lh(14px)','Trsdu(0.3s)']

    def getCurrentPrice(self, symb):
        """This method scrapes the current price of the specificed stock
         and returns it in the form of a float"""
        url = self.base_url+symb
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        raw = soup.find(self.price_tag, class_=self.price_class)
        price = float(raw.text)
        return price

    def getDetails(self, symb):
        """Gets all the stock meta-data specially:
        Price, Prev. Close, Open, Bid, Ask, Day's Range, 52-week range, Volume,
        Avg Volume, Market Cap, Beta, PE ratio, EPS, Earnings date,
        Forward Dividend & yield Ex-dividend date & 1y taget est
        These are currently given as raw strings, should create a new method for
        processing them into more usable formats.
        Details are returned as a list (may wish to convert this to an object)"""
        url = self.base_url+symb
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        table_elements = soup.find_all(self.detail_tags[0], class_=self.detail_classes[0])
        details_ls = []
        for item in table_elements:
            detail = item.find(self.detail_tags[1], class_=self.detail_classes[1])
            if detail != None:
                details_ls.append(detail.text)
            else:
                details_ls.append(item.text)
        details_ls.insert(0,self.getCurrentPrice(symb))
        return details_ls

    def getHistoricalData(self, symb):
        """Much to my suprise yahoo let you just download historical data without
        any kind of anti-scraping measures! This function grabs that data for a
        specificed timeframe and returns it in the form of a pands dataframe.
        Need to add facility to specify date range!"""
        url = f'https://query1.finance.yahoo.com/v7/finance/download/{symb}?period1=1283990400&period2=1604707200&interval=1d&events=history&includeAdjustedClose=true'
        raw = str(requests.get(url).content)[2:-1]
        data = [row.split(',') for row in raw.split('\\n')]
        df = pd.DataFrame(data[1:],columns=data[0])
        # Correct datatypes
        df['Date'] = pd.to_datetime(df['Date'], yearfirst=True)
        df[['Open','High','Low','Close','Adj Close']] = df[['Open','High','Low','Close','Adj Close']].astype(dtype=float)
        df.Volume = df.Volume.astype(dtype=int)
        return df

    def plotStock(self,symb, props):
        """This function lets one plot any subset of the fields returned by the
        getHistoricalData function. props can be a string or a list of strings"""
        data = self.getHistoricalData(symb)
        if type(props) == str:
            data = data[['Date',props]]
        else:
            data = data[['Date',*props]]
        data.plot(x='Date')
        plt.show()

if __name__ == "__main__":
    #Just example code to illustrate how the API can be used
    stock = YahooStock()
    # Get current price
    price = stock.getPrice('AMD')
    print(price)
    # Get Stock price and meta data
    meta_data = stock.getDetails('AMD')
    print(meta_data)
    # Get historical Data
    data = stock.getHistoricalData('AMD')
    print(data)
    # Plot historical data (Note function overloading)
    stock.plotStock('AMD',['Open','Close'])
    stock.plotStock('AMD','Volume')
