
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from anthropic import Anthropic
from dotenv import load_dotenv
import os

load_dotenv()
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY", "")
cliente = Anthropic()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

IDIOMAS = {
    "ingles":    {"nombre": "inglÃ©s",    "en": "English",    "profesor": "an English teacher"},
    "frances":   {"nombre": "francÃ©s",   "en": "French",     "profesor": "a French teacher"},
    "portugues": {"nombre": "portuguÃ©s", "en": "Portuguese", "profesor": "a Portuguese teacher"},
    "italiano":  {"nombre": "italiano",  "en": "Italian",    "profesor": "an Italian teacher"},
    "aleman":    {"nombre": "alemÃ¡n",    "en": "German",     "profesor": "a German teacher"},
    "espanol":   {"nombre": "espaÃ±ol",   "en": "Spanish",    "profesor": "a Spanish teacher"},
    "chino":     {"nombre": "chino",     "en": "Chinese (Mandarin)", "profesor": "a Mandarin Chinese teacher"},
    "japones":   {"nombre": "japones",   "en": "Japanese",   "profesor": "a Japanese teacher"},
    "coreano":   {"nombre": "coreano",   "en": "Korean",     "profesor": "a Korean teacher"},
}

def get_idioma(idioma: str):
    return IDIOMAS.get(idioma, IDIOMAS["ingles"])

class MensajeCorrector(BaseModel):
    texto: str
    idioma: str = "ingles"

class MensajeChat(BaseModel):
    historial: list
    system: str = ""
    idioma: str = "ingles"

class MensajeGramatica(BaseModel):
    estructura: str
    idioma: str = "ingles"

class MensajeDiagnostico(BaseModel):
    respuestas: list
    idioma: str = "ingles"

class MensajeVocabulario(BaseModel):
    nivel: str
    palabras_vistas: list = []
    idioma: str = "ingles"

class MensajeSituacion(BaseModel):
    situacion: str
    historial: list
    nivel: str = "B1"
    idioma: str = "ingles"

class MensajeResumen(BaseModel):
    situacion: str
    historial: list
    nivel: str = "B1"
    idioma: str = "ingles"

class MensajeDictado(BaseModel):
    nivel: str = "B1"
    cantidad: int = 5
    idioma: str = "ingles"

class MensajeCorreccionDictado(BaseModel):
    original: str
    escrito: str
    idioma: str = "ingles"

class MensajeLectura(BaseModel):
    nivel: str = "B1"
    tema: str = ""
    idioma: str = "ingles"

class MensajeCultura(BaseModel):
    categoria: str = "expresiones"
    nivel: str = "B1"
    idioma: str = "ingles"

class MensajeEjercicios(BaseModel):
    tipo: str = "completar"
    nivel: str = "B1"
    idioma: str = "ingles"

@app.get("/")
def inicio():
    return {"mensaje": "Servidor Language Learning App funcionando"}

@app.post("/corregir")
def corregir(datos: MensajeCorrector):
    id = get_idioma(datos.idioma)
    respuesta = cliente.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""You are {id['profesor']} for Spanish speakers from Argentina.
Analyze this sentence written in {id['en']} and respond ONLY in Spanish.

Format:
NIVEL: [Correcto/Errores menores/Errores importantes]
ERRORES: [list of errors in Spanish]
CORRECCION: [corrected sentence in {id['en']}]
EXPLICACION: [explanation in Spanish]
CONSEJO: [short tip in Spanish]

Sentence: {datos.texto}"""
        }]
    )
    return {"respuesta": respuesta.content[0].text}

@app.post("/chat")
def chat(datos: MensajeChat):
    id = get_idioma(datos.idioma)
    respuesta = cliente.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=f"You are a friendly {id['en']} tutor. Respond in {id['en']}. Correct errors at the end in Spanish between parentheses. Be brief and encouraging.",
        messages=datos.historial
    )
    return {"respuesta": respuesta.content[0].text}

@app.post("/gramatica")
def gramatica(datos: MensajeGramatica):
    import json
    id = get_idioma(datos.idioma)
    respuesta = cliente.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"""Sos un profesor de {id['nombre']} para hispanohablantes argentinos.
Para la estructura gramatical "{datos.estructura}" en {id['en']}, generÃ¡ exactamente 3 ejemplos.

RespondÃ© ÃšNICAMENTE con este formato JSON, sin texto extra:
{{
  "significado": "explicaciÃ³n en espaÃ±ol de cuÃ¡ndo y cÃ³mo se usa esta estructura",
  "ejemplos": [
    {{
      "ingles": "la oraciÃ³n en {id['en']}",
      "espaÃ±ol": "la traducciÃ³n al espaÃ±ol argentino",
      "fonetica": "pronunciaciÃ³n simplificada en espaÃ±ol",
      "explicacion": "explicaciÃ³n gramatical breve en espaÃ±ol"
    }}
  ]
}}"""
        }]
    )
    texto = respuesta.content[0].text.strip()
    if texto.startswith("```"):
        texto = texto.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(texto)

@app.post("/diagnostico")
def diagnostico(datos: MensajeDiagnostico):
    import json
    id = get_idioma(datos.idioma)
    texto_respuestas = "\n".join([
        f"Pregunta {i+1}: {r['pregunta']} â†’ Respuesta del estudiante: {r['respuesta']}"
        for i, r in enumerate(datos.respuestas)
    ])
    respuesta = cliente.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""Sos un evaluador de {id['nombre']}. Analiza estas respuestas y determinÃ¡ el nivel MCER.

{texto_respuestas}

RespondÃ© ÃšNICAMENTE con este JSON sin texto extra:
{{
  "nivel": "A1/A2/B1/B2/C1",
  "puntos_fuertes": ["punto 1", "punto 2"],
  "puntos_debiles": ["punto 1", "punto 2"],
  "descripcion": "descripciÃ³n del nivel en espaÃ±ol de 2 oraciones",
  "recomendacion": "quÃ© deberÃ­a practicar primero, en espaÃ±ol"
}}"""
        }]
    )
    texto = respuesta.content[0].text.strip()
    if texto.startswith("```"):
        texto = texto.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(texto)

@app.post("/vocabulario")
def vocabulario(datos: MensajeVocabulario):
    import json
    id = get_idioma(datos.idioma)
    palabras_excluir = ", ".join(datos.palabras_vistas) if datos.palabras_vistas else "ninguna"
    respuesta = cliente.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"""Sos un profesor de {id['nombre']}. GenerÃ¡ 10 palabras de vocabulario en {id['en']} para nivel {datos.nivel}.
NO incluyas estas palabras: {palabras_excluir}

RespondÃ© ÃšNICAMENTE con este JSON:
{{
  "palabras": [
    {{
      "ingles": "la palabra en {id['en']}",
      "espaÃ±ol": "traducciÃ³n al espaÃ±ol argentino",
      "categoria": "sustantivo/verbo/adjetivo/adverbio",
      "ejemplo": "oraciÃ³n de ejemplo en {id['en']}",
      "ejemplo_espaÃ±ol": "traducciÃ³n del ejemplo",
      "nivel": "{datos.nivel}"
    }}
  ]
}}"""
        }]
    )
    texto = respuesta.content[0].text.strip()
    if texto.startswith("```"):
        texto = texto.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(texto)

@app.post("/situacion")
def situacion(datos: MensajeSituacion):
    id = get_idioma(datos.idioma)
    respuesta = cliente.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=f"""You are an actor playing real-life situations so a {id['en']} student at level {datos.nivel} can practice conversation.

Current situation: {datos.situacion}

Rules:
1. Always respond in {id['en']}
2. Use vocabulary appropriate for level {datos.nivel}
3. If the student makes grammatical errors, add at the end: (CorrecciÃ³n: cÃ³mo deberÃ­a decirse, en espaÃ±ol)
4. Keep the scene realistic
5. Ask questions to move the conversation forward
6. Short messages, maximum 3 sentences""",
        messages=datos.historial
    )
    return {"respuesta": respuesta.content[0].text}

@app.post("/resumen-situacion")
def resumen_situacion(datos: MensajeResumen):
    import json
    id = get_idioma(datos.idioma)
    conversacion = "\n".join([
        f"{'Estudiante' if m['role'] == 'user' else 'Tutor'}: {m['content']}"
        for m in datos.historial
    ])
    respuesta = cliente.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""AnalizÃ¡ esta conversaciÃ³n de prÃ¡ctica de {id['nombre']} y dÃ¡ un resumen del desempeÃ±o.

SituaciÃ³n: {datos.situacion}
Nivel: {datos.nivel}
ConversaciÃ³n:
{conversacion}

RespondÃ© ÃšNICAMENTE con este JSON:
{{
  "puntaje": 85,
  "resumen": "descripciÃ³n breve en espaÃ±ol",
  "errores_frecuentes": ["error 1", "error 2"],
  "frases_utiles": ["frase Ãºtil 1", "frase Ãºtil 2"],
  "consejo": "consejo principal en espaÃ±ol"
}}"""
        }]
    )
    texto = respuesta.content[0].text.strip()
    if texto.startswith("```"):
        texto = texto.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(texto)

@app.post("/dictado/frases")
def dictado_frases(datos: MensajeDictado):
    import json
    id = get_idioma(datos.idioma)
    respuesta = cliente.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""GenerÃ¡ {datos.cantidad} frases en {id['en']} para un ejercicio de dictado, nivel {datos.nivel}.

RespondÃ© ÃšNICAMENTE con este JSON:
{{
  "frases": [
    {{
      "texto": "la frase en {id['en']}",
      "traduccion": "traducciÃ³n al espaÃ±ol argentino"
    }}
  ]
}}"""
        }]
    )
    texto = respuesta.content[0].text.strip()
    if texto.startswith("```"):
        texto = texto.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(texto)

@app.post("/dictado/corregir")
def corregir_dictado(datos: MensajeCorreccionDictado):
    import json
    id = get_idioma(datos.idioma)
    respuesta = cliente.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""Comparar estas dos frases en {id['en']} y analizar los errores del dictado.

Frase original: "{datos.original}"
Lo que escribiÃ³ el estudiante: "{datos.escrito}"

RespondÃ© ÃšNICAMENTE con este JSON:
{{
  "puntaje": 85,
  "palabras": [
    {{
      "palabra": "cada palabra del original",
      "estado": "correcta/incorrecta/faltante",
      "escrita": "lo que escribiÃ³ el estudiante"
    }}
  ],
  "errores": ["descripciÃ³n de cada error en espaÃ±ol"],
  "consejo": "consejo breve en espaÃ±ol"
}}"""
        }]
    )
    texto = respuesta.content[0].text.strip()
    if texto.startswith("```"):
        texto = texto.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(texto)

@app.post("/lectura/generar")
def generar_lectura(datos: MensajeLectura):
    import json
    id = get_idioma(datos.idioma)
    tema_instruccion = f"sobre el tema: {datos.tema}" if datos.tema else "sobre un tema interesante y variado"
    respuesta = cliente.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"""GenerÃ¡ un texto en {id['en']} para lectura graduada, nivel {datos.nivel}, {tema_instruccion}.

Longitud: A1/A2=100 palabras, B1/B2=200 palabras, C1=300 palabras.
Luego generÃ¡ 4 preguntas de comprensiÃ³n con 4 opciones cada una.

RespondÃ© ÃšNICAMENTE con este JSON:
{{
  "titulo": "tÃ­tulo del texto",
  "texto": "el texto completo en {id['en']}",
  "palabras_clave": ["palabra1", "palabra2", "palabra3", "palabra4", "palabra5"],
  "preguntas": [
    {{
      "pregunta": "la pregunta en {id['en']}",
      "opciones": ["opciÃ³n A", "opciÃ³n B", "opciÃ³n C", "opciÃ³n D"],
      "correcta": "opciÃ³n A",
      "explicacion": "por quÃ© es correcta, en espaÃ±ol"
    }}
  ]
}}"""
        }]
    )
    texto = respuesta.content[0].text.strip()
    if texto.startswith("```"):
        texto = texto.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(texto)

@app.post("/cultura")
def cultura(datos: MensajeCultura):
    import json
    id = get_idioma(datos.idioma)
    respuesta = cliente.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"""Sos un profesor de {id['nombre']} y cultura. GenerÃ¡ 5 elementos de la categorÃ­a "{datos.categoria}" para nivel {datos.nivel}.

RespondÃ© ÃšNICAMENTE con este JSON:
{{
  "items": [
    {{
      "expresion": "la expresiÃ³n en {id['en']}",
      "tipo": "modismo/phrasal verb/slang/diferencia cultural/referencia",
      "significado": "quÃ© significa en espaÃ±ol argentino",
      "origen": "de dÃ³nde viene, en espaÃ±ol",
      "ejemplo_us": "ejemplo de uso en {id['en']}",
      "ejemplo_uk": "variante si aplica",
      "ejemplo_espaÃ±ol": "traducciÃ³n del ejemplo",
      "nivel_dificultad": "facil/medio/dificil"
    }}
  ]
}}"""
        }]
    )
    texto = respuesta.content[0].text.strip()
    if texto.startswith("```"):
        texto = texto.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(texto)

@app.post("/ejercicios")
def ejercicios(datos: MensajeEjercicios):
    import json
    id = get_idioma(datos.idioma)
    respuesta = cliente.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"""Sos un profesor de {id['nombre']}. GenerÃ¡ 5 ejercicios de tipo "{datos.tipo}" para nivel {datos.nivel}.

RespondÃ© ÃšNICAMENTE con este JSON:
{{
  "tipo": "{datos.tipo}",
  "ejercicios": [
    {{
      "instruccion": "instrucciÃ³n breve en espaÃ±ol",
      "enunciado": "el ejercicio en {id['en']} con ___ donde va la respuesta",
      "respuesta": "la respuesta correcta",
      "explicacion": "por quÃ© es correcta, en espaÃ±ol",
      "pista": "una pista breve en espaÃ±ol"
    }}
  ]
}}"""
        }]
    )
    texto = respuesta.content[0].text.strip()
    if texto.startswith("```"):
        texto = texto.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(texto)
class MensajeFrases(BaseModel):
    idioma: str = "ingles"

@app.post("/frases")
def frases(datos: MensajeFrases):
    import json
    id = get_idioma(datos.idioma)
    respuesta = cliente.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""GenerÃ¡ 7 frases cÃ©lebres o proverbios en {id['en']} con su traducciÃ³n al espaÃ±ol argentino.

RespondÃ© ÃšNICAMENTE con este JSON:
{{
  "frases": [
    {{
      "idioma": "la frase en {id['en']}",
      "espaÃ±ol": "traducciÃ³n al espaÃ±ol argentino"
    }}
  ]
}}"""
        }]
    )
    texto = respuesta.content[0].text.strip()
    if texto.startswith("```"):
        texto = texto.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(texto)
class MensajePreguntasDiagnostico(BaseModel):
    idioma: str = "ingles"

@app.post("/diagnostico/preguntas")
def preguntas_diagnostico(datos: MensajePreguntasDiagnostico):
    import json
    id = get_idioma(datos.idioma)
    respuesta = cliente.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"""GenerÃ¡ 10 preguntas de opciÃ³n mÃºltiple para evaluar el nivel MCER de {id['en']} de un estudiante hispanohablante argentino.

2 preguntas nivel A1, 2 nivel A2, 2 nivel B1, 2 nivel B2, 2 nivel C1.

RespondÃ© ÃšNICAMENTE con este JSON:
{{
  "preguntas": [
    {{
      "id": 1,
      "nivel": "A1",
      "pregunta": "la pregunta en espaÃ±ol sobre {id['en']}",
      "opciones": ["opciÃ³n A", "opciÃ³n B", "opciÃ³n C", "opciÃ³n D"],
      "correcta": "opciÃ³n A"
    }}
  ]
}}"""
        }]
    )
    texto = respuesta.content[0].text.strip()
    if texto.startswith("```"):
        texto = texto.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(texto)
class MensajeLeccion(BaseModel):
    idioma: str = "ingles"
    nivel: str = "A1"
    leccion_numero: int = 1

@app.post("/leccion")
def generar_leccion(datos: MensajeLeccion):
    import json
    id = get_idioma(datos.idioma)
    TEMAS_A1 = ["Saludos y presentaciones","Numeros del 1 al 20","Colores basicos","Dias de la semana","Meses del anio","La familia","Partes del cuerpo","Comidas y bebidas","Objetos del hogar","Ropa basica","Animales comunes","Medios de transporte","El clima","Profesiones basicas","Lugares de la ciudad","Los numeros 20 al 100","Preguntas basicas","Verbos de accion basicos","Adjetivos basicos","Mi rutina diaria"]
    TEMAS_A2 = ["Rutinas diarias","Compras en el mercado","Pedir comida","Hablar del pasado","Planes futuros","Describir personas","Describir lugares","Dar direcciones","Tiempo libre","La salud","Viajes y vacaciones","El trabajo","Las emociones","La casa","Hacer comparaciones","El dinero","La tecnologia basica","Deportes","La naturaleza","Las fiestas y celebraciones"]
    TEMAS_B1 = ["Expresar opiniones","Experiencias pasadas","Hacer hipotesis","Describir procesos","Habitos pasados","Acuerdo y desacuerdo","Dar consejos","Planes y predicciones","Contar historias","Causa y efecto","Cultura y tradiciones","Medios de comunicacion","El medio ambiente","Tecnologia","Relaciones personales","Politica basica","Arte y musica","Ciencia basica","Educacion","El mundo laboral"]

    TEMAS_CHINO_A1 = ["Introduccion a los caracteres chinos Hanzi","El sistema Pinyin romanizacion","Los trazos basicos del chino","Radicales mas comunes","Numeros en chino y caracteres","Saludos y caracteres basicos","Colores en chino con caracteres","La familia en chino con caracteres","Comidas tipicas chinas con caracteres","Lugares en chino con caracteres","Verbos basicos en chino con caracteres","Adjetivos basicos en chino","Los tonos del chino mandarin","Frases de supervivencia en chino","Escritura de mi nombre en chino","Numeros del 1 al 100 en chino","Preguntas basicas en chino","El tiempo en chino","Transporte en chino","Mi rutina en chino"]
    TEMAS_JAPONES_A1 = ["Introduccion al Hiragana parte 1 vocales","Introduccion al Hiragana parte 2 consonantes","Introduccion al Katakana parte 1","Introduccion al Katakana parte 2","Kanji basicos mas usados","Saludos en japones con escritura","Numeros en japones con escritura","La familia en japones con escritura","Colores en japones con escritura","Comidas japonesas con escritura","Verbos basicos en japones","Particulas basicas wa ga wo","Frases de supervivencia en japones","Escritura de mi nombre en Katakana","Los contadores en japones","Preguntas basicas en japones","El tiempo en japones","Transporte en japones","Mi rutina en japones","Cultura japonesa basica"]
    TEMAS_COREANO_A1 = ["Introduccion al Hangul vocales basicas","Introduccion al Hangul consonantes basicas","Combinaciones de Hangul silabas","Escritura del Hangul practica","Saludos en coreano con Hangul","Numeros en coreano con Hangul","La familia en coreano con Hangul","Colores en coreano con Hangul","Comidas coreanas con Hangul","Verbos basicos en coreano","Adjetivos basicos en coreano","Frases de supervivencia en coreano","Escritura de mi nombre en Hangul","Particulas basicas del coreano","Preguntas basicas en coreano","El tiempo en coreano","Transporte en coreano","Mi rutina en coreano","Cultura coreana basica","K-pop y cultura popular coreana"]

    if datos.idioma == "chino":
        temas_nivel = TEMAS_CHINO_A1 if datos.nivel == "A1" else TEMAS_A1
    elif datos.idioma == "japones":
        temas_nivel = TEMAS_JAPONES_A1 if datos.nivel == "A1" else TEMAS_A1
    elif datos.idioma == "coreano":
        temas_nivel = TEMAS_COREANO_A1 if datos.nivel == "A1" else TEMAS_A1
    else:
        TEMAS = {"A1": TEMAS_A1, "A2": TEMAS_A2, "B1": TEMAS_B1}
        temas_nivel = TEMAS.get(datos.nivel, TEMAS_A1)
    tema = temas_nivel[min(datos.leccion_numero - 1, len(temas_nivel) - 1)]
    TEMAS = {"A1": TEMAS_A1, "A2": TEMAS_A2, "B1": TEMAS_B1}
    temas_nivel = TEMAS.get(datos.nivel, TEMAS_A1)
    tema = temas_nivel[min(datos.leccion_numero - 1, len(temas_nivel) - 1)]
    respuesta = cliente.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"""Sos un profesor de {id['nombre']} para hispanohablantes argentinos.
Genera una leccion completa sobre "{tema}" para nivel {datos.nivel}.
Responde UNICAMENTE con este JSON:
{{
  "tema": "{tema}",
  "nivel": "{datos.nivel}",
  "leccion": {datos.leccion_numero},
  "explicacion": "explicacion clara del tema en espanol, 3-4 parrafos",
  "vocabulario": [
    {{"palabra": "palabra en {id['en']}", "traduccion": "traduccion al espanol", "ejemplo": "ejemplo en {id['en']}", "ejemplo_traduccion": "traduccion del ejemplo"}}
  ],
  "ejercicios": [
    {{"tipo": "elegir", "consigna": "consigna en espanol", "pregunta": "la pregunta", "opciones": ["A", "B", "C", "D"], "respuesta": "correcta", "explicacion": "por que es correcta"}}
  ],
  "frase_del_dia": "frase motivadora en {id['en']}",
  "frase_traduccion": "traduccion de la frase"
}}
El vocabulario debe tener exactamente 5 palabras.
Los ejercicios deben ser exactamente 3."""
        }]
    )
    texto = respuesta.content[0].text.strip()
    if texto.startswith("```"):
        texto = texto.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(texto)
