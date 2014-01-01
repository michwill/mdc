#!/usr/bin/python2

import urllib2, json, sys

# You can donate some mBTC here ;-)
wallet = u"15r271ADbvPkCcENraokEzrRgLrmaSpfc8"
if len(sys.argv) > 1:
	wallet = sys.argv[1]

exchange_currency = "USD"
if len(sys.argv) > 2:
	exchange_currency = sys.argv[2]

response = urllib2.urlopen("http://middlecoin2.s3-website-us-west-2.amazonaws.com/json")
data = json.loads(response.read())
response.close()

response = urllib2.urlopen("http://data.mtgox.com/api/1/BTC%s/ticker" % exchange_currency)
ticker = json.loads(response.read())
response.close()
c = float(ticker["return"]["avg"]["value"])/1e3

print "Middlecoin info"
print "Date:", data["time"]

for i in data["report"]:
    if i[0] == wallet:
        break

print "    Hashrate:\t%s MH/s" % i[1]["megahashesPerSecond"]

my = i[1]
for k in my.keys():
    my[k] = float(my[k]) * 1000

def write(greeting, value):
    print "    %s:\t%.2f mBTC = %.2f %s" % (greeting, value, c*value, exchange_currency)

print "    Rejected:\t%.1f%%" % (my.get("rejectedMegahashesPerSecond", 0) / my["megahashesPerSecond"] * 100)
if "paidOut" in my:
    write("Total paid", my["paidOut"])
write("Exchanged", my["bitcoinBalance"])
write("To be paid", my["immatureBalance"] + my["unexchangedBalance"] + my["bitcoinBalance"])
