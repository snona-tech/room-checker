import math
import os
from time import sleep

import adafruit_dht
import board
import requests
import schedule

DHT_DEVICE: adafruit_dht.DHT22 = adafruit_dht.DHT22(board.D15)  # type: ignore

BASE_TEMPERATURE_C = 26.5
BASE_HUMIDITY_PERCENT = 50
ACCEPTABLE_TEMPERATURE_C_RANGE = 1.5
ACCEPTABLE_HUMIDITY_PERCENT_RANGE = 10


class RoomStatus:
    temperature: float
    humidity: float

    def __init__(self, temperature, humidity):
        self.temperature = temperature
        self.humidity = humidity


def send_line_notify(notification_message: str):
    line_notify_token = os.environ.get("LINE_NOTIFY_TOKEN")
    line_notify_api = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {line_notify_token}"}
    data = {"message": notification_message}
    requests.post(line_notify_api, headers=headers, data=data)


def get_room_status():
    try:
        temperature_c = DHT_DEVICE.temperature
        humidity = DHT_DEVICE.humidity
        status = RoomStatus(temperature_c, humidity)
        return status

    except RuntimeError as error:
        print(error.args[0])

    except Exception as error:
        DHT_DEVICE.exit()
        raise error


def difference_from_baseline(target: float, base: float):
    return target - base


def is_acceptable_temperature(temperature: float):
    difference = difference_from_baseline(temperature, BASE_TEMPERATURE_C)
    return math.fabs(difference) < ACCEPTABLE_TEMPERATURE_C_RANGE


def is_acceptable_humidity(humidity: float):
    difference = difference_from_baseline(humidity, BASE_HUMIDITY_PERCENT)
    return math.fabs(difference) < ACCEPTABLE_HUMIDITY_PERCENT_RANGE


def task():
    status = get_room_status()

    if status is None:
        send_line_notify("部屋の状態が取得できませんでした。")
        return

    current_temperature = status.temperature
    current_humidity = status.humidity

    if not is_acceptable_temperature(current_temperature):
        diff = difference_from_baseline(current_temperature, BASE_TEMPERATURE_C)
        icon = "🥶" if diff < 0 else "🥵"
        send_line_notify(
            f"室温が許容範囲外です{icon}\n室温：{current_temperature} ℃\n温度差：{round(diff,1)}"
        )

    if not is_acceptable_humidity(current_humidity):
        diff = difference_from_baseline(current_humidity, BASE_HUMIDITY_PERCENT)
        icon = "☀️" if diff < 0 else "💧"
        send_line_notify(
            f"湿度が許容範囲外です{icon}\n湿度：{current_humidity} ％\n湿度差：{round(diff,1)}"
        )


if __name__ == "__main__":
    if os.environ.get("LINE_NOTIFY_TOKEN") is None:
        print("LINE 通知トークンを設定してください。")
        DHT_DEVICE.exit()
        exit(1)

    schedule.every(5).minutes.do(task)

    while True:
        schedule.run_pending()
        sleep(1)
