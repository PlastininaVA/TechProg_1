import json

import pytest
import requests_mock
from requests.models import Response
from weather_03.weather_wrapper import BASE_URL, FORECAST_URL, WeatherWrapper

API_KEY = "key"
CITIES = {
    "london": 10.6,
    "moscow": 22.2,
    "c": 30.0,
    "b": 30.0,
    "d": 29.0,
}
CITIES_TOMORROW = {
    "london": 15.6,
    "moscow": 22.8,
    "c": 25.0,
    "b": 29.3,
    "d": 29.2,
}


@pytest.fixture(scope="session", autouse=True)
def api():
    wrapper = WeatherWrapper(API_KEY)
    yield wrapper


def test_get(api: WeatherWrapper):
    city = "london"
    json_data = {"key": "value"}
    with requests_mock.Mocker() as mock:
        mock.get(BASE_URL, json=json_data)
        data = api.get(city, BASE_URL)
        history = mock.request_history[0]
        assert history.method == "GET"
        assert history.qs == {
            "q": [city],
            "appid": [API_KEY],
            "units": ["metric"],
        }
        assert data.status_code == 200
        assert data.json() == json_data


def test_get_invalid_response(api: WeatherWrapper, mocker):
    r = Response()
    r.status_code = 400
    mocker.patch.object(WeatherWrapper, "get", new=lambda _, c, u: r)
    with pytest.raises(AttributeError) as e:
        api.get_response_city("", BASE_URL)
    assert str(e.value) == "Incorrect city"


def test_get_response(api: WeatherWrapper):
    city = "london"
    json = {"key": "value"}
    with requests_mock.Mocker() as mock:
        mock.get(BASE_URL, json=json)
        data = api.get_response_city(city, BASE_URL)
        assert data == json


with open("./tests/test_03/resources/weather.json", "r") as f:
    weather = json.load(f)
with open("./tests/test_03/resources/forecast.json", "r") as f:
    forecast = json.load(f)


@pytest.fixture()
def mock_urls(requests_mock):
    requests_mock.get(BASE_URL, json=weather)
    requests_mock.get(FORECAST_URL, json=forecast)


@pytest.mark.usefixtures("mock_urls")
def test_get_temperature(api: WeatherWrapper):
    temp = api.get_temperature("")
    assert temp == weather["main"]["temp"]


@pytest.mark.usefixtures("mock_urls")
def test_get_tomorrow_temp(api: WeatherWrapper):
    temp = api.get_tomorrow_temperature("")
    assert temp == forecast["list"][7]["main"]["temp"]


@pytest.fixture()
def mock_temp(mocker):
    mocker.patch.object(
        WeatherWrapper, "get_temperature", new=lambda _, city: CITIES.get(city, 0.0)
    )
    mocker.patch.object(
        WeatherWrapper,
        "get_tomorrow_temperature",
        new=lambda _, city: CITIES_TOMORROW.get(city, 0.0),
    )


@pytest.mark.usefixtures("mock_temp")
def test_diff(api: WeatherWrapper):
    for city1 in CITIES:
        for city2 in CITIES:
            temp = api.find_diff_two_cities(city1, city2)
            assert temp == CITIES[city1] - CITIES[city2]


def get_temp_diff(city1: str, city2: str) -> int:
    return int(abs(CITIES[city1] - CITIES[city2]))


@pytest.mark.usefixtures("mock_temp")
@pytest.mark.parametrize(
    "city1,city2,expected",
    [
        (
            "b",
            "d",
            f"Weather in b is warmer than in d by {get_temp_diff('b', 'd')} degrees",
        ),
        (
            "d",
            "b",
            f"Weather in d is colder than in b by {get_temp_diff('b', 'd')} degrees",
        ),
    ],
)
def test_diff_str(api: WeatherWrapper, city1: str, city2: str, expected: str):
    assert expected == api.get_diff_string(city1, city2)


@pytest.mark.usefixtures("mock_temp")
@pytest.mark.parametrize(
    "city,expected",
    [
        ("london", "The weather in london tomorrow will be much warmer than today"),
        ("moscow", "The weather in moscow tomorrow will be warmer than today"),
        ("c", "The weather in c tomorrow will be much colder than today"),
        ("b", "The weather in b tomorrow will be colder than today"),
        ("d", "The weather in d tomorrow will be the same than today"),
    ],
)
def test_tomorrow_diff(api: WeatherWrapper, city: str, expected: str):
    assert expected == api.get_tomorrow_diff(city)
