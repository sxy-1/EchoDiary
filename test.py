"""
天气查询测试
"""

import sys
import requests

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QApplication,
    QHBoxLayout,
    QLabel,
    QComboBox,
)
from qfluentwidgets import FluentTranslator, PrimaryPushButton, TextEdit

# 城市代码字典
CITY_CODES = {
    "北京": "101010100",
    "上海": "101020100",
    "广州": "101280101",
    "深圳": "101280601",
    "天津": "101030100",
    "重庆": "101040100",
    "杭州": "101210101",
    "南京": "101190101",
    "武汉": "101200101",
    "成都": "101270101",
}


class WeatherWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("WeatherWidget")
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        # 城市选择区域
        city_layout = QHBoxLayout()
        city_label = QLabel("选择城市:")
        self.city_combo = QComboBox()
        for city in CITY_CODES.keys():
            self.city_combo.addItem(city)

        city_layout.addWidget(city_label)
        city_layout.addWidget(self.city_combo)
        city_layout.addStretch()

        # 天气按钮
        weather_button = PrimaryPushButton(text="获取天气")
        weather_button.clicked.connect(self.get_weather)

        # 显示区域
        self.result_display = TextEdit()
        self.result_display.setReadOnly(True)

        main_layout.addLayout(city_layout)
        main_layout.addWidget(weather_button)
        main_layout.addWidget(self.result_display)
        self.setLayout(main_layout)

    def get_weather(self):
        city = self.city_combo.currentText()
        city_id = CITY_CODES.get(city)

        try:
            self.result_display.setPlainText(f"正在获取{city}的天气信息...")
            url = f"http://t.weather.sojson.com/api/weather/city/{city_id}"
            response = requests.get(url)
            data = response.json()

            if data.get("status") == 200:
                weather_info = self._format_weather_data(data)
                self.result_display.setPlainText(weather_info)
            else:
                self.result_display.setPlainText(
                    f"获取天气信息失败: {data.get('message')}"
                )
        except Exception as e:
            self.result_display.setPlainText(f"发生错误: {str(e)}")

    def _format_weather_data(self, data):
        city_info = data.get("cityInfo", {})
        weather_data = data.get("data", {})
        today = (
            weather_data.get("forecast", [])[0] if weather_data.get("forecast") else {}
        )

        formatted_text = f"城市: {city_info.get('city', '未知')}\n"
        formatted_text += f"更新时间: {data.get('time', '未知')}\n"
        formatted_text += f"当前温度: {weather_data.get('wendu', '未知')}℃\n"
        formatted_text += f"湿度: {weather_data.get('shidu', '未知')}\n"
        formatted_text += f"空气质量: {weather_data.get('quality', '未知')}\n"
        formatted_text += f"PM2.5: {weather_data.get('pm25', '未知')}\n"
        formatted_text += f"PM10: {weather_data.get('pm10', '未知')}\n"
        formatted_text += f"感冒指数: {weather_data.get('ganmao', '未知')}\n\n"

        if today:
            formatted_text += f"今日天气: {today.get('type', '未知')}\n"
            formatted_text += (
                f"气温: {today.get('low', '未知')} ~ {today.get('high', '未知')}\n"
            )
            formatted_text += f"风向: {today.get('fx', '未知')}\n"
            formatted_text += f"风力: {today.get('fl', '未知')}\n"
            formatted_text += f"日出: {today.get('sunrise', '未知')}\n"
            formatted_text += f"日落: {today.get('sunset', '未知')}\n"
            formatted_text += f"提示: {today.get('notice', '无')}"

        return formatted_text


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 安装翻译器
    translator = FluentTranslator()
    app.installTranslator(translator)

    w = WeatherWidget()
    w.resize(500, 400)
    w.show()
    app.exec()
