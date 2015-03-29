# -*- coding: utf-8 -*-
"""
Explore NYC!
By Sebastien Siclait, Lindsay Schiminske and Narcisa Codreanu
At DevFest 2015, Hosted by ADI

This app is designed to allow the user to find a random location, using Yelp's 
database, to explore! The bounds are set to New York and the user is encouraged to
search for general categories.

Made possible with Yelp's API and Google's Maps API

"""
from flask import Flask, jsonify, render_template, request, redirect
from random import choice
from datetime import datetime
import argparse
import json
import pprint
import sys
import urllib
import urllib2

import oauth2
import requests

# # Create an Flask app object.  We'll use this to create the routes.
explore = Flask(__name__)

# # Allow Flask to autoreload when we make changes to `app.py`.
explore.config['DEBUG'] = True # Enable this only while testing!

@explore.route("/")
def start():
    hour = datetime.now().hour
    url= "http://www.layoverguide.com/wp-content/uploads/2011/02/The-Statue-of-Liberty-and-Manhattan-Skyline-New-York-City-NY.jpg"
    if hour <= 7 or hour >= 19:
        url = "http://1.bp.blogspot.com/-b5500NEMEJM/USTsQ9KopBI/AAAAAAAAAwA/mJo9rV-7XwI/s1600/New_York_skyline-City_Landscape_Wallpaper_1366x768.jpg"
    return render_template('hello.html',img_url=url)

@explore.route("/page", methods = ["POST","GET"])
def hello():
    if request.method == "POST":
        response_dict = search(request.form["user_search"], DEFAULT_LOCATION)
        # return response_dict["businesses"][0]["categories"][0][1]
        #return jsonify(response_dict)
        #return render_template("results.html", response_dict = response_dict) 
        return redirect("/page/" + request.form["user_search"])
    else:# request.method == "GET":
        return render_template("search.html")

@explore.route("/page/<term>")
def query(term):
        response_dict = search(term, DEFAULT_LOCATION)
        rand_val = choice(response_dict["businesses"]) 
        return render_template("results.html", api_data = rand_val) 
       # response_dict = search(term, DEFAULT_LOCATION)
        # return response_dict["businesses"][0]["categories"][0][1]
       # return jsonify(response_dict)
 
# @explore.route('/')
# def go():
#         return render_template("search.html")


API_HOST = 'api.yelp.com'
DEFAULT_TERM = ''
DEFAULT_LOCATION = 'New York, NY'
SEARCH_LIMIT = 20
SEARCH_PATH = '/v2/search/'
BUSINESS_PATH = '/v2/business/'

# OAuth credential placeholders that must be filled in by users.
CONSUMER_KEY = "ZHREaNdbx6l8INiJaknBjQ"
CONSUMER_SECRET = "KaPHWS8TpwU7jngDQhNjL1eicGE"
TOKEN = "xDi0welpu5ShSkbW6lw7JMxp0WIcsSq2"
TOKEN_SECRET = "BcOCcNW_L9aS7JjB_KJWhEKtlRI"

#@app.route('/search')#, methods=["GET", "POST"])
# @explore.route('/')
# def hello():
#     return render_template('hello.html')

def equest(host, path, url_params=None):
    """Prepares OAuth authentication and sends the equest to the API.

    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        url_params (dict): An optional set of query parameters in the equest.

    Returns:
        dict: The JSON response from the equest.

    Raises:
        urllib2.HTTPError: An error occurs from the HTTP equest.
    """
    url_params = url_params or {}
    url = 'http://{0}{1}?'.format(host, urllib.quote(path.encode('utf8')))

    consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
    oauth_equest = oauth2.Request(method="GET", url=url, parameters=url_params)

    oauth_equest.update(
        {
            'oauth_nonce': oauth2.generate_nonce(),
            'oauth_timestamp': oauth2.generate_timestamp(),
            'oauth_token': TOKEN,
            'oauth_consumer_key': CONSUMER_KEY
        }
    )
    token = oauth2.Token(TOKEN, TOKEN_SECRET)
    oauth_equest.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
    signed_url = oauth_equest.to_url()
    
    print u'Querying {0} ...'.format(url)

    conn = urllib2.urlopen(signed_url, None)
    try:
        response = json.loads(conn.read())
    finally:
        conn.close()

    return response

def search(term, location):
    """Query the Search API by a search term and location.

    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.

    Returns:
        dict: The JSON response from the equest.
    """
    
    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': SEARCH_LIMIT
    }
    return equest(API_HOST, SEARCH_PATH, url_params=url_params)

def get_business(business_id):
    """Query the Business API by a business ID.

    Args:
        business_id (str): The ID of the business to query.

    Returns:
        dict: The JSON response from the equest.
    """
    business_path = BUSINESS_PATH + business_id 

    return equest(API_HOST, business_path)

def query_api(term, location):
    """Queries the API by the input values from the user.

    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """
    response = search(term, location)

    businesses = response.get('businesses')

    if not businesses:
        print u'No businesses for {0} in {1} found.'.format(term, location)
        return

    business_id = businesses[0]['id']

    print u'{0} businesses found, querying business info for the top result "{1}" ...'.format(
        len(businesses),
        business_id
    )

    response = get_business(business_id)

    print u'Result for business "{0}" found:'.format(business_id)
    pprint.pprint(response, indent=2)

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-q', '--term', dest='term', default=DEFAULT_TERM, type=str, help='Search term (default: %(default)s)')
    parser.add_argument('-l', '--location', dest='location', default=DEFAULT_LOCATION, type=str, help='Search location (default: %(default)s)')

    input_values = parser.parse_args()

    try:
        query_api(input_values.term, input_values.location)
    except urllib2.HTTPError as error:
        sys.exit('Encountered HTTP error {0}. Abort program.'.format(error.code))

    # Handle
# @app.errorhandler(404)
# def not_found(error):
#     return "Sorry, I haven't coded that yet.", 404

# @app.errorhandler(500)
# def internal_server_error(error):
#     return "My code broke, my bad.", 500


# # If the user executed this python file (typed `python app.py` in their
# # terminal), run our app.
# if __name__ == '__main__':
#     app.run(host='0.0.0.0')
if __name__ == '__main__':
    # main()
    explore.run(host='0.0.0.0', port=5000)
