from django.shortcuts import render
import random
import requests
import json

latitude_CONSTANT = 0
longitude_CONSTANT = 0
API_KEY = 'AIzaSyDYLcz-BMVS5EJxqSGk_szhs6cpWuM-IVk'
API_URL = 'https://maps.googleapis.com/maps/api/directions/' \
		  'json?origin=Chicago,IL&destination=Los+Angeles,CA' \
		  '&departure_time=1473538824&unit=metric&mode=driving&key=' + API_KEY


def gen_rand_points(latitude, longitude):
	x = []
	y = []
	z = []
	for i in range(5):
		# x.append(random.uniform(latitude+latitude_CONSTANT, latitude-latitude_CONSTANT))
		# y.append(random.uniform(longitude+longitude_CONSTANT, longitude-longitude_CONSTANT))
		z.append((random.uniform(latitude + latitude_CONSTANT, latitude - latitude_CONSTANT), \
				  random.uniform(longitude + longitude_CONSTANT, longitude - longitude_CONSTANT)))
	return z


def make_api_requests(self, s_lat, s_lng, e_lat, e_lng):
	API_URL = 'https://maps.googleapis.com/maps/api/directions/' \
			  'json?origin='+s_lat+','+s_lng+'&destination='+e_lat+','+e_lng+ \
			  'departure_time=1473538824&unit=metric&' \
			  'mode=driving&key=AIzaSyDYLcz-BMVS5EJxqSGk_szhs6cpWuM-IVk'
	r = requests.get(API_URL)
	print(r.status_code)
	return json.loads(r.text)


def populate_data(self):
	paths = []
	maps_json = make_api_requests()
	routes = maps_json["routes"]
	for route in routes:
		legs = route["legs"]
		for leg in legs:
			steps = leg["steps"]
			for step in steps:
				path = Path()
				path.startpoint_lat = step["start_location"]["lat"]
				path.startpoint_lng = step["start_location"]["lng"]
				path.endpoint_lat = step["end_location"]["lat"]
				path.endpoint_lng = step["end_location"]["lng"]
				path.distance = step["distance"]["value"]
				path.time_actual = step["duration"]["value"]
				path.time_in_traffic = time_in_traffic_fromlatlng(path.startpoint_lat, path.startpoint_lng,
																  path.endpoint_lat, path.endpoint_lng)

				paths.append(path)
	return paths


def time_in_traffic_fromlatlng(s_lat, s_lng, e_lat, e_lng):
	API_URL = 'https://maps.googleapis.com/maps/api/directions/' \
			  'json?origin='+s_lat+','+s_lng+'&destination='+e_lat+','+e_lng+ \
			  'departure_time=1473538824&unit=metric&' \
			  'mode=driving&key=AIzaSyDYLcz-BMVS5EJxqSGk_szhs6cpWuM-IVk'
	r = requests.get(API_URL)
	print(r.status_code)
	maps_json = json.loads(r.text)
	routes = maps_json["routes"]
	for route in routes:
		legs = route["legs"]
		for leg in legs:
			s = leg["duration_in_traffic"]
	return s


class Path:
	startpoint_lat = 0.0
	startpoint_lng = 0.0
	endpoint_lat = 0.0
	endpoint_lng = 0.0
	distance = 0.0
	time_actual = 0
	time_in_traffic = 0
	traffic_score = 0.0

	def calculate_traffic_score(self):
		self.traffic_score = (self.time_actual - self.time_in_traffic) / self.distance

	# def data_entry(self,leg):
	# 	self.startpoint=(leg["start_address"]["lat"], leg["start_address"]["lng"])
