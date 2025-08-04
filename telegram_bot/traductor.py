from pymongo import MongoClient
from database import connect_to_database, insert_document, upsertDocument, findDocument, updateDocument, findDocuments, deleteDocument
# from translate import Translator
from googletrans import Translator
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from settings import BOT_TOKEN

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def manejadorIniciarTraduccion(update, context, user_id):
        
    iniciarTraduccion(update, context, user_id)
    
def iniciarTraduccion(update, context, user_id):
    
    keyboard = ReplyKeyboardMarkup([["Inglés 🇬🇧"], ["Francés 🇫🇷"], ["Japonés 🇯🇵"]], resize_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text="¿A qué idioma quieres traducir?" , reply_markup=keyboard)
    
    activarFlag(update, context, user_id, "flagIntroducirIdioma")
    

def introducirTraduccion(update, context, idioma, user_id):
    
    codigoIdioma = ""
    
    if idioma == "Inglés 🇬🇧":
        codigoIdioma = "en"
    elif idioma == "Francés 🇫🇷":
        codigoIdioma = "fr"
    elif idioma == "Japonés 🇯🇵":
        codigoIdioma = "ja"
    
    vaciarFlags(update, context, user_id)
    
    activarFlag(update, context, user_id, "flagTraducir")
    
    db = connect_to_database()
        
    collection = db['flags']
                        
    datosActualizar = {
        "codigoIdioma": codigoIdioma
    }
                    
    query = {"idUsuario": user_id}
                   
    upsertDocument(collection, query, datosActualizar)
    
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Traducirás al '{idioma}'!\n"
                                                                     "Escribe mensajes y los traduciré", reply_markup=ReplyKeyboardRemove())
    
def traducir(update, context, mensaje, user_id):
    
    db = connect_to_database()
        
    collection = db['flags']
      
    query = {"idUsuario": user_id}
                   
    documentoFlags = findDocument(collection, query)
    
    codigoIdioma = documentoFlags["codigoIdioma"]
    
    bandera = ""
    
    if codigoIdioma == "en":
        bandera = "🇬🇧"
    elif codigoIdioma == "fr":
        bandera = "🇫🇷"
    elif codigoIdioma == "ja":
        bandera = "🇯🇵"
        
    """
    traductor = Translator(to_lang=codigoIdioma)
    traduccion = traductor.translate(mensaje)
    """
    
    #translator = Translator()
    #traduccion = translator.translate(mensaje, dest=codigoIdioma)
    
    keyboard = [[InlineKeyboardButton("Cancelar", callback_data="cancelar")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"{bandera}: {traduccion.text}", reply_markup=reply_markup)

def vaciarFlags(update, context, user_id):
    
    db = connect_to_database()
        
    collection = db['flags']
                        
    datosActualizar = {
        "flagIntroducirIdioma": 0,
        "flagTraducir": 0
    }
                    
    query = {"idUsuario": user_id}
                   
    upsertDocument(collection, query, datosActualizar)
    
def activarFlag(update, context, user_id, flag):
    
    db = connect_to_database()
        
    collection = db['flags']
                        
    datosActualizar = {
        flag: 1
    }
                    
    query = {"idUsuario": user_id}
                   
    upsertDocument(collection, query, datosActualizar)
    
def boton_presionado_traductor(update, context):
    
    user_id = update.callback_query.from_user.id

    textoBotonAux = update.callback_query
    textoBoton = textoBotonAux.data
    
    if textoBoton == "cancelar":
        cancelarTraduccion(update, context, user_id)
        
def cancelarTraduccion(update, context, user_id):
    vaciarFlags(update, context, user_id)
    
    context.bot.send_message(chat_id=update.effective_chat.id, text="Recibido, dejamos de traducir.", reply_markup=ReplyKeyboardRemove())

    