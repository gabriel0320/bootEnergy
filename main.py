from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.requests import Request
import random
import pandas as pd

app = FastAPI()
# Servir archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")
vectorRespuestas = []
respuestasEncuesta = {}
contadorPreguntas = 1
# Diccionario de categorías con palabras clave y respuestas
categorias = {
    "saludo": {
        "palabras_claves": ["hola", "buenos dias", "buenas tardes", "buenas noches", "que tal", "como estas", "saludos"],
        "respuestas": ["Hola, ¿qué tal?", "Buenos días, un gusto saludarte", "Buenas tardes, un gusto saludarte", "Buenas noches, que descanses"]
    },
    "despedida": {
        "palabras_claves": ["adios", "chao", "hasta luego", "nos vemos", "bye", "gracias","suerte"],
        "respuestas": ["Gracias por su visita", "Un gusto atenderlo", "Que tenga un buen día", "Nos vemos pronto"]
    },
    "encuesta": {
        "palabras_claves": ["encuesta"],
        "respuestas": ["Bienvenido a la encuesta, por favor responda las siguientes preguntas:"]
    },
    "pregunta1": {
        "palabras_claves": ["nombre"],
        "respuestas": ["Ingrese por favor su nombre completo: "]
    },
    "pregunta2": {
        "palabras_claves": ["email"],
        "respuestas": ["Ingrese su correo electrónico: "]
    },
    "pregunta3": {
        "palabras_claves": ["bombillos"],
        "respuestas": ["¿Cuántas bombillos tiene en su casa?"]
    },
	"pregunta4": {
        "palabras_claves": ["ahorradores"],
        "respuestas": ["¿Son ahorradores, Si/No?"]
    },
    
    "pregunta5": {
        "palabras_claves": ["dispositivosAltoConsumo"],
        "respuestas": ["¿Cuántos dispositivos electrónicos o electrodomésticos de alto consumo (aire acondicionado, calefacción, horno eléctrico) usa con regularidad?"]
    },
    
    "pregunta6": {
        "palabras_claves": ["Franja"],
        "respuestas": ["¿En qué franja horaria sueles consumir más electricidad? (mañana, tarde, noche)"]
    },
    
    "pregunta7": {
        "palabras_claves": ["apagaDispositivos"],
        "respuestas": ["¿Apaga completamente los dispositivos electrónicos (como TV, computadoras, etc.) o los deja en modo standby cuando no los usa?"]
    },
    
    "pregunta8": {
        "palabras_claves": ["cocimientoClasificacion"],
        "respuestas": ["¿Conoces la clasificación de eficiencia energética para los electrodomésticos?"]
    }
}

# Clasificador de categorías
def clasificar_categoria(frase):
    frase = frase.lower()
    for categoria, data in categorias.items():
        if any(palabra_clave in frase for palabra_clave in data["palabras_claves"]):
            return categoria
    return "desconocido"

def almacenar_respuestas(frase):
    vectorRespuestas.append(frase)

def almacenar_respuestas_csv(respuestas, archivo_csv):
    try:
        # Leer las respuestas existentes en el archivo CSV
        df_existente = pd.read_csv(archivo_csv)
    except FileNotFoundError:
        # Si el archivo no existe, crear un DataFrame vacío
        df_existente = pd.DataFrame()

    # Crear un DataFrame con las nuevas respuestas
    df_nuevas = pd.DataFrame([respuestas])

    # Concatenar las respuestas nuevas con las existentes
    df_combinado = pd.concat([df_existente, df_nuevas], ignore_index=True)

    # Guardar el DataFrame combinado en el archivo CSV
    df_combinado.to_csv(archivo_csv, index=False)

numeroPreguntas = 9
# Chatbot
def chatbot(frase_usuario,contadorPreguntas):
    archivo_csv = "respuestas_encuesta.csv"
    if (contadorPreguntas > numeroPreguntas):
     categoria = clasificar_categoria(frase_usuario)
    else:
     categoria = "encuesta"
     almacenar_respuestas(frase_usuario)

    if (categoria.startswith("pregunta") or categoria == "encuesta") and contadorPreguntas <= numeroPreguntas and contadorPreguntas > 0:
        respuestasEncuesta[categoria] = frase_usuario
        
        proxima_pregunta = f"pregunta{contadorPreguntas}"
        if proxima_pregunta in categorias:
            return random.choice(categorias[proxima_pregunta]["respuestas"])
        else:
            almacenar_respuestas_csv(vectorRespuestas, archivo_csv)
            return "Gracias por completar la encuesta."
        
    if categoria == "desconocido":
        return "Lo siento, no entendí tu pregunta. Por favor, sea más específico."
    
    return random.choice(categorias[categoria]["respuestas"])

# Modelo para entrada de datos
class FraseEntrada(BaseModel):
    frase: str
# USO DE CHATBOOT EN CONSOLA
#if __name__ == "__main__":
#    print("Chatbot iniciado. Escriba 'salir' para terminar la conversación.")
#    while True:
#        usuario_input = input("Tú: ")
#        
#        if usuario_input.lower() == "salir":
#            print("Chatbot: ¡Hasta luego!")
##            df = pd.DataFrame([vectorRespuestas])
#            df.to_csv("respuestas_encuesta.csv", index=False)
#            break
#        respuesta = chatbot(usuario_input,contadorPreguntas)
#        print(f"Chatbot: {respuesta}")
#        contadorPreguntas += 1

# Endpoint del chatbot
#@app.post("/chatbot/")
#def obtener_respuesta(entrada: FraseEntrada):
#    respuesta = chatbot(entrada.frase)
#    return {"respuesta": respuesta}
@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    with open("static/index.html") as f:
        return HTMLResponse(f.read())

@app.post("/chatbot/")
async def obtener_respuesta(entrada: FraseEntrada, request: Request): 
    global contadorPreguntas
    respuesta = chatbot(entrada.frase, contadorPreguntas)
    contadorPreguntas += 1
    return {"respuesta": respuesta}