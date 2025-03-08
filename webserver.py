from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "¡El bot está en línea!"  # Mensaje que se mostrará cuando accedas a la URL

def run():
    app.run(host='0.0.0.0', port=8080)  # Inicia el servidor en el puerto 8080

def keep_alive():
    t = Thread(target=run)  # Crea un hilo para ejecutar el servidor
    t.start()