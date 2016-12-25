import feedparser
from flask import Flask, render_template
from flask import request, make_response
import json
import urllib2
import urllib
import datetime


app = Flask(__name__)


RSS_FEEDS = {
'bbc': "http://feeds.bbci.co.uk/news/rss.xml",
'nyt': 'http://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
'cnn': 'http://rss.cnn.com/rss/edition.rss'
}


WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=82bc8d7f159174755381f48ca4fc906d'
CURRENCY_URL ="https://openexchangerates.org//api/latest.json?app_id=f3edae85645543b7aa5f19f613b92ed9"


DEFAULTS = {'publication':'bbc',
            'city': 'London,UK',
            'currency_from': 'GBP',
            'currency_to': 'USD'}
@app.route("/")
def home():
	#News
	# get customised headlines, based on user input or default
	publication = get_value_with_fallback("publication")
	articles = get_news(publication)

	# get customised weather based on user input or default
	city = get_value_with_fallback("city")
	weather = get_weather (city)
	
	# get customised currency based on user input or default
	currency_from = get_value_with_fallback("currency_from")
	currency_to = get_value_with_fallback("currency_to")
	rate, currencies = get_rate(currency_from, currency_to)


	response = make_response(render_template("home2.html",
	articles=articles,
	weather=weather,
	currency_from=currency_from,
	currency_to=currency_to,
	rate=rate,
	currencies=sorted(currencies)))
	expires = datetime.datetime.now() + datetime.timedelta(days=365)
	response.set_cookie("publication", publication, expires=expires)
	response.set_cookie("city", city, expires=expires)
	response.set_cookie("currency_from",
	currency_from, expires=expires)
	response.set_cookie("currency_to", currency_to, expires=expires)
	return response
	# return render_template("home2.html", articles=articles,
	# 	weather=weather, currency_from = currency_from, 
	# 	currency_to = currency_to, rate = rate,
	# 	currencies = sorted(currencies))

def get_news(query):
	if not query or query.lower() not in RSS_FEEDS:
	   publication = DEFAULTS["publication"]
	else:
	   publication = query.lower()
	feed = feedparser.parse(RSS_FEEDS[publication])
	
	return feed['entries']
def get_weather(query):
	query = urllib.quote(query)
	url = WEATHER_URL.format(query)
	data = urllib2.urlopen(url).read()
	parsed = json.loads(data)
	weather = None
	if parsed.get('weather'):
	   weather ={'description':parsed['weather'][0]['description'],
	    'temperature':parsed['main']['temp'],
	    'city':parsed['name'],
	    'country': parsed['sys']['country']
	   }
	return weather
def get_rate(frm, to):
	all_currency = urllib2.urlopen(CURRENCY_URL).read()
	parsed = json.loads(all_currency).get('rates')
	frm_rate = parsed.get(frm.upper())
	to_rate = parsed.get(to.upper())

	return (to_rate/frm_rate , parsed.keys())

def get_value_with_fallback(key):
   if request.args.get(key):
       return request.args.get(key)
   if request.cookies.get(key):
       return request.cookies.get(key)
   return DEFAULTS[key]


   #  .format(first_article.get("title"), first_article.
   # get("published"), first_article.get("summary"))


if __name__ == "__main__":
    app.run(port=5000, debug=True)