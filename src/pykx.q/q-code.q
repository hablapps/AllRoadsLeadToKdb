system"c 40 150";
system"l pykx.q";

.pykx.pyexec"from haversine import haversine_vector, Unit";


// data loading
weather:.Q.id("  II ***",(24*2)#"FS";enlist ";")0:`$":../../dic_meteo22.csv";
traffic:.Q.id("IPS  J S";enlist ";")0:`$":../../12-2022.csv";
weather_station:.Q.id("SISS";enlist ";")0:`$":../../Estaciones_control_datos_meteorologicos.csv";
traffic_station:.Q.id("SISSSSSSS";enlist ";")0:`$":../../pmed_ubicacion_12-2022.csv";

-1"loaded input data";

weather:(`ANO`MES`DIA`ESTACION`MAGNITUD!`year`month`day`weather_station`magnitude) xcol weather

// preprocess weather data
weather:`weather_station`date xcols `year`month`day _update date:"D"$(raze')flip(year;month;day) from weather;

cw:cols weather;
mc:(neg 2*24)_ cw;
tr:{(flip;enlist,cw where cw like x,"*")};

ops:(mc,`time`magnitude_value`ok)!mc,((#;(count,`i);(enlist;(*;01:00;til,24)));tr"H";tr"V");
weather:ungroup?[weather;();0b;ops];
weather:delete from weather where ok<>`V;
weather:update date:("P"$((string date),'" ",'string"t"$time))from weather;
weather:update weather_station:"j"$weather_station from weather;
weather:delete valid,time from weather;
mag:80 81 82 83 86 87 88 89!`ultraviolet`wind`direction`temperature`humidity`pressure`solar`rainfall;
weather:update mag magnitude from weather;
u:value mag;
weather:0!exec u#magnitude!magnitude_value by date,weather_station from weather;
weather:0f^weather;
-1"preprocessed weather table";

weather_station:(`CODIGO_CORTO`LONGITUD`LATITUD!`weather_station`longitude`latitude)xcol weather_station
traffic_station:(`id`longitud`latitud!`traffic_station`longitude`latitude)xcol traffic_station

-1"preprocessed weather and traffic station data";

traffic:(`fecha`id!`date`traffic_station)xcol traffic;
traffic:`date xasc select traffic_load:avg carga by date: 0D01:00:00 xbar date,traffic_station from traffic where error=`N
-1"preprocessed traffic data";

b:select "F"$string longitude,"F"$string latitude from weather_station;
a:select "F"$string longitude,"F"$string latitude from traffic_station;
pow2:xexp[;2];
/ distance:{[x1;x2;y1;y2;pow2]abs(pow2[x1]-pow2[y1])+abs(pow2[x2]-pow2[y2])}[;;;;pow2];
/ distance_matrix:distance[b.longitude; b.latitude]'[a.longitude; a.latitude];

.pykx.setdefault"pd";
.pykx.set[`a;`longitude`latitude#a];
.pykx.set[`b;`longitude`latitude#b];
distance_matrix:flip(.pykx.eval"haversine_vector(a, b, Unit.KILOMETERS, comb=True)")`;
-1"calculated distance matrix";

ids:distance_matrix?'min each distance_matrix;

distance_table:select "I"$string traffic_station,"F"$string weather_station:weather_station[ids][`weather_station] from traffic_station;

complete:(`traffic_station xkey traffic) lj `traffic_station xkey distance_table;
complete:0!aj[`weather_station`date;complete;weather];
complete:update hour:`hh$date,weekday:("d"$date)mod 7 from complete;
-1"built complete table. begin model prep";
/ complete:("PJFFFFFFFFFJFJJF";enlist ",")0:`$":../complete.csv";
minMaxScale:{[l]
    minL:min l;
    maxL:max l;
    ({(x-y)%(z-y)}[;minL;maxL]')l};

final:select date, traffic_station, hour, weekday,
             traffic_load: traffic_load%100,
             temperature:minMaxScale temperature,
             rainfall:minMaxScale rainfall 
      from complete
      where weekday>1,
            9<hour,
            hour<20,
            40 <= (avg; traffic_load) fby traffic_station;

-1"preprocessed final table";

time_window:{[tt;data;lb]
    op:$[tt=`train;#;_];                                      / `train or `test decide the operator
    m:`rainfall`temperature`traffic_load`hour`weekday;        / the 5 columns we need
    data:?[data;();`traffic_station;m!({(y;(-;(count;x);80);x)}[;op]')m]; / first 80 or until the last 80 depending on operator 
    sw:{({y#z _x}[x;y;]')til count b:(y+1) _x}[;lb];          / sliding window function. takes the matrix and divides into chunks of 5x5
    gl:{(y+1) _(flip x)[2]}[;lb];                             / gets the load (y data)
    toMatrix:{({[t;i]value t[i]}[x;]')til count x:flip x};    / table to matrix
    data:(toMatrix')data;                                     / convert each subtable (data is a keyed table) to a matrix
    X:(sw')data;                                              / apply sliding window to get X
    y:(gl')data;                                              / and gl to get y
    (X;y)                                                     / return both
    };

train:time_window[`train;final;5];

-1"train shape:";
show first train[0][3403];

test:time_window[`test;final;5];

-1"test shape:";
show first test[0][3403];

.pykx.setdefault"py";

system"l kerasmodel.p";

-1"fit model";
modelfit:.pykx.get`fit;
modelfit[train[0][3403];train[1][3403];test[0][3403];test[1][3403]];

-1"predict model";
modelpredict:.pykx.get`predict;
res:modelpredict[train[0][3403]];

-1"final result:";
show res`;
exit 1;





/ models:.pykx.import[`keras.models];
/ sequential:models[`:Sequential][];
/ dense:.pykx.import[`keras.layers]`:Dense;
/ lstm:.pykx.import[`keras.layers]`:LSTM;
/ dropout:.pykx.import[`keras.layers]`:Dropout;

/ input:.pykx.import[`keras.layers]`:Input;
/ x:input[(5;5)]
/ layer:lstm[500;`return_sequences pykw 1b;`input_shape pykw (5,5)]
/ model[`:add]lstm[500;`return_sequences pykw 1b;`input_shape pykw (5,5)];


/ break;

/ model`:add lstm[500;`return_sequences pykw 1b;`input_shape pykw (5,5)];
/ model[`:add]lstm[250;`return_sequences pykw 1b];
/ model[`:add]lstm[50;`return_sequences pykw 0b];
/ model[`:add]dropout[0.2];
/ model[`:add]dense[1];
/ model[`:compile][`loss pykw`mae;`optimizer pykw`adam];
/ model[`:summary][];

/ .pykx.pyexec"from keras.models import Sequential";
/ .pykx.pyexec"from keras.layers import Dense";
/ .pykx.pyexec"from keras.layers import LSTM, Dropout, Conv1D";
/ .pykx.pyexec"import numpy as np";

/ .pykx.pyexec"model = Sequential()";
/ .pykx.pyexec"model.add(LSTM(units = 500, return_sequences=True, input_shape=[None,5]))";
/ .pykx.pyexec"model.add(LSTM(units = 250,return_sequences=True))";
/ .pykx.pyexec"model.add(LSTM(units = 50, return_sequences=False))";
/ .pykx.pyexec"model.add(Dropout(0.2))";
/ .pykx.pyexec"model.add(Dense(units = 1))";
/ .pykx.pyexec"model.compile(loss='mae', optimizer='adam')";
/ .pykx.pyexec"model.summary()";

/ .pykx.setdefault"py";

/ .pykx.set[`train_X;train[0][3403]];
/ .pykx.set[`train_y;train[1][3403]];
/ .pykx.set[`test_X;test[0][3403]];
/ .pykx.set[`test_y;test[1][3403]];

/ .pykx.pyexec"model.fit(train_X, train_y, epochs=3, batch_size=64, validation_data=(test_X, test_y), verbose=1, shuffle=False)";


/ result:.pykx.qeval"model.predict(train_X)"





