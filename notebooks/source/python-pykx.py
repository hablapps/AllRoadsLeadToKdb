

###############################
### EMBRACING PYKX (Step 1) ###
###############################

import pykx as kx
from sklearn.linear_model import LinearRegression
from scipy.spatial.distance import cdist

kx.q('system"c 200 250"')

# We assume a pykx object loaded somehow...
weather_ori_kx = kx.q.read.csv('../data/abr_meteo23.csv', types='IIII****FSFSFSFSFSFSFSFSFSFSFSFSFSFSFSFSFSFSFSFSFSFSFSFS', delimiter=';', as_table=True)

# Instead of turning into pandas, we start adapting expressions

weather_ori_kx = kx.q.xcol({'ANO': 'year', 'MES': 'month', 'DIA': 'day'}, weather_ori_kx)
weather_ori_kx = kx.q.qsql.update(weather_ori_kx, columns = {'FECHA': '"D"$(raze\')flip(year;month;day)'})
weather_ori_kx = kx.q.qsql.delete(weather_ori_kx, ['year', 'month', 'day', 'PUNTO_MUESTREO'])

cols = kx.q.cols(weather_ori_kx)
def xexpr(pattern):
  xcols = cols[kx.q.where(kx.q.like(cols, pattern))]
  xsel = kx.q.sv(b";", kx.q.string(xcols)).py().decode("utf-8")
  return (xcols, 'flip(' + xsel + ')')

hora = 'count[i]#enlist 01:00*til 24'
(hcols, valor) = xexpr(b'H*')
(vcols, valid) = xexpr(b'V*')

weather = kx.q.qsql.update(weather_ori_kx, columns = {'HORA': hora, 'VALOR': valor, 'VALID': valid})
weather = kx.q.qsql.delete(weather, columns = kx.q.raze(hcols,vcols).py())
weather = kx.q.ungroup(weather)
weather = kx.q('_', kx.q('1#`VALID'), kx.q.qsql.select(weather, where = 'VALID=`V'))

magnitude = {80:"ULTRAVIOLETA", 
             81:"VIENTO", 
             82:"DIRECCION", 
             83:"TEMPERATURA", 
             86:"HUMEDAD", 
             87:"PRESION", 
             88:"SOLAR", 
             89:"PRECIPITACION"}
u = list(magnitude.values())
u = kx.q('`$', kx.q.string(u))
kx.q.set('magnitude', magnitude)
df1 = kx.q.qsql.update(weather, columns = {'MAGNITUD': 'magnitude "j"$MAGNITUD'})
weather = kx.q('{exec x#MAGNITUD!VALOR by FECHA,HORA,ESTACION from y}', u, df1)
wstation = kx.q.read.csv('../data/Estaciones_control_datos_meteorologicos.csv', types=" IFF", delimiter=";", as_table=True)
wstation = kx.q.xcol({'CODIGO_CORTO': 'ESTACION'}, kx.q.xkey('CODIGO_CORTO', wstation))
wjoin = kx.q.lj(weather, wstation)
wjoin = kx.q.qsql.delete(wjoin, columns = ['ESTACION'])
wjoin = kx.q('xkey[`FECHA`HORA`LATITUD`LONGITUD]', wjoin)

pmed = kx.q.read.csv('../data/pmed_ubicacion_04-2023.csv', types = "SII**FFFF", delimiter = ";", as_table=True)
pmedpos = kx.q('`longitud`latitud#', pmed)
wstapos = kx.q('`LONGITUD`LATITUD#0!', wstation)
dist = kx.toq(cdist(pmedpos.pd(), wstapos.pd()))
ids = kx.q.each(kx.q('{first where x=min x}'), dist)
pmedest = kx.q('^', pmed, kx.q('0!', wstation)[ids])
pmedest = kx.q.qsql.delete(pmedest, columns = ['LONGITUD', 'LATITUD'])

traffic = kx.q.read.csv('../data/04-2023.csv', types = "IPSIIIISI", delimiter = ";", as_table = True)
trapmedest = kx.q.lj(traffic, kx.q.xkey('id', pmedest))

weather = kx.q.qsql.update(weather, {'fecha': 'FECHA+HORA'})
ajoin = kx.q.aj(kx.q('`ESTACION`fecha'), trapmedest, kx.q("0!", weather))

comp = kx.q.qsql.select(ajoin,
                        columns = {'hour': 'HORA',
                                   'weekday': '("d"$fecha)mod 7',
                                   'estacion': 'ESTACION',
                                   'direccion': 'DIRECCION',
                                   'humedad': 'HUMEDAD',
                                   'precipitacion': 'PRECIPITACION',
                                   'carga': 'carga',
                                   'temperatura': 'TEMPERATURA',
                                   'viento': 'VIENTO',
                                   'presion': 'PRESION',
                                   'solar': 'SOLAR'})

loads = kx.q.qsql.select(comp,
                         columns = {'carga_avg': 'avg carga'},
                         by = ['hour', 'weekday', 'estacion'])

temps = kx.q.qsql.select(comp,
                         columns = {'temps_avg': 'avg temperatura'},
                         by = ['hour'])

comp = kx.q("3!", comp)
comp = kx.q("1!0!", kx.q.lj(comp, loads))
comp = kx.q("0!", kx.q.lj(comp, temps))

comp = kx.q.qsql.update(comp,
                        columns = {'carga': 'carga-carga_avg',
                                   'temperatura': 'temperatura-temps_avg'})

comp = kx.q('0^', comp)

# distrito = kx.q.read.csv("Distritos.csv", types = "JFFJJSSS", delimiter=";", as_table=True)
distrito = kx.q('1!("JFFJJSSS";enlist ";")0:`$":../data/Distritos.csv"')

rainyJam = kx.q.qsql.select(ajoin,
                            columns = {'PRECIPITACION': 'avg PRECIPITACION',
                                       'TEMPERATURA': 'avg TEMPERATURA',
                                       'CARGA': 'avg carga'},
                            by = {'OBJECTID': 'distrito'},
                            where = ['carga>75', 'PRECIPITACION>0'])

from IPython.core.debugger import set_trace;set_trace()

rainyJam = kx.q.lj(rainyJam, distrito)
rainyJam = kx.q.qsql.select(rainyJam, columns = ['NOMBRE', 'PRECIPITACION', 'TEMPERATURA', 'CARGA'])

print(rainyJam)

comp = comp.pd()

def modelo(tabla):
    X = tabla[["direccion", "humedad", "precipitacion", "presion", "solar", "temperatura", "viento" ]].to_numpy()
    y = tabla["carga"].to_numpy().ravel()
    reg = LinearRegression().fit(X, y)
    
    return reg.score(X, y)

print(modelo(comp))