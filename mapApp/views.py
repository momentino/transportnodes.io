# pages/views.py

 # Spiegazione view di Filippo Momentè
 # Qui si trovano le viste, le quali contengono la logica che sta dietro alle pagine del template




from django.views.generic import TemplateView

from mapApp.models import Country
from mapApp.models import Airports
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.list import ListView
from django.views.decorators.http import  require_http_methods
import string
import requests
import urllib3
import xmltodict
import json
from datetime import datetime,timedelta
from .forms import ContactForm
from django.views.generic.edit import FormView
from mapApp.airports.AirportArrivals import AirportArrivals

class HomePageView(TemplateView):
    template_name = 'home.html'
    
# vista della pagina che contiene l'elenco delle nazioni e il numero di aereoporti per ogni nazione
class AirportsView(TemplateView): 
    template_name = 'airports.html'
    
    # funzione che restituisce tutte le nazioni dal database
    def get_queryset(self) :
        queryset = Country.objects.all()
        return queryset

    # funzione che restituisce tutti gli aereoporti dal database
    def get_airport_queryset(self):
        airport_queryset = Airports.objects.all()
        return airport_queryset

    # funzione che costruisce e restituisce il contesto che viene utilizzato nella pagina per 
    # poter mostrare le nazioni e il numero di aereoporti per ogni nazione
    def get_context_data(self, **kwargs):
        context = super(AirportsView, self).get_context_data(**kwargs) #qui costruiamo il contesto
        context["page_title"] = "Airports by country · Transportnodes.io" #titolo della pagina
        # prendiamo gli iso delle nazioni di cui abbiamo almeno 1 aereoporto nel database
        # e creiamo una lista in modo da poter avere la lista delle nazioni di cui abbiamo aereoporti
        # questo serve per evitare di portarci nel contesto nazioni di cui non abbiamo aereoporti. 
        # Queste non ci interessano.
        countries_with_airports_queryset = self.get_airport_queryset().values('iso_country').distinct()
        countries_with_airports_list = []
        for j in countries_with_airports_queryset:
            countries_with_airports_list.append(j["iso_country"].lower())

        # facciamo un ciclo per ogni lettera dell'alfabeto perchè vogliamo dividere le nazioni in ordine alfabetico e per lettera
        for i in string.ascii_uppercase:
            # creiamo un elemento del contesto per ogni lettera e prendiamo i valori dal database delle nazioni che iniziano 
            # per quella lettera e per le quali abbiamo almeno un aereoporto memorizzato
            context[i+"_list"] = self.get_queryset().filter(nicename__startswith=i, iso__in=countries_with_airports_list).values()
            # per ogni nazione poi aggiungiamo il conto degli aereoporti
            for j in context[i+"_list"]:
                # il conto degli aereoporti (SELECT COUNT(*)...GROUP BY iso , 
                # dove iso dell'aereoporto è uguale all' iso della nazione )
                j['count'] = str(self.get_airport_queryset().filter(iso_country=j["iso"].upper()).count())
                if(j['count'] == "1"):
                    j['count'] = j['count'] + " airport"
                else: 
                    j['count'] = j['count'] + " airports"
        return context

class AirportsCountryView(TemplateView):
    template_name = 'airport-countries/airport-country.html'
# funzione che restituisce tutte le nazioni dal database
    def get_queryset(self) :
        queryset = Country.objects.all()
        return queryset

    # funzione che restituisce tutti gli aereoporti dal database
    def get_airport_queryset(self):
        airport_queryset = Airports.objects.all()
        return airport_queryset
    
    # costruzione del contesto
    def get_context_data(self, **kwargs):
        context = super(AirportsCountryView, self).get_context_data(**kwargs) #qui costruiamo il contesto
         

        # prendiamo il parametro country contenuto nell'URL e lo usiamo per ottenere nome, ISO e aereoporti associati 
        # alla nazione
        
        
        context['country'] = self.kwargs['param']
        
        context['nicename'] = self.get_queryset().filter(urlname__iexact=context['country']).values("nicename")
        
        context['nicename'] = context['nicename'][0]['nicename']
        context['iso'] = self.get_queryset().filter(urlname__iexact=context['country']).values("iso")
        context["iso"] = context["iso"][0]["iso"] #prendo il valore dell'iso dato che il risultato della query sopra era {'iso':'af'}
        for i in string.ascii_uppercase:
            context[i+'_airports'] = self.get_airport_queryset().filter(name__startswith=i, iso_country__iexact=context["iso"]).values("name","iata_code","icao_code","url_name").order_by("name")
        
        context["page_title"] = "Airports in " + context["nicename"] + " · Transportnodes.io" #titolo della pagina
        return context





class SpecificAirportView(TemplateView):
        template_name = 'specific-airport/specific-airport.html'
        # funzione che restituisce tutte le nazioni dal database
        def get_queryset(self) :
            queryset = Country.objects.all()
            return queryset

        # funzione che restituisce tutti gli aereoporti dal database
        def get_airport_queryset(self):
            airport_queryset = Airports.objects.all()
            return airport_queryset
        
        #funzione che gestisce connessione all'api per mostrare il meteo attuale nella pagina
        def connect_to_openweather_api(self,latitude, longitude):
            api_key = ""
            lat = latitude
            lon = longitude
            #cerchiamo il tempo attuale nel luogo delle coordinate dell'aereoporto
            url = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&appid=%s&units=metric" % (lat, lon, api_key)

            response = requests.get(url)
            data = json.loads(response.text)
            return data

        def get_aviation_weather_data(self,icao):
            url = "https://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&stationString=" + icao.upper() +"&hoursBeforeNow=72"

            http = urllib3.PoolManager()

            response = http.request('GET', url)
            try:
                data = xmltodict.parse(response.data, attr_prefix='', cdata_key='')
                
            except:
                print("Failed to parse xml from response (%s)")
            return data

        def get_notam(self,icao):
            

            data = {
            'grant_type': 'client_credentials',
            'client_id': '',
            'client_secret': ''
            }

            auth_response = requests.post('https://api.autorouter.aero/v1.0/oauth2/token', data=data)
            data = json.loads(auth_response.text)
            access_token = data["access_token"]

            headers = {
                'Authorization': 'Bearer ' + access_token,
            }
           # http = urllib3.PoolManager()
           # url = "https://api.autorouter.aero/v1.0/notam?itemas=['"+ icao +"']&offset=0&limit=10"
           # response = http.request('GET', url)
            notam_response = requests.get('https://api.autorouter.aero/v1.0/notam?itemas=["'+ icao +'"]&offset=0&limit=10', headers=headers)
            notam_data = json.loads(notam_response.text)
            return notam_data
        
        @require_http_methods(['GET'])
        def get_scheduled_arrivals(request):
            iata = request.GET.get('iata')
            icao = request.GET.get('icao')
            name= request.GET.get('name')
            today=request.GET.get('today')
            tomorrow=request.GET.get('tomorrow')


            
          
            airport_schedule = AirportArrivals(iata,icao,name,today,tomorrow)
            return JsonResponse(airport_schedule.get_schedule(), safe=False)
         
        def set_today_tomorrow(self,context):
            today = datetime.utcnow()
            tomorrow = datetime.utcnow() + timedelta(days=1)
            today_day = today.strftime("%d")
            today_month = (today.strftime("%B"))[0:3]
            today_month = today_month.upper()
            tomorrow_day = tomorrow.strftime("%d")
            tomorrow_month = (tomorrow.strftime("%B"))[0:3]
            tomorrow_month = tomorrow_month.upper()


            weekDays = ("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")
            today_weekday=today.weekday()
            tomorrow_weekday=tomorrow.weekday()
            today_weekday = weekDays[today_weekday]
            tomorrow_weekday = weekDays[tomorrow_weekday]
            context["today_formatted"] = today_weekday+", "+today_day+" "+today_month.capitalize()
            context["tomorrow_formatted"] = tomorrow_weekday+", "+tomorrow_day+" "+tomorrow_month.capitalize()

            return context
        def set_METAR_info(self,context):
            # connessione all'API per avere in risposta il meteo alle coordinate dell'aereoporto usando OpenWeatherMap API
            data = self.connect_to_openweather_api(context["airport"][0]["latitude_deg"], context["airport"][0]["longitude_deg"])
            # connessione al servizione del meteo per l'aviazione statunitense per i METAR
            weather_data = self.get_aviation_weather_data(context["icao"])

            
            # Verifichiamo se è giorno o notte (usando OpenWeatherMap API)
            if(data["current"]["dt"]<data["current"]["sunset"]):
                context["airport_weather_day_or_night"] = "day"
                    
            else:
                context["airport_weather_day_or_night"] = "night"
            
            # Se ci sono errori relativi al recupero dei METAR sull'aereoporto
            # oppure la chiamata all'api dei METAR restituisce 0 risultati, usiamo OpenWeatherMap
            if( not( weather_data["response"]["errors"] == None) or (weather_data["response"]["data"]["num_results"] == "0")):
                
                # inseriamo nel contesto i dati relativi a temperatura e tipologia del meteo (Clear, Cloudy, Rainy...)

                temp = data["current"]["temp"]
                weather_type = data["current"]["weather"][0]["main"]
                weather_id = data["current"]["weather"][0]["id"]
                wind_speed = data["current"]["wind_speed"]
                wind_direction = data["current"]["wind_deg"]
                wind_beaufort = round(0.725*(data["current"]["wind_speed"])**(2/3))
                context["airport_weather_temp"] = temp
                context["airport_weather_type"] = weather_type
                context["airport_weather_id"] = weather_id
                context["airport_weather_wind_speed"] = wind_speed
                context["airport_weather_wind_direction"] = wind_direction
                context["airport_weather_wind_beaufort"] = wind_beaufort
                context["weather_icon"] = "na"
                context["weather_desc"] = "N/A"
            else:
                
                context["airport_metar_story"] = weather_data

                # Gestione caso in cui le informazioni relative al vento non sono disponibili
                try:
                    wind_speed = weather_data["response"]["data"]["METAR"][0]["wind_speed_kt"] 
                    wind_direction = int(weather_data["response"]["data"]["METAR"][0]["wind_dir_degrees"]) 
                    wind_beaufort = round(0.725*(round(int(weather_data["response"]["data"]["METAR"][0]["wind_speed_kt"])))**(2/3))
                except:
                    wind_speed = "N/A"
                    wind_direction = "N/A"
                    wind_beaufort = "na"

                temp = weather_data["response"]["data"]["METAR"][0]["temp_c"] + " °C"
                context["airport_weather_wind_speed"] = wind_speed
                context["airport_weather_wind_direction"] = wind_direction
                context["airport_weather_wind_beaufort"] = wind_beaufort
                
                context["airport_weather_temp"] = temp

                # controllo per mostrare informazioni corrette in caso di vento variabile
                # il fenomeno non viene catturato automaticamente ed è necessario impostare un icona e la scritta "VARIABLE"
                # a mano
                # In caso la direzione del vento sia 0°, ma la velocità non è zero, sta a indicare nelle API che il 
                # vento è variabile.

                if((context["airport_weather_wind_direction"] == 0) and (context["airport_weather_wind_speed"] != 0)):
                    context["airport_weather_wind_direction"] = "VARIABLE"

                # decodifica fenomeno meteo
                intensity = {
                    "-" : "Weak",
                    "":"",
                    "+":"Strong",
                    "VC":"Nearby"}
                descriptor = { 
                    "MI":"Shallow",
                    "BC": "Patches",
                    "PR":"Partial",
                    "DR":"Low drifting", 
                    "BL": "Blowing",
                    "SH":"Showers",
                    "TS":"Thunderstorm",
                    "FZ":"Freezing/Supercooled"}
                   
                precipitation = {
                    "DZ":{
                        "weather" : "Drizzle",
                        "icon": "sprinkle"},
                    "RA":{
                        "weather": "Rain",
                        "icon": "rain"},
                    "SN":{
                        "weather":"Snow",
                        "icon": "snow"},
                    "SG":{
                        "weather": "Snow grains",
                        "icon":"snow"},
                    "IC":{
                        "weather":"Ice crystals",
                        "icon":"snowflake-cold"},
                    "PL":{
                        "weather":"Ice pellets",
                        "icon":"sleet"},
                    "GR":{
                        "weather":"Hail",
                        "icon":"hail"},
                    "GS":{
                        "weather":"Small hail",
                        "icon":"hail"},
                    "UP":{
                        "weather":"Undefined precipitation",
                        "icon":"na"
                        }
                    }
                obscuration = {
                    "BR":{
                        "weather":"Mist",
                        "icon":"fog"},
                    "FG":{
                        "weather":"Fog",
                        "icon":"fog"},
                    "FU":{
                        "weather":"Smoke",
                        "icon":"smoke"},
                    "VA":{
                        "weather":"Volcanic ash",
                        "icon":"volcano"},
                    "DU":{
                        "weather":"Widespread dust",
                        "icon":"dust"},
                    "SA":{
                        "weather":"Sand",
                        "icon":"sandstorm"},
                    "HZ":{
                        "weather":"Haze",
                        "icon":"fog"}}
                other = {
                    "PO":{
                        "weather":"Dust/Sand whirls",
                        "icon":"sandstorm"},
                    "SQ":{
                        "weather":"Squalls",
                        "icon":"rain-wind"},
                    "FC":{
                        "weather":"Funnel cloud/s",
                        "icon":"tornado"},
                    "SS":{
                        "weather":"Sandstorm",
                        "icon":"sandstorm"},
                    "DS":{
                        "weather":"Duststorm",
                        "icon":"sandstorm"}}
                
                # Se abbiamo un fenomeno meteo codificato nella wx_string (quelli dei codici presenti nei dizionari, costruiamo la descrizione del fenomeno e assegniamo il valore all'icona)
                icon = ""
                desc = ""
                if("wx_string" in weather_data["response"]["data"]["METAR"][0]):
                    weather_descriptor = weather_data["response"]["data"]["METAR"][0]["wx_string"]
                    i = 0
                    while i<(len(weather_descriptor)-1):
                        
                        if(weather_descriptor[i] in intensity):
                            desc = desc + " " + intensity[weather_descriptor[i]]
                            i = i +1
                        elif((weather_descriptor[i] + weather_descriptor[i+1]) in intensity):
                            desc = desc + " " + intensity[weather_descriptor[i] + weather_descriptor[i+1]]
                            i = i + 2
                        elif((weather_descriptor[i] + weather_descriptor[i+1]) in descriptor):
                            desc = desc + " " + descriptor[weather_descriptor[i] + weather_descriptor[i+1]]
                            i = i + 2
                        elif((weather_descriptor[i] + weather_descriptor[i+1]) in precipitation):
                            
                            desc = desc + " " + precipitation[weather_descriptor[i] + weather_descriptor[i+1]]["weather"]
                            icon = precipitation[weather_descriptor[i] + weather_descriptor[i+1]]["icon"]
                           
                            i = i + 2
                        elif((weather_descriptor[i] + weather_descriptor[i+1]) in obscuration):
                            desc = desc + " " + obscuration[weather_descriptor[i] + weather_descriptor[i+1]]
                            icon = obscuration[weather_descriptor[i] + weather_descriptor[i+1]][obscuration[weather_descriptor[i] + weather_descriptor[i+1]]]    
                            i = i + 2
                        elif((weather_descriptor[i] + weather_descriptor[i+1]) in other):
                            desc = desc + " " + other[weather_descriptor[i] + weather_descriptor[i+1]]
                            icon = other[weather_descriptor[i] + weather_descriptor[i+1]][other[weather_descriptor[i] + weather_descriptor[i+1]]]   
                            i = i + 2
                    print(desc)
                if(("wx_string" not in weather_data["response"]["data"]["METAR"][0]) or (desc !="")):
                    
                    # se non abbiamo un fenomeno atmoferico al momento, controlliamo la condizione delle nubi, costruendo la descrizione e l'icona
                    
                    
                    try:
                        for sky_cond in weather_data["response"]["data"]["METAR"][0]["sky_condition"]:
                            if (sky_cond["sky_cover"] == "CAVOK"):
                                desc = "Ceiling and visibility OK"
                                if ( context["airport_weather_day_or_night"] == "day"):
                                    icon = "day-sunny"
                                else:
                                    icon = "night-clear"
                            elif (sky_cond["sky_cover"] == "OVC"):
                                if(desc == ""):
                                    desc = "Overcast"
                                icon= "cloud"
                            elif (sky_cond["sky_cover"] == "FEW"):
                                if(desc == ""):
                                    desc = "Few clouds"
                                icon = context["airport_weather_day_or_night"] + "-" +"cloudy"
                            elif (sky_cond["sky_cover"] == "BKN"):
                                if(desc == ""):
                                    desc = "Broken clouds"
                                icon = "cloud"
                            elif (sky_cond["sky_cover"] == "SCT"):
                                if(desc == ""):
                                    desc = "Scattered clouds"
                                icon = context["airport_weather_day_or_night"] + "-" +"cloudy"
                    except:
                        sky_cond = weather_data["response"]["data"]["METAR"][0]["sky_condition"]["sky_cover"]
                        
                        if (sky_cond == "CAVOK"):
                            if(desc == ""):
                                desc = "Ceiling and visibility OK"
                            if ( context["airport_weather_day_or_night"] == "day"):
                                icon = "day-sunny"
                            else:
                                icon = "night-clear"
                        elif (sky_cond == "OVC"):
                            if(desc == ""):
                                desc = "Overcast"
                            icon= "cloud"
                        elif (sky_cond == "FEW"):
                            if(desc == ""):
                                desc = "Few clouds"
                            icon = context["airport_weather_day_or_night"] + "-" +"cloudy"
                        elif (sky_cond == "BKN"):
                            if(desc == ""):
                                desc = "Broken clouds"
                            icon = "cloud"
                        elif (sky_cond == "SCT"):
                            if(desc == ""):
                                desc = "Scattered clouds"
                            icon = context["airport_weather_day_or_night"] + "-" +"cloudy"
            
                   
                
                context["weather_icon"] = icon
                
                context["weather_desc"] = desc
                return context

        # costruzione del contesto
        def get_context_data(self, **kwargs):
            context = super(SpecificAirportView, self).get_context_data(**kwargs) #qui costruiamo il contesto
            
            # imposta data di oggi e di domani formattata
            self.set_today_tomorrow(context)

            # prendiamo il parametro country contenuto nell'URL e lo usiamo per ottenere nome, ISO e aereoporti associati 
            # alla nazione
            context['icao'] = (self.kwargs['param']).upper()
            
            context['airport'] = self.get_airport_queryset().filter(icao_code__iexact=context["icao"]).values()

            # Costruzione titolo pagina
            if(context["airport"][0]["iata_code"] != ""):
                context["page_title"] = context["airport"][0]["name"] + " (" + context["airport"][0]["icao_code"] + "/" + context["airport"][0]["iata_code"]  +")" + "· Transportnodes.io" #titolo della pagina
            else:
                context["page_title"] = context["airport"][0]["name"] + " (" + context["airport"][0]["icao_code"] +")" + "· Transportnodes.io" #titolo della pagina
            
            # inseriamo le nazioni
            context['country'] = self.get_queryset().filter(iso__iexact=(context["airport"][0]["iso_country"]).lower()).values("nicename")

            # inseriamo l'altitudine dell'aereoporto convertita da piedi a metri
            
            if(context["airport"][0]["elevation_ft"] != ""):
                context['elevation_m'] = round(float(context["airport"][0]["elevation_ft"])*0.3048,2)
           
           
            self.set_METAR_info(context)
            # Per poter fornire nelle varie sezioni della pagina dell'aereoporto le informazioni separatemente
            # Controlliamo l'url
            current_url = self.request.resolver_match.url_name
            if( current_url == "specific_airport_notam"):
                context["notam_data"] = self.get_notam(context["airport"][0]["icao_code"])
            return context  

class GeneralAirportView(TemplateView):
        
        def get(self, *args, **kwargs):
            airport_queryset = Airports.objects.all()
            country_queryset = Country.objects.all()
            
            urlname = country_queryset.filter(urlname__iexact=kwargs["param"]).values("urlname")
        
            icao = airport_queryset.filter(icao_code__iexact=kwargs["param"]).values("icao_code")
            if (urlname and kwargs["param"] == urlname[0]["urlname"]):
                return AirportsCountryView.as_view()(self.request,**kwargs)            
            elif (not urlname and kwargs["param"].upper() == icao[0]["icao_code"]):
                return SpecificAirportView.as_view()(self.request,**kwargs) 
class TrainStationsView(TemplateView): 
    template_name = 'trainstations.html'

class PortsView(TemplateView): 
    template_name = 'ports.html'

class TrafficView(TemplateView): 
    template_name = 'traffic.html'

class TrackingView(TemplateView): 
    template_name = 'tracking.html'

class SearchListView(ListView):
    model = Airports
    template_name = 'home.html'

    def get_context_data(self, *args, **kwargs):
        context = super(SearchListView, self).get_context_data(*args, **kwargs)
        context['query'] = self.request.GET.get('q')
        return context

    def get_queryset(self, *args, **kwargs):
        name_qs = super(SearchListView, self).get_queryset(*args, **kwargs)
        query = self.request.GET.get('q')

        if query:
            user_qs = self.model.objects.filter(
                Q(name__icontains=query)
                )
        return name_qs


class ContactUsView(FormView):
    template_name = 'contact-us.html'
    form_class = ContactForm
    success_url = '/message-sent/'
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
          
        # Se il form è valido, invia email con il contenuto del form
        form.send_email()
        return super().form_valid(form)
   

class MessageSentView(TemplateView):
    template_name = 'message-sent.html'
    
        
@require_http_methods(['GET'])
def search_ajax(request):
    q = request.GET.get('q')
    data = {}

    if q:
        names = Airports.objects.filter(name__icontains=q).values("name")
        data = [{'name': name["name"]} for name in names]
    return JsonResponse(data, safe=False)