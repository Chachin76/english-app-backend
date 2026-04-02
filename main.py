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
    "ingles":    {"nombre": "inglés",    "en": "English",    "profesor": "an English teacher"},
    "frances":   {"nombre": "francés",   "en": "French",     "profesor": "a French teacher"},
    "portugues": {"nombre": "portugués", "en": "Portuguese", "profesor": "a Portuguese teacher"},
    "italiano":  {"nombre": "italiano",  "en": "Italian",    "profesor": "an Italian teacher"},
    "aleman":    {"nombre": "alemán",    "en": "German",     "profesor": "a German teacher"},
    "espanol":   {"nombre": "español",   "en": "Spanish",    "profesor": "a Spanish teacher"},
    "chino":     {"nombre": "chino",     "en": "Chinese (Mandarin)", "profesor": "a Mandarin Chinese teacher"},
    "japones":   {"nombre": "japonés",   "en": "Japanese",   "profesor": "a Japanese teacher"},
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
Para la estructura gramatical "{datos.estructura}" en {id['en']}, generá exactamente 3 ejemplos.

Respondé ÚNICAMENTE con este formato JSON, sin texto extra:
{{
  "significado": "explicación en español de cuándo y cómo se usa esta estructura",
  "ejemplos": [
    {{
      "ingles": "la oración en {id['en']}",
      "español": "la traducción al español argentino",
      "fonetica": "pronunciación simplificada en español",
      "explicacion": "explicación gramatical breve en español"
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
        f"Pregunta {i+1}: {r['pregunta']} → Respuesta del estudiante: {r['respuesta']}"
        for i, r in enumerate(datos.respuestas)
    ])
    respuesta = cliente.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""Sos un evaluador de {id['nombre']}. Analiza estas respuestas y determiná el nivel MCER.

{texto_respuestas}

Respondé ÚNICAMENTE con este JSON sin texto extra:
{{
  "nivel": "A1/A2/B1/B2/C1",
  "puntos_fuertes": ["punto 1", "punto 2"],
  "puntos_debiles": ["punto 1", "punto 2"],
  "descripcion": "descripción del nivel en español de 2 oraciones",
  "recomendacion": "qué debería practicar primero, en español"
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
            "content": f"""Sos un profesor de {id['nombre']}. Generá 10 palabras de vocabulario en {id['en']} para nivel {datos.nivel}.
NO incluyas estas palabras: {palabras_excluir}

Respondé ÚNICAMENTE con este JSON:
{{
  "palabras": [
    {{
      "ingles": "la palabra en {id['en']}",
      "español": "traducción al español argentino",
      "categoria": "sustantivo/verbo/adjetivo/adverbio",
      "ejemplo": "oración de ejemplo en {id['en']}",
      "ejemplo_español": "traducción del ejemplo",
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
3. If the student makes grammatical errors, add at the end: (Corrección: cómo debería decirse, en español)
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
            "content": f"""Analizá esta conversación de práctica de {id['nombre']} y dá un resumen del desempeño.

Situación: {datos.situacion}
Nivel: {datos.nivel}
Conversación:
{conversacion}

Respondé ÚNICAMENTE con este JSON:
{{
  "puntaje": 85,
  "resumen": "descripción breve en español",
  "errores_frecuentes": ["error 1", "error 2"],
  "frases_utiles": ["frase útil 1", "frase útil 2"],
  "consejo": "consejo principal en español"
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
            "content": f"""Generá {datos.cantidad} frases en {id['en']} para un ejercicio de dictado, nivel {datos.nivel}.

Respondé ÚNICAMENTE con este JSON:
{{
  "frases": [
    {{
      "texto": "la frase en {id['en']}",
      "traduccion": "traducción al español argentino"
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
Lo que escribió el estudiante: "{datos.escrito}"

Respondé ÚNICAMENTE con este JSON:
{{
  "puntaje": 85,
  "palabras": [
    {{
      "palabra": "cada palabra del original",
      "estado": "correcta/incorrecta/faltante",
      "escrita": "lo que escribió el estudiante"
    }}
  ],
  "errores": ["descripción de cada error en español"],
  "consejo": "consejo breve en español"
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
            "content": f"""Generá un texto en {id['en']} para lectura graduada, nivel {datos.nivel}, {tema_instruccion}.

Longitud: A1/A2=100 palabras, B1/B2=200 palabras, C1=300 palabras.
Luego generá 4 preguntas de comprensión con 4 opciones cada una.

Respondé ÚNICAMENTE con este JSON:
{{
  "titulo": "título del texto",
  "texto": "el texto completo en {id['en']}",
  "palabras_clave": ["palabra1", "palabra2", "palabra3", "palabra4", "palabra5"],
  "preguntas": [
    {{
      "pregunta": "la pregunta en {id['en']}",
      "opciones": ["opción A", "opción B", "opción C", "opción D"],
      "correcta": "opción A",
      "explicacion": "por qué es correcta, en español"
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
            "content": f"""Sos un profesor de {id['nombre']} y cultura. Generá 5 elementos de la categoría "{datos.categoria}" para nivel {datos.nivel}.

Respondé ÚNICAMENTE con este JSON:
{{
  "items": [
    {{
      "expresion": "la expresión en {id['en']}",
      "tipo": "modismo/phrasal verb/slang/diferencia cultural/referencia",
      "significado": "qué significa en español argentino",
      "origen": "de dónde viene, en español",
      "ejemplo_us": "ejemplo de uso en {id['en']}",
      "ejemplo_uk": "variante si aplica",
      "ejemplo_español": "traducción del ejemplo",
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
            "content": f"""Sos un profesor de {id['nombre']}. Generá 5 ejercicios de tipo "{datos.tipo}" para nivel {datos.nivel}.

Respondé ÚNICAMENTE con este JSON:
{{
  "tipo": "{datos.tipo}",
  "ejercicios": [
    {{
      "instruccion": "instrucción breve en español",
      "enunciado": "el ejercicio en {id['en']} con ___ donde va la respuesta",
      "respuesta": "la respuesta correcta",
      "explicacion": "por qué es correcta, en español",
      "pista": "una pista breve en español"
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
            "content": f"""Generá 7 frases célebres o proverbios en {id['en']} con su traducción al español argentino.

Respondé ÚNICAMENTE con este JSON:
{{
  "frases": [
    {{
      "idioma": "la frase en {id['en']}",
      "español": "traducción al español argentino"
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
            "content": f"""Generá 10 preguntas de opción múltiple para evaluar el nivel MCER de {id['en']} de un estudiante hispanohablante argentino.

2 preguntas nivel A1, 2 nivel A2, 2 nivel B1, 2 nivel B2, 2 nivel C1.

Respondé ÚNICAMENTE con este JSON:
{{
  "preguntas": [
    {{
      "id": 1,
      "nivel": "A1",
      "pregunta": "la pregunta en español sobre {id['en']}",
      "opciones": ["opción A", "opción B", "opción C", "opción D"],
      "correcta": "opción A"
    }}
  ]
}}"""
        }]
    )
    texto = respuesta.content[0].text.strip()
    if texto.startswith("```"):
        texto = texto.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(texto)