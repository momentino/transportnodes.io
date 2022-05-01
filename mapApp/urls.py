# pages/urls.py

# URL : 
# prima parte : url, 
# seconda : vista associata all'url, 
# terza : nome dell'url che si da nei link in HTML
from django.urls import path
from django.urls import re_path
from .views import ContactUsView, GeneralAirportView, HomePageView
from .views import AirportsView
from .views import TrainStationsView
from .views import PortsView
from .views import TrafficView
from .views import TrackingView
from .views import AirportsCountryView
from .views import SpecificAirportView
from .views import ContactUsView
from .views import MessageSentView
from .views import search_ajax

from .views import SearchListView
urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('airports/', AirportsView.as_view(), name='airports'), 
    path('airports/<slug:param>/', GeneralAirportView.as_view(), name="general_airport"),
    path('airports/<slug:param>/arrivals/', SpecificAirportView.as_view(), name='specific_airport_arrivals'),
    path('airports/<slug:param>/departures/', SpecificAirportView.as_view(), name='specific_airport_departures'),
    path('airports/<slug:param>/weather/', SpecificAirportView.as_view(), name='specific_airport_weather'),  
    path('airports/<slug:param>/notam/', SpecificAirportView.as_view(), name='specific_airport_notam'), 
    path('trainstations/', TrainStationsView.as_view(), name='trainstations'), 
    path('ports/', PortsView.as_view(), name='ports'), 
    path('traffic/', TrafficView.as_view(), name='traffic'), 
    path('tracking/', TrackingView.as_view(), name='tracking'), 
    path('', SearchListView.as_view(), name='home'),
    path('contact-us/', ContactUsView.as_view(), name='contact-us'),
    path('message-sent/', MessageSentView.as_view(), name='message-sent'),
    path('ajaxsearch/', search_ajax, name='search_ajax'),
    path('airport_arrivals_data', SpecificAirportView.get_scheduled_arrivals, name='airport_arrivals_data'),
]