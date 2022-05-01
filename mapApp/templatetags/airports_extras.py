from django.http import QueryDict
from django import template
from datetime import datetime
from dateutil import tz
from django.utils import datastructures
import timezonefinder, pytz

register = template.Library()

@register.filter(name='rimuoviTrattiniBassi')
def rimuoviTrattiniBassi(value):
    # Converte "_" in " "
    return value.replace("_", " ")

#filtro per sostituire caratteri nei template
@register.filter(name='replace')
def replace(value, args):
    qs = QueryDict(args)
    #before è il primo parametro ovvero il valore che vogliamo rimpiazzare, after è il secondo parametro ovvero il carattere rimpiazzante
    if 'before' in qs and 'after' in qs:
        return value.replace(qs['before'], qs['after'])
    else:
        return value
#filtro per convertire da unix timestamp a orario locale, fornendo in input delle coordinate e un timestamp
@register.filter(name="unixtolocaltime")
def unixlocaltime(unixtimestamp,args):
    
    qs = QueryDict(args)
    #controlliamo se i parametri di latitudine e logitudine sono stati inseriti
    if 'long' in qs and 'lat' in qs:
        
        lt=(float)(qs["lat"])
        long=(float)(qs["long"])
        #otteniamo dal timestamp fornito come parametro la data (UTC)
        date = datetime.utcfromtimestamp(unixtimestamp)
        tf = timezonefinder.TimezoneFinder()

        # Otteniamo la timezone alle coordinate fornite come parametri
        timezone_str = tf.certain_timezone_at(lat=lt, lng=long)
        old_timezone = pytz.utc
        new_timezone = pytz.timezone(timezone_str)
        #convertiamo la data da utc alla nuova timezone
        new_timezone_timestamp = old_timezone.localize(date).astimezone(new_timezone) 
        return str(new_timezone_timestamp.strftime("%b %d %H:%M:%S"))

#filtro per convertire da unix timestamp a orario UTC
@register.filter(name="unixtoutctime")
def unixtoutctime(s):
    return datetime.utcfromtimestamp(s).strftime('%Y-%m-%d %H:%M:%S') # datetime.datetime.fromtimestamp(s)