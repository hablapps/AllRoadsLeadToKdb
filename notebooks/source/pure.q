system"l ml/ml.q";
.ml.loadfile`:init.q;

weather:.Q.id("  II ***",(24*2)#"FS";enlist ";")0:`$":../data/abr_meteo23.csv";
weather:`ESTACION`FECHA xcols `ANO`MES`DIA _update FECHA:"D"$(raze')flip(ANO;MES;DIA) from weather;
cw:cols weather;
mc:(neg 2*24)_ cw;
tr:{(flip;enlist,cw where cw like x,"*")};
ops:(mc,`HORA`VALOR`OK)!mc,((#;(count,`i);(enlist;(*;01:00;til,24)));tr"H";tr"V");
weather:ungroup?[weather;();0b;ops];
weather:delete from weather where OK<>`V;
weather:update FECHA:("P"$((string FECHA),'" ",'string"t"$HORA))from weather;
weather:update ESTACION: "j"$ESTACION from weather;
weather:delete VALIDO,HORA from weather;
mag:80 81 82 83 86 87 88 89!`ULTRAVIOLETA`VIENTO`DIRECCION`TEMPERATURA`HUMEDAD`PRESION`SOLAR`PRECIPITACION;
weather:update mag MAGNITUD from weather;
u:value mag;
weather:0!exec u#MAGNITUD!VALOR by FECHA,ESTACION from weather;
weather:lower[cols weather]xcol weather;

traffic:.Q.id("IPS  J S";enlist ";")0:`$":../data/04-2023.csv";
traffic: `fecha xasc select avg carga by fecha,id from traffic where error=`N;

weather_station:.Q.id("SISS";enlist ";")0:`$":../data/Estaciones_control_datos_meteorologicos.csv";
traffic_station:.Q.id("SISSSSSSS";enlist ";")0:`$":../data/pmed_ubicacion_04-2023.csv";

b:select "F"$ string LONGITUD, "F"$ string LATITUD from weather_station;
a:select "F"$ string longitud, "F"$ string latitud from traffic_station;
distance:{[x1;x2;y1;y2]abs(x1-y1)+abs(x2-y2)};
distance_matrix:distance[b.LONGITUD; b.LATITUD]'[a.longitud; a.latitud];

station_index:distance_matrix?'min each distance_matrix;
tabla_distancia: select id,estacion:station_index from traffic_station;

tr:update "I"$string id from 0!traffic;
td:update "I"$string id from tabla_distancia;
uni:tr lj 1!td;
completa:uni lj 2!`fecha`estacion xcols weather;
t:select [20] carga from completa;
mdl1:.ml.ts.SARIMA.fit[1700#completa[`carga];1700#completa[`fecha];numLags;integrate;mavgVals;isTrend;seasDict]
show mdl1:.ml.ts.SARIMA.fit t;
show pred:predict t;

/ exit 0;