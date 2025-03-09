import discord
import requests
import json
from discord.ext import commands
import os
import webserver
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

GEMINI_API_KEY = "AIzaSyBnaO6WXeemBkFS5jpaaltCfflvCltZgAY"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

def cargar_informacion():
    try:
        with open("informacion.txt", "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print("Error: El archivo 'informacion.txt' no se encontró.")
        return ""

def dividir_texto(texto, limite=2000):
    fragmentos = []
    while len(texto) > limite:
        ultimo_espacio = texto.rfind(' ', 0, limite)
        if ultimo_espacio == -1:
            ultimo_espacio = limite
        fragmentos.append(texto[:ultimo_espacio])
        texto = texto[ultimo_espacio:].lstrip()
    fragmentos.append(texto)
    return fragmentos

@bot.command(name='ask')
async def ask(ctx, *, question: str):
    await ctx.defer()

    informacion_servidor = cargar_informacion()

    context = (
        "Eres un asistente virtual gato macho llamado 'Emi'. Tu tarea es responder preguntas y brindar explicaciones breves "
        "sobre el servidor de Minecraft StormCraft ambientado en Naruto. "
        "Puedes referirte a la gente diciendo 'Miau g'. "
        "Usa emojis para mandar mensajes más llamativos a los jugadores. "
        "Responde las preguntas de manera concisa sin alargar tus respuestas. "
        f"Aquí tienes información sobre el servidor:\n{informacion_servidor} "
        "Complementa esta información con datos de la wiki de Naruto o los videojuegos si corresponde."
    )
    
    model = "gemini-2.0-flash-exp"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
    
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

    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status() 
        answer = response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No pude generar una respuesta.")
        
        fragmentos = dividir_texto(answer)
        
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

@bot.command(name='rule')
async def rule(ctx, *, question: str):
    await ctx.defer()

    normas_servidor = cargar_normas()

    context = (
        "Eres un bot asistente del servidor de Minecraft StormCraft ambientado en Naruto. "
        "Tu tarea es responder preguntas y brindar explicaciones breves sobre las normas del servidor. "
        "Debes ayudar a los jugadores a resolver sus dudas o conflictos con las normas. "
        f"Aquí tienes las normas del servidor:\n{normas_servidor} "
    )
    
    model = "gemini-2.0-flash-exp"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
    
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

    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        answer = response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No pude generar una respuesta.")
        
        fragmentos = dividir_texto(answer)
        
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

def cargar_normas():
    try:
        with open("normas.txt", "r", encoding="utf-8") as file:
            return file.read() 
    except FileNotFoundError:
        print("Error: El archivo 'normas.txt' no se encontró.")
        return ""
    
# Evento cuando el bot está listo
@bot.event
async def on_ready():
    print(f'{bot.user} ha iniciado sesión en Discord.')

# Iniciar el bot
webserver.keep_alive()
bot.run(DISCORD_TOKEN)
