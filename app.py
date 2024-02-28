from flask import Flask, request, render_template
import requests
import pytz
from datetime import datetime
from timezonefinder import TimezoneFinder
# import sys

app = Flask(__name__)

API_KEY = "d0fecbac2de207691da56baaaa47d56b" #personal API key
BASE_URL = "https://api.openweathermap.org/data/2.5/weather" #link to API that will be called

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        weather_location = request.form['city'].strip()
        city_request_url = f"{BASE_URL}?appid={API_KEY}&q={weather_location}"
        info = requests.get(city_request_url)
        if check(info):
            data = info.json()
            weather_data = convert(data)
            formatted_data = format(weather_data)
            return render_template('index.html', weather=formatted_data)
        else:
            error = "An Error Has Occurred."
            return render_template('index.html', error=error)
    return render_template('index.html')

def check(response): #check function that checks if the url works (200 -> "indicates that the request has succeeded")
    if response.status_code == 200:
        return True
    else:
        return False

def convert(weather): #convert function that manipulates the data
    lat, lon = weather["coord"]["lat"], weather["coord"]["lon"]
    temp, feelTemp = weather["main"]["temp"], weather["main"]["feels_like"]
    desc = (weather["weather"][0]["description"]).title()
    city = weather["name"]

    #call conversion function to convert from kelvin to celsius/ fahrenheit
    newTemp = temp_conv(temp)
    newFeelTemp = temp_conv(feelTemp)

    #call time function to convert the latitude and longitude to time
    current_time = time(lat, lon)

    return current_time, newTemp, newFeelTemp, desc, city #return as a tuple of all values taken from data

def temp_conv(temp): #temperature conversion function (from kelvin to celcius/ fahrenheit)
    fahr = round((temp - 273.15) * 9/5 + 32)
    cel = round((temp - 273.15))

    return fahr, cel #return both as a tuple

def time(lat, lon): #takes the latitude and longitude to find the time (uses the timezonefinder and datetime libraries)
    obj = TimezoneFinder()
    tz = obj.timezone_at(lng = lon, lat = lat)
    timezone = pytz.timezone(tz)
    dt = datetime.now(timezone)
    mil_time = dt.strftime("%H:%M:%S")

    hour, min, s = mil_time.split(":") #taking hour/ min values

    #non-military time converter
    if int(hour) == 0:
        new_hour = int(hour) + 12
        return f"{new_hour:02}:{min} AM"
    elif int(hour) == 12:
        return f"{hour}:{min} PM"
    elif int(hour) > 12:
        new_hour = int(hour) - 12
        return f"{new_hour:02}:{min} PM"
    else:
        return f"{hour}:{min} AM"
    
if __name__ == "__main__":
    app.run(debug=True)