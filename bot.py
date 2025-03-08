import discord
import requests
import json
from discord.ext import commands
import os
import webserver
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Cargar configuración
GEMINI_API_KEY = "AIzaSyBnaO6WXeemBkFS5jpaaltCfflvCltZgAY"

# Configuración del bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

# Cargar información del archivo txt completo
def cargar_informacion():
    try:
        with open("informacion.txt", "r", encoding="utf-8") as file:
            return file.read()  # Lee todo el contenido del archivo
    except FileNotFoundError:
        print("Error: El archivo 'informacion.txt' no se encontró.")
        return ""

# Función para dividir un texto en fragmentos de menos de 2000 caracteres
def dividir_texto(texto, limite=2000):
    fragmentos = []
    while len(texto) > limite:
        # Encuentra el último espacio dentro del límite
        ultimo_espacio = texto.rfind(' ', 0, limite)
        if ultimo_espacio == -1:
            ultimo_espacio = limite  # Si no hay espacios, corta en el límite
        fragmentos.append(texto[:ultimo_espacio])
        texto = texto[ultimo_espacio:].lstrip()  # Elimina espacios al inicio del siguiente fragmento
    fragmentos.append(texto)  # Añade el último fragmento
    return fragmentos

# Comando para hacer preguntas a la IA
@bot.command(name='ask')
async def ask(ctx, *, question: str):
    await ctx.defer()  # Respuesta diferida (para indicar que el bot está procesando)

    # Cargar el contenido completo del archivo txt
    informacion_servidor = cargar_informacion()

    # Contexto sobre quién es el bot y qué hace
    context = (
        "Eres un asistente virtual gato macho llamado 'Emi'. Tu tarea es responder preguntas y brindar explicaciones breves "
        "sobre el servidor de Minecraft StormCraft ambientado en Naruto. "
        "Puedes referirte a la gente diciendo 'Miau g'. "
        "Usa emojis para mandar mensajes más llamativos a los jugadores. "
        "Responde las preguntas de manera concisa sin alargar tus respuestas. "
        f"Aquí tienes información sobre el servidor:\n{informacion_servidor} "
        "Complementa esta información con datos de la wiki de Naruto o los videojuegos si corresponde."
    )
    
    # URL de la API de Gemini
    model = "gemini-2.0-flash-exp"  # Sustituye con el modelo que deseas usar
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
    
    # Datos para la solicitud con contexto
    data = {
        "contents": [
            {
                "parts": [
                    {"text": context},
                    {"text": question}
                ]
            }
        ]
    }

    # Encabezados de la solicitud
    headers = {
        'Content-Type': 'application/json'
    }

    # Enviar la solicitud a la API
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Lanza una excepción si la respuesta no es exitosa
        answer = response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No pude generar una respuesta.")
        
        # Dividir la respuesta en fragmentos de menos de 2000 caracteres
        fragmentos = dividir_texto(answer)
        
        # Enviar cada fragmento como un mensaje separado
        for fragmento in fragmentos:
            await ctx.send(fragmento)
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            await ctx.send("Error: No autorizado. Verifica tu clave de API.")
        elif response.status_code == 404:
            await ctx.send("Error: Endpoint no encontrado. Revisa la URL o el modelo.")
        else:
            await ctx.send(f"Hubo un error al procesar la pregunta: {e}")
    except Exception as e:
        await ctx.send(f"Hubo un error al procesar la pregunta: {e}")

# Evento cuando el bot está listo
@bot.event
async def on_ready():
    print(f'{bot.user} ha iniciado sesión en Discord.')

# Iniciar el bot
webserver.keep_alive()
bot.run(DISCORD_TOKEN)