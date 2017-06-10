# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 12:29:44 2017

@author: AlvaroSanchez91
"""

#######################################################################
# VISUALIZACIÓN
#
# Una vez hemos calculadas nuestras similitudes entre libros (mediante tf-idf y lsa),
#podemos hacer una visualización creando un grafo mediante gephi.
#
# Tomaremos un umbral apartir del cual consideraremos que dos libros son similares.
#Si la similitud de dos libros supera dicho umbral crearemos una arista que los conecte,
# y dicha arista tendrá un grosor directamente proporcional a su similitud.
#
# Mediante gephi se construirá el grafo, se calcularán las familias del mismo,
# y se pintarán de distintos colores.



###########################################################################
# GENERACIÓN DE NODOS Y ARISTAS
#
# Construiremos dos tablas de datos, la de los nodos indicara el nombre del libro,
#el autor etc. La de las aristas conectara pares de libros e indicará el grosor de las aristas.
#
# Estas tablas son las que leerá gephi posteriormente para generar los grafos.


#Importamos las funciones necesarias
import pandas as pd
from scraping import *
from funciones import *

#función para guardar csv de nodos y de aristas:
#
#El punto de corte esta en 0 para luego elegir el que se quiera (eliminando aristas).
#Esto se debe a que puede tardarse mucho en generar el modelo, de modo que guardamos todos los resultados,
#para despues borrar los que no nos interesen.
#
#En nodos_file y en aristas_file se elige el normbre del archivo para guardar los datos.
def crearModeloGephi(Libros, lib_tfidf,lsi,indice,UMBRAL_SIMILITUD=0 , nodos_file='nodos.csv',aristas_file='aristas.csv'):
    
    #Creamos el csv con los nodos
    nodos=pd.DataFrame()
    for i in Libros:
        nodo=pd.DataFrame()
        nodo['ID']=[i]
        nodo['Label']=Libros[i]['Titulo']
        nodo['Autor']=Libros[i]['Autor']
        nodo['Genero']=Libros[i]['Género']
        nodo['Literatura']=Libros[i]['Literatura']
        nodos=pd.concat([nodos,nodo])
   
    nodos.to_csv(path_or_buf=nodos_file, sep=';', index=False)
    
    codigosLibros = crearCodigosLibros(Libros)
   
    #creamos el csv con las aristas
    aristas=pd.DataFrame()

    aristas['Source']=[0]
    aristas['Target']=[0]
    aristas['Weight']=[1]
    aristas['Label']=[str(0)+' to '+str(-1)]
    aristas['Type']=['Undirected']    
    for i, doc in enumerate(lib_tfidf):
        vec_lsi = lsi[doc]

        indice_similitud = indice[vec_lsi]

        for j, elemento in enumerate(Libros):
            s = indice_similitud[j]
            if (s > UMBRAL_SIMILITUD) & (i != j):
                LibroJ =Libros[codigosLibros[j]]

                arista=pd.DataFrame()
                arista['Source']=[int(codigosLibros[i])]
                arista['Target']=[int(codigosLibros[j])]
                arista['Weight']=[s]
                arista['Label']=[str(int(codigosLibros[i]))+' to '+str(int(codigosLibros[j]))]
                arista['Type']=['Undirected']
                
                if sum(aristas['Label']==arista['Label'][0])==0:
                    aristas=pd.concat([aristas,arista])
                    
    aristas.reset_index(drop=True, inplace=True)
    aristas=aristas.drop(0)
    aristas.to_csv(path_or_buf=aristas_file, sep=';', index=False)
    
    
    
##Ejemplo de como crear los csv de nodos y aristas para 200 libros
#Libros   = leer_libros(200)
#palabras    = preprocesarLibros(Libros)
#textos      = crearColeccionTextos(Libros)
#diccionario = crearDiccionario(textos)
#corpus      = crearCorpus(textos,diccionario)

#lib_tfidf   = crearTfIdf(corpus)
#(lsi,indice)= crearLSA(corpus,lib_tfidf,diccionario,TOTAL_TOPICOS_LSA,UMBRAL_SIMILITUD)
#
#
#crearModeloGephi(Libros,lib_tfidf,lsi,indice,UMBRAL_SIMILITUD=0.5,nodos_file='nodos200.csv',aristas_file='aristas200.csv')


    
    