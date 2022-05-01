
from django.db.models.query import EmptyQuerySet, QuerySet
from mapApp.models import FlightData
from mapApp.models import Airports
from datetime import datetime, timedelta
import timezonefinder, pytz
# Classe che si occupa di gestire i dati relativi agli arrivi in un aereoporto
class AirportArrivals:
    iata = ""
    icao = ""
    today = ""
    tomorrow = ""
   
    def __init__(self, iata, icao, name, today, tomorrow):
        self.iata = iata
        self.icao = icao
        self.name = name
        self.today = today
        self.tomorrow = tomorrow

        
        pass
    def get_flight_queryset(self):
        flight_queryset = FlightData.objects.all()
        return flight_queryset
    def get_airport_queryset(self):
        airport_queryset = Airports.objects.all()
        return airport_queryset
    def get_schedule(self):
        schedule = []
        # Se non ci sono errori nelle chiamate dell'API, appendi il risultato alla schedule generale
        try:
            f_queryset = self.get_flight_queryset().filter(arrival_arpt=self.icao).values()
            for f in f_queryset:
            

                airline = f["airline"]
                departure_arpt = f["departure_arpt"]
                acid = f["acid"]
                status = f["status"]
                aircraft = f["aircraft"]
                arr_fulltime = datetime.strptime(str(f["scheduled_arr_time"]), '%Y-%m-%d %H:%M:%S')
                est_arr_fulltime = ""

               
                if (str(f["est_arr_time"]) != 'None'):
                    
                    est_arr_fulltime = datetime.strptime(str(f["est_arr_time"]), '%Y-%m-%d %H:%M:%S')
                    
                
                today = datetime.strptime(str(datetime.today())[:10],'%Y-%m-%d')
                tomorrow = datetime.strptime(str(datetime.today() + timedelta(days=1))[:10],'%Y-%m-%d')
                
                # departure airport info
                dept_airport_info = self.get_airport_queryset().filter(icao_code=departure_arpt).values()
                # Action in case of unknown ICAO code regarding the departure airport
                if(dept_airport_info.count() == 0):
                    print("Non conosco "+departure_arpt)
                    dept_airport_name="UNREGISTERED"
                    dept_airport_iata="UNREGISTERED"
                else:
                    dept_airport_name = dept_airport_info[0]["name"]
                    dept_airport_iata = dept_airport_info[0]["iata_code"]
                
                # Generate right timezone
                this_airport_info = self.get_airport_queryset().filter(icao_code=self.icao).values("latitude_deg","longitude_deg")
                this_lat = this_airport_info[0]["latitude_deg"]
                this_long = this_airport_info[0]["longitude_deg"]
                tf = timezonefinder.TimezoneFinder()

                # From the lat/long, get the tz-database-style time zone name (e.g. 'America/Vancouver') or None
                timezone_str = tf.certain_timezone_at(lat=this_lat, lng=this_long)
                
                
                if timezone_str is None:
                    print ("Could not determine the time zone")
                else:
                    # Display the current time in that time zone
                    timezone = pytz.timezone(timezone_str)
                  
                    # set local time
                    arr_fulltime = arr_fulltime + timezone.utcoffset(arr_fulltime)
                    arr_date = str(arr_fulltime)[:10]
                    arr_time = str(arr_fulltime)[11:]

                    # Se tempo di arrivo stimato esiste allora impostalo col fuso orario corretto e imposta lo stato
                    if(est_arr_fulltime !="" and (est_arr_fulltime>datetime.utcnow())):
                        est_arr_fulltime = est_arr_fulltime + timezone.utcoffset(est_arr_fulltime)
                        print(est_arr_fulltime)
                        print(datetime.utcnow())
                        est_arr_time = str(est_arr_fulltime)[11:]

                        status = status + " "+est_arr_time
                    elif (est_arr_fulltime !="" and (est_arr_fulltime<=datetime.utcnow())):
                        status = "Arrived"
                # unknown airline
                if (airline == "XXX"):
                    
                    airline = ""

                # Check if flight is on time, late or very late
               
                if(est_arr_fulltime !=""):
                    print(est_arr_fulltime)
                    print(datetime.strptime(str(est_arr_fulltime + timedelta(minutes=20)),'%Y-%m-%d %H:%M:%S'))
                    est_arr_fulltime_on_time_offset = datetime.strptime(str(est_arr_fulltime + timedelta(minutes=10)),'%Y-%m-%d %H:%M:%S')
                    est_arr_fulltime_small_delay_offset = datetime.strptime(str(est_arr_fulltime + timedelta(minutes=60)),'%Y-%m-%d %H:%M:%S')
                if(est_arr_fulltime=="" or (arr_fulltime<est_arr_fulltime_on_time_offset)):
                    flight_time_desc = "On time"
                elif(arr_fulltime<est_arr_fulltime_small_delay_offset):
                    flight_time_desc="Small delay"
                else:
                    flight_time_desc="Delay"
                schedule_instance = {
                                'arrival_sort': str(arr_fulltime),
                                'airline': airline, 
                                'flight_no': acid, 
                                'aircraft': aircraft,
                                'from_iata': dept_airport_iata,
                                'from_name': dept_airport_name,
                                'from_icao': departure_arpt,
                                'arrival_date': str(arr_date),
                                'arrival_time': str(arr_time),
                                'flight_status': status,
                                'flight_time_desc': flight_time_desc

                }
                schedule.append(schedule_instance.copy())
                
            # aggiungo un istanza che serve ad inserire nella tabella il divisorio relativo alla data di oggi e domani
            schedule_instance = {
                                    'arrival_sort': str(today),
                                    'airline': "", 
                                    'flight_no': "", 
                                    'aircraft': "",
                                    'from_iata': "",
                                    'from_name': "",
                                    'from_icao': "",
                                    'arrival_date': "today",
                                    'arrival_time': "",
                                    'flight_status': "",
                                    'flight_time_desc':""
                                    }
            schedule.append(schedule_instance.copy())
            schedule_instance = {
                                    'arrival_sort': str(tomorrow),
                                    'airline': "", 
                                    'flight_no': "", 
                                    'aircraft': "",
                                    'from_iata': "",
                                    'from_name': "",
                                    'from_icao': "",
                                    'arrival_date': "tomorrow",
                                    'arrival_time': "",
                                    'flight_status': "",
                                    'flight_time_desc':""
                                    }
           
            schedule.append(schedule_instance.copy())
        except:
         
            pass
        # restituisco il dizionario ordinato per data
        return sorted(schedule, key=lambda k: k['arrival_sort'])