# -*- coding: utf-8 -*-
"""
Created on Sun Apr  2 10:34:26 2017

@author: lucia
"""

from bs4 import BeautifulSoup
import requests
import re


url = 'http://www.leemp3.com/disponibles_textos.htm'
soup = BeautifulSoup(requests.get(url).text)
def caracteristicas():
    autores=[]
    generos=[]
    literaturas=[]
    urls=[]
    titulos=[]
    nombres_ficheros=[]
    all_lines = soup('tr') ## primer parametro nombre de la etiqueta y el segundo puede ser nombre de la clase, identificador...
    for line in all_lines[0:len(all_lines)-1]:
        autores.append(line.find_all('td')[0].text)
        titulos.append(line.find_all('td')[1].text)
        url_htm=line.find_all('td')[1].find('a').get('href')
        url=(re.sub(r'.htm',r'.txt', url_htm))
        nombres_ficheros.append(url.split("/")[-1])
        urls.append(url)
        literaturas.append(line.find_all('td')[2].text)
        generos.append(line.find_all('td')[3].text)
    return autores,generos,literaturas,urls,nombres_ficheros,titulos
    

autores=caracteristicas()[0]
generos=caracteristicas()[1]
literaturas=caracteristicas()[2]
urls=caracteristicas()[3]
nombres_ficheros=caracteristicas()[4]
titulos=caracteristicas()[5]

def crea_diccionario():
    Diccionario=dict()
    for i in range(len(autores)):
        dic=dict()
        Diccionario[i]=dic
        dic['id']=i
        dic['Autor']=autores[i]
        dic['Género']=generos[i]
        dic['Literatura']=literaturas[i]
        dic['url']=urls[i]
        dic['Titulo']=titulos[i]
        dic['Nombre_fichero']=nombres_ficheros[i]
    return Diccionario
        

        
Diccionario=crea_diccionario()


def obtener_texto(a,b):
    if a>b:
        pass
    else:
        for i in range(a,b+1):
            url = Diccionario[i]['url']
            soup = BeautifulSoup(requests.get(url).text)
            nombre=Diccionario[i]['Titulo']
            archi=open("libros/"+nombre,'w',encoding='utf8')          
            archi.write(str(i)+"\n\n")
            archi.write(url+"\n\n")
            archi.write(str(soup)[15:-18])
            archi.close()
            print(i)     
     
            

    


