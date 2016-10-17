from math import sin, cos
from django.http import HttpResponse
import random
import requests
import json

from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg
from .models import TrafficModel

from django.utils import timezone


@csrf_exempt
def request_static(request):
    pass


@csrf_exempt
def request_dynamic(request):
    print('hello')
    if request.method == "POST":
        json_data = request.POST
        latitude = float(json_data["latitude"])
        longitude = float(json_data["longitude"])
        ROADS_API_URL = "https://roads.googleapis.com/v1/nearestRoads?points="
        for i in range(51):
            radians = 3.14 * 0.02 * i
            x_latitude = float(latitude) + latitude_CONSTANT * cos(radians)
            y_longitude = float(longitude) + longitude_CONSTANT * sin(radians)
            ROADS_API_URL += str(x_latitude) + ',' + str(y_longitude) + '|'
        ROADS_API_URL = ROADS_API_URL[:(len(ROADS_API_URL) - 1)]
        ROADS_API_URL += '&key=AIzaSyCOhrN9Tbo_a1sxm9Kcy2zxb4C7b51XB1k'
        print(ROADS_API_URL)
        r = requests.get(ROADS_API_URL)
        json_response_data = json.loads(r.text)
        infos = json_response_data["snappedPoints"]
        a = {'roads': []}
        place_id_list = []
        for id in infos:
            place_id_list.append(id["placeId"])
        # place_id_set = set(place_id_list)
        w = TrafficModel.objects.values('place_id')
        w = w.annotate(total_avg_speed=Avg('avg_speed'))
        w = w.order_by('total_avg_speed')
        print(w)
        traffic_places_list = []
        for member in w:
            if member["total_avg_speed"] <= 20.0:
                traffic_places_list.append(member)
        print(traffic_places_list)
        print(type(traffic_places_list))
        for place in traffic_places_list:
            c = getplace_name_from_id(place["place_id"])
            if(c is None):
                pass
            else:
                a["roads"].append(c)

        return json.dumps(a)


def getplace_name_from_id(placeid):
    r = requests.get("https://maps.googleapis.com/maps/api/place/details/json?"
                     "placeid=" + placeid +
                     "&key=AIzaSyB5OBkGEowp58z-e8NoCmWeHlV2osjZgqc")
    print(r.text)
    json_place_data = json.loads(r.text)
    if json_place_data["status"] == "NOT_FOUND":
        return None
    else:
        print(json_place_data)
        print("step1")
        print(json_place_data)
        lat = json_place_data["result"]["geometry"]["location"]["lat"]
        print("step2")
        lng = json_place_data["result"]["geometry"]["location"]["lng"]
        place_name = json_place_data["result"]["name"]
        return_dict = {"lat": lat, "lng": lng, "name": place_name}
    return return_dict


@csrf_exempt
def post_current_data(request):
    if request.method == "POST":
        js_data = request.POST
        json_string = js_data["Json"]
        json_data = json.dumps(json_string)
        print(json_data)
        tm = TrafficModel()
        tm.latitude = float(json_data["latitude"])
        tm.longitude = float(json_data["longitude"])
        print("ste3")
        tm.avg_speed = float(json_data["avg_speed"])
        tm.record_time = timezone.now()
        tm.place_id = get_place_id(json_data["latitude"],
                                   json_data["longitude"])
        tm.save()
        return HttpResponse(request_dynamic(request))


def get_place_id(lat, lng):
    points = str(lat) + ',' + str(lng)
    r = requests.get('https://roads.googleapis.com/v1/nearestRoads?'
                     'points=' + points +
                     '&key=AIzaSyCOhrN9Tbo_a1sxm9Kcy2zxb4C7b51XB1k')
    json_response = json.loads(r.text)
    place_id = json_response["snappedPoints"][0]["placeId"]
    return place_id


paths = []

latitude_CONSTANT = 0.00904470708
longitude_CONSTANT = 0.00959214211

API_KEY = 'AIzaSyDYLcz-BMVS5EJxqSGk_szhs6cpWuM-IVk'


# API_URL = 'https://maps.googleapis.com/maps/api/directions/' \
# 		  'json?origin=Chicago,IL&destination=Los+Angeles,CA' \
# 		  '&departure_time=1473538824&unit=metric&mode=driving&key=' + API_KEY


def gen_rand_points(latitude, longitude):
    # x = []
    # y = []
    z = []
    for i in range(8):
        # x.append(random.uniform(latitude+latitude_CONSTANT,
        #                         latitude-latitude_CONSTANT))
        # y.append(random.uniform(longitude+longitude_CONSTANT,
        #                         longitude-longitude_CONSTANT))
        z.append((random.uniform(latitude + latitude_CONSTANT,
                                 latitude - latitude_CONSTANT),
                  random.uniform(longitude + longitude_CONSTANT,
                                 longitude - longitude_CONSTANT)))
    return z


def make_api_requests(s_lat, s_lng, e_lat, e_lng):
    API_URL = 'https://maps.googleapis.com/maps/api/directions/' \
              'json?origin=' + str(s_lat) + ',' + str(s_lng) + \
              '&destination=' + str(e_lat) + ',' + str(e_lng) + \
              '&departure_time=1474538824&unit=metric&' \
              'mode=driving&key=AIzaSyDYLcz-BMVS5EJxqSGk_szhs6cpWuM-IVk'
    print(API_URL)
    r = requests.get(API_URL)
    print(r.status_code)
    print(r.text)
    return json.loads(r.text)


def populate_data_helper(s_lat, s_lng, e_lat, e_lng):
    maps_json = make_api_requests(s_lat, s_lng, e_lat, e_lng)
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
                path.time_in_traffic = time_in_traffic_fromlatlng(
                    path.startpoint_lat, path.startpoint_lng,
                    path.endpoint_lat,
                    path.endpoint_lng
                )

                paths.append(path)


def populate_data(lat_post, lng_post):
    rand_num_list = gen_rand_points(lat_post, lng_post)
    for rand_num_tuple in rand_num_list:
        x, y = rand_num_tuple
        populate_data_helper(lat_post, lng_post, x, y)
    for path in paths:
        path.calculate_traffic_score()


def time_in_traffic_fromlatlng(s_lat, s_lng, e_lat, e_lng):
    API_URL = 'https://maps.googleapis.com/maps/api/directions/' \
              'json?origin=' + str(s_lat) + ',' + str(s_lng) + \
              '&destination=' + str(e_lat) + ',' + str(e_lng) + \
              '&departure_time=1474538824&unit=metric&' \
              'mode=driving&key=AIzaSyDYLcz-BMVS5EJxqSGk_szhs6cpWuM-IVk'
    print(API_URL)
    r = requests.get(API_URL)
    print(r.status_code)
    print(r.text)
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
        try:
            actual_time_score = self.distance / self.time_actual
            traffic_time_score = self.distance / self.time_in_traffic
            self.traffic_score = actual_time_score - traffic_time_score
        except ZeroDivisionError:
            self.traffic_score = -1

        # def data_entry(self,leg):
        # 	self.startpoint=(leg["start_address"]["lat"],
        #                    leg["start_address"]["lng"])


if __name__ == "__main__":
    populate_data(49.5544, -71.9902)
    print(paths)
