import random
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

def imagen_alazar():
    imagenes = [
        "https://lurei.wordpress.com/wp-content/uploads/2010/09/shark-attack.png",
        "https://i.redd.it/fun-fact-deidara-is-the-only-character-to-fight-all-4-v0-t31q1yzcmzeb1.jpg?width=969&format=pjpg&auto=webp&s=c8c10ec75755ceb51609036fac77bcc37f5c19be",
        "https://static0.gamerantimages.com/wordpress/wp-content/uploads/2023/07/minato-rasengan-training-minato-one-shot-naruto.jpg",
        "https://i.pinimg.com/736x/7a/68/24/7a68244dd5ce3a530286528c4b63251f.jpg",
        "https://play-reactor.com/wp-content/uploads/2012/01/modo-bijuu.jpg",
        "https://dailyanimeart.com/wp-content/uploads/2013/04/madara-and-hashirama-go-at-it.jpg?w=1112",
        "https://i.redd.it/bruh-did-kakuzu-really-fought-hashirama-v0-5e1vmhxckhuc1.jpg?width=640&format=pjpg&auto=webp&s=d31d2b9c856b18fb2fa2c816149fabc421667cd1",
        "https://preview.redd.it/ceb0x6ugul131.jpg?auto=webp&s=1fea2680ed5fb4682de1972dcf08cc04e9192dad",
        "https://wallpapers.com/images/high/naruto-manga-pictures-16crc9y08xfpf1fz.webp",
        "https://preview.redd.it/in-your-opinion-what-is-the-best-naruto-manga-panel-v0-j3vd0uhf9vic1.jpeg?auto=webp&s=c440ae6c179746d666eab7cbf2dd449650194570",
        "https://dailyanimeart.com/wp-content/uploads/2014/04/naruto-and-sasuke-vs-madara-header1.png?w=730",
        "https://e0.pxfuel.com/wallpapers/702/164/desktop-wallpaper-high-resolution-naruto-manga-alecto-connachan-manga-panel.jpg",
        "https://pbs.twimg.com/media/EuSUk2mXMA8Z-yU.jpg",
        "https://i.pinimg.com/550x/30/94/b5/3094b5c3ce16be45a8ccf29c015550ec.jpg",
        "https://i.pinimg.com/originals/65/a0/53/65a0533ef50665cfb37747707a904bfd.png",
        "https://static1.cbrimages.com/wordpress/wp-content/uploads/2023/05/naruto-and-gaara-are-mirror-images-of-each-other.jpg",
        "https://64.media.tumblr.com/018fd453d6ab90f4d4f384e4f1ba49dc/tumblr_p5asvkGozg1wn6oeco1_1280.jpg",
        "https://s1.zerochan.net/NARUTO.600.1291562.jpg",
        "https://pbs.twimg.com/media/GeVkdifbEAAgD4z.png:large",
        "https://pbs.twimg.com/media/EMUkDKVVUAAvaUI.jpg",
        "https://static.zerochan.net/Orochimaru.full.4054191.jpg",
        "https://i.pinimg.com/736x/81/85/5e/81855eb921b82e0221cc099cceafe1e9.jpg",
        "https://iareawesomeness.wordpress.com/wp-content/uploads/2009/02/jiraiyaminatonaruto.jpg?w=584",
        "https://comicvine.gamespot.com/a/uploads/original/11130/111307227/7581777-3047237936-wcWoP.jpg",
        "https://pbs.twimg.com/media/FugML0GXgAEW1-5.png",
        "https://preview.redd.it/vmhz1zi4ebn41.jpg?auto=webp&s=178ac04f93caaeca10a52040233fdcfa3e57cee1"
    ]

    return random.choice(imagenes)

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
        ultimo_punto = texto.rfind('.', 0, limite)
        ultimo_salto = texto.rfind('\n', 0, limite)

        if ultimo_punto == -1 and ultimo_salto == -1:
            ultimo_punto = texto.rfind(' ', 0, limite)
        else:
            ultimo_punto = max(ultimo_punto, ultimo_salto)

        if ultimo_punto == -1:
            ultimo_punto = limite

        fragmentos.append(texto[:ultimo_punto + 1].strip())
        texto = texto[ultimo_punto + 1:].lstrip()

    fragmentos.append(texto.strip()) 
    return fragmentos

@bot.tree.command(name="ask", description="Hazle una pregunta al bot Emi")
async def ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer()

    informacion_servidor = cargar_informacion()
    
    context = f"""
    Eres un asistente virtual gato macho llamado 'Emi' 🐱. Tu misión es responder preguntas y brindar explicaciones sobre el servidor de Minecraft **StormCraft**, 
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

     **Complementa tu respuesta con datos de la wiki de Naruto o videojuegos cuando sea relevante.**  
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

        url = imagen_alazar()

        for fragmento in fragmentos:
            embed = discord.Embed(
            title=interaction.user.name + " pregunta: " + question,
            description=fragmento,
            color=discord.Color.blue()
            )
            embed.set_image(url=url)
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