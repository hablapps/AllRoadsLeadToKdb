import re
import pandas as pd
import numpy as np
import csv 

import pandas as pd
import csv
import numpy as np
from scipy.spatial.distance import cdist
import re
import pandas as pd
import numpy as np
import csv

#########################
####  CARGA DE DATOS ####
#########################

#Cargar tabla trafico
trafico = pd.read_csv('04-2023.csv', sep = ";", quotechar='"', encoding='utf-8').dropna()

#Cargar tabla meteorológica
weather_ori = pd.read_csv('abr_meteo23.csv', sep = ";", quoting=csv.QUOTE_NONE, encoding='utf-8').dropna()

#Carga tablas estaciones y localizaciones
df3 = pd.read_csv('pmed_ubicacion_04-2023.csv', sep = ";", quoting=csv.QUOTE_NONE, encoding='utf-8').dropna()
df4 = pd.read_csv('Estaciones_control_datos_meteorologicos.csv', sep = ";", quoting=csv.QUOTE_NONE, encoding='latin-1')

# Cambiar Año/Mes/Dia por fecha
weather_ori = weather_ori.rename(columns={"ANO": "year", "MES": "month", "DIA":"day"})
weather_ori["FECHA"] = pd.to_datetime(weather_ori[["year", "month", "day"]])

###############################
####  PREPROCESADO TRÁFICO ####
###############################

# Quitar datos con errores
trafico= trafico[trafico["error"] == "N"]
# String a fecha
trafico['FECHA'] = pd.to_datetime(trafico['fecha'], errors='coerce')
# Eliminar columnas innecesarias
trafico.drop(["tipo_elem", "error", "intensidad", "ocupacion",  "vmed", "periodo_integracion", "fecha"], axis=1, inplace=True)
# Agrupar los datos de hora en hora
trafico.resample("1H", on="FECHA").mean()

############################
#### PREPROCESADO METEO ####
############################

# Separacion por horas de las H
weather= weather_ori.melt(id_vars=["ESTACION", "MAGNITUD", "FECHA"],
                          value_vars=[x for x in weather_ori.columns if re.match("^H", x)],
                          var_name="HORA")
# Separacion por horas de las V
weather2 = weather_ori.melt( value_vars=[x for x in weather_ori.columns if re.match("^V", x)])

# Entero a Hora
weather["HORA"] = weather["HORA"].str[1:]
weather["HORA"] = pd.to_timedelta(weather['HORA'].astype(int)-1, unit='h')
weather["FECHA"] = weather["FECHA"] + weather["HORA"]

# Seleccion de los valores == V
weather= weather[weather2["value"] == "V"]

# Mapeado de los datos de magnitud con los valores
df1 = weather.assign(MAGNITUD = weather["MAGNITUD"].map({80:"ULTRAVIOLETA",
                                                             81:"VIENTO",
                                                             82:"DIRECCION",
                                                             83:"TEMPERATURA",
                                                             86:"HUMEDAD",
                                                             87:"PRESION",
                                                             88:"SOLAR",
                                                             89:"PRECIPITACION"})) \
                                                             .MAGNITUD.str.get_dummies() \
                                                             .multiply(weather["value"], axis="index") \

# Unirlo a la anterior tabla
weather = pd.concat([weather, df1], axis=1).drop(['MAGNITUD', "value", "HORA"], axis=1)

# Agrupar por fecha, hora y estacion
weather = weather.groupby([ "FECHA", "ESTACION"]).sum().reset_index()

##################################
####  PREPROCESADO DISTANCIAS ####
##################################

# Calculo de distancias de sensores meteo y trafico
distancias = pd.DataFrame()
distancias["id"] = pd.Series([df3.index[np.argmin(x)] for x in cdist(df4[["LONGITUD", "LATITUD"]], df3[["\"longitud\"","\"latitud\""]])])
distancias["ESTACION"] = df4["CÓDIGO_CORTO"]

#######################
#### JUNTAR TABLAS ####
#######################

# Juntar tiempo con distancias
df5 = weather.merge(distancias, on="ESTACION")
# Juntar anterior con trafico
df5 = df5.merge(trafico, on=["id", "FECHA"])
# Renombra columna id por estacion_traf
df5.rename(columns={"id": 'estacion_traf'}, inplace=True)
# Añadir dia de la semana y hora
df5["WEEKDAY"] = df5["FECHA"].dt.weekday
df5["HOUR"] = df5["FECHA"].dt.hour

########################
#### MODELO SKLEARN ####
########################

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn import preprocessing

# Entrada
X = df5[["HOUR", "WEEKDAY", "DIRECCION",  "HUMEDAD",  "PRECIPITACION",  "PRESION",  "SOLAR",  "TEMPERATURA",  "VIENTO" ]].to_numpy()
# Preprocesado de la entrada
scaler = preprocessing.StandardScaler().fit(X)
X = scaler.transform(X)

# Salida
y = df5[["carga"]].to_numpy().ravel()

# Definicion y entrenamiento del modelo
reg = LogisticRegression(max_iter=10000).fit(X, y)

#Resultado
print(reg.score(X, y))

