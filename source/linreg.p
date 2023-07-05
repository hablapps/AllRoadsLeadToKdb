from sklearn.linear_model import LinearRegression


def model(table):
    X = table[["direccion", "humedad", "precipitacion", "presion", "solar", "temperatura", "viento" ]].to_numpy()
    y = table["carga"].to_numpy().ravel()
    reg = LinearRegression().fit(X, y)
    
    return reg.score(X, y)