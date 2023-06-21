import pygame, sys, time
from config import *
from sprites import Player, Ball, Block, Mejoras, Disparo
import sqlite3
import string
import random

class Game:
    #Variable de clase para puntaje gral
    puntaje_total = 0
 
    def __init__(self):

        #Inicio pygame
        pygame.init()

        #Inicio la pantalla
        self.screen = pygame.display.set_mode((ANCHO_VENTANA,ALTO_VENTANA))
        pygame.display.set_caption('Arkanoid')

        #Contador para selector de level
        self.level_select = 1

        #Inicializo la libreria para usar sonidos
        pygame.mixer.init()
        
        #Cargo los sonidos
        self.sonido_muerte = pygame.mixer.Sound(f"{DIRECTORIO_SONIDOS + SONIDO_MUERTE}.ogg")
        self.sonido_muerte.set_volume(VOLUMEN_SONIDOS)
        self.sonido_expand = pygame.mixer.Sound(f"{DIRECTORIO_SONIDOS + SONIDO_EXPAND}.ogg")
        self.sonido_expand.set_volume(VOLUMEN_SONIDOS)
        self.sonido_golpe_bloque = pygame.mixer.Sound(f"{DIRECTORIO_SONIDOS + SONIDO_GOLPE_BLOQUE}.ogg")
        self.sonido_golpe_bloque.set_volume(VOLUMEN_SONIDOS)
        self.sonido_golpe_bloque_2 = pygame.mixer.Sound(f"{DIRECTORIO_SONIDOS + SONIDO_GOLPE_BLOQUE_2}.ogg")
        self.sonido_golpe_bloque_2.set_volume(VOLUMEN_SONIDOS)
        self.sonido_golpe_pad = pygame.mixer.Sound(f"{DIRECTORIO_SONIDOS + SONIDO_GOLPE_PAD}.ogg")
        self.sonido_golpe_pad.set_volume(VOLUMEN_SONIDOS)
        self.sonido_laser = pygame.mixer.Sound(f"{DIRECTORIO_SONIDOS + SONIDO_LASER}.ogg")
        self.sonido_laser.set_volume(VOLUMEN_SONIDOS)
        self.sonido_vida_extra = pygame.mixer.Sound(f"{DIRECTORIO_SONIDOS + SONIDO_VIDA_EXTRA}.ogg")
        self.sonido_vida_extra.set_volume(VOLUMEN_SONIDOS)
        self.sonido_mejora = pygame.mixer.Sound(f"{DIRECTORIO_SONIDOS + SONIDO_MEJORA}.ogg")
        self.sonido_mejora.set_volume(VOLUMEN_SONIDOS)

        #Seteo la musica
        pygame.mixer.music.load(f"{DIRECTORIO_SONIDOS + SONIDO_MUSICA}.mp3")
        pygame.mixer.music.set_volume(0.02)

        #Cargo el fondo principal
        self.fondo = pygame.image.load(f'{DIRECTORIO_BASE}graphics/fondo_main.png').convert_alpha()

        #Grupos de sprites
        self.all_sprites = pygame.sprite.Group()
        self.block_sprites = pygame.sprite.Group()
        self.player_sprite = pygame.sprite.Group()
        self.ball_sprite = pygame.sprite.Group()
        self.sprites_mejoras = pygame.sprite.Group()
        self.sprites_disparos = pygame.sprite.Group()

        #Instancio player y bola
        self.player = Player([self.all_sprites, self.player_sprite], self.reproducir_sonido)
        self.ball = Ball([self.all_sprites, self.ball_sprite], self.player, self.block_sprites, self.perder_vida, self.reproducir_sonido)

        #Imagen de los corazones
        self.image_corazon = pygame.image.load(f"{DIRECTORIO_BASE}graphics\heart.png").convert_alpha()
        self.image_corazon = pygame.transform.scale(self.image_corazon, (35, ALTO_CORAZONES))

        #Variables de disparos
        self.image_disparo = pygame.image.load(f"{DIRECTORIO_BASE}graphics/projectile.png").convert_alpha()
        self.tiempo_disparos = 0
        self.cooldown_disparo = False

    #Creo un método para poder sumar puntajes desde la clase Blocks
    def sumar_puntaje(self, puntaje_a_sumar):
        self.puntaje_total += puntaje_a_sumar

    #Blitea el puntaje en pantalla
    def mostrar_puntaje(self):
        texto = f"Puntaje: {self.puntaje_total}"
        fuente = pygame.font.SysFont(FUENTE_MENU, TAMAÑO_FUENTE_PUNTAJE)
        image_texto = fuente.render(texto, True, COLOR_TEXTO_MENU)
        texto_rect = image_texto.get_rect()
        texto_rect.x = (ANCHO_VENTANA - OFFSET_PUNTAJE)
        texto_rect.y = 4
        self.screen.blit(image_texto, texto_rect)

    #Lo llamo al instanciar los bloques para determinar que bloques sueltan mejoras
    def crear_mejora(self, posicion):
        #Genero un número aleatorio y lo comparo con mis probabilidades de crear una mejora
        if random.random() < MEJORA_CHANCE:
            #Si tiene una mejora determina probabilidad de cada mejora en base a la probabilidad que determino
            tipo_mejora = random.choices(
                population=[mejora[0] for mejora in MEJORAS_CHANCES],
                weights=[mejora[1] for mejora in MEJORAS_CHANCES]
            )[0]

            #Instancio las mejoras
            Mejoras(posicion, tipo_mejora, [self.all_sprites, self.sprites_mejoras])

    #Metodo para mostrar el texto que le paso centrado en la x
    def mostrar_texto_centrado(self, texto, tamaño, y):
        font = pygame.font.SysFont(FUENTE_MENU, tamaño)
        image_texto = font.render(texto, True, COLOR_TEXTO_MENU)
        texto_rect = image_texto.get_rect()
        texto_rect.centerx = (ANCHO_VENTANA // 2)
        texto_rect.y = y
        self.screen.blit(image_texto, texto_rect)

    #Metodo para mostrar el texto que le paso en la posicion pasada
    def mostrar_texto(self, texto, tamaño, x, y):
        font = pygame.font.SysFont(FUENTE_MENU, tamaño)
        image_texto = font.render(texto, True, COLOR_TEXTO_MENU)
        texto_rect = image_texto.get_rect()
        texto_rect.x = x
        texto_rect.y = y
        self.screen.blit(image_texto, texto_rect)

    #Metodo para mostrar el texto que le paso en la posicion pasada con fuente pixelada
    def mostrar_texto_pixelado(self, texto, tamaño, x, y):
        font = pygame.font.Font(FUENTE_PIXEL, tamaño)
        image_texto = font.render(texto, True, COLOR_TEXTO_MENU)
        texto_rect = image_texto.get_rect()
        texto_rect.x = x
        texto_rect.y = y
        self.screen.blit(image_texto, texto_rect)
    
    #Crea los bloques del level y al llamarlo del main_game los muestra en pantalla
    def level_config(self):
        #Determina el level que se va a crean
        self.selector_level()
        self.spawn_jugador(True)
        #Con enumerate me devuelve el index de la fila y la fila en si
        for fila_index, fila in enumerate(self.level_layout):
            for columna_index, columna in enumerate(fila):
                if columna != ' ':
                #Separo el espacio entre bloques para que me quede 1 pixel arriba y 1 pixel abajo
                    y = fila_index * (ALTO_BLOQUES + ENTRE_BLOQUES) + ENTRE_BLOQUES // 2 + CORRECCION_CORAZONES
                    x = columna_index * (ANCHO_BLOQUES + ENTRE_BLOQUES) + ENTRE_BLOQUES // 2
                    #Instancio el bloque en la posicion determinada
                    Block(columna, (x, y), self.block_sprites, self.crear_mejora, self)
        #Inicio la musica al iniciar el level
        pygame.mixer.music.play(loops=-1)

    #Segun la variable de level_select cambio el layout
    def selector_level(self):
        if self.level_select == 1:
            self.level_layout = LEVEL_1_LAYOUT
        elif self.level_select == 2:
            self.level_layout = LEVEL_2_LAYOUT
        elif self.level_select == 3:
            self.level_layout = LEVEL_3_LAYOUT

    #Pinto la pantalla de negro, quito todo lo dibujado, vuelvo el jugador y la pelota a la posicion inicial, y los vuelvo a dibujar
    def limpiar_pantalla(self):
        self.screen.fill((0, 0, 0))
        self.block_sprites.empty()
        self.sprites_mejoras.empty()
        self.sprites_disparos.empty()
        self.all_sprites.empty()
        self.player.reiniciar_posicion()
        self.player.quitar_mejora()
        self.ball.reiniciar_posicion()
        self.all_sprites.add(self.player_sprite)
        self.all_sprites.add(self.ball_sprite)
 
    #Cuando se rompe un bloque, chequeo si queda algun sprite de bloques, si no hay ninguno, pasa de nivel
    def check_win(self):
        if len(self.block_sprites) == 0:
            self.level_select += 1
            #Si paso del level maximo determino instancia de game over como True
            if self.level_select == 4:
                self.game_over(True)
            self.limpiar_pantalla()
            self.level_config()
        
    #Bliteo las vidas en pantalla arriba a la izquierda
    def mostrar_corazones(self):
        for i in range(self.player.corazones):
            #Determina la posicion de cada corazon en base al ancho de la imagen mas 2 pixeles entre medio
            x = 2 + i * (self.image_corazon.get_width() + 2)
            self.screen.blit(self.image_corazon, (x, 4))

    #Chequeo si el player colisiona con una mejora y la aplico
    def colisiones_mejoras(self):
        #Recorre los grupos de sprites de player y mejoras y chequea si colisionan, con el dokill: True los saca del grupo
        sprites_colisionados = pygame.sprite.spritecollide(self.player, self.sprites_mejoras, True)
        for sprite in sprites_colisionados:
            self.player.mejora(sprite.tipo_mejora)

    #Bliteo los disparos en pantalla cuando el jugador tiene la mejora de laser y aprieta ESPACIO
    def crear_disparos(self):
        self.reproducir_sonido(SONIDO_LASER)
        for disparo in self.player.laser_rects:
            #genero el disparo 30 pixeles sobre el laser
            posicion = disparo.midtop - pygame.math.Vector2(0, 30)
            #Instancio el disparo y lo llamo cuando aprieta SPACE
            Disparo(posicion, self.image_disparo, [self.all_sprites, self.sprites_disparos])

    #Evita el spam de los disparos por el jugador con un timer de 0,4 segundos
    def timer_laser(self):
        if pygame.time.get_ticks() - self.tiempo_disparos >= 400:
            self.cooldown_disparo = True
    
    #Chequeo si los disparos bliteados colisionan con algun bloque y le aplican daño
    def colisiones_disparos(self):
        for disparo in self.sprites_disparos:
            #Guarda en una lista las colisiones estre disparos y bloques
            sprites_colisionados = pygame.sprite.spritecollide(disparo, self.block_sprites, False)
            if sprites_colisionados:
                for sprite in sprites_colisionados:
                    #Le aplico daño al bloque
                    sprite.aplicar_daño(1)
                #Borro el disparo cuando colisiona
                disparo.kill()
    
    #Cuando el jugador muere se llama este metodo
    def perder_vida(self):
        #Le quito una vida al jugador
        self.player.corazones -= 1
        #Le quito la mejora
        self.player.quitar_mejora()
        #Pongo el sonido de muerte
        self.reproducir_sonido(SONIDO_MUERTE)
        #Respawneo el jugador en la posicion inicial
        self.spawn_jugador()

    #Spawnea el jugador en el centro de la pantalla luego de mostrar pantalla de vidas o level, y evitar movimiento por 2 segundos
    def spawn_jugador(self, pasar_level = False):
        #Limpio los eventos previos para que el usuario no pueda lanzar la bola mientras spawnea
        pygame.event.get()
        #Redibujar fondo y tapar todos los sprites
        self.screen.blit(self.fondo, (0,0))
        #Redibujar vidas
        self.mostrar_corazones()
        #Redibujar puntaje
        self.mostrar_puntaje()
        #Redibujar bloques
        self.block_sprites.update()
        self.block_sprites.draw(self.screen)
        if pasar_level:
            #Si paso el level muestra pantalla de level
            self.screen.fill("Black")
            self.mostrar_texto_centrado(f"LEVEL {self.level_select}", TAMAÑO_FUENTE_MENU, 420)
        else:
            #Si perdio vida muestra vidas restantes
            self.mostrar_texto_centrado(f"VIDAS RESTANTES: {self.player.corazones}", TAMAÑO_FUENTE_MENU, 420)
        pygame.display.flip()
        self.player.reiniciar_posicion()
        self.ball.reiniciar_posicion()
        #Delay de 2 segundos durante los cuales detiene el resto del juego
        pygame.time.delay(2000)
        #Limpio los eventos previos para que el usuario no pueda lanzar la bola mientras spawnea
        pygame.event.get()
    
    #Metodo para reproducir sonidos, recibe el nombre del sonido
    def reproducir_sonido(self, sonido):
        if sonido == SONIDO_MUERTE:
            self.sonido_muerte.play()
        elif sonido == SONIDO_EXPAND:
            self.sonido_expand.play()
        elif sonido == SONIDO_GOLPE_BLOQUE:
            self.sonido_golpe_bloque.play()
        elif sonido == SONIDO_GOLPE_BLOQUE_2:
            self.sonido_golpe_bloque_2.play()
        elif sonido == SONIDO_GOLPE_PAD:
            self.sonido_golpe_pad.play()
        elif sonido == SONIDO_LASER:
            self.sonido_laser.play()
        elif sonido == SONIDO_VIDA_EXTRA:
            self.sonido_vida_extra.play()
        elif sonido == SONIDO_MEJORA:
            self.sonido_mejora.play()

    #Pantalla de menu
    def menu(self):
        while True:
            #Fondo propio
            fondo_menu = pygame.image.load(f"{DIRECTORIO_BASE}graphics/fondo_menu.png").convert_alpha()
            fondo_escalado = pygame.transform.scale(fondo_menu, (ANCHO_VENTANA,ALTO_VENTANA))
            self.screen.blit(fondo_escalado, (0, 0))

            self.mostrar_texto_centrado("Press SPACE to play", TAMAÑO_FUENTE_MENU, 480)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.main_game()

            pygame.display.flip()

    #Pantalla de niveles adaptable al nivel seleccionado
    def main_game(self):
        last_time = time.time()
        self.level_config()
        self.player.corazones = CORAZONES_JUGADOR
        while True:
            
            #Timer para limitar los FPS
            delta_time = time.time() - last_time
            last_time = time.time()

            #Loop de eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.ball.active = True
                        #Detecta que el player tenga mejora laser y no tenga el disparo en cooldown
                        if self.player.puede_disparar and self.cooldown_disparo:
                            self.crear_disparos()
                            self.cooldown_disparo = False
                            #Timer para detectar el cooldown
                            self.tiempo_disparos = pygame.time.get_ticks()
                    #Comandos para testeo de niveles
                    if event.key == pygame.K_F1:
                        self.level_select = 1
                        self.limpiar_pantalla()
                        self.level_config()
                    if event.key == pygame.K_F2:
                        self.level_select = 2
                        self.limpiar_pantalla()
                        self.level_config()
                    if event.key == pygame.K_F3:
                        self.level_select = 3
                        self.limpiar_pantalla()
                        self.level_config()
                    if event.key == pygame.K_F5:
                        self.player.mejora(MEJORA_LASER)
                    if event.key == pygame.K_F6:
                        self.player.corazones += 1

            #Finaliza el loop main game y corre el game_over si pierde todas las vidas
            if self.player.corazones <= 0:
                self.game_over()
            
            #Dibujo del fondo
            self.screen.blit(self.fondo, (0,0))

            #Updates
            self.all_sprites.update(delta_time)
            self.block_sprites.update(delta_time)
            self.colisiones_mejoras()
            self.timer_laser()
            self.colisiones_disparos()

            #dibujos de superficies
            self.all_sprites.draw(self.screen)
            self.block_sprites.draw(self.screen)
            self.mostrar_corazones()
            self.mostrar_puntaje()

            pygame.display.flip()

    #Pantalla de Game Over
    def game_over(self, gano = False):
        #Quito la musica
        pygame.mixer.music.stop()

        #Trae todas las letras de la A a la Z en mayusculas
        letras = string.ascii_uppercase
        indice_1 = 0
        indice_2 = 0
        indice_3 = 0
        pos = 1
        marco_tamaño = 200
        marco_borde = 4

        #Si el usuario presiona la tecla ENTER pasa a la pantalla de puntos
        flag = True
        while flag:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        flag = False
                    if event.key == pygame.K_LEFT:
                        pos -= 1
                        if pos == 0:
                            pos = 3
                    if event.key == pygame.K_RIGHT:
                        pos += 1
                        if pos == 4:
                            pos = 1
                    if event.key == pygame.K_UP:
                        if pos == 1:
                            indice_1 += 1
                        elif pos == 2:
                            indice_2 += 1
                        elif pos == 3:
                            indice_3 += 1
                    if event.key == pygame.K_DOWN:
                        if pos == 1:
                            indice_1 -= 1
                        elif pos == 2:
                            indice_2 -= 1
                        elif pos == 3:
                            indice_3 -= 1

            self.screen.fill("Black")
            if gano:
                self.mostrar_texto_centrado("VICTORY!", TAMAÑO_FUENTE_MENU, 180)
            else:
                self.mostrar_texto_centrado("GAME OVER", TAMAÑO_FUENTE_MENU, 180)
            self.mostrar_texto_centrado(f"Puntaje: {self.puntaje_total}", TAMAÑO_FUENTE_MENU, 240)
            
            #Calculo donde dibujar el marco de la letra seleccionada
            #Empieza en 500 la primer letra y la siguiente desde el proximo marco
            marco_x = 500 + (pos - 1) * marco_tamaño
            marco_y = 490
            pygame.draw.rect(self.screen, (255, 255, 255), (marco_x, marco_y, marco_tamaño, marco_tamaño), marco_borde)
            #Descomentar para que la letra tenga fondo negro, si el color de fondo es otro
            #pygame.draw.rect(self.screen, (0, 0, 0), (marco_x + 4, marco_y + 4, marco_tamaño - 8, marco_tamaño - 8))

            self.mostrar_texto_pixelado(letras[indice_1], 150, 525, 500)
            self.mostrar_texto_pixelado(letras[indice_2], 150, 725, 500)
            self.mostrar_texto_pixelado(letras[indice_3], 150, 925, 500)

            pygame.display.flip()
        
        #Pasa los indices a letras (que contiene las letras en ascii) para concatenar el string
        nombre = letras[indice_1] + letras[indice_2] + letras[indice_3]

        #Guardo el puntaje y las iniciales del jugador en la DB
        with sqlite3.connect(f"{DIRECTORIO_BASE}arkanoid_db.db") as conexion:
            try:
                #Hago el insert en la base de datos
                conexion.execute('''
                    insert into score (nombre, puntaje)
                    values (?, ?)
                ''', (nombre, self.puntaje_total))
                
                conexion.commit()
            except Exception as error:
                print("Hubo un error al insertar en la tabla score: ", error)
        
        #Reinicio el puntaje total
        self.puntaje_total = 0
        #Reinicio el nivel a 1
        self.level_select = 1
        #Quito todo lo dibujado de la pantalla
        self.limpiar_pantalla()
        #Muestro la pantalla de puntuaciones
        self.puntuaciones()
        
    #Pantalla final de puntuaciones, muestra top 10 mejores puntajes
    def puntuaciones(self):
        self.screen.fill("Black")
        self.mostrar_texto_centrado("MEJORES PUNTAJES", TAMAÑO_FUENTE_MENU, 180)

        #Busco los 10 puntajes más altos en la DB ordenados por mayor a menor
        with sqlite3.connect(f"{DIRECTORIO_BASE}arkanoid_db.db") as conexion:
            cursor = conexion.execute("SELECT nombre, puntaje FROM score ORDER BY puntaje DESC LIMIT 10")

        y_pos_texto = 310
        self.mostrar_texto_pixelado("NOMBRE", TAMAÑO_FUENTE_PUNTAJE_TABLA, OFFSET_PUNTAJE_TABLA_NOMBRE, y_pos_texto)
        self.mostrar_texto_pixelado("PUNTAJE", TAMAÑO_FUENTE_PUNTAJE_TABLA, OFFSET_PUNTAJE_TABLA_PUNTAJE, y_pos_texto)
        y_pos_texto += 30

        for fila in cursor:
            y_pos_texto += 45
            self.mostrar_texto_pixelado(fila[0], TAMAÑO_FUENTE_PUNTAJE_TABLA, OFFSET_PUNTAJE_TABLA_NOMBRE, y_pos_texto)
            self.mostrar_texto_pixelado(str(fila[1]), TAMAÑO_FUENTE_PUNTAJE_TABLA, OFFSET_PUNTAJE_TABLA_PUNTAJE, y_pos_texto)
        
        tiempo_inicial = pygame.time.get_ticks()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.menu()

            tiempo_actual = pygame.time.get_ticks()
            timer = tiempo_actual - tiempo_inicial

            #Hago un contador de 10 segundos para volver al menu inicial automaticamente
            if timer >= 10000:
                self.menu()

            pygame.display.flip()

game = Game()
game.menu()