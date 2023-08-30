#!/usr/bin/env python
# coding: utf-8

# # Post PYKX

# In[1]:


import pykx as kx
from haversine import haversine_vector, Unit
from keras.models import Sequential
from keras.layers import Dense,LSTM 
import matplotlib.pyplot as plt
import numpy as np


# ## Data loading

# ### Weather

# In[2]:


weather = kx.q.read.csv('../dic_meteo22.csv', types='I'*4 + '*'*4 + 'FS'*24, delimiter=';')


# In[3]:


weather[:3].pd()


# In[4]:


weather = kx.q.xcol({'ANO': 'year', 'MES': 'month', 'DIA': 'day', 'ESTACION':'weather_station', 'MAGNITUD':'magnitude'}, weather)
weather = kx.q.qsql.delete(weather, ['PUNTO_MUESTREO', 'PROVINCIA', 'MUNICIPIO'])
weather = kx.q.qsql.update(weather, columns = {'date':'"D"$ raze each flip(year;month;day)'})
weather = kx.q.qsql.delete(weather, ['year', 'month', 'day'])
weather[:3].pd()


# In[5]:


def functionalSearch(cols, pattern, func):
    xcols = cols[kx.q.where(kx.q.like(cols, pattern))]
    xstring = func.format(kx.q.sv(b";", kx.q.string(xcols)).py().decode("utf-8"))
    return xcols, xstring


# In[7]:


cols = kx.q.cols(weather)
hcols, value = functionalSearch(cols, b'H*', "flip({})")
vcols, valid = functionalSearch(cols, b'V*', "flip({})")
weather = kx.q.qsql.update(weather, columns = {'hour': 'count[i]#enlist 01:00*til 24', 'values': value, 'valid': valid})
weather = kx.q.qsql.delete(weather, columns = kx.q.raze(hcols,vcols).py())
weather[:3].pd()


# In[8]:


weather = kx.q.ungroup(weather)


# In[9]:


weather = kx.q.qsql.select(weather, where = 'valid=`V')
weather = kx.q.qsql.update(weather, columns = {'date': 'date+hour'})
weather = kx.q.qsql.delete(weather, columns = ["valid", "hour"])
weather[:3].pd()


# In[10]:


magnitude = {80:"ultraviolet", 
             81:"wind", 
             82:"direction", 
             83:"temperature", 
             86:"humidity", 
             87:"pressure", 
             88:"solar", 
             89:"rainfall"}


# In[11]:


weather = kx.q('{update magnitude: x magnitude from y}', magnitude, weather)


# In[12]:


weather = kx.q('{exec (value x)#magnitude!values by date,weather_station from y}',magnitude,weather)


# ### Traffic

# In[13]:


traffic = kx.q.read.csv('../12-2022.csv', types="IPSIIIISI", delimiter=';')


# In[14]:


traffic = kx.q.qsql.select(traffic,
                         columns = {'traffic_load': 'avg carga'},
                         by = {"date":'fecha', "traffic_station": 'id'}, 
                         where = "error=`N")


# ### Location

# In[15]:


kx.q["weather_station"] = kx.q(".Q.id", kx.q.read.csv('../Estaciones_control_datos_meteorologicos.csv', types=" IFF", delimiter=";", as_table=True))
kx.q["traffic_station"] = kx.q.read.csv('../pmed_ubicacion_12-2022.csv', types = "SII**FFFF", delimiter = ";", as_table=True)


# In[16]:


kx.q("weather_station:(`CDIGO_CORTO`LONGITUD`LATITUD!`weather_station`longitude`latitude) xcol weather_station")
kx.q("traffic_station:(`id`longitud`latitud!`traffic_station`longitude`latitude) xcol traffic_station")


# In[18]:


dist = kx.toq(
            haversine_vector(kx.q('`longitude`latitude # weather_station').pd(), 
                             kx.q('`longitude`latitude # traffic_station').pd(),
                             Unit.KILOMETERS, comb=True))


# In[19]:


ids = kx.q.each(kx.q('{first where x=min x}'), dist)
distance_table = kx.q('{traffic_station ^ weather_station[x]}' ,  ids)
distance_table = kx.q.qsql.delete(distance_table, columns = ['tipo_elem','distrito','cod_cent','nombre','utm_x','utm_y','longitude', 'latitude'])


# ### Join Table

# In[20]:


complete = kx.q.lj(traffic, kx.q.xkey('traffic_station', distance_table))
complete = kx.q.aj(kx.toq(['date','weather_station']), complete, weather)
complete = kx.q.qsql.update(kx.q("0^",complete),  {"hour":"`hh$date", "weekday":'("d"$date)mod 7'})


# ### Modelo

# In[21]:


kx.q("minMaxScale:{[l] {(x-y)%(z-y)}[;min l;max l]l}")
                  
final = kx.q.qsql.select(complete, columns = {"date": "date",
                                              "traffic_station":"traffic_station",
                                              "hour":"hour", 
                                              "weekday": "weekday", 
                                              "traffic_load": "traffic_load%100",
                                              "rainfall":"minMaxScale rainfall"}
                                    )


# In[22]:


kx.q("""sw:{({y#z _x}[x;y;]')til count b:y _x}""")


# In[23]:


kx.q("""gt:{y _(flip x)[z]}""") # gets target (in position z)


# In[24]:


kx.q("""toMatrix:{({[t;i]value t[i]}[x;]')til count x:flip x}""") # table to matrix


# In[25]:


_=kx.q("""
        prepareData:{[data; ntest; chunkLen; columns; locTarget]  
            train:(toMatrix')?[data;();`traffic_station;columns!({(y;(-;(count;x);z);x)}[;_;ntest]')columns]; 
            test:(toMatrix')?[data;();`traffic_station;columns!({(y;(-;(count;x);z);x)}[;#;ntest]')columns];                                                                               
            (((sw[;chunkLen]')test;(gt[;chunkLen;locTarget]')test);((sw[;chunkLen]')train;(gt[;chunkLen;locTarget]')train))   
        }
    """)


# In[26]:




station_id = 4010

station = kx.q.qsql.select(final, where=["traffic_station="+str(station_id)])

data = kx.q("prepareData", station, 500, 5, kx.SymbolVector(['rainfall', 'traffic_load', 'hour', 'weekday']), 1)

X_train, y_train = np.array(data[0][0][station_id].py()), np.array(data[0][1][station_id].py())
X_test, y_test =  np.array(data[1][0][station_id].py()), np.array(data[1][1][station_id].py())


# In[27]:


model = Sequential()
model.add(LSTM(units = 50, return_sequences=False, input_shape=[None,4]))
model.add(Dense(units = 1))
model.compile(loss='mae', optimizer='adam')

def fit(train_X, train_y, test_X, test_y):
    return model.fit(train_X, train_y, 
                    epochs=50, batch_size=8, 
                    validation_data=(test_X, test_y), 
                    verbose=0, shuffle=False)


def predict(data):
    return model.predict(data, verbose=0)


# In[28]:




history = fit(X_train,y_train,X_test,y_test)

plt.plot(history.history['loss'], label='train')
plt.plot(history.history['val_loss'], label='validation')

plt.title("Train and Validation Loss Curves")
plt.xlabel("Epochs")
plt.ylabel("Loss")
plt.legend()
plt.show()


# In[29]:


plt.plot(y_test, label='test real')
plt.plot(range(200,495), model.predict(X_test[200:], verbose=0).flatten(), label='test predict')
plt.title("Real test vs Predicted test")
plt.xlabel("Time(15 min)")
plt.ylabel("Load")
plt.legend(loc="upper right")
plt.show()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




