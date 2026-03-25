from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from anthropic import Anthropic
from dotenv import load_dotenv
import os

load_dotenv()
os.environ ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY", "")
cliente = Anthropic()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class MensajeCorrector(BaseModel):
    texto: str

class MensajeChat(BaseModel):
    historial: list
    system: str = ""

@app.get("/")
def inicio():
    return {"mensaje": "Servidor English App funcionando"}

@app.post("/corregir")
def corregir(datos: MensajeCorrector):
    respuesta = cliente.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": "INSTRUCCION: Responde UNICAMENTE en español. Sos un profesor de ingles. Analiza esta oracion: NIVEL: [Correcto/Errores menores/Errores importantes] ERRORES: [lista] CORRECCION: [corregida] EXPLICACION: [en español] CONSEJO: [corto]. Oracion: " + datos.texto
        }]
    )
    return {"respuesta": respuesta.content[0].text}

@app.post("/chat")
def chat(datos: MensajeChat):
    respuesta = cliente.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system="Sos un tutor de ingles amigable. Responde en ingles. Corrige errores al final en español entre parentesis. Se breve y alentador.",
        messages=datos.historial
    )
    return {"respuesta": respuesta.content[0].text}
class MensajeGramatica(BaseModel):
    estructura: str

@app.post("/gramatica")
def gramatica(datos: MensajeGramatica):
    respuesta = cliente.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"""Sos un profesor de inglés para hispanohablantes argentinos.
Para la estructura gramatical "{datos.estructura}" generá exactamente 3 ejemplos.

Respondé ÚNICAMENTE con este formato JSON, sin texto extra:
{{
  "significado": "explicación en español de cuándo y cómo se usa esta estructura",
  "ejemplos": [
    {{
      "ingles": "la oración en inglés",
      "español": "la traducción al español argentino",
      "fonetica": "pronunciación simplificada en español, por ejemplo: du yu hæv...",
      "explicacion": "explicación gramatical breve en español"
    }}
  ]
}}"""
        }]
    )
    import json
    texto = respuesta.content[0].text
    texto_limpio = texto.strip()
    if texto_limpio.startswith("```"):
        texto_limpio = texto_limpio.split("\n", 1)[1]
        texto_limpio = texto_limpio.rsplit("```", 1)[0]
    return json.loads(texto_limpio)
class MensajeDiagnostico(BaseModel):
    respuestas: list

class MensajeNivel(BaseModel):
    nivel: str
    tema: str = ""

@app.post("/diagnostico")
def diagnostico(datos: MensajeDiagnostico):
    import json
    texto_respuestas = "\n".join([
        f"Pregunta {i+1}: {r['pregunta']} → Respuesta del estudiante: {r['respuesta']}"
        for i, r in enumerate(datos.respuestas)
    ])
    respuesta = cliente.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""Sos un evaluador de ingles. Analiza estas respuestas y determina el nivel MCER del estudiante.

{texto_respuestas}

Responde UNICAMENTE con este JSON sin texto extra:
{{
  "nivel": "A1/A2/B1/B2/C1",
  "puntos_fuertes": ["punto 1", "punto 2"],
  "puntos_debiles": ["punto 1", "punto 2"],
  "descripcion": "descripcion del nivel en espanol de 2 oraciones",
  "recomendacion": "que deberia practicar primero, en espanol"
}}"""
        }]
    )
    texto = respuesta.content[0].text.strip()
    if texto.startswith("```"):
        texto = texto.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(texto)
class MensajeVocabulario(BaseModel):
    nivel: str
    palabras_vistas: list = []

@app.post("/vocabulario")
def vocabulario(datos: MensajeVocabulario):
    import json
    palabras_excluir = ", ".join(datos.palabras_vistas) if datos.palabras_vistas else "ninguna"
    respuesta = cliente.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"""Sos un profesor de ingles. Genera 10 palabras de vocabulario para nivel {datos.nivel}.
NO incluyas estas palabras que el estudiante ya vio: {palabras_excluir}

Responde UNICAMENTE con este JSON sin texto extra:
{{
  "palabras": [
    {{
      "ingles": "la palabra en ingles",
      "español": "traduccion al espanol argentino",
      "categoria": "sustantivo/verbo/adjetivo/adverbio",
      "ejemplo": "oracion de ejemplo en ingles",
      "ejemplo_español": "traduccion del ejemplo",
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
class MensajeSituacion(BaseModel):
    situacion: str
    historial: list
    nivel: str = "B1"

@app.post("/situacion")
def situacion(datos: MensajeSituacion):
    respuesta = cliente.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=f"""Sos un actor que interpreta situaciones de la vida real para que un estudiante de ingles nivel {datos.nivel} practique conversacion.

Situacion actual: {datos.situacion}

Reglas:
1. Responde SIEMPRE en ingles, en el rol asignado
2. Usa vocabulario apropiado para nivel {datos.nivel}
3. Si el estudiante comete errores gramaticales, al final de tu respuesta agrega entre parentesis: (Correccion: como deberia decirse, en espanol)
4. Mantene la escena realista y fluida
5. Hace preguntas para avanzar la conversacion
6. Mensajes cortos, maximo 3 oraciones""",
        messages=datos.historial
    )
    return {"respuesta": respuesta.content[0].text}

class MensajeResumen(BaseModel):
    situacion: str
    historial: list
    nivel: str = "B1"

@app.post("/resumen-situacion")
def resumen_situacion(datos: MensajeResumen):
    import json
    conversacion = "\n".join([
        f"{'Estudiante' if m['role'] == 'user' else 'Tutor'}: {m['content']}"
        for m in datos.historial
    ])
    respuesta = cliente.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""Analiza esta conversacion de practica de ingles y da un resumen del desempeno del estudiante.

Situacion: {datos.situacion}
Nivel del estudiante: {datos.nivel}

Conversacion:
{conversacion}

Responde UNICAMENTE con este JSON:
{{
  "puntaje": 85,
  "resumen": "descripcion breve del desempeno en espanol",
  "errores_frecuentes": ["error 1", "error 2"],
  "frases_utiles": ["frase util 1", "frase util 2"],
  "consejo": "consejo principal para mejorar en espanol"
}}"""
        }]
    )
    texto = respuesta.content[0].text.strip()
    if texto.startswith("```"):
        texto = texto.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(texto)
class MensajeDictado(BaseModel):
    nivel: str = "B1"
    cantidad: int = 5

class MensajeCorreccionDictado(BaseModel):
    original: str
    escrito: str

@app.post("/dictado/frases")
def dictado_frases(datos: MensajeDictado):
    import json
    respuesta = cliente.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""Genera {datos.cantidad} frases en ingles para un ejercicio de dictado, nivel {datos.nivel}.

Las frases deben:
- Ser naturales y variadas en tema
- Tener longitud apropiada para el nivel ({datos.nivel})
- Incluir vocabulario comun del nivel

Responde UNICAMENTE con este JSON:
{{
  "frases": [
    {{
      "texto": "la frase en ingles",
      "traduccion": "traduccion al espanol argentino"
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
    respuesta = cliente.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""Compara estas dos frases y analiza los errores del dictado.

Frase original: "{datos.original}"
Lo que escribio el estudiante: "{datos.escrito}"

Responde UNICAMENTE con este JSON:
{{
  "puntaje": 85,
  "palabras": [
    {{
      "palabra": "cada palabra del original",
      "estado": "correcta/incorrecta/faltante",
      "escrita": "lo que escribio el estudiante para esa palabra"
    }}
  ],
  "errores": ["descripcion de cada error en espanol"],
  "consejo": "consejo breve en espanol"
}}"""
        }]
    )
    texto = respuesta.content[0].text.strip()
    if texto.startswith("```"):
        texto = texto.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(texto)
class MensajeLectura(BaseModel):
    nivel: str = "B1"
    tema: str = ""

class MensajeRespuestaLectura(BaseModel):
    texto: str
    pregunta: str
    respuesta: str
    nivel: str = "B1"

@app.post("/lectura/generar")
def generar_lectura(datos: MensajeLectura):
    import json
    tema_instruccion = f"sobre el tema: {datos.tema}" if datos.tema else "sobre un tema interesante y variado"
    respuesta = cliente.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"""Genera un texto en ingles para lectura graduada, nivel {datos.nivel}, {tema_instruccion}.

El texto debe:
- Tener longitud apropiada para el nivel ({datos.nivel}): A1/A2=100 palabras, B1/B2=200 palabras, C1=300 palabras
- Usar vocabulario y estructuras apropiadas para el nivel
- Ser interesante y real, no artificial
- Tener un titulo

Luego genera 4 preguntas de comprension con 4 opciones cada una.

Responde UNICAMENTE con este JSON:
{{
  "titulo": "titulo del texto",
  "texto": "el texto completo en ingles",
  "palabras_clave": ["palabra1", "palabra2", "palabra3", "palabra4", "palabra5"],
  "preguntas": [
    {{
      "pregunta": "la pregunta en ingles",
      "opciones": ["opcion A", "opcion B", "opcion C", "opcion D"],
      "correcta": "opcion A",
      "explicacion": "por que es correcta, en espanol"
    }}
  ]
}}"""
        }]
    )
    texto = respuesta.content[0].text.strip()
    if texto.startswith("```"):
        texto = texto.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(texto)
class MensajeCultura(BaseModel):
    categoria: str = "expresiones"
    nivel: str = "B1"

@app.post("/cultura")
def cultura(datos: MensajeCultura):
    import json
    respuesta = cliente.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"""Sos un profesor de ingles y cultura anglofona. 
Genera 5 elementos de la categoria "{datos.categoria}" para nivel {datos.nivel}.

Responde UNICAMENTE con este JSON:
{{
  "items": [
    {{
      "expresion": "la expresion o elemento cultural en ingles",
      "tipo": "modismo/phrasal verb/slang/diferencia cultural/referencia",
      "significado": "que significa en espanol argentino",
      "origen": "de donde viene o por que se dice (breve, en espanol)",
      "ejemplo_us": "ejemplo de uso en ingles americano",
      "ejemplo_uk": "como se dice o usa en ingles britanico (si aplica, sino igual)",
      "ejemplo_español": "traduccion del ejemplo",
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
class MensajeEjercicios(BaseModel):
    tipo: str = "completar"
    nivel: str = "B1"

@app.post("/ejercicios")
def ejercicios(datos: MensajeEjercicios):
    import json
    respuesta = cliente.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"""Sos un profesor de ingles. Genera 5 ejercicios de tipo "{datos.tipo}" para nivel {datos.nivel}.

Responde UNICAMENTE con este JSON:
{{
  "tipo": "{datos.tipo}",
  "ejercicios": [
    {{
      "instruccion": "instruccion breve en espanol",
      "enunciado": "el ejercicio en ingles con ___ donde va la respuesta",
      "respuesta": "la respuesta correcta",
      "explicacion": "por que es correcta, en espanol",
      "pista": "una pista breve en espanol"
    }}
  ]
}}"""
        }]
    )
    texto = respuesta.content[0].text.strip()
    if texto.startswith("```"):
        texto = texto.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(texto)    