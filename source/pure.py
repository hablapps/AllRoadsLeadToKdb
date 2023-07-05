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
####  DATA LOADING  ####
#########################

traffic = pd.read_csv('../data/04-2023.csv', sep = ";", quotechar='"', encoding='utf-8').dropna()

weather_ori = pd.read_csv('../data/abr_meteo23.csv', sep = ";", quoting=csv.QUOTE_NONE, encoding='utf-8').dropna()

df3 = pd.read_csv('../data/pmed_ubicacion_04-2023.csv', sep = ";", quoting=csv.QUOTE_NONE, encoding='utf-8').dropna()
df4 = pd.read_csv('../data/Estaciones_control_datos_meteorologicos.csv', sep = ";", quoting=csv.QUOTE_NONE, encoding='latin-1')

weather_ori = weather_ori.rename(columns={"ANO": "year", "MES": "month", "DIA":"day"})
weather_ori["FECHA"] = pd.to_datetime(weather_ori[["year", "month", "day"]])

################################
####  TRAFFIC PREPROCESSING ####
################################

trafico= trafico[trafico["error"] == "N"]
trafico['FECHA'] = pd.to_datetime(trafico['fecha'], errors='coerce')
trafico.drop(["tipo_elem", "error", "intensidad", "ocupacion",  "vmed", "periodo_integracion", "fecha"], axis=1, inplace=True)
trafico.resample("1H", on="FECHA").mean()

#############################
#### METEO PREPROCESSING ####
#############################

weather= weather_ori.melt(id_vars=["ESTACION", "MAGNITUD", "FECHA"],
                          value_vars=[x for x in weather_ori.columns if re.match("^H", x)],
                          var_name="HORA")
weather2 = weather_ori.melt( value_vars=[x for x in weather_ori.columns if re.match("^V", x)])

weather["HORA"] = weather["HORA"].str[1:]
weather["HORA"] = pd.to_timedelta(weather['HORA'].astype(int)-1, unit='h')
weather["FECHA"] = weather["FECHA"] + weather["HORA"]

weather= weather[weather2["value"] == "V"]

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

weather = pd.concat([weather, df1], axis=1).drop(['MAGNITUD', "value", "HORA"], axis=1)

weather = weather.groupby([ "FECHA", "ESTACION"]).sum().reset_index()

##################################
####  DISTANCE PREPROCESSING  ####
##################################

distancias = pd.DataFrame()
distancias["id"] = pd.Series([df3.index[np.argmin(x)] for x in cdist(df4[["LONGITUD", "LATITUD"]], df3[["\"longitud\"","\"latitud\""]])])
distancias["ESTACION"] = df4["CODIGO_CORTO"]

#####################
#### JOIN TABLES ####
#####################

df5 = weather.merge(distancias, on="ESTACION")
df5 = df5.merge(trafico, on=["id", "FECHA"])
df5.rename(columns={"id": 'estacion_traf'}, inplace=True)
df5["WEEKDAY"] = df5["FECHA"].dt.weekday
df5["HOUR"] = df5["FECHA"].dt.hour
print(df5)

#######################
#### SKLEARN MODEL ####
#######################

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn import preprocessing

X = df5[["HOUR", "WEEKDAY", "DIRECCION",  "HUMEDAD",  "PRECIPITACION",  "PRESION",  "SOLAR",  "TEMPERATURA",  "VIENTO" ]].to_numpy()
scaler = preprocessing.StandardScaler().fit(X)
X = scaler.transform(X)

y = df5[["carga"]].to_numpy().ravel()

reg = LogisticRegression(max_iter=10000).fit(X, y)

print(reg.score(X, y))

