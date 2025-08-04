import logging
import re
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from unidecode import unidecode
from database import  connect_to_database, findDocument, limpiarFlags
from listaCompra import *
from traductor import *
import sys
import signal
from settings import BOT_TOKEN

# Configura el token de tu bot proporcionado por el BotFather

class TelegramBot:
    
    inicializadas = 0

    def __init__(self, token):
    
        # Configuración de registro para mensajes de error
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)

        # Creamos el objeto Updater
        self.updater = Updater(token=BOT_TOKEN, use_context=True)
        self.dispatcher = self.updater.dispatcher
        
        # Asociamos los comandos con sus respectivos manejadores
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(CommandHandler("help", self.help))

        # Asociamos el manejador de mensajes
        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.respond_to_message))
        
        
        self.dispatcher.add_handler(CommandHandler("listas", self.irListas))

        self.dispatcher.add_handler(CommandHandler("traducir", self.irTraduccion))


        limpiarFlags()
                
        # Manejar la señal de interrupción (Control+C)
        signal.signal(signal.SIGINT, self.stop_bot)
        
        return

    def limpiarTexto(self, text):
        # Eliminamos las tildes
        textoSinTildes = unidecode(text)
        
        # Utilizamos una expresión regular para quitar signos de puntuación y otros caracteres no deseados
        textoLimpio = re.sub(r'[^\w\s]', '', textoSinTildes)
        return textoLimpio

    def start(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="¡Hola! Soy Rewibot. ¡Escribe /help para obtener ayuda!")

    def help(self, update, context):
        
        keyboard = ReplyKeyboardMarkup([["/start"], ["/help"], ["/listas"]], resize_keyboard=True)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Lista de comandos del bot:\n\n"
                                                                        "🤖 Comandos generales 🤖\n"
                                                                        "/start - Iniciar el bot\n"
                                                                        "/help - Mostrar este mensaje de ayuda\n\n"
                                                                        "📝 Listas de la compra 📝 \n"
                                                                        "/listas para acceder al menu", reply_markup = keyboard)
    
    def stop_bot(self, sig, frame):
        # Función para detener el bot y cerrar la ejecución
        self.updater.stop()
        sys.exit(0)


    """ //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////// """

    def respond_to_message(self, update, context):
        
        user_id = update.message.from_user.id
        user_name = update.message.from_user.first_name
        
        listaFlags = self.obtenerFlags(user_id)
                
        hayFlags = self.verificarFlags(listaFlags, context, update)
        
        # Obtener el mensaje del usuario
        mensaje = update.message.text
                
        # obtener el usuario
        user = update.message.from_user
        
        if hayFlags:
            
            self.gestionarFlags(update, context, mensaje, listaFlags)
        else:
            
            if self.inicializadas == 0:
                self.inicializarFlags(user_id, user_name)
                self.inicializadas = 1

            # Obtener el mensaje del usuario
            user_message = update.message.text.lower()
            mensaje = self.limpiarTexto(user_message)

            if mensaje == "hola":
                context.bot.send_message(chat_id=update.effective_chat.id, text="Hola {}. \n"
                                                                                "Dale a 👉 /help para ver los comandos disponibles.".format(user.first_name))

            elif mensaje in ["que tal", "como estas", "que tal estas", "como andas"]:
                context.bot.send_message(chat_id=update.effective_chat.id, text="bien y tu?")

            # Responder de manera predeterminada a otros mensajes
            elif "gracias" in mensaje:
                context.bot.send_message(chat_id=update.effective_chat.id, text="de nada para eso estamos jjajajaj 😁")
                
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="{} 😂".format(mensaje))  
            
            
    def gestionarFlags(self, update, context, mensaje, listaFlags):
        
        user_id = update.message.from_user.id
        user_name = update.message.from_user.first_name
            
        if listaFlags["flagNuevaLista"] == 1:
            manejarLista(update, context)
        if listaFlags["flagNuevoProducto"] == 1:
            nombreListaAux = listaFlags["nombreLista"]
            añadirProducto(update, context, nombreListaAux) 
        if listaFlags["flagMenuLista"] == 1:
            if mensaje == "Crear nueva lista":
                startLista(update, context)
            if mensaje == "Ver mis listas":
                ver_listas(update, context, mensaje)
            if mensaje == "Modificar una lista":
                modificar_listas(update, context)
            if mensaje == "Eliminar una lista":
                ver_listas(update, context, mensaje)
        if listaFlags["flagEliminarProducto"] == 1:
            nombreListaAux = listaFlags["nombreLista"]    
            eliminarProducto(update, context, nombreListaAux, user_id)
            
        if listaFlags["flagIntroducirIdioma"] == 1:
            introducirTraduccion(update, context, mensaje, user_id)
        if listaFlags["flagTraducir"] == 1:
            traducir(update, context, mensaje, user_id)
            
    """ /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////// """


    def obtenerFlags(self, idUsuario):
        
        db = connect_to_database()
        collection = db['flags']
        query = {"idUsuario": idUsuario}
        
        documentoFlags = findDocument(collection, query)
        
        if documentoFlags:
            # Si se encontró el documento, creamos un diccionario con los campos y sus valores
            listaFlags = {campo: valor for campo, valor in documentoFlags.items()}
            return listaFlags
        else:
        # Si no se encontró el documento, devolvemos None
            return None
        
    def verificarFlags(self, listaFlags, context, update):

        if listaFlags is not None:
            if 1 in listaFlags.values():
                return True
            
        # Si no se encontró ningún 1 en los valores del diccionario o listaFlags es none, devuelve False
        return False
    
    def inicializarFlags(self, idUsuario, user_name):
        db = connect_to_database()
        collection = db['flags']
        query = {"idUsuario": idUsuario}
                
        documento_flags = {
            "idUsuario": idUsuario,
            "nombreUsuario": user_name,
            "flagNuevaLista": 0,
            "flagNuevoProducto": 0,
            "flagMenuLista": 0,
            "flagVerLista": 0,
            "flagIntroducirIdioma": 0,
            "flagEliminarProducto": 0,
            "productos": [],
            "flagTraducir": 0
        }
        
        upsertDocument(collection, query, documento_flags)
    
    def irTraduccion(self, update, context):
        user_id = update.message.from_user.id
        user_name = update.message.from_user.first_name
  
        if self.inicializadas == 0:
                self.inicializarFlags(user_id, user_name)
                self.inicializadas = 1
                
        self.dispatcher.add_handler(CallbackQueryHandler(boton_presionado_traductor))

        manejadorIniciarTraduccion(update, context, user_id)
        
    def irListas(self, update, context):
        user_id = update.message.from_user.id
        user_name = update.message.from_user.first_name
      
        if self.inicializadas == 0:
                self.inicializarFlags(user_id, user_name)
                self.inicializadas = 1
                
        self.dispatcher.add_handler(CallbackQueryHandler(boton_presionado_listas))
        
        manejadorMenuListas(update, context, user_id)

# Iniciar el bot  

if __name__ == '__main__':
    
    a = TelegramBot(BOT_TOKEN)
    a.updater.start_polling()
    a.updater.idle()
