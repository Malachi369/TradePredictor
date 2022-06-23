from keys import ameritrade
import requests
import time
from statistics import mean, stdev
import matplotlib.pyplot as plt

Stock = "SPY"
TIME_PERIOD = 20
THRESHOLD = 0.3
# THRESHOLD = 0.1
PORTION = 0.5
endDate = "1654308000000" #US/Eastern Time: 2022-06-03 22:00:00
# endDate = "1654912800000" #US/Eastern Time: 2022-06-10 22:00:00

position = {
    "amount": 100,
    "average_cost": 400,
    "earning": 0
}

payload = {
    "apikey": ameritrade,
    "periodType": "day",
    "period": "5",
    "frequencyType": "minute",
    "frequency": "1",
    "endDate": endDate
}

url = "https://api.tdameritrade.com/v1/marketdata/{}/pricehistory".format(Stock)
results = requests.get(url, params=payload)
price, bup_price, bdown_price = [], [], []
position_amount = []

# function to calculate bollinger bands
def get_BBands(prices, time_period):

    prices = prices[-time_period:]
    ma = mean(prices)
    std = stdev(prices)
    bup = ma + 2*std # THRESHOLD可以加到这里
    bdown = ma - 2*std
    return bup, bdown

# place order
def place_order(bup, bdown, cur_price):
    if cur_price + THRESHOLD > bup:
        # place selling order
        selling_amount = position["amount"]*PORTION
        if selling_amount < 0.1:
            print("cannot sell stock at amount less than 0.1")
            return
        position["earning"] += selling_amount*(cur_price-position["average_cost"])
        position["amount"] = position["amount"]*(1-PORTION)
        print("Sell {} amount of {} at ${}".format(str(selling_amount), Stock, str(cur_price)))
        print(position["earning"])
    if cur_price - THRESHOLD < bdown:
        # place buying order
        buying_amount = position["amount"] * PORTION
        total_value = buying_amount * cur_price + position["amount"] * position["average_cost"]
        position["amount"] = position["amount"] * (1 + PORTION)
        position["average_cost"] = total_value / position["amount"]
        print("Buy {} amount of {} at ${}".format(str(buying_amount), Stock, str(cur_price)))

def main():
    for candle in results.json()["candles"]:
        cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(candle["datetime"])/1000.0))
        cur_price = (candle["low"] + candle["high"]) / 2
        price.append(cur_price)

        if len(price) >= TIME_PERIOD:
            period_price = price[-TIME_PERIOD:]
            bup, bdown = get_BBands(period_price, TIME_PERIOD)
            bup_price.append(bup)
            bdown_price.append(bdown)
            place_order(bup, bdown, cur_price)
        else:
            bup_price.append(cur_price)
            bdown_price.append(cur_price)
        position_amount.append(position["amount"])
    print(position)

    plt.plot(price, '-.')
    plt.plot(bup_price, '-g.')
    plt.plot(bdown_price, '-r.')
    # plt.plot(position_amount, '-b.')
    plt.show()


# print to log
import sys
old_stdout = sys.stdout
log_file = open("message.txt","w")
sys.stdout = log_file

main()

sys.stdout = old_stdout
log_file.close()
