# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 11:27:03 2017

@author: lucia
"""
from scraping import *
import nltk


##########################################################################
### Paso 1: Leer ficheros con los textos de los libros
##########################################################################

def leer_libros(libros_max=3282):
    Diccionario_texto=dict()
    for i in range(0,libros_max):
        Diccionario_texto[i]=Diccionario[i]
        texto=open("libros/"+Diccionario_texto[i]['Nombre_fichero'],'r',encoding='utf8')
        Diccionario_texto[i]['texto_completo']=texto.read()[0:10000]
    return Diccionario_texto

################################################################
### Paso 2: Preprocesado y limpieza de los textos de los libros
################################################################



from nltk.tokenize import RegexpTokenizer
tokenizer = RegexpTokenizer(r'\w+') 

from nltk.corpus import stopwords
stopWords = set(stopwords.words('spanish')) 

from nltk.stem import SnowballStemmer
stemmer = SnowballStemmer("spanish")

def obtenerNombresPropios(nombres, texto):

    for frase in nltk.sent_tokenize(texto):
        #
        # nltk.word_tokenize devuelve la lista de palabras que forman
        #    la frase (tokenización)
        #
        # nltk.pos_tag devuelve el part of speech (categoría) correspondiente
        #    a la palabra introducida
        #
        # nltk.ne_chunk devuelve la etiqueta correspondiente al part of
        #    speech
        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(frase))):
            ## chunk son como trozos
            ## CHUNK que tienen la etiqueta person: que son los nombres propios(son part of speech)
            ## pos_tag nos dice si la palabra es un verbo, un nombre...
            
            try:
                if chunk.label() == 'PERSON':
                    for c in chunk.leaves():
                        if str(c[0].lower()) not in nombres: 
                            nombres.append(str(c[0]).lower())
                            ##añade los nombres pero en minusculas
            except AttributeError:
                pass
    return nombres

def preprocesarLibros(libros):
    nombresPropios = []

    for elemento in libros:
        print(elemento)

        libro = libros[elemento]

        ## Eliminación de signos de puntuación usando tokenizer
        texto_completo = libro['texto_completo']
        texto = ' '.join(tokenizer.tokenize(texto_completo))
        libro['texto'] = texto
        

        ## buscamos los nombres propios que haya dentro de texto
        nombresPropios = obtenerNombresPropios(nombresPropios, texto) 
       
    ignoraPalabras = stopWords
    ignoraPalabras.union(nombresPropios)

    palabras = [[]]
    for elemento in libros:
        libro = libros[elemento]

        texto = libro['texto']
        for palabra in tokenizer.tokenize(texto):
            if (palabra.lower() not in ignoraPalabras):
                palabras.append([(stemmer.stem(palabra.lower()))])

    return palabras

##########################################################################
### Paso 3: Creación de la colección de textos
##########################################################################

from gensim import corpora, models, similarities
    
def crearColeccionTextos(Libros):
    print("Creando colección global de resúmenes")
    textos = []
    
    for elemento in Libros.keys():
        Libro = Libros[elemento]
        texto = Libro['texto']
        lista = texto.split(' ')

        textos.append(lista)

    return textos
    
##########################################################################
### Paso 4: Creación del diccionario de palabras
##########################################################################
###
### El diccionario está formado por la concatenación de todas las
### palabras que aparecen los libros
###
### Básicamente esta función mapea cada palabra única con su identificador
###
### Es decir, si tenemos N palabras, lo que conseguiremos al final
### es que cada libro sea representado mediante un vector en un
### espacio de N dimensiones

def crearDiccionario(textos):
    print("Creación del diccionario global")
    return corpora.Dictionary(textos)


##########################################################################
### Paso 5: Creación del corpus de resúmenes preprocesados
##########################################################################
###
### Crearemos un corpus con la colección de todos los resúmenes
### previamente pre-procesados y transformados usando el diccionario
###

def crearCorpus(textos,diccionario):
    print("Creación del corpus global con los libros")
    return [diccionario.doc2bow(texto) for texto in textos]



##########################################################################
### Paso 6: Creación del modelo tf-idf
##########################################################################

def crearTfIdf(corpus):
    print("Creación del Modelo Espacio-Vector Tf-Idf")
    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]
    return corpus_tfidf

##########################################################################
### Paso 7: Creación del modelo LSA (Latent Semantic Analysis)
##########################################################################

#import gensim
#import numpy as np

### Valores clave para controlar el proceso
TOTAL_TOPICOS_LSA = 20
UMBRAL_SIMILITUD = 0.8

def crearLSA(corpus,pel_tfidf,diccionario,TOTAL_TOPICOS_LSA):
    print("Creación del modelo LSA: Latent Semantic Analysis")

    lsi = models.LsiModel(pel_tfidf, id2word=diccionario, num_topics=TOTAL_TOPICOS_LSA)

    indice = similarities.MatrixSimilarity(lsi[pel_tfidf]) 

    return (lsi,indice)



def crearCodigosLibros(Libros):
    codigosLibros = []
    for i, elemento in enumerate(Libros):
        Libro = Libros[elemento]
        codigosLibros.append(Libro['id'])
    return codigosLibros



def crearModeloSimilitud(Libros, lib_tfidf,lsi,indice,UMBRAL_SIMILITUD=0.8):
    codigosLibros = crearCodigosLibros(Libros)
    print("Creando enlaces de similitud entre libros")
        
    for i, doc in enumerate(lib_tfidf):
        print("============================")
        LibroI = Libros[codigosLibros[i]]
        print("Libro I = ",LibroI['id'],"  " ,LibroI['Titulo'],"  " , LibroI['Género'])

        vec_lsi = lsi[doc]
        indice_similitud = indice[vec_lsi]
        similares = []
        for j, elemento in enumerate(Libros):
            s = indice_similitud[j]
            if (s > UMBRAL_SIMILITUD) & (i != j):
                LibroJ =Libros[codigosLibros[j]]
                similares.append((codigosLibros[j], s))
                
                print("   Similitud: ",s,"   ==> Libro J = ",LibroJ['id'],"  ",LibroJ['Titulo'], "  ", LibroJ['Género'])
                    
            similares = sorted(similares, key=lambda item: -item[1])

            LibroI['similares'] = similares
            LibroI['totalSimilares'] = len(similares)

 
        
        
def crearModeloSimilitud_libro(iden,Libros, lib_tfidf,lsi,indice,UMBRAL_SIMILITUD=0.8):
    print("Creando enlaces de similitudes con el libro: ",Libros[iden]['Titulo'])
    codigosLibros = crearCodigosLibros(Libros)
        
    print("============================")
    LibroI = Libros[iden]
        
    print("Libro I = ",LibroI['id'],"  " ,LibroI['Titulo'],"  " , LibroI['Género'])

            
    vec_lsi = lsi[lib_tfidf[iden]]
    indice_similitud = indice[vec_lsi]
    similares = []
    for j, elemento in enumerate(Libros):
        s = indice_similitud[j]
        if (s > UMBRAL_SIMILITUD) & (iden != j):
               LibroJ =Libros[codigosLibros[j]]
               similares.append((codigosLibros[j], s))
               print("   Similitud: ",s,"   ==> Libro J = ",LibroJ['id'],"  ",LibroJ['Titulo'], "  ", LibroJ['Género'])
                
        similares = sorted(similares, key=lambda item: -item[1])

        LibroI['similares'] = similares
        LibroI['totalSimilares'] = len(similares)

       
        
def crearModeloSimilitud_todos(lista,diccionario):
    codigosLibros = crearCodigosLibros(Libros)

    palabras    = preprocesarLibros(Libros)
    textos      = crearColeccionTextos(Libros)
    diccionario = crearDiccionario(textos)
    corpus      = crearCorpus(textos,diccionario)
    lib_tfidf   = crearTfIdf(corpus)
    (lsi,indice)= crearLSA(corpus,lib_tfidf,diccionario,TOTAL_TOPICOS_LSA)
    print("Creando enlaces de similitudes")

    SIMILARES=[]   
    for iden,doc in enumerate(lib_tfidf):
        if iden in (range(len(lista))):
            vec_lsi = lsi[lib_tfidf[iden]]
            indice_similitud = indice[vec_lsi]
            for j, elemento in enumerate(Libros):
                s = indice_similitud[j]
                if (iden != j and j not in lista)  :
                        LibroJ =Libros[codigosLibros[j]]
                        SIMILARES.append((codigosLibros[j], s))
    SIMILARES = sorted(SIMILARES, key=lambda item: -item[1])
    LibroJ =Libros[SIMILARES[0][0]]        
    print("Quizás te interesaría leer el libro: ", LibroJ['Titulo'],"\n del autor: ",LibroJ['Autor'])

        
        
def crearModeloSimilitud_recomendador(lista,Libros,diccionario, lib_tfidf,lsi,indice):
    print("Creando enlaces de similitudes")
    SIMILARES=[]   
    for iden,doc in enumerate(lib_tfidf):
        if iden in (range(len(lista))):
            vec_lsi = lsi[lib_tfidf[iden]]
            indice_similitud = indice[vec_lsi]
            for j in Libros.keys():
                s = indice_similitud[j]
                if  (iden != j and Libros[j]['id'] not in lista):
                        LibroJ =Libros[j]
                        SIMILARES.append((j, s))

    SIMILARES = sorted(SIMILARES, key=lambda item: -item[1])
    if SIMILARES==[]:
        print(crearModeloSimilitud_todos(lista,diccionario ,salida=None))
    else:
        LibroJ =Libros[SIMILARES[0][0]]        
        print("Quizás te interesaría leer el libro: ", LibroJ['Titulo'],"\n del autor: ",LibroJ['Autor'])
       
        

def recomendador(lista):
        num=0
        Géneros=[]
        dic_recomen=dict()
        dic_recomendador=dict()
        for i in lista:
            if Libros[i]['Género'] not in Géneros:
                Géneros.append(Libros[i]['Género'])
        for i in lista:
            for j in Libros.keys():
                if Libros[j]['Autor']==Libros[i]['Autor'] and Libros[j]['Género'] in Géneros:
                     dic_recomen[j]=Libros[j]
        for i in dic_recomen.keys():
            dic_recomendador[num]=dic_recomen[i]
            num+=1
        TOTAL_TOPICOS_LSA = 20

        palabras    = preprocesarLibros(dic_recomendador)
        textos     = crearColeccionTextos(dic_recomendador)
        diccionario = crearDiccionario(textos)
        corpus      = crearCorpus(textos,diccionario)
        lib_tfidf   = crearTfIdf(corpus)
        (lsi,indice)= crearLSA(dic_recomendador,lib_tfidf,diccionario,TOTAL_TOPICOS_LSA)
        crearModeloSimilitud_recomendador(lista,dic_recomendador,diccionario,lib_tfidf,lsi,indice)
        
        
        
## EJEMPLO DE COMO CREAR "crearModeloSimilitud" y "crearModeloSimilitud_libro" con los 200 primeros libros

#Libros   = leer_libros(200)
#palabras    = preprocesarLibros(Libros)
#textos      = crearColeccionTextos(Libros)
#diccionario = crearDiccionario(textos)
#corpus      = crearCorpus(textos,diccionario)
#lib_tfidf   = crearTfIdf(corpus)
#(lsi,indice)= crearLSA(corpus,lib_tfidf,diccionario,TOTAL_TOPICOS_LSA)
#
#crearModeloSimilitud(Libros,lib_tfidf,lsi,indice,UMBRAL_SIMILITUD=UMBRAL_SIMILITUD)
#crearModeloSimilitud_libro(12,Libros,lib_tfidf,lsi,indice,UMBRAL_SIMILITUD=UMBRAL_SIMILITUD)


## EJEMPLO DE COMO CREAR "recomendador" con los 200 primeros libros

#Libros   = leer_libros(200)
#recomendador([1,7,12])