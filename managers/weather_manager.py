import os
import json
import requests
from typing import List, Dict, Any, Optional


class WeatherManager:
    def __init__(self):
        city_json_path = os.path.join("data", "config", "city_code.json")
        with open(city_json_path, "r", encoding="utf-8") as f:
            self.city_codes: Dict[str, str] = json.load(f)

    def get_all_cities(self) -> List[str]:
        """获取所有城市名"""
        return list(self.city_codes.keys())

    def get_city_code(self, city_name: str) -> Optional[str]:
        """根据城市名获取城市代码"""
        return self.city_codes.get(city_name)

    def get_weather(self, city_name: str) -> Dict[str, Any]:
        """根据城市名获取天气信息（返回原始API数据）"""
        city_code = self.get_city_code(city_name)
        if not city_code:
            raise ValueError(f"未找到城市: {city_name}")
        print(f"城市代码: {city_code}")
        url = f"http://t.weather.sojson.com/api/weather/city/{city_code}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_today_weather_type(self, city_name: str) -> str:
        """获取指定城市今天的天气类型（如：阴、晴、多云等）"""
        weather_data = self.get_weather(city_name)
        return weather_data["data"]["forecast"][0]["type"]


if __name__ == "__main__":
    manager = WeatherManager()
    print(manager.get_all_cities())
    print(manager.get_today_weather_type("上海"))
