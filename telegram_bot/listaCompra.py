from pymongo import MongoClient
from database import connect_to_database, insert_document, upsertDocument, findDocument, updateDocument, findDocuments, deleteDocument
from telegram.ext import ConversationHandler
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from settings import BOT_TOKEN

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def manejadorMenuListas(update, context, user_id):
    
    menuListas(update, context, user_id)
    
def menuListas(update, context, user_id):    

    keyboard = ReplyKeyboardMarkup([["Crear nueva lista"],["Ver mis listas"], ["Modificar una lista"], ["Eliminar una lista"]], resize_keyboard=True)
    context.bot.send_message(update.effective_chat.id, "📝 MENÚ DE LISTAS 📝", reply_markup=keyboard)
    
    keyboard = [[InlineKeyboardButton("Salir del menu", callback_data="salirMenu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(update.effective_chat.id, "👇 Salir del menu 👇", reply_markup=reply_markup)    

    
    """
    keyboard = [[InlineKeyboardButton("Crear nueva lista", callback_data="nuevaLista")], [InlineKeyboardButton("Ver tus listas", callback_data="verListas")],
                [InlineKeyboardButton("Modificar lista", callback_data="modificarLista")], [InlineKeyboardButton("EliminarLista", callback_data="eliminarLista")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.bot.send_message(chat_id=update.effective_chat.id, text="¿Qué quieres hacer?", reply_markup=reply_markup)
    """
    
    db = connect_to_database()
    collection = db['flags']
        
    datosActualizar = {
        "flagNuevaLista": 0,
        "flagNuevoProducto": 0,
        "flagMenuLista": 1,
        "flagVerLista": 0,
        "flagModificarLista": 0,
        "flagEliminarProducto": 0,
        "flagEliminarLista": 0,
        "flagAñadirProducto": 0
    }
    
    query = {"idUsuario": user_id}
           
    upsertDocument(collection, query, datosActualizar)    

# Función para responder al comando /nuevaLista
def manejarLista(update, context):
        nombreLista = update.message.text
        user_id = update.message.from_user.id
        user_name = update.message.from_user.first_name
        

        # Establecer la conexión con la base de datos
        db = connect_to_database()
        collection = db['listaCompra']  # Reemplaza 'listaCompra' con el nombre de tu colección

        # Insertar el documento en la colección
        documento_lista = {
            "nombreLista": nombreLista,
            "idUsuario": user_id,
            "nombreUsuario": user_name,
            "productos": []
        }
        insert_document(collection, documento_lista)
        
            # Responder al usuario con un mensaje de confirmación
        context.bot.send_message(chat_id=update.effective_chat.id, text="¡Nueva lista de compra creada!")
        
        
        collection = db['flags']
        
        datosActualizar = {
            "flagNuevaLista": 0,
            "flagNuevoProducto": 0,
            "nombreLista": nombreLista,
            "flagMenuLista": 0,
            "flagVerLista": 0
        }
    
        query = {"idUsuario": user_id}
            
        upsertDocument(collection, query, datosActualizar)
        
        modificar_lista(update, context, nombreLista, user_id)
        
def manejadorAñadirProducto(update, context, nombreLista, user_id):
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Nombre del producto que quieres añadir:")
        
        db = connect_to_database()
    
        collection = db['flags']
            
        datosActualizar = {
            "flagNuevaLista": 0,
            "flagNuevoProducto": 1,
            "flagMenuLista": 0,
            "flagVerLista": 0,
            "flagModificarLista": 0,
            "nombreLista": nombreLista
        }
        
        query = {"idUsuario": user_id}
                
        upsertDocument(collection, query, datosActualizar)

def manejadorEliminarProducto(update, context, nombreLista, user_id):
    db = connect_to_database()
    collection = db['listaCompra']  # Reemplaza 'listaCompra' con el nombre de tu colección

    query = {"nombreLista": nombreLista}
    documentoLista = findDocument(collection, query)
    
    productos = documentoLista.get("productos", [])
    
    #keyboard = ReplyKeyboardMarkup([["Crear nueva lista"],["Ver tus listas"], ["Modificar una lista"], ["Eliminar una lista"]], resize_keyboard=True)
    keyboard = [[producto] for producto in productos]
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    if len(productos) == 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"⚠️ No hay productos para eliminar ⚠️", reply_markup=ReplyKeyboardRemove())
        modificar_lista(update, context, nombreLista, user_id)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="¿Qué producto quieres eliminar?", reply_markup=reply_markup)

def eliminarProducto(update, context, nombreLista, nombreProducto):
    
        nombreProducto = update.message.text
        user_id = update.message.from_user.id
        user_name = update.message.from_user.first_name

        # Establecer la conexión con la base de datos
        db = connect_to_database()
        collection = db['listaCompra']  # Reemplaza 'listaCompra' con el nombre de tu colección

        query = {"nombreLista": nombreLista}
        documentoLista = findDocument(collection, query)  
        
        if documentoLista:
            
            # Obtener el array de productos del documento
            productos = documentoLista.get("productos", [])

            # Buscar el índice del producto en el array
            indice_producto = None
            for i, producto in enumerate(productos):
                if producto == nombreProducto:
                    indice_producto = i
                    break
            
            if len(productos) == 0:
                context.bot.send_message(chat_id=update.effective_chat.id, text=f"⚠️ No hay productos para eliminar ⚠️", reply_markup=ReplyKeyboardRemove())
                modificar_lista(update, context, nombreLista, user_id)

            else:    
                if indice_producto is not None:
                    # Eliminar el producto del array
                    productos.pop(indice_producto)

                    # Actualizar el documento en la base de datos con el nuevo array de productos
                    updateDocument(collection, query, {"productos": productos})

                    context.bot.send_message(chat_id=update.effective_chat.id, text=f"❌ '{nombreProducto}' eliminado ❌", reply_markup=ReplyKeyboardRemove())
                
                    modificar_lista(update, context, nombreLista, user_id)
                    
                    db = connect_to_database()
        
                    collection = db['flags']
                        
                    datosActualizar = {
                        "flagNuevaLista": 0,
                        "flagNuevoProducto": 0,
                        "flagMenuLista": 0,
                        "flagVerLista": 0,
                        "flagModificarLista": 1,
                        "flagEliminarProducto": 0,
                        "nombreLista": nombreLista
                    }
                    
                    query = {"idUsuario": user_id}
                    
                    upsertDocument(collection, query, datosActualizar)
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text=f"⚠️ Producto '{nombreProducto}' no encontrado ⚠️.")
                    context.bot.send_message(chat_id=update.effective_chat.id, text=f"¿Qué producto quieres eliminar?")
                    

def añadirProducto(update, context, nombreLista):
        nombreProducto = update.message.text
        user_id = update.message.from_user.id
        user_name = update.message.from_user.first_name

        # Establecer la conexión con la base de datos
        db = connect_to_database()
        collection = db['listaCompra']  # Reemplaza 'listaCompra' con el nombre de tu colección

        query = {"nombreLista": nombreLista}
        documentoLista = findDocument(collection, query)
        
        if documentoLista:
            
            # Obtener el array de productos del documento
            productos = documentoLista.get("productos", [])

            # Agregar el nuevo producto al array
            productos.append(nombreProducto)

            # Actualizar el documento en la base de datos con el nuevo array de productos
            updateDocument(collection, query, {"productos": productos})

            context.bot.send_message(chat_id=update.effective_chat.id, text=f"✅ '{nombreProducto}' añadido ✅.")
        
            modificar_lista(update, context, nombreLista, user_id)


def startLista( update, context):
    
    context.bot.send_message(chat_id=update.effective_chat.id, text="Vale 👍", reply_markup=ReplyKeyboardRemove())
    
    keyboard = [[InlineKeyboardButton("Cancelar", callback_data="Cancelar")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.bot.send_message(chat_id=update.effective_chat.id, text="¿Qué nombre quieres ponerle?", reply_markup=reply_markup)
    
    db = connect_to_database()
    collection = db['flags']
    
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    
    documento_flags = {
            "idUsuario": user_id,
            "nombreUsuario": user_name,
            "flagNuevaLista": 1,
            "flagNuevoProducto": 0,
            "flagMenuLista": 0,
            "flagVerLista": 0,
            "productos": []
        }
    
    query = {"idUsuario": user_id}
        
    upsertDocument(collection, query, documento_flags)

def cancelarLista(update, context, user_id):

    db = connect_to_database()
    
    collection = db['flags']
    query = {"idUsuario": user_id}
    listaFlags = findDocument(collection, query)

    collection = db['flags']
        
    datosActualizar = {
        "flagNuevaLista": 0,
        "flagNuevoProducto": 0,
        "nombreLista": "",
        "flagMenuLista": 0,
        "flagVerLista": 0,
        "flagModificarLista": 0,
        "flagAñadirProducto": 0,
        "flagEliminarProducto": 0
    }
    
    query = {"idUsuario": user_id}
           
    upsertDocument(collection, query, datosActualizar)    

    if listaFlags["flagNuevaLista"] == 1:
        menuListas(update, context, user_id)
        
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Vale, salimos del menu de listas 👍", reply_markup=ReplyKeyboardRemove())

def ver_lista(update, context, nombreLista):

        # Establecer la conexión con la base de datos
        db = connect_to_database()
        collection = db['listaCompra']  
        query = {"nombreLista": nombreLista}
        listaCompra = findDocument(collection, query)
        
        ticket = generar_ticket_lista(listaCompra["nombreLista"], listaCompra["productos"])
        
        keyboard = [[InlineKeyboardButton("Volver al menu", callback_data="volverMenu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        context.bot.send_message(chat_id=update.effective_chat.id, text=ticket, reply_markup=reply_markup)
        
        collection = db['flags']
        
        datosActualizar = {
            "flagNuevaLista": 0,
            "flagNuevoProducto": 0,
            "nombreLista": "",
            "flagMenuLista": 0,
            "flagVerLista": 0,
            "flagModificarLista": 0,
            "nombreLista": nombreLista
        }
        
        user_id = listaCompra["idUsuario"]
        query = {"idUsuario": user_id}
            
        upsertDocument(collection, query, datosActualizar)
        
def modificar_lista(update, context, nombreLista, user_id):

        # Establecer la conexión con la base de datos
        db = connect_to_database()
        collection = db['listaCompra']  
        query = {"nombreLista": nombreLista}
        listaCompra = findDocument(collection, query)
        
        collection = db['flags']
        
        datosActualizar = {
            "flagNuevaLista": 0,
            "flagNuevoProducto": 0,
            "nombreLista": "",
            "flagMenuLista": 0,
            "flagVerLista": 0,
            "flagModificarLista": 1,
            "nombreLista": nombreLista
        }
        
        query = {"idUsuario": user_id}
            
        upsertDocument(collection, query, datosActualizar)   
        
        keyboard = [[InlineKeyboardButton("Añadir producto", callback_data="añadirProducto")], [InlineKeyboardButton("Eliminar producto", callback_data="eliminarProducto")], [InlineKeyboardButton("Salir", callback_data="salir")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        ticket = generar_ticket_lista(listaCompra["nombreLista"], listaCompra["productos"])
        context.bot.send_message(chat_id=update.effective_chat.id, text=ticket, reply_markup=reply_markup)
                
        

"""////////////////////////////////// FUNCIONES AUXILIARES //////////////////////////////////"""

def ver_listas(update, context, mensaje):
    
    # palabras = ["palabra1", "palabra2", "palabra3"]
    user_id = update.message.from_user.id
 
    db = connect_to_database()
    
    collection = db['flags']
    
    datosActualizar = ""

    if mensaje == "Ver mis listas":
        
        datosActualizar = {
            "flagNuevaLista": 0,
            "flagNuevoProducto": 0,
            "flagMenuLista": 0,
            "flagVerLista": 1,
            "falgEliminarLista": 0
        }
        
    elif mensaje == "Eliminar una lista":
        
        datosActualizar = {
            "flagNuevaLista": 0,
            "flagNuevoProducto": 0,
            "flagMenuLista": 0,
            "flagVerLista": 0,
            "flagEliminarLista": 1
        }
        
    query = {"idUsuario": user_id}
            
    upsertDocument(collection, query, datosActualizar)

    collection = db['listaCompra']
    
    query = {"idUsuario": user_id}
           
    findDocuments(collection, query)
    listas = collection.find(query)

    palabras = []

    # Iterar sobre los documentos y agregar los nombres de las listas al array
    for documento in listas:
        nombre = documento["nombreLista"]
        palabras.append(nombre)

    if len(palabras) == 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No tienes ninguna lista creada 😭")
        menuListas(update, context)
    else:
        keyboard = [[InlineKeyboardButton(palabra, callback_data=palabra)] for palabra in palabras]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if mensaje == "Ver mis listas":
            # update.message.reply_text(text="¿Cuál de tus listas de la compra quieres ver?", reply_markup=reply_markup)
            context.bot.send_message(chat_id=update.effective_chat.id, text="¡Muy bien!", reply_markup=ReplyKeyboardRemove())
            context.bot.send_message(chat_id=update.effective_chat.id, text="¿Cual de tus listas quieres ver?", reply_markup=reply_markup)
        elif mensaje == "Eliminar una lista":
            context.bot.send_message(chat_id=update.effective_chat.id, text="¡Muy bien!", reply_markup=ReplyKeyboardRemove())
            context.bot.send_message(chat_id=update.effective_chat.id, text="¿Cual de tus listas quieres eliminar?", reply_markup=reply_markup)
        
def modificar_listas(update, context):
    
    # palabras = ["palabra1", "palabra2", "palabra3"]
    user_id = update.message.from_user.id
 
    db = connect_to_database()
    
    collection = db['flags']
        
    datosActualizar = {
        "flagNuevaLista": 0,
        "flagNuevoProducto": 0,
        "flagMenuLista": 0,
        "flagVerLista": 0,
        "flagModificarLista": 1
    }
    
    query = {"idUsuario": user_id}
            
    upsertDocument(collection, query, datosActualizar)

    collection = db['listaCompra']
    
    query = {"idUsuario": user_id}
           
    findDocuments(collection, query)
    listas = collection.find(query)

    palabras = []

    # Iterar sobre los documentos y agregar los nombres de las listas al array
    for documento in listas:
        nombre = documento["nombreLista"]
        palabras.append(nombre)

    if len(palabras) == 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No tienes ninguna lista creada 😭")
    else:
        keyboard = [[InlineKeyboardButton(palabra, callback_data=palabra)] for palabra in palabras]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # update.message.reply_text(text="¿Cuál de tus listas de la compra quieres ver?", reply_markup=reply_markup)
        context.bot.send_message(chat_id=update.effective_chat.id, text="¿Cual de tus listas quieres modificar?", reply_markup=reply_markup)

    
def generar_ticket_lista(nombreLista, productos):
    separador = "─"

    anchura_maxima_ticket = 10

    # Encabezado del ticket
    encabezado = f"{separador * (anchura_maxima_ticket)}\n"
    encabezado += f" {nombreLista} \n"
    encabezado += f"{separador * (anchura_maxima_ticket)}\n"

    cuerpo = ""

    for producto in productos:
        # Agregar cada producto en una línea diferente
        cuerpo += f" {producto} \n"
        
    if len(productos) == 0:
        cuerpo = "⚠️ Lista vacía ⚠️"

    # Combinar encabezado y cuerpo del ticket
    ticket = encabezado + cuerpo
    
    lineas = ticket.strip().split("\n")
    ticket = "\n".join(line.center(len(line) + (anchura_maxima_ticket - len(line)) // 2) for line in lineas)


    # Agregar el borde inferior del ticket
    ticket += f"\n{separador * (anchura_maxima_ticket)}\n"

    return ticket

def boton_presionado_listas(update, context):
    
    user_id = update.callback_query.from_user.id

    
    db = connect_to_database()
    collection = db['flags']
    
    query = {"idUsuario": user_id}
            
    listaFlags = findDocument(collection, query)
    
    textoBotonAux = update.callback_query
    textoBoton = textoBotonAux.data
    
    if listaFlags["flagVerLista"] == 1:
        query = update.callback_query
        palabra_seleccionada = query.data
        ver_lista(update, context, palabra_seleccionada)
    elif listaFlags["flagModificarLista"] == 1:
        
        if textoBoton == "añadirProducto":
            
            db = connect_to_database()
    
            collection = db['flags']
                
            datosActualizar = {
                "flagNuevaLista": 0,
                "flagNuevoProducto": 1,
                "flagMenuLista": 0,
                "flagVerLista": 0,
                "flagModificarLista": 0
            }
            
            query = {"idUsuario": user_id}
            
            db = connect_to_database()
            collection = db['flags']
            
            query = {"idUsuario": user_id}
                    
            listaFlags = findDocument(collection, query)
                    
            upsertDocument(collection, query, datosActualizar)
            manejadorAñadirProducto(update, context, listaFlags["nombreLista"], user_id)
        elif textoBoton == "eliminarProducto":
            db = connect_to_database()
    
            collection = db['flags']
                
            datosActualizar = {
                "flagNuevaLista": 0,
                "flagNuevoProducto": 0,
                "flagMenuLista": 0,
                "flagVerLista": 0,
                "flagModificarLista": 0,
                "flagEliminarProducto": 1
            }
            
            query = {"idUsuario": user_id}
            upsertDocument(collection, query, datosActualizar)
            manejadorEliminarProducto(update, context, listaFlags["nombreLista"], user_id)
            
        elif textoBoton == "salir":
            menuListas(update, context, user_id)
        
        else:
            query = update.callback_query
            palabra_seleccionada = query.data
            modificar_lista(update, context, palabra_seleccionada, user_id)
    elif listaFlags["flagEliminarLista"] == 1:
        
        eliminarLista(update, context, textoBoton, user_id)
    elif listaFlags["flagMenuLista"] == 1:
        if textoBoton == "salirMenu":
            cancelarLista(update, context, user_id)

    else:
        
        if textoBoton == "volverMenu":
            menuListas(update, context, user_id)
        else:
            cancelarLista(update, context, user_id)
        
def eliminarLista(update, context, nombreLista, user_id):
    
    db = connect_to_database()
    collection = db['listaCompra']
    query = {"nombreLista": nombreLista}
    
    deleteDocument(collection, query)
    
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Lista '{nombreLista}' eliminada correctamente")
    
    menuListas(update, context, user_id)
