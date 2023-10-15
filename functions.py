import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import random
from shapely.geometry import Polygon
import matplotlib.patheffects as pe
from shapely.ops import unary_union
import numpy as np
import matplotlib.patches as mpatches

def generar_mapa_inicial():
    file_path = "mapaMálaga.geojson"
    gdf = gpd.read_file(file_path)

    num_municipios = len(gdf)

    #Escojo algunos colores llamativos manualmente
    colors = [
        "#278a8f", "#3417f5", "#acfd1a", "#a623ef", "#235954", "#0be8bf", "#354aef", "#f00834", "#d604bc", "#89eccc", "#25f216",
        "#e2e2b2", "#e42355", "#fe7945", "#0a996f", "#0a6789", "#e25858", "#c0efd2", "#b5ac01",
        "#e86e1c", "#d41e45", "#cd5c5c"
    ]

    #Añado algunos colores de esta paleta de colores tambien (tiene que quedar bonito, que los colores aleatorios que genera la funcion del final son muy feos xd)
    colors2 = list(sns.color_palette("hls", 30))
    colors2 = list(set(colors2)) #Esto hace que no haya repetidos
    colors = colors + colors2

    #Si el array de colores es mayor al numero de municipios, cojo len(gdf) municipios solo
    if (len(gdf)-len(colors))<=0:
        colors = colors[:len(gdf)]
    else:
    #En caso contrario (la mayoria de veces, depende del mapa que cojas), completa el array con colores aleatorios. Si genero todos los colores aleatorios salen mapas muy feos xd
        colors = definir_colores(gdf,colors)

    random.shuffle(colors)

    #Genero las columnas color y dominador, necesarias para el algoritmo
    gdf["color"] = colors

    gdf["dominador"] = gdf["mun_name"]

    #Genero el mapa
    fig, ax = plt.subplots(figsize=(10, 8))
    gdf.plot(ax=ax, color=gdf["color"], edgecolor="black", linewidth=0.5)

    ax.set_axis_off()

    ax.set_facecolor("white")

    plt.savefig("mapa_coloreado.png", bbox_inches="tight", pad_inches=0, facecolor="white")

    return gdf

def conquistador(gdf):
    num_municipios = len(gdf)
    
    while True:
        indice_municipio_aleatorio = random.randint(0, num_municipios - 1)

        municipio_actual = gdf.loc[indice_municipio_aleatorio, "geometry"]
        dominador_actual_nombre = gdf.loc[indice_municipio_aleatorio, "dominador"]
        municipios_lindantes = gdf[gdf.geometry.touches(municipio_actual)]
        no_conquistados = municipios_lindantes[municipios_lindantes["dominador"] != dominador_actual_nombre]
        
        if len(no_conquistados) > 0:
            return indice_municipio_aleatorio

def conquistado(gdf, indice_conquistador):
    municipio_conquistador = gdf.loc[indice_conquistador, "geometry"]
    municipios_lindantes = gdf[gdf.geometry.touches(municipio_conquistador)]
    
    while True:
        indice_municipio_conquistado = random.choice(municipios_lindantes.index)
        dominador_actual_nombre = gdf.loc[indice_conquistador, "dominador"]
        
        if (gdf.loc[indice_municipio_conquistado, "dominador"]!=dominador_actual_nombre) and (gdf.loc[indice_municipio_conquistado, "dominador"]!=gdf.loc[conquistador, "dominador"]):
            return indice_municipio_conquistado


def consecuencias_conquista(gdf, conquistador, conquistado, i):

    color_conquistado = gdf.loc[conquistado, "color"]
    conquistador_name = gdf.loc[conquistador, "dominador"]
    conquistado_name = gdf.loc[conquistado, "mun_name"]
    dominador_anterior = gdf.loc[conquistado, "dominador"]
    gdf.loc[conquistado, "dominador"] = gdf.loc[conquistador, "dominador"]
    gdf.at[conquistado, "color"] = gdf.loc[conquistador, "color"]
    dominador_derrotado = gdf[gdf["dominador"] == dominador_anterior]

    #Con estos if describo las distintas situaciones que se pueden dar al conquistar un municipio
    with open("conquistas.txt", "a") as file:
        if len(dominador_derrotado) == 0:
            if dominador_anterior != gdf.loc[conquistado, "mun_name"]:
                if fin(gdf):
                    file.write(gdf.loc[conquistador, "dominador"] + " conquista " + conquistado_name + ", previamente ocupada por " + dominador_anterior + ". " + dominador_anterior + " ha sido derrotado." + gdf.loc[conquistador, "dominador"] + " ha conquistado todo el territorio malageño.")
                else:
                    file.write(gdf.loc[conquistador, "dominador"] + " conquista " + conquistado_name + ", previamente ocupada por " + dominador_anterior + ". " + dominador_anterior + " ha sido derrotado." + "\n")
            else:
                file.write(gdf.loc[conquistador, "dominador"] + " conquista " + conquistado_name + ". " + dominador_anterior + " ha sido derrotado." + "\n")
        else:
            if dominador_anterior != gdf.loc[conquistado, "mun_name"]:
                file.write(gdf.loc[conquistador, "dominador"] + " conquista " + conquistado_name + ", previamente ocupada por " + dominador_anterior + ".\n")
            else:
                file.write(gdf.loc[conquistador, "dominador"] + " conquista " + conquistado_name + ".\n")

    fig, ax = plt.subplots(figsize=(10, 8))
    
    gdf.plot(ax=ax, color=gdf["color"], edgecolor="black", linewidth=0.75)
    aspect = ax.get_aspect()
    
    geom_conquistado = gdf.loc[conquistado, "geometry"]
    conquistador_geom = gdf.loc[conquistador, "geometry"]

    dominador_anterior_geom = gdf.loc[conquistador, "geometry"]

    aspect = ax.get_aspect()

    grouped = gdf.groupby('dominador')['geometry']
    unions = grouped.apply(unary_union)
    geom_conquistador = unions[conquistador_name]

    shadow_effect = [pe.SimpleLineShadow(shadow_color='black', alpha=0.5, offset=(0, 0), linewidth=3.25)]
    if len(dominador_derrotado)!=0:
        conquistado_geom = unions[dominador_anterior]
        edgecolor = 'red'
        linewidth = 1.75
        gdf_result = gpd.GeoDataFrame({'geometry': [conquistado_geom]})
        gdf_result.boundary.plot(ax=ax, path_effects=shadow_effect)
        gdf_result.boundary.plot(ax=ax, edgecolor=edgecolor, linewidth=linewidth)

    edgecolor = 'blue'
    linewidth = 1.45
    gdf_result_perdedor = gpd.GeoDataFrame({'geometry': [geom_conquistado]})
    gdf_result = gpd.GeoDataFrame({'geometry': [geom_conquistador]})
    gdf_result.boundary.plot(ax=ax, path_effects=shadow_effect)
    #La siguiente linea es para que el territorio conquistado quede con un patron de lineas. A mi no me gusta como se queda asi que no lo dejo
    #gdf_result_perdedor.boundary.plot(ax=ax, hatch='////', edgecolor=color_conquistado, linewidth=0)
    gdf_result.boundary.plot(ax=ax, edgecolor=edgecolor, linewidth=linewidth)

    grouped = gdf.groupby('dominador')['geometry']
    unions = grouped.apply(unary_union)
    
    ax.set_axis_off()
    ax.set_facecolor("white")

    ax.set_aspect(aspect)

    #Estos if son para intentar evitar que los nombres se solapen. Es una solucion algo bruta, pero funciona. Si vas a reutilizar el codigo con otra provincia/region, posiblemente tengas que ajustar los decimales
    if (conquistador_geom.centroid.y-geom_conquistado.centroid.y)<0.02 and (conquistador_geom.centroid.y-geom_conquistado.centroid.y)>-0.02:
        if conquistador_geom.centroid.y>geom_conquistado.centroid.y:
            ax.annotate(gdf.loc[conquistador, "dominador"], xy=(conquistador_geom.centroid.x, conquistador_geom.centroid.y+(0.04-abs(conquistador_geom.centroid.y-geom_conquistado.centroid.y)*2)), xytext=(3, 3), textcoords="offset points", fontsize=8, color='white', path_effects=[pe.withStroke(linewidth=2, foreground='black')])
            
            ax.annotate(conquistado_name, xy=(geom_conquistado.centroid.x, geom_conquistado.centroid.y-(0.04-abs(conquistador_geom.centroid.y-geom_conquistado.centroid.y)*2)), xytext=(3, 3), textcoords="offset points", fontsize=8, color='white', path_effects=[pe.withStroke(linewidth=2, foreground='black')])
        else:
            ax.annotate(gdf.loc[conquistador, "dominador"], xy=(conquistador_geom.centroid.x, conquistador_geom.centroid.y-(0.04-abs(conquistador_geom.centroid.y-geom_conquistado.centroid.y)*2)), xytext=(3, 3), textcoords="offset points", fontsize=8, color='white', path_effects=[pe.withStroke(linewidth=2, foreground='black')])
            
            ax.annotate(conquistado_name, xy=(geom_conquistado.centroid.x, geom_conquistado.centroid.y+(0.04-abs(conquistador_geom.centroid.y-geom_conquistado.centroid.y)*2)), xytext=(3, 3), textcoords="offset points", fontsize=8, color='white', path_effects=[pe.withStroke(linewidth=2, foreground='black')])
    else:
        ax.annotate(gdf.loc[conquistador, "dominador"], xy=(conquistador_geom.centroid.x, conquistador_geom.centroid.y), xytext=(3, 3), textcoords="offset points", fontsize=8, color='white', path_effects=[pe.withStroke(linewidth=2, foreground='black')])
            
        ax.annotate(conquistado_name, xy=(geom_conquistado.centroid.x, geom_conquistado.centroid.y), xytext=(3, 3), textcoords="offset points", fontsize=8, color='white', path_effects=[pe.withStroke(linewidth=2, foreground='black')])
    plt.savefig("res/mapa_" + str(i) + ".png", bbox_inches="tight", pad_inches=0, facecolor="white")

def fin(gdf):
    num_dominadores = len(gdf["dominador"].unique())
    return num_dominadores == 1

def revolucion(gdf,i):
    num_municipios = len(gdf)
    
    while True:
        indice_municipio_aleatorio = random.randint(0, num_municipios - 1)

        anterior_dominador = gdf.loc[indice_municipio_aleatorio, "dominador"]

        derrotado = gdf[gdf["dominador"] == gdf.loc[indice_municipio_aleatorio, "mun_name"]]
        
        if gdf.loc[indice_municipio_aleatorio,"dominador"]!=gdf.loc[indice_municipio_aleatorio,"mun_name"] and len(derrotado)==0:
            nuevo_color = ("#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)]))
            gdf.loc[indice_municipio_aleatorio,"color"] = nuevo_color
            gdf.loc[indice_municipio_aleatorio, "dominador"] = gdf.loc[indice_municipio_aleatorio,"mun_name"]

            with open("conquistas.txt", "a") as file:
                file.write("El Frente de Liberación de " + gdf.loc[indice_municipio_aleatorio,"mun_name"] + " ha liderado la insurrección hacia la independencia de su municipio. Desde ahora, " + gdf.loc[indice_municipio_aleatorio,"mun_name"] + " se erige como un territorio fuera de las garras de " + anterior_dominador + ".\n")

            fig, ax = plt.subplots(figsize=(10, 8))
            gdf.plot(ax=ax, color=gdf["color"], edgecolor="black", linewidth=0.75)
            ax.set_axis_off()
            ax.set_facecolor("white")
   
            geom_Independizado = gdf.loc[indice_municipio_aleatorio, "geometry"]

            ax.annotate(gdf.loc[indice_municipio_aleatorio, "mun_name"], xy=(geom_Independizado.centroid.x, geom_Independizado.centroid.y), xytext=(3, 3), textcoords="offset points", fontsize=8, color='white', path_effects=[pe.withStroke(linewidth=2, foreground='black')])
    
            plt.savefig("res/mapa_" + str(i) + ".png", bbox_inches="tight", pad_inches=0, facecolor="white")

            break

def definir_colores(gdf,colors):
    i = len(colors)

    while True:
        #Con esto genero colores aleatorios
        colors.append("#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)]))
        i += 1

        colors = list(set(colors)) #Me aseguo de eliminar repetidos

        #Si hay tantos colores diferentes como municipios me salgo y retorno el array
        if len(colors) == len(set(colors)) and i>=len(gdf):
            return colors

        #Si hay algun color repetido al generar el numero necesario de colores, dejo el array como estaba y se sigue ejecutando el while
        if len(colors) != len(set(colors)) and i>=len(gdf):
            colors = [
        "#278a8f", "#3417f5", "#acfd1a", "#a623ef", "#235954", "#0be8bf", "#354aef", "#f00834", "#d604bc", "#89eccc", "#25f216",
        "#e2e2b2", "#49fecf", "#e42355", "#fe7945", "#cf0638", "#fa6632", "#0a996f", "#0a6789", "#e25858", "#c0efd2", "#b5ac01",
        "#e86e1c", "#d41e45", "#cd5c5c",
        ]
            i=len(colors)
