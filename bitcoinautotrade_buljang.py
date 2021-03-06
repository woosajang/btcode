import time

import numpy as np
import pyupbit
import datetime

access = ""
secret = ""


def get_boonbong(ticker):
    df_min = pyupbit.get_ohlcv(ticker, interval='minute3', count=150)
    volume = df_min.iloc[-2, 4]
    close = df_min.iloc[-2, 3]
    open = df_min.iloc[-2, 0]
    volume_pre = df_min.iloc[-3, 4]
    close_pre = df_min.iloc[-3, 3]
    open_pre = df_min.iloc[-3, 0]
    volume_all = df_min.iloc[:, 4]
    volume_list = volume_all.to_list()
    avg_vol = np.average(volume_list)
    # print(ticker,volume, close, open,avg_vol)
    return volume, close, open, volume_pre, close_pre, open_pre, avg_vol


def get_target_price(ticker):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = (df.iloc[0]['high'] - df.iloc[0]['low'])
    last_price = df.iloc[0]['close']
    open_price = df.iloc[0]['open']
    return target_price, last_price, open_price


def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time


def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0


def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]


# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

coin_list = ["KRW-BTC", "KRW-XEC", "KRW-KNC", "KRW-AERGO", "KRW-GLM", "KRW-WAVES",
             "KRW-SAND", "KRW-CHZ", "KRW-ATOM", "KRW-ICX", "KRW-OMG", "KRW-SBD",
             "KRW-AXS", "KRW-PLA", "KRW-ETC","KRW-AAVE","KRW-NEAR","KRW-MLK" ,
             "KRW-HUM", "KRW-ELF", "KRW-POWR", "KRW-AQT", "KRW-SOL"]  # 8
k_list = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5,  0.5,
          0.5, 0.5,0.5]
rate_list = [0.6995, 0.2995, 0.2995, 0.2995, 0.2995, 0.2995, 0.2995, 0.2995, 0.2995, 0.2995,
             0.2995, 0.2995, 0.2995,0.2995, 0.2995, 0.2995, 0.2995, 0.2995, 0.2995, 0.2995,
             0.2995,0.2995,0.2995 ]
i_list = []
ik_list = []
i_list_short = []
ik_list_short = []
bbk = []
time_short = []
long = 0
bbk_short = []

krw = get_balance("KRW")
krw_buy = get_balance("KRW")

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=1800):
            # 대형주

            for c in range(0, len(coin_list)):
                target_price_orgin, last_price, open_price = get_target_price(coin_list[c])
                target_price = target_price_orgin * k_list[c] + last_price
                current_price = get_current_price(coin_list[c])
                max_price = target_price_orgin + last_price
                target_price_short = target_price_orgin * 0.2 + last_price
                time.sleep(0.1)
                volume, close, open, volume_pre, close_pre, open_pre, avg_vol = get_boonbong(coin_list[c])
                if target_price < current_price and coin_list[c] not in i_list:
                    bbk.append(coin_list[c])

                # print(coin_list[c], target_price, current_price)
                if target_price < current_price and coin_list[c] not in i_list and coin_list[
                    c] not in i_list_short and krw_buy > 5000 \
                        and bbk.count(
                    coin_list[c]) > 2000 and current_price < max_price and last_price / open_price < 1.1 and long == 1:
                    if krw_buy < krw * 0.30:
                        oder_krw = krw_buy * 0.9995
                    else:
                        oder_krw = krw * rate_list[c]
                    if coin_list[c] == "KRW-BTC" and krw_buy < krw * 0.70:
                        oder_krw = krw_buy * 0.9995
                    upbit.buy_market_order(coin_list[c], oder_krw)
                    print(f"{coin_list[c]} 매수합니다")
                    time.sleep(10)
                    krw_buy = get_balance("KRW")
                    i_list.append(coin_list[c])
                    ik_list.append(current_price)

                elif volume > avg_vol * 2 and avg_vol * 1.7 < volume_pre < volume and close - open > 0 and close_pre - open_pre > 0\
                        and close < current_price and coin_list[c] not in i_list and coin_list[
                    c] not in i_list_short and krw_buy > 5000 \
                        and last_price / open_price < 1.1 and current_price < max_price:
                    if krw_buy < krw * 0.30:
                        oder_krw = krw_buy * 0.9995
                    else:
                        oder_krw = krw_buy * 0.2995
                    upbit.buy_market_order(coin_list[c], oder_krw)
                    print(f"{coin_list[c]} 단타 매수합니다")
                    time.sleep(10)
                    krw_buy = get_balance("KRW")
                    i_list_short.append(coin_list[c])
                    ik_list_short.append(current_price)
                    now_short = datetime.datetime.now()
                    time_short.append(now_short)

            # 조기 매도

            for s in range(0, len(i_list)):
                target_price_sell = ik_list[s]
                current_price_sell = get_current_price(i_list[s])
                coin = get_balance(i_list[s][4:])
                now_cell = datetime.datetime.now()
                if i_list[s] == "KRW-BTC":
                    profit = 1.03
                else:
                    profit = 1.05
                if target_price_sell * profit < current_price_sell and coin > 0:
                    upbit.sell_market_order(i_list[s], coin)
                    print(f"{i_list[s]} 이익 실현 매도합니다")
                    krw_buy = get_balance("KRW")

            for o in range(0, len(i_list_short)):
                volume_s, close_s, open_s, volume_pre_s, close_pre_s, open_pre_s, avg_vol_s = get_boonbong(i_list_short[o])
                target_price_sell_short = ik_list_short[o]
                current_price_sell_short = get_current_price(i_list_short[o])
                coin = get_balance(i_list_short[o][4:])
                now_cell = datetime.datetime.now()
                if i_list_short[o] == "KRW-BTC":
                    profit = 1.05
                else:
                    profit = 1.22
                if target_price_sell_short * profit < current_price_sell_short and coin > 0 :
                    upbit.sell_market_order(i_list_short[o], coin)
                    print(f"{i_list_short[o]} 이익 실현 매도합니다")
                    krw_buy = get_balance("KRW")
                if now_cell - time_short[o] > datetime.timedelta(
                        seconds=480) and coin > 0\
                        and (close_s - open_s) *0.5 + open_s > current_price_sell_short:
                    bbk_short.append(i_list_short[o])
                    print(f"손절 횟수 {i_list_short[o]}: {bbk_short.count(i_list_short[o])}")
                if now_cell - time_short[o] > datetime.timedelta(
                        seconds=480) and coin > 0\
                        and bbk_short.count(i_list_short[o])>10 and (close_s - open_s) *0.5 + open_s > current_price_sell_short:
                    upbit.sell_market_order(i_list_short[o], coin)
                    print(f"{i_list_short[o]} 매도합니다")
                    krw_buy = get_balance("KRW")
                    # while i_list_short[o] in bbk_short:
                    #     bbk_short.remove(i_list_short[o])
                    # i_list_short.remove(i_list_short[o])
                    # ik_list_short.remove(ik_list_short[o])
                    # time_short.remove(time_short[o])

        else:
            for ss in range(0, len(i_list)):
                coin = get_balance(i_list[ss][4:])
                if coin > 0:
                    upbit.sell_market_order(i_list[ss], coin)
                    print(f"{i_list[ss]} 매도합니다")

            for oo in range(0, len(i_list_short)):
                coin = get_balance(i_list_short[oo][4:])
                if coin > 0:
                    upbit.sell_market_order(i_list_short[oo], coin)
                    print(f"{i_list_short[oo]} 최종 매도합니다")

            krw = get_balance("KRW")
            krw_buy = get_balance("KRW")
            i_list = []
            ik_list = []
            bbk = []
            i_list_short = []
            ik_list_short = []
            time_short = []
            bbk_short = []

        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)

