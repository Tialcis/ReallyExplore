from flask import Flask, jsonify, render_template, request
import requests
import sample

# Create an Flask app object.  We'll use this to create the routes.
searchyelp = Flask(__name__)

# Allow Flask to autoreload when we make changes to `app.py`.
searchyelp.config['DEBUG'] = True # Enable this only while testing!


@searchyelp.route('/name')
def my_name():
	return "Dan Schlosser"

@searchyelp.route('/website')
def website():
	return "adicu.com"

@searchyelp.route('/search')
def search():
	sample.main()

# Handle
@searchyelp.errorhandler(404)
def not_found(error):
	return "Sorry, I haven't coded that yet.", 404

@searchyelp.errorhandler(500)
def internal_server_error(error):
	return "My code broke, my bad.", 500


# If the user executed this python file (typed `python app.py` in their
# terminal), run our app.
if __name__ == '__main__':
	searchyelp.run(host='0.0.0.0')