#!usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import urllib
import json
import autooauth as oauth


def getWeather(city):
    #查询yahoo weather，获取json返回的天气信息
    yql = "http://query.yahooapis.com/v1/public/yql?q=SELECT%20*%20FROM%20weather.bylocation%20WHERE%20location%3D'" + city + "'%20AND%20unit%3D%22c%22&format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys"
    weather = json.loads(urllib2.urlopen(yql).read())
    #提取天气内容
    weather = weather['query']['results']['weather']['rss']['channel']
    return weather

def getAqiforecast():
    '''查询北京翌日首要污染物'''
    highaqi = 0
    query = 'http://zx.bjmemc.com.cn/ashx/DayForecast.ashx1'
    aqi = json.loads(urllib2.urlopen(query).read())[0]
    # 提取翌日首要污染物的高值
    if aqi['AQID'].find('-') != -1:
        highaqi = aqi['AQID'][aqi['AQID'].rfind('-')+1:]
    # (AQI高值，AQI类型：数值)
    aqi = (int(highaqi), aqi['PriPollutantD']+u': '+aqi['AQID'])
    return aqi

def forecastInfo(weather):
    forecast_info = {}
    #提取城市和时间
    forecast_info['date_and_city'] = weather['item']['title']
    #返回今日和明日天气
    forecast_info['forecast'] = (weather['item']['forecast'][0],weather['item']['forecast'][1])
    return forecast_info

def tempCompare(forecast_info,aqi):
    is_weather_changed = 0
    tody_all = forecast_info['forecast'][0]
    tomorrow_all = forecast_info['forecast'][1]

    #比较今明温度
    lowcondition_change = int(tomorrow_all['low']) - int(tody_all['low'])
    highcondition_change = int(tomorrow_all['high']) - int(tody_all['high'])

    #判断是否是雨雪天气
    bad_weather = ['pour', 'snow', 'rain', 'showers', 'sleet', 'hail', 'storm', 'blizzard']
    is_bad_weather = 0
    for i in bad_weather:
        if i in tomorrow_all['text'].lower():
            is_bad_weather = 1

    if lowcondition_change > 3 or lowcondition_change < -3:
        is_weather_changed = 1
    elif highcondition_change > 3 or highcondition_change < -3:
        is_weather_changed = 1
    elif is_bad_weather:
        is_weather_changed = 1
    elif aqi[0] > 200:
        is_weather_changed = 1
    else:
        pass
    return (is_weather_changed, lowcondition_change, highcondition_change, aqi)

if __name__ == '__main__':
    city = 'Beijing'
    query_weather = getWeather(city)
    forecast_info = forecastInfo(query_weather)
    try:
        aqi = getAqiforecast()
    except:
        aqi = (200, 'AQI: N/A')
    is_weather_changed, lowcondition_change, highcondition_change, aqi = tempCompare(forecast_info, aqi)
    if is_weather_changed:
        audience = u'@人形鼠昂天使心 @Ginni @沈楚桉'
        content = "Tomorrow(%s): %s, high around %sC (%+dC), low around %sC (%+dC). %s. %s. %s" % (
            forecast_info['forecast'][1]['date'],
            forecast_info['forecast'][1]['text'],
            forecast_info['forecast'][1]['high'],
            highcondition_change,
            forecast_info['forecast'][1]['low'],
            lowcondition_change,
            aqi[1],
            forecast_info['date_and_city'],
            audience,
            )
        # print content
        oauth.apply_access_token()
        oauth.client.post.statuses__update(status=content)


