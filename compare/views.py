from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import loader, RequestContext
from pprint import pprint as pp
from accounts.models import UserInfo
from accounts.searchlog import save_to_log
from .weather import get_local_time, query_api
import math
import numpy as np
from datetime import datetime

from bokeh.plotting import figure, output_file, show 
from bokeh.embed import components
from bokeh.models import ColumnDataSource, LinearAxis, Range1d


def index(request):
    """
    POST/GET - /, 
    POST: Pass two arguments to openweathermap API and get weather info and save to search history
    GET: 
    """
    data = []
    error = None
    query_log = []
    if request.method == 'POST':
        city1 = request.POST['compareinput1']
        city2 = request.POST['compareinput2']
        if not city1 or not city2:
            error = 'Must pick 2 cities'
            return render(request, 'compare/index.html', {
                'city1': city1,
                'city2': city2,
                'error': error,
                })
        for c in (city1, city2):
            resp = query_api(c)
            pp(resp)
            if resp and resp['cod'] != '404':
                resp['sunrise'] = get_local_time(resp['sys']['sunrise'], resp['sys']['country'], resp['name'])
                resp['sunset'] = get_local_time(resp['sys']['sunset'], resp['sys']['country'], resp['name'])
                data.append(resp)
        if len(data) != 2:
            error = 'Did not get complete response from Weather API'
        else:
            save_to_log(request, [city1, city2])
        if request.user.is_authenticated:
            queries = UserInfo.objects.get(user = request.user)
            query_log = queries.search_history
        return render(request, 'compare/index.html', {
            'city1': city1,
            'city2': city2,
            'data': data,
            'error': error,
            'query_log': query_log,
            })
    else:
        if request.user.is_authenticated:
            queries = UserInfo.objects.get(user = request.user)
            query_log = queries.search_history
        return render(request, 'compare/index.html', {'query_log': query_log})

def forecast(request, city_name):
    """
    GET - /forecast/<city_name>, constructs interactive bokeh plot from city name taken from
    the request object
    """
    error = None
    x = []
    y1 = []
    y2 = []
    max_temp = 0
    max_wind = 0
    resp = query_api(city_name, data_type='forecast')
    if resp and resp['cod'] != 404:
        for r in resp['list']:
            dt = datetime.strptime(r['dt_txt'], '%Y-%m-%d %H:%M:%S')
            x.append(str(dt.day)+"."+str(dt.month)+" - "+" "+str(dt.hour)+":00")
            y1.append(r['main']['temp'])
            y2.append(r['wind']['speed'])
            if r['main']['temp'] > max_temp: max_temp = r['main']['temp']
            if r['wind']['speed'] > max_wind: max_wind = r['wind']['speed']

    title = '5 day weather forecast for - '+city_name.title()
    source = ColumnDataSource(data=dict(x=x, y1=y1, y2=y2))
    TOOLTIPS = [
        ('Day/Time', '@x'[0:4]),
        ('Temperature', '@y1 C°'),
        ('Wind', '@y2 m/s')
    ]
    plot = figure(
        title=title,
        x_range=x,
        y_range=(0,int(math.ceil(max_temp / 10.0)) * 10),
        x_axis_label = 'Dates',
        y_axis_label = 'C°',
        plot_width = 1000,
        plot_height = 400,
        toolbar_location=None,
        tooltips = TOOLTIPS
        )
    plot.xaxis.major_label_orientation = np.pi/4
    plot.line(x='x', y='y1', source=source, legend='Temperature', line_width=2, color='red')
    plot.extra_y_ranges = {'windspeed_range': Range1d(start=0, end=int(math.ceil(max_wind / 10.0)) * 10)}
    plot.add_layout(LinearAxis(y_range_name='windspeed_range'), 'right')
    plot.circle(x='x', y='y2', source=source, legend='WindSpeed', y_range_name='windspeed_range', color='blue')

    script, div = components(plot)
    return render(request, 'compare/forecast.html', {
        'script': script, 
        'div': div, 
        'city_name': city_name,
        })

def handler404(request, *args, **argv):
    """Handle 404 errors"""
    response = render_to_response('404.html', {},
        context_instance=RequestContext(request))
    response.status_code = 404
    return response


def handler500(request, *args, **argv):
    """Handle 500 errors"""
    response = render_to_response('500.html', {},
        context_instance=RequestContext(request))
    response.status_code = 500
    return response

