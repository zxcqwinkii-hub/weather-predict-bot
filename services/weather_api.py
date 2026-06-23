import httpx

async def get_weather_by_city(city_name: str) -> dict | None:
    """Получить погоду по названию города через Open-Meteo API"""
    
    # 1. Геокодим город в координаты
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=ru"
    
    async with httpx.AsyncClient() as client:
        try:
            geo_resp = await client.get(geo_url, timeout=10.0)
            geo_resp.raise_for_status()
            geo_data = geo_resp.json()
            
            if not geo_data.get('results'):
                return None
                
            lat = geo_data['results'][0]['latitude']
            lon = geo_data['results'][0]['longitude']
            resolved_city = geo_data['results'][0]['name']

            # 2. Получаем погоду
            weather_url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={lat}&longitude={lon}"
                f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code"
                f"&hourly=temperature_2m,precipitation_probability"
                f"&timezone=auto&forecast_days=1"
            )
            
            weather_resp = await client.get(weather_url, timeout=10.0)
            weather_resp.raise_for_status()
            weather_data = weather_resp.json()
            
            return {
                "city": resolved_city,
                "current": weather_data['current'],
                "hourly": weather_data['hourly']
            }
        except Exception as e:
            print(f"Ошибка при получении погоды: {e}")
            return None