from django.shortcuts import render
import requests
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from datetime import datetime, timedelta
import pytz
import os

API_KEY = 'ab49ef7fd02440c5275a44b71565f6ae'
BASE_URL = 'https://api.openweathermap.org/data/2.5/'

def get_current_weather(city):
    url = f"{BASE_URL}weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    return {
        'city': data['name'],
        'current_temp': round(data['main']['temp']),
        'feels_like': round(data['main']['feels_like']),
        'temp_min': round(data['main']['temp_min']),
        'temp_max': round(data['main']['temp_max']),
        'humidity': round(data['main']['humidity']),
        'description': data['weather'][0]['description'],
        'country': data['sys']['country'],
        'pressure': data['main']['pressure'],
        'wind_speed': data['wind']['speed'],
        'clouds': data.get('clouds', {}).get('all', 0),
        'wind_deg': data['wind'].get('deg', 0)
    }

def get_weather_class(description):
    weather_map = {
        'clear sky': 'clear',
        'few clouds': 'cloudy',
        'scattered clouds': 'cloudy',
        'broken clouds': 'overcast',
        'overcast clouds': 'overcast',
        'shower rain': 'shower',
        'rain': 'rain',
        'thunderstorm': 'thunder',
        'snow': 'snow',
        'mist': 'mist',
        'fog': 'fog',
        'drizzle': 'drizzle'
    }
    for key in weather_map:
        if key in description.lower():
            return weather_map[key]
    return 'clear'

def get_ml_predictions(weather_data):
    try:
        # Create sample historical data for ML model
        sample_data = {
            'MinTemp': [weather_data['temp_min'] - 5 + i for i in range(100)],
            'MaxTemp': [weather_data['temp_max'] - 3 + i for i in range(100)],
            'Humidity': [weather_data['humidity'] - 10 + (i % 20) for i in range(100)],
            'Pressure': [weather_data['pressure'] - 5 + (i % 10) for i in range(100)],
            'Temp': [weather_data['current_temp'] - 3 + (i % 6) for i in range(100)],
            'WindGustSpeed': [weather_data['wind_speed'] + (i % 5) for i in range(100)],
            'WindGustDir': [0, 1, 2, 3] * 25,
            'RainTomorrow': [0, 1] * 50
        }
        
        df = pd.DataFrame(sample_data)
        
        # Train rain prediction model
        X = df[['MinTemp', 'MaxTemp', 'WindGustDir', 'WindGustSpeed', 'Humidity', 'Pressure', 'Temp']]
        y = df['RainTomorrow']
        rain_model = RandomForestClassifier(n_estimators=50, random_state=42)
        rain_model.fit(X, y)
        
        # Predict rain
        current_data = [[weather_data['temp_min'], weather_data['temp_max'], 0, 
                        weather_data['wind_speed'], weather_data['humidity'], 
                        weather_data['pressure'], weather_data['current_temp']]]
        rain_pred = rain_model.predict(current_data)[0]
        
        # Generate future predictions
        future_temps = [weather_data['current_temp'] + np.random.randint(-3, 4) for _ in range(5)]
        future_humidity = [weather_data['humidity'] + np.random.randint(-10, 11) for _ in range(5)]
        
        timezone = pytz.timezone('UTC')
        now = datetime.now(timezone)
        future_times = [(now + timedelta(hours=i+1)).strftime('%H:%M') for i in range(5)]
        
        return {
            'rain_prediction': 'Yes' if rain_pred else 'No',
            'future_temps': list(zip(future_times, future_temps)),
            'future_humidity': list(zip(future_times, future_humidity))
        }
    except:
        return {
            'rain_prediction': 'No',
            'future_temps': [],
            'future_humidity': []
        }

def index(request):
    # Default context with all required fields
    context = {
        'city': 'London',
        'country': 'GB',
        'current_temp': 20,
        'feels_like': 22,
        'temp_min': 18,
        'temp_max': 25,
        'humidity': 65,
        'clouds': 30,
        'pressure': 1013,
        'description': 'clear sky',
        'weather_class': 'clear',
        'wind_speed': 3.5,
        'rain_prediction': 'No',
        'location': 'London',
        'future_temps': [(f'{i+1}:00', 20+i) for i in range(5)],
        'future_humidity': [(f'{i+1}:00', 65+i*2) for i in range(5)],
        'error': None
    }
    print(f"DEBUG: Default weather class: weather-{context['weather_class']}")
    
    if request.method == 'POST':
        city = request.POST.get('city', 'London')
        try:
            current_weather = get_current_weather(city)
            weather_class = get_weather_class(current_weather['description'])
            print(f"DEBUG: Weather description: '{current_weather['description']}', Weather class: 'weather-{weather_class}'")
            ml_predictions = get_ml_predictions(current_weather)
            
            context.update({
                'city': current_weather['city'],
                'country': current_weather['country'],
                'current_temp': current_weather['current_temp'],
                'feels_like': current_weather['feels_like'],
                'temp_min': current_weather['temp_min'],
                'temp_max': current_weather['temp_max'],
                'humidity': current_weather['humidity'],
                'clouds': current_weather['clouds'],
                'pressure': current_weather['pressure'],
                'description': current_weather['description'],
                'weather_class': weather_class,
                'wind_speed': current_weather['wind_speed'],
                'location': city,
                'rain_prediction': ml_predictions['rain_prediction'],
                'future_temps': ml_predictions['future_temps'],
                'future_humidity': ml_predictions['future_humidity'],
                'error': None
            })
        except Exception as e:
            print(f"DEBUG: Error occurred: {str(e)}")
            context.update({
                'error': f'City "{city}" not found. Please try another city.',
                'location': city
            })
    
    return render(request, 'weather.html', context)