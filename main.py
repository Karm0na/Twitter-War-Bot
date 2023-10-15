import functions
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import random
from shapely.geometry import Polygon
from shutil import rmtree
from os import remove
import os

os.mkdir('res')
gdf = functions.generar_mapa_inicial()
i=0

while not functions.fin(gdf):
    #El algoritmo funciona de la siguiente manera: se elige un municipio conquistador aleatorio, y de sus municipios lindantes se elige otro, que sera el conquistado
    conquistador = functions.conquistador(gdf)
    conquistado = functions.conquistado(gdf, conquistador)

    derrotado = functions.consecuencias_conquista(gdf, conquistador, conquistado,i)

    r = random.randint(0,99)
    if(r<2 and i>300):
        #Pongo la independencia de los municipios a partir de la iteracion 300 para reducir el numero de iteraciones un poco
        #(La independencia de un municipio añade como minimo 2 lineas mas, cuando se independiza y cuando es derrotada otra vez)
        i += 1
        functions.revolucion(gdf,i)

    i += 1
