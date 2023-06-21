DIRECTORIO_BASE = "Pygame/"

ANCHO_VENTANA = 1600
ALTO_VENTANA = 900

LEVEL_1_LAYOUT = [
    "122222222221",
    "112222222211",
    "111222222111",
    " 1111111111 ",
    "  11111111  ",
    "   111111   "]

LEVEL_2_LAYOUT = [
    "            ",
    " 44444444444",
    "            ",
    "33333333333 ",
    "            ",
    " 33333333333",
    "            ",
    "22222222222 ",
    "            ",
    " 22222222222",
    "            ",
    "11111111111 ",
    "            ",
    "  1111111111"]

LEVEL_3_LAYOUT = [
    "7           ",
    "66          ",
    "555         ",
    "4444        ",
    "44444       ",
    "333333      ",
    "3333333     ",
    "22222222    ",
    "222222222   ",
    "1111111111  ",
    "11111111111 ",
    "444444444441"]

REFERENCIAS_COLORES = {
    '1': 'red',
    '2': 'blue',
    '3': 'cyan',
    '4': 'green',
    '5': 'yellow',
    '6': 'orange',
    '7': 'magenta'}

ENTRE_BLOQUES = 2
#Divido el alto de la ventana por la cantidad de filas en mi layout
ALTO_BLOQUES = ALTO_VENTANA // 21 - ENTRE_BLOQUES
#Divido el ancho de la ventana por la cantidad de columnas en una de las filas del layout
ANCHO_BLOQUES = ANCHO_VENTANA // 12 - ENTRE_BLOQUES

#Espacio para corazones
ALTO_CORAZONES = 25
CORRECCION_CORAZONES = ALTO_CORAZONES + 5
CORAZONES_JUGADOR = 3

#Mejoras
MEJORA_EXPAND = 1
MEJORA_VIDA = 2
MEJORA_LASER = 3
MEJORA_VELOCIDAD = 4

#Probabilidad de mejoras
MEJORA_CHANCE = 0.4
MEJORAS_CHANCES = [
    (MEJORA_EXPAND, 0.35),
    (MEJORA_VIDA, 0.1),
    (MEJORA_LASER, 0.25),
    (MEJORA_VELOCIDAD, 0.3),
]

VELOCIDAD_PLAYER = 800
VELOCIDAD_PELOTA = 750
VELOCIDAD_BONUS = 250

FUENTE_MENU = "Calibriblack"
FUENTE_PIXEL = f"{DIRECTORIO_BASE}assets/fuente.ttf"
TAMAÑO_FUENTE_MENU = 110
TAMAÑO_FUENTE_PUNTAJE = 33
TAMAÑO_FUENTE_PUNTAJE_TABLA = 40
OFFSET_PUNTAJE = 170
OFFSET_PUNTAJE_TABLA_NOMBRE = 350
OFFSET_PUNTAJE_TABLA_PUNTAJE = 1000
COLOR_TEXTO_MENU = (255, 255, 255)

PUNTAJE_BASE_BLOQUE = 100

DIRECTORIO_SONIDOS = DIRECTORIO_BASE + "sounds/"
SONIDO_MUERTE = "death"
SONIDO_EXPAND = "expand"
SONIDO_GOLPE_BLOQUE = "hit_brick"
SONIDO_GOLPE_BLOQUE_2 = "hit_brick_2"
SONIDO_GOLPE_PAD = "hit_pad"
SONIDO_LASER =  "laser_shoot"
SONIDO_MUSICA = "music"
SONIDO_VIDA_EXTRA = "one-up"
SONIDO_MEJORA = "powerup"
VOLUMEN_SONIDOS = 0.1

#Layout para testear el cambio de nivel
"""
LEVEL_TEST_LAYOUT = [
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "      1     ",]
"""