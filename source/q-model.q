system"c 40 200";
system"l pykx.q";
complete:("PJFFFFFFFFFJFJJF";enlist ",")0:`$":../complete.csv";
final:select from complete where WEEKDAY<5,9<HOUR,HOUR<20;
final:select from final where 40 <= (avg;traffic_load) fby traffic_station;
final:update traffic_load:traffic_load%100 from final;

minMaxScale:{[l]
    minL:min l;
    maxL:max l;
    ({(x-y)%(z-y)}[;minL;maxL]')l};

scaledRainfall:minMaxScale final[`rainfall];
scaledTemperature:minMaxScale final[`temperature];

final[`rainfall]:scaledRainfall;
final[`temperature]:scaledTemperature;

time_window:{[tt;data;lb]
    lb:lb+1;
    op:$[tt=`train;#;_];                                      / `train or `test decide the operator
    m:`rainfall`temperature`traffic_load`HOUR`WEEKDAY;        / the 5 columns we need
    data:?[data;();`traffic_station;m!({(y;(-;(count;x);80);x)}[;op]')m]; / first 80 or until the last 80 depending on operator 
    sw:{({y#z _x}[x;5;]')til count b:y _x}[;lb];              / sliding window function. takes turbomatrix and divides into chunks of 5x5
    gl:{y _(flip x)[2]}[;lb];                                  / gets the load (y data)
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

modelfit:.pykx.get`fit;
modelfit[train[0][3403];train[1][3403];test[0][3403];test[1][3403]];

modelpredict:.pykx.get`predict;
res:modelpredict[train[0][3403]];





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





