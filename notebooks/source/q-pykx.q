// load libraries and apply configuration
// in q mem space
system"l pykx.q";
system"l linreg.p";

// in python mem space
.pykx.pyexec"import numpy as np";
.pykx.pyexec"from scipy.spatial.distance import cdist";

// config
system"c 200 250";
.pykx.i.defaultConv:"pd";

// data loading
weather:.Q.id("  II ***",(24*2)#"FS";enlist ";")0:`$":../data/abr_meteo23.csv";
traffic:.Q.id("IPS  J S";enlist ";")0:`$":../data/04-2023.csv";
weather_station:.Q.id("SISS";enlist ";")0:`$":../data/Estaciones_control_datos_meteorologicos.csv";
traffic_station:.Q.id("SISSSSSSS";enlist ";")0:`$":../data/pmed_ubicacion_04-2023.csv";

// preprocess weather data
weather:`ESTACION`FECHA xcols `ANO`MES`DIA _update FECHA:"D"$(raze')flip(ANO;MES;DIA) from weather;
cw:cols weather;
mc:(neg 2*24)_ cw;
tr:{(flip;enlist,cw where cw like x,"*")};
ops:(mc,`HORA`VALOR`OK)!mc,((#;(count,`i);(enlist;(*;01:00;til,24)));tr"H";tr"V");
weather:ungroup?[weather;();0b;ops];
weather:delete from weather where OK<>`V;
weather:update FECHA:("P"$((string FECHA),'" ",'string"t"$HORA))from weather;
weather:update ESTACION:"j"$ESTACION from weather;
weather:delete VALIDO,HORA from weather;
mag:80 81 82 83 86 87 88 89!`ULTRAVIOLETA`VIENTO`DIRECCION`TEMPERATURA`HUMEDAD`PRESION`SOLAR`PRECIPITACION;
weather:update mag MAGNITUD from weather;
u:value mag;
weather:0!exec u#MAGNITUD!VALOR by FECHA,ESTACION from weather;
weather:lower[cols weather]xcol weather;

// preprocess traffic data
traffic:`fecha xasc select avg carga by fecha,id from traffic where error=`N;

// use PyKX to run cdist function
b:select "F"$string LONGITUD, "F"$string LATITUD from weather_station;
a:select "F"$string longitud, "F"$string latitud from traffic_station;
.pykx.set[`xa1;a[`longitud]];
.pykx.set[`xa2;a[`latitud]];
.pykx.set[`yb1;b[`LONGITUD]];
.pykx.set[`yb2;b[`LATITUD]];
distance_matrix:flip(.pykx.eval"cdist(np.dstack((yb1,yb2))[0], np.dstack((xa1,xa2))[0])")`;

station_index:distance_matrix?'min each distance_matrix;
tabla_distancia:select id,estacion:station_index,"F"$string longitud,"F"$string latitud from traffic_station;

tr:update "I"$string id from 0!traffic;
td:update "I"$string id from tabla_distancia;
uni:tr lj 1!td;
completa:uni lj 2!`fecha`estacion xcols weather;

// prepare table for model
completa:update hour:`hh$fecha,weekday:("d"$fecha)mod 7 from completa;
completa:3!`hour`weekday`estacion xcols 0^completa;
cargas:select carga_avg:avg carga by hour,weekday,estacion from completa;
temps:select temps_avg:avg temperatura by hour from completa;

completa:1!0!completa lj cargas;
completa:update carga:carga-carga_avg,temperatura:temperatura-temps_avg from 0!completa lj temps;

// use PyKX to run custom model code
modelfunc:.pykx.get`modelo;
res:modelfunc[completa];

print res`;
exit 1;