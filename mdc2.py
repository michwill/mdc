#!/usr/bin/python2
# -*- coding: cp1250 -*-
import urllib2, json, datetime, os, sys, time
from fractions import gcd
######################################################
#You can donate some mBTC here ;-)
#orignal script:
#   michwill    15r271ADbvPkCcENraokEzrRgLrmaSpfc8
#more info version:
#   vosovich
#this modified version:
#   mardilv     1PkCFatY7jgxY8BFaZe1YeL1baa8G7tVuR
######################>CONFIG<#######################
#insert your adress here, between quotation marks
wallet = u"1PkCFatY7jgxY8BFaZe1YeL1baa8G7tVuR"
if len(sys.argv) > 1:
	wallet = sys.argv[1]
#set in minutes but accepts fractions, in reality intervals will be slightly longer
#as getting and processing data from api's takes some time
#default values: 5 and 5
mdc_checktime_interval = float(5)
ex_checktime_interval = float(5)
#displaying funds in microBTC ( 1 microBTC = 0.000001 BTC )
#accepted values: True, False
mbtc = False
#displaying exchange rates from Mt.Gox, BTC-E and Bitstamp
mtgox = True
btce = True
bit = True
#which currency to display exchange rates for
usd = True
euro = True
#set currency to use in estimation
#accepted values: USD, EUR
exchange_currency = "USD"
if len(sys.argv) > 2:
	exchange_currency = sys.argv[2]
#exchange rate source for calculcating balances in USD
#accepted values: mtg_avg, mtg_last, btce_avg, btce_last, bit_avg, bit_last
#to use exchange rates from site for calculating you have to enable it above
#Bitstamp doesn't exchange BTC for EUR, so don't set it Bitstamp if you want
#your Middlecoin balances calculated to EUR
exchange = "mtg_avg"
#clears terminal screen before every refresh
#this DOESN'T clear IDLE shell window
#and will be annoying while enabled while using IDLE(popping black terminal for split second)
#accepted values: True, False
to_clear_or_not_to_clear = False
#middlecoin json adress
mdc_json = "http://middlecoin2.s3-website-us-west-2.amazonaws.com/json"

def write(greeting, value, mode):
    if mode:
        print "    %s:\t%.2f mBTC = %.2f %s" % (greeting, value*1000, c*value, exchange_currency)
    else:
        print "    %s:\t%f BTC = %f %s" % (greeting, value, c*value, exchange_currency)
def f(x):
    if x == "mtg_avg" :
        return "Mt.Gox Average"
    elif x == "mtg_last" :
        return "Mt.Gox Last"
    elif x == "btce_avg" :
        return "BTC-E Average"
    elif x == "btce_last" :
        return "BTC-E Last"
    elif x == "bit_avg" :
        return "Bitstamp Average"
    elif x == "bit_last" :
        return "Bitstamp Last"
    else:
        return -1
        
runningFlag = True

mdc_checktime_counter = float(0)
ex_checktime_counter = float(0)

# stash update values, lets webservers send us 304 if the data
#  is not updated. Reduces server load and lets us query more often 
#  for updates without download penalty  
mdc_etag = None
mdc_last_modified = None

sleeptime = gcd(mdc_checktime_interval, ex_checktime_interval)

while runningFlag:

    if to_clear_or_not_to_clear:
        os.system('cls' if os.name=='nt' else 'clear')

    print "Refresh interval : %.2f seconds." % (sleeptime*60)
    print "Middlecoin info update in : %.2f seconds" %(mdc_checktime_counter*60)
    print "Exchanges info update in : %.2f seconds" %(ex_checktime_counter*60)
    
    if mdc_checktime_counter <= 0:    
        request = urllib2.Request(mdc_json)

        # lets save the whales and such, let smart webservers send us
        # 304 if the data hasn't changed yet
        if mdc_etag:
            request.add_header('If-None-Match', mdc_etag)
        if mdc_last_modified:
            request.add_header('If-Modified-Since', mdc_last_modified)
        try:
            response = urllib2.urlopen(request)
            # It is ok for servers to ignore/not respond with these
            mdc_etag = response.headers.get('ETag', None)
            mdc_last_modified = response.headers.get('Last-Modified', None)
            data = json.loads(response.read())
            last_update = data['time']
            response.close()
            mdc_checktime_counter = mdc_checktime_interval
        except urllib2.HTTPError, e:
            if e.code == 304:
                last_update = "%s (cached)" %(data['time'],)
            # just ignore for now, previous version would just crash
            pass

    if ex_checktime_counter <= 0:
        if btce:
            if usd:
                response = urllib2.urlopen("https://btc-e.com/api/2/btc_usd/ticker")
                btcticker = json.loads(response.read())
                response.close()
                btce_avg = float(btcticker["ticker"]["avg"])
                btce_last = float(btcticker["ticker"]["last"])
                btce_timestamp = int(btcticker["ticker"]["updated"])
                btcetime = datetime.datetime.fromtimestamp( btce_timestamp )
            if euro:
                response = urllib2.urlopen("https://btc-e.com/api/2/btc_eur/ticker")
                btcticker = json.loads(response.read())
                response.close()
                e_btce_avg = float(btcticker["ticker"]["avg"])
                e_btce_last = float(btcticker["ticker"]["last"])
                e_btce_timestamp = int(btcticker["ticker"]["updated"])
                e_btcetime = datetime.datetime.fromtimestamp( btce_timestamp )
        
        response = urllib2.urlopen("http://data.mtgox.com/api/1/BTCUSD/ticker")
        ticker = json.loads(response.read())
        response.close()
        mtg_avg = float(ticker["return"]["avg"]["value"])
        mtg_last = float(ticker["return"]["last"]["value"])
        mtgtimestamp = int(ticker["return"]["now"])/1e6
        mtgtime = datetime.datetime.fromtimestamp( mtgtimestamp )
        if ((mtgox == True)and(euro == True)):
            response = urllib2.urlopen("http://data.mtgox.com/api/1/BTCEUR/ticker")
            ticker = json.loads(response.read())
            response.close()
            e_mtg_avg = float(ticker["return"]["avg"]["value"])
            e_mtg_last = float(ticker["return"]["last"]["value"])
            e_mtgtimestamp = int(ticker["return"]["now"])/1e6
            e_mtgtime = datetime.datetime.fromtimestamp( mtgtimestamp )
        
        if ((bit == True) and ( usd == True )):
            response = urllib2.urlopen("https://www.bitstamp.net/api/ticker/")
            bit_ticker = json.loads(response.read())
            response.close()
            bit_avg = (float(bit_ticker["high"])+float(bit_ticker["low"]))/2
            bit_last = float(bit_ticker["last"])
            bit_timestamp = int(bit_ticker["timestamp"])
            bit_time = datetime.datetime.fromtimestamp( bit_timestamp ) 


        ex_checktime_counter = ex_checktime_interval
        
    if exchange_currency == "USD":
        if ((exchange == "mtg_avg") and (mtgox == True)):
            c = mtg_avg
        elif ((exchange == "mtg_last") and (mtgox == True)) :
            c = mtg_last
        elif ((exchange == "btce_avg")and (btce == True)):
            c = btce_avg
        elif ((exchange == "btce_last") and (btce == True)):
            c = btce_last
        elif ((exchange == "bit_last") and (bit == True)):
            c = bit_last    
        elif ((exchange == "bit_avg") and (bit == True)):
            c = bit_avg
        else:
            exchange = "mtg_avg"
            c = mtg_avg
    elif exchange_currency == "EUR":
        if ((exchange == "mtg_avg") and (mtgox == True)):
            c = e_mtg_avg
        elif ((exchange == "mtg_last") and (mtgox == True)) :
            c = e_mtg_last
        elif ((exchange == "btce_avg")and (btce == True)):
            c = e_btce_avg
        elif ((exchange == "btce_last") and (btce == True)):
            c = e_btce_last
        elif ((exchange == "bit_last") and (bit == True)):
            c = e_bit_last    
        elif ((exchange == "bit_avg") and (bit == True)):
            c = e_bit_avg
        else:
            exchange = "mtg_avg"
            c = e_mtg_avg
        
    print "Middlecoin info"
    print "Wallet : %s" % wallet
    print "Data Updated:", last_update

    for i in data["report"]:
        if i[0] == wallet:
            break

    print "    Hashrate:\t%s MH/s" % i[1]["megahashesPerSecond"]

    my = i[1]
    for k in my.keys():
        my[k] = float(my[k])
          
    print "    Rejected:\t%.1f%%" % (my.get("rejectedMegahashesPerSecond", 0) / my["megahashesPerSecond"]* 100)
    write("Total paid   ", my.get("paidOut", 0),mbtc)
    write("Total unpaid ", my.get("immatureBalance", 0) + my.get("unexchangedBalance", 0) + my.get("bitcoinBalance", 0), mbtc)
    write("Exchanged    ", my.get("bitcoinBalance", 0),mbtc)
    write("Unexchanged  ", my.get("unexchangedBalance", 0),mbtc)
    write("Immature     ", my.get("immatureBalance", 0),mbtc)
    print "%s values based on %s." % (exchange_currency, f(exchange))
    if (btce or mtgox or bit):
        print "Exchange info"
    if  mtgox:
        print "Mt.Gox"
        if usd: 
            print "Date:", mtgtime.strftime("%Y-%m-%d %H:%M:%S")
            print "    Average\t :\t$%f" % (mtg_avg)
            print "    Last\t :\t$%f" % (mtg_last)
        if euro:
            print "Date:", e_mtgtime.strftime("%Y-%m-%d %H:%M:%S")
            print "    Average\t :\t€%f" % (e_mtg_avg)
            print "    Last\t :\t€%f" % (e_mtg_last)        
    if btce:
        print "BTC-E"
        if usd:
            print "Date:", btcetime.strftime("%Y-%m-%d %H:%M:%S")
            print "    Average\t :\t$%f" % (btce_avg)
            print "    Last\t : \t$%f" % (btce_last)
        if euro:
            print "Date:", e_btcetime.strftime("%Y-%m-%d %H:%M:%S")
            print "    Average\t :\t€%f" % (e_btce_avg)
            print "    Last\t : \t€%f" % (e_btce_last)
            
    if ((bit==True) and (usd == True)):
        print "Bitstamp"
        print "Date:", bit_time.strftime("%Y-%m-%d %H:%M:%S")
        print "    Average\t :\t$%f" % (bit_avg)
        print "    Last\t : \t$%f" % (bit_last)
    print "Khash/s      \t :\t%.2f" % (my["megahashesPerSecond"]*1000)
    print "Shares last h\t :\t%.0f" % (my["lastHourShares"])
    print "\n"
    mdc_checktime_counter -= sleeptime
    ex_checktime_counter -= sleeptime
    time.sleep(sleeptime*60)
    

