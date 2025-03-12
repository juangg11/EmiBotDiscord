import discord
import requests
import json
from discord.ext import commands
from discord import app_commands
import os
import webserver

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

GEMINI_API_KEY = "AIzaSyBnaO6WXeemBkFS5jpaaltCfflvCltZgAY"

intents = discord.Intents.default()
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
    
    async def setup_hook(self):
        await self.tree.sync()
        print("Comandos sincronizados.")

bot = MyBot() 

def cargar_informacion():
    try:
        with open("informacion.txt", "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print("Error: El archivo 'informacion.txt' no se encontró.")
        return ""

def dividir_texto(texto, limite=1000):
    fragmentos = []
    while len(texto) > limite:
        ultimo_espacio = texto.rfind(' ', 0, limite)
        if ultimo_espacio == -1:
            ultimo_espacio = limite
        fragmentos.append(texto[:ultimo_espacio])
        texto = texto[ultimo_espacio:].lstrip()
    fragmentos.append(texto)
    return fragmentos

@bot.tree.command(name="ask", description="Hazle una pregunta al bot Emi")
async def ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer()

    informacion_servidor = cargar_informacion()

    context = f"""
    Eres un asistente virtual gato macho llamado 'Emi'. Tu misión es responder preguntas y brindar explicaciones sobre el servidor de Minecraft **StormCraft**, 
    ambientado en el mundo de **Naruto**. 

     **Tu estilo**:
    - Hablas de manera **relajada, amigable y juguetona**. Como un gato curioso y sabio.  
    - Usas **emojis** 🐾 para hacer las respuestas más llamativas y expresivas.  
    - A veces puedes soltar un **"Miau g"** para referirte a los jugadores o añadir un toque felino en tu respuesta.  

     **Cómo responder**:
    - Responde de manera **concisa** pero **informativa**, mantén la respuesta directa y al punto.  
    - Si no tienes suficiente información sobre un tema, **sé honesto y di que no sabes**. No inventes respuestas.  
    - Si alguien pregunta algo que no tiene que ver con el servidor, responde con algo como **"Miau g, solo respondo cosas sobre StormCraft 😺"**.

     **Información sobre el servidor**:
    {informacion_servidor}

    📚 **Complementa tu respuesta con datos de la wiki de Naruto o videojuegos cuando sea relevante.**  
    """

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
        ],
        "generationConfig": {
            "maxOutputTokens": 300
        }
    }

    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        answer = response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No pude generar una respuesta.")

        fragmentos = dividir_texto(answer, 4096)

        for i, fragmento in enumerate(fragmentos):
            embed = discord.Embed(
                title=interaction.user.name + " pregunta: " + question if i == 0 else "Continuación...",
                description=fragmento,
                color=discord.Color.blue()
            )
            await interaction.followup.send(embed=embed)

    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            await interaction.followup.send("Error: No autorizado. Verifica tu clave de API.")
        elif response.status_code == 404:
            await interaction.followup.send("Error: Endpoint no encontrado. Revisa la URL o el modelo.")
        else:
            await interaction.followup.send(f"Hubo un error al procesar la pregunta: {e}")
    except Exception as e:
        await interaction.followup.send(f"Hubo un error al procesar la pregunta: {e}")

# Evento cuando el bot está listo
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'{bot.user} ha iniciado sesión en Discord y los comandos están sincronizados.')

# Iniciar el bot
webserver.keep_alive()
bot.run(DISCORD_TOKEN)
