import sys
import csv
import random

RUTA_ARCHIVO_TWEETS = 'tweets.csv'
RUTA_FAVORITOS = 'favoritos.csv'
MENSAJE_AYUDA = 'BIENVENIDO A ALGOTWEETS! \nLos comandos disponibles son los siguientes (debe ingresar obligatoriamente uno):\n\n* GENERAR: permite generar un tweet pseudo-aleatoriamente utilizando como fuente los tweets de los usuarios seleccionados.\nA continuación del comando puede listar los usuarios con los que quiere generar tweets (deben existir en los tweets almacenados). Si no lo hace, se utilizarán todos los disponibles.\nEj.: "python3 algotweets.py generar lesluthiersq erescurioso"\n\n* TRENDING: muestra tos temas más comunes de los que se habla en los tweets almacenados. A continuación del comando debe ingresar obligatoriamente la cantidad que quiere ver.\n Ej.: "python3 algotweets.py trending 3" le mostrará los tres primeros temas más comentados.\n\n* FAVORITOS: le permite ver los tweets que ha almacenado como favoritos. Opcionalmente, puede ingresar a continuación la cantidad que quiere ver.\nEj.: "python3 algotweets.py favoritos 3" le mostrará los últimos 3 tweets guardados en favoritos.'
MENSAJE_AGREGAR_FAVORITOS = '¿Desea agregar este tweet a favoritos? [s/n]: '
MENSAJE_AGREGAR_FAVORITOS_INGRESO_INVALIDO = 'No se reconoce la respuesta. ' + MENSAJE_AGREGAR_FAVORITOS
MENSAJE_AGREGAR_FAVORITOS_ERROR = 'No se pudo agregar el tweet a favoritos, verifique que no tenga el archivo abierto y vuelva a intentar.'
MENSAJE_ABRIR_ARCHIVO_ERROR = 'No se pudo cargar el archivo con tweets almacenados, verifique que no se encuentre abierto y que esté en la ruta correspondiente, y vuelva a intentar.'
MENSAJE_ABRIR_ARCHIVO_FAV_ERROR = 'No se pudo cargar el archivo con tweets almacenados, verifique que no se encuentre abierto y que ya haya agregado algún tweet como favorito, y vuelva a intentar.'
MENSAJE_TWEET_AGREGADO = 'Tweet agregado a favoritos.'
MENSAJE_GENERANDO_TWEET = 'Generando tweet a partir de: '
sys.argv.pop(0) #Elimina el nombre del archivo de la lista de comandos ingresados por el usuario

def procesar_archivo_tweets(archivo_tweets):
    """Recibe el archivo con los tweets almacenados.
    Devuelve un diccionario que contiene los trending topics en formato {#topic: cantidad de veces que aparece}
    y otro para las palabras utilizadas por cada usuario, en formato {usuario: {palabra: [palabras siguientes]}}"""
    trending_topics = {}
    palabras_por_usuario = {}
    with open (archivo_tweets, encoding = "utf8") as source:
        source_csv = csv.reader(source, delimiter = '\t')
        for usuario, tweet in source_csv:
            palabras_tweet, cantidad_palabras = tweet.split(), len(tweet.split())
            palabras_por_usuario[usuario] = palabras_por_usuario.get(usuario, {})
            for p in range(cantidad_palabras):
                palabra, proxima_palabra = palabras_tweet[p], ''
                if palabra[0] == '#':
                    trending_topics[palabra] = trending_topics.get(palabra, 0) + 1
                if p != cantidad_palabras - 1:
                    proxima_palabra = palabras_tweet[p + 1]
                palabras_por_usuario[usuario][palabra] = palabras_por_usuario[usuario].get(palabra, {})
                palabras_por_usuario[usuario][palabra][proxima_palabra] = palabras_por_usuario[usuario][palabra].get(proxima_palabra, 0) + 1
    return trending_topics, palabras_por_usuario

def mostrar_tweet_generado(palabras_por_usuario, lista_usuarios, trending_topics):
    """Recibe el diccionario de palabras, la lista de usuarios entre los que se deben mezclar tweets, 
    y el diccionario de trending topics.
    Imprime un nuevo tweet generado pseudo-aleatoriamente entre dichos usuarios."""
    lista_usuarios_nueva = regularizar_lista_usuarios(palabras_por_usuario, lista_usuarios)
    print(MENSAJE_GENERANDO_TWEET + ', '.join(lista_usuarios_nueva) + '...')
    palabras_usuarios_elegidos = generar_diccionario_palabras_usuarios(palabras_por_usuario, lista_usuarios_nueva)
    tweet_nuevo = generar_tweet(palabras_usuarios_elegidos)
    tweet_nuevo = tweet_nuevo[0].upper() + tweet_nuevo[1:] #Capitaliza el tweet
    print(f'"""\n{tweet_nuevo}\n"""\n')
    ofrecer_agregar_favoritos(tweet_nuevo)

def generar_tweet(palabras_usuarios_elegidos):
    """Recibe el diccionario de palabras para los usuarios elegidos.
    Devuelve un nuevo tweet generado pseudo-aleatoriamente usando como fuente los tweets de dichos usuarios."""
    tweet_nuevo = ''
    proxima_palabra = random.choice(list(palabras_usuarios_elegidos.keys()))
    while len(tweet_nuevo + proxima_palabra) < 281 and proxima_palabra != '':
        tweet_nuevo += proxima_palabra + ' '
        cant_proximas_palabras = sum(palabras_usuarios_elegidos[proxima_palabra].values())
        eleccion, suma_apariciones_palabras = random.randint(1, cant_proximas_palabras), 0
        for palabra in palabras_usuarios_elegidos[proxima_palabra]:
            suma_apariciones_palabras += palabras_usuarios_elegidos[proxima_palabra][palabra]
            if suma_apariciones_palabras >= eleccion:
                proxima_palabra = palabra
                break
    return tweet_nuevo

def generar_diccionario_palabras_usuarios(palabras_por_usuario, lista_usuarios):
    """Recibe el diccionario de palabras general, y la lista de usuarios que se utilizarán para generar un tweet.
    Devuelve un nuevo diccionario que contiene como:
    * Claves: cada una de las palabras utilizadas por los usuarios de la lista recibida.
    * Valores: otro diccionario con las palabras que siguen a las claves, y como valor, la cantidad de apariciones de cada una."""
    dic_palabras_usuarios = {}
    for usuario in lista_usuarios:
        for palabra in palabras_por_usuario[usuario]:
            dic_palabras_usuarios[palabra] = dic_palabras_usuarios.get(palabra, {})
            for palabra_siguiente in palabras_por_usuario[usuario][palabra]:
                dic_palabras_usuarios[palabra][palabra_siguiente] = dic_palabras_usuarios[palabra].get(palabra_siguiente, 0) + palabras_por_usuario[usuario][palabra][palabra_siguiente]
    return dic_palabras_usuarios
    
def ofrecer_agregar_favoritos(tweet_nuevo):
    """Recibe el nuevo tweet generado y ofrece al usuario agregarlo a favoritos.
    Si acepta, lo guarda en la ruta correspondiente al final del archivo (RUTA_FAVORITOS).
    Si no puede acceder al archivo, muestra en pantalla un mensaje de ayuda."""
    quiere_agregar_favoritos = input(MENSAJE_AGREGAR_FAVORITOS).lower()
    while quiere_agregar_favoritos not in ('s', 'n'):
        quiere_agregar_favoritos = input(MENSAJE_AGREGAR_FAVORITOS_INGRESO_INVALIDO).lower()
    if quiere_agregar_favoritos == 's':
        try:
            with open (RUTA_FAVORITOS, 'a', encoding = 'utf-8') as tweet_favoritos:
                tweet_favoritos.write(tweet_nuevo + '\n')
            print(MENSAJE_TWEET_AGREGADO)
        except (PermissionError, IOError):
            print(MENSAJE_AGREGAR_FAVORITOS_ERROR)

def regularizar_lista_usuarios(palabras_por_usuario, lista_usuarios):
    """Recibe el diccionario de palabras y la lista de usuarios entre los que se mezclarán tweets.
    Devuelve una nueva lista regularizada (verifica que un usuario no esté dos veces, y si la lista estaba vacía la completa con todos los usuarios)."""
    if len(lista_usuarios) == 0:
        return list(palabras_por_usuario.keys())
    lista_usuarios_nueva = []
    for usuario in lista_usuarios:
        if usuario not in lista_usuarios_nueva:
            lista_usuarios_nueva.append(usuario)
    return lista_usuarios_nueva            

def mostrar_trending_topics(palabras_por_usuario, ingreso_auxiliar, trending_topics):
    """Recibe el diccionario de palabras, el ingreso auxiliar al comando principal, y los trending topics.
    Imprime tantos trending topics como el usuario haya indicado."""
    cantidad_trending_topics = int(ingreso_auxiliar[0])
    trending_topics_ordenados = sorted(trending_topics.items(), key = lambda x: -x[1])
    for i in range (min(cantidad_trending_topics, len(trending_topics_ordenados))):
        print(trending_topics_ordenados[i][0])

def mostrar_favoritos(palabras_por_usuario, ingreso_auxiliar, trending_topics):
    """Recibe el diccionario de palabras, el ingreso auxiliar al comando, y el diccionario de trending topics.
    Muestra tantos favoritos como el usuario haya indicado, y sino especificó un número imprime todos.
    Si no puede abrir el archivo de favoritos, muestra un mensaje de ayuda."""
    try:
        with open (RUTA_FAVORITOS, encoding = 'utf-8') as favoritos:
            favoritos_descendente = [tweet for tweet in favoritos][::-1]
    except (PermissionError, IOError, FileNotFoundError):
        print(MENSAJE_ABRIR_ARCHIVO_FAV_ERROR)
        return
    if len(ingreso_auxiliar) == 1:
        cantidad_favoritos = int(ingreso_auxiliar[0])
        contador = 0
        while contador < cantidad_favoritos and contador < len(favoritos_descendente):
            print(favoritos_descendente[contador])
            contador += 1
        return
    for tweet in favoritos_descendente:
        print(tweet)

def es_comando_valido(palabras_por_usuario, comando_principal, ingreso_auxiliar):
    """Recibe el diccionario de palabras, el comando principal, y el ingreso auxiliar al mismo
    Verifica si dicho comando es válido, devuelve un booleano."""
    if comando_principal not in ('generar', 'trending', 'favoritos'):
        return False
    largo_ingreso_auxiliar = len(ingreso_auxiliar)
    if comando_principal == 'generar' and largo_ingreso_auxiliar != 0:
        for usuario in ingreso_auxiliar:
            if usuario not in palabras_por_usuario:
                return False
    if comando_principal == 'trending' and (largo_ingreso_auxiliar != 1 or not sys.argv[1].isdigit() or sys.argv[1] == '0'):
            return False
    if comando_principal == 'favoritos' and (largo_ingreso_auxiliar > 1 or (largo_ingreso_auxiliar == 1 and not sys.argv[1].isdigit())):
            return False
    return True

COMANDOS = {'generar': mostrar_tweet_generado, 'trending': mostrar_trending_topics, 'favoritos': mostrar_favoritos}

def main():
    """Función principal del programa.
    Si no puede abrir el archivo de tweets muestra en pantalla un mensaje de ayuda.
    Si el comando ingresado, o su información auxiliar no son válidos, imprime instrucciones de uso.
    Sino, ejecuta el comando según lo solicitado por el usuario."""
    if len(sys.argv) == 0:
        print(MENSAJE_AYUDA)
        return
    comando_principal = sys.argv[0].lower()
    ingreso_auxiliar = sys.argv[1:]
    try:
        trending_topics, palabras_por_usuario = procesar_archivo_tweets(RUTA_ARCHIVO_TWEETS)
    except (IOError, PermissionError, FileNotFoundError):
        print(MENSAJE_ABRIR_ARCHIVO_ERROR)
        return
    if not es_comando_valido(palabras_por_usuario, comando_principal, ingreso_auxiliar):
        print(MENSAJE_AYUDA)
        return
    COMANDOS[comando_principal](palabras_por_usuario, ingreso_auxiliar, trending_topics)

main()