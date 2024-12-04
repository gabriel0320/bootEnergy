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
numeroPreguntas = 11
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
        "respuestas": ["¿En qué franja horaria sueles consumir más electricidad? Responda el numero: 1 (Mañana), 2 (Tarde), 3 (Noche)"]
    },
    
    "pregunta7": {
        "palabras_claves": ["apagaDispositivos"],
        "respuestas": ["¿Apaga completamente los dispositivos electrónicos (como TV, computadoras, etc.) o los deja en modo standby cuando no los usa?"]
    },
    
    "pregunta8": {
        "palabras_claves": ["cocimientoClasificacion"],
        "respuestas": ["¿Conoces la clasificación de eficiencia energética para los electrodomésticos?"]
    },
    
    "pregunta9": {
        "palabras_claves": ["personasEnCasa"],
        "respuestas": ["¿cuantas personas viven en casa?"]
    },
    
    "pregunta10": {
        "palabras_claves": ["teletrabajo"],
        "respuestas": ["¿haces teletrabajo?"]
    }
}
def clasificar_consumo_energia(bombillos, ahorradores, dispositivos_alto_consumo, franja_horaria, apaga_dispositivos, conoce_clasificacion, personas, teletrabajo):
    # Puntuaciones iniciales
    puntuacion = 0

    # Bombillos
    if int(bombillos) > 10:
        puntuacion += 3
    elif 5 <= bombillos <= 10:
        puntuacion += 2
    else:
        puntuacion += 1
    
    # Bombillos ahorradores
    if ahorradores.lower() == 'si':
        puntuacion -= 2
    else:
        puntuacion += 2
    
    # Dispositivos de alto consumo
    puntuacion += int(dispositivos_alto_consumo) * 3

    # Franja horaria
    if int(franja_horaria) == 3:
        puntuacion += 3
    elif int(franja_horaria) == 2:
        puntuacion += 2
    else:
        puntuacion += 1
    
    # Apagar dispositivos completamente
    if apaga_dispositivos.lower() == 'si':
        puntuacion -= 2
    else:
        puntuacion += 2
    
    # Conocimiento de clasificación de eficiencia energética
    if conoce_clasificacion.lower() == 'si':
        puntuacion -= 1
    else:
        puntuacion += 1
    
    # Número de personas en casa
    if int(personas) > 4:
        puntuacion += 3
    elif 2 <= int(personas) <= 4:
        puntuacion += 2
    else:
        puntuacion += 1
    
    # Teletrabajo
    if teletrabajo.lower() == 'si':
        puntuacion += 3
    else:
        puntuacion += 1
    
    # Clasificación final
    if puntuacion >= 15:
        return "Alto"
    elif 8 <= puntuacion < 15:
        return "Normal"
    else:
        return "Bajo"

# Ejemplo de uso
# perfil_consumo = clasificar_consumo_energia(8, 'si', 2, 3, 'no', 'si', 4, 'si')
# print(f"El perfil de consumo de energía es: {perfil_consumo}")

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
        df_existente = pd.read_csv(archivo_csv)
    except FileNotFoundError:
        df_existente = pd.DataFrame()

    df_nuevas = pd.DataFrame([respuestas])
    df_combinado = pd.concat([df_existente, df_nuevas], ignore_index=True)
    df_combinado.to_csv(archivo_csv, index=False)

def generar_Recomendaciones(vectorRespuestas):
    clasificacion =clasificar_consumo_energia(vectorRespuestas[3], vectorRespuestas[4], vectorRespuestas[5],
                                vectorRespuestas[6], vectorRespuestas[7], vectorRespuestas[8], 
                                vectorRespuestas[9], vectorRespuestas[10])
    recomendar = "Hola,"+vectorRespuestas[1]+ " Aqui tienes las recomendaciones: \n"
    recomendar = recomendar + "El perfil de consumo de energía es: " + clasificacion + "\n"
    recomendar = recomendar + "la clasificación de eficiencia energética para los electrodomésticos! Esta clasificación se utiliza para medir y comunicar cuán eficientes son los electrodomésticos en términos de consumo de energía. La clasificación se presenta generalmente en una etiqueta que se pega al electrodoméstico y varía según la región, pero una de las más conocidas es la clasificación de la Unión Europea, que va desde la letra A+++ (más eficiente) hasta la G (menos eficiente).\n"
    recomendar = recomendar + "Gracias por completar la encuesta. No te vayas, podemos seguir halando"
    return recomendar

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
            return generar_Recomendaciones(vectorRespuestas)
        
    if categoria == "desconocido":
        return "Lo siento, no entendí tu pregunta. Por favor, sea más específico."
    
    return random.choice(categorias[categoria]["respuestas"])

# Modelo para entrada de datos
class FraseEntrada(BaseModel):
    frase: str
# USO DE CHATBOOT EN CONSOLA
if __name__ == "__main__":
    print("Chatbot iniciado. Escriba 'salir' para terminar la conversación.")
    while True:
        usuario_input = input("Tú: ")
        
        if usuario_input.lower() == "salir":
            print("Chatbot: ¡Hasta luego!")
            df = pd.DataFrame([vectorRespuestas])
            df.to_csv("respuestas_encuesta.csv", index=False)
            break
        respuesta = chatbot(usuario_input,contadorPreguntas)
        print(f"Chatbot: {respuesta}")
        contadorPreguntas += 1

