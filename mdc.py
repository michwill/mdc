#!/usr/bin/python2

import urllib2, json, sys
from collections import defaultdict
from datetime import datetime

# You can donate some mBTC here ;-)
wallet = u"15r271ADbvPkCcENraokEzrRgLrmaSpfc8"
if len(sys.argv) > 1:
	wallet = sys.argv[1]

exchange_currency = "USD"
if len(sys.argv) > 2:
	exchange_currency = sys.argv[2]

response = urllib2.urlopen("http://middlecoin.com/json")
data = json.loads(response.read())
response.close()

response = urllib2.urlopen("http://api.bitcoincharts.com/v1/weighted_prices.json")
ticker = json.loads(response.read())
response.close()
c = float(ticker[exchange_currency]["24h"])

print "Middlecoin info"
try:
    dt = datetime.utcnow() - datetime.strptime(data["time"], "%Y-%m-%d %H:%M:%S")
except:
    dt = None
if dt:
    print "Last update: %.1f minutes ago (%s UTC)" % (abs(dt.total_seconds()/60.), data["time"])

for i in data["report"]:
    if i[0] == wallet:
        break

print "    Hashrate:\t%s MH/s" % i[1].get("megahashesPerSecond", 0)

my = defaultdict(float)
my.update(i[1])
for k in my.keys():
    try:
        my[k] = float(my[k]) * 1000
    except:
        my[k] = 0

def write(greeting, value):
    print "    %s:\t%.2f mBTC = %.2f %s" % (greeting, value, c*value/1e3, exchange_currency)

if my["megahashesPerSecond"] > 0:
    print "    Rejected:\t%.1f%%" % (my["rejectedMegahashesPerSecond"] / (my["megahashesPerSecond"] + my["rejectedMegahashesPerSecond"]) * 100)
write("Total paid", my["paidOut"])
write("Exchanged", my["bitcoinBalance"])
write("To be paid", my["immatureBalance"] + my["unexchangedBalance"] + my["bitcoinBalance"])
print "1 BTC / %.2f %s" % (c, exchange_currency)
