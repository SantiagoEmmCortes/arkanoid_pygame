import pygame
from config import *
from random import choice, randint

class Player(pygame.sprite.Sprite):
    def __init__(self, groups, reproducir_sonido):   #Constructor del Player
        super().__init__(groups)
        #Constructor de la superclase sprite (Mismo que hacer pygame.sprite.Sprite.__init__(self, groups))

        self.reproducir_sonido = reproducir_sonido

        #Imagen del player
        self.image = pygame.image.load(f"{DIRECTORIO_BASE}graphics/pad_corto.png")
        self.image = pygame.transform.scale(self.image, (ANCHO_VENTANA // 10, ALTO_VENTANA // 25))

        #Obtengo el display para poder usarlo en este archivo
        self.screen = pygame.display.get_surface()

        #Rectangulos y posiciones
        self.rect = self.image.get_rect(midbottom = (ANCHO_VENTANA / 2, ALTO_VENTANA - 20))
        self.rect_previo = self.rect.copy()
        self.direccion = pygame.math.Vector2()  #Guarda la direccion como vector (x,y)
        self.velocidad = VELOCIDAD_PLAYER
        self.pos = pygame.math.Vector2(self.rect.topleft)

        #Corazones
        self.corazones = CORAZONES_JUGADOR

        #Lasers
        self.puede_disparar = False
        self.cant_laser = 0
        self.laser_image = pygame.image.load(f"{DIRECTORIO_BASE}\graphics\laser.png").convert_alpha()
        self.laser_rects = []

        self.isplayer = True

    #Devuelve el player a la posicion inicial
    def reiniciar_posicion(self):
        self.rect = self.image.get_rect(midbottom = (ANCHO_VENTANA / 2, ALTO_VENTANA - 20))
        self.pos = pygame.math.Vector2(self.rect.topleft)

    #Input de teclas izquierda y derecha
    def input(self):
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.direccion.x = 1
        elif teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.direccion.x = -1
        else:
            self.direccion.x = 0

    #Colision del player con los bordes de la pantalla
    def limitador_de_pantalla(self):
        if self.rect.right > ANCHO_VENTANA:
            self.rect.right = ANCHO_VENTANA
            self.pos.x = self.rect.x
        if self.rect.left < 0:
            self.rect.left = 0
            self.pos.x = self.rect.x

    #Aplica las mejoras al player
    def mejora(self, tipo_mejora):
        if tipo_mejora == MEJORA_VELOCIDAD:
            self.quitar_mejora()
            self.velocidad = VELOCIDAD_PLAYER + VELOCIDAD_BONUS
            self.reproducir_sonido(SONIDO_MEJORA)
        if tipo_mejora == MEJORA_VIDA:
            self.corazones += 1
            self.reproducir_sonido(SONIDO_VIDA_EXTRA)
        if tipo_mejora == MEJORA_EXPAND:
            self.quitar_mejora()
            #Imagen del pad mas grande
            self.image = pygame.image.load(f"{DIRECTORIO_BASE}graphics/pad_largo.png")
            self.image = pygame.transform.scale(self.image, (ANCHO_VENTANA // 8, ALTO_VENTANA // 25))
            self.rect = self.image.get_rect(center = self.rect.center)
            self.pos.x = self.rect.x
            self.reproducir_sonido(SONIDO_EXPAND)
        if tipo_mejora == MEJORA_LASER:
            self.quitar_mejora()
            self.puede_disparar = True
            self.cant_laser = 2
            self.reproducir_sonido(SONIDO_MEJORA)

    #Saca la mejora del player activa, se llama al perder corazon o agarrar otra mejora
    def quitar_mejora(self):
        #Cambio la velocidad del jugador a la normal
        self.velocidad = VELOCIDAD_PLAYER
        #Vuelvo a dejar el pad en el tamaño original
        self.image = pygame.image.load(f"{DIRECTORIO_BASE}graphics/pad_corto.png")
        self.image = pygame.transform.scale(self.image, (ANCHO_VENTANA // 10, ALTO_VENTANA // 25))
        self.rect = self.image.get_rect(center = self.rect.center)
        self.pos.x = self.rect.x
        #Quito lasers
        self.cant_laser = 0
        self.puede_disparar = False

    #Blitea la imagen de los lasers/disparadores
    def mostrar_lasers(self):
        #Lo inicializo nuevamente vacio para resetearlo
        self.laser_rects = []
        if self.cant_laser == 2:
            #Centra los lasers en base al largo del player
            calculo_posicion = self.rect.width / (self.cant_laser + 1)
            for i in range(self.cant_laser):
                x = self.rect.left + calculo_posicion * (i + 1) #Si no el primero empezaria en 0
                laser_rect = self.laser_image.get_rect(midbottom = (x, self.rect.top))
                self.laser_rects.append(laser_rect)

            for laser_rect in self.laser_rects:
                self.screen.blit(self.laser_image, laser_rect)

    #Actualiza posicion del player y lasers
    def update(self, delta_time):
        #Actualizo el rect previo antes de que se actualice su posicion para mantener la anterior
        self.rect_previo = self.rect.copy()
        self.input()
        self.pos.x += self.direccion.x * self.velocidad * delta_time
        self.rect.x = round(self.pos.x) #Self.rect recibe un int, y la pos es float,
                                    #Con round me aseguro de acercarme al valor real
        self.limitador_de_pantalla()
        self.mostrar_lasers()

class Ball(pygame.sprite.Sprite):
    def __init__(self, groups, player, blocks, perder_vida, reproducir_sonido):
        super().__init__(groups)

        #Paso el player y bloques para chequear colisiones con la bola
        self.player = player
        self.blocks = blocks
        
        self.perder_vida = perder_vida

        self.reproducir_sonido = reproducir_sonido

        self.image = pygame.image.load(f"{DIRECTORIO_BASE}graphics/ball.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (30 ,30))

        #lo spawneo sobre el centro del player
        self.rect = self.image.get_rect(midbottom = player.rect.midtop)
        self.rect_previo = self.rect.copy()

        #El x se selecciona al azar entre 1 y -1, y la y siempre es hacia arriba
        self.direccion = pygame.math.Vector2((choice((1, -1)), -1))
        self.velocidad = VELOCIDAD_PELOTA
        self.pos = pygame.math.Vector2(self.rect.topleft)

        #Inicia como falsa hasta apretar SPACE
        self.active = False

    #Reinicia posicion de la pelota y la inactiva
    def reiniciar_posicion(self):
        self.rect = self.image.get_rect(midbottom = self.player.rect.midtop)
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.active = False

    #Chequeo colisiones de bola con pantalla
    def colision_con_pantalla(self, direccion):
        if direccion == "horizontal":
            if self.rect.left < 0:
                self.rect.left = 0
                self.pos.x = self.rect.x
                self.direccion.x *= -1
                #Invierte el sentido de la direccion

            if self.rect.right > ANCHO_VENTANA:
                self.rect.right = ANCHO_VENTANA
                self.pos.x = self.rect.x
                self.direccion.x *= -1

        if direccion == "vertical":
            if self.rect.top < 0:
                self.rect.top = 0
                self.pos.y = self.rect.y
                self.direccion.y *= -1

            #Si la pelota sale por debajo de la pantalla, el jugador muere e inactiva la pelota
            if self.rect.bottom > ALTO_VENTANA:
                self.active = False
                self.direccion.y = -1
                self.perder_vida()
    
    #Detecta las colisiones entre grupos de sprites
    def colisiones(self, direccion):
        #pygame.sprite.spritecollide(sprite, group, dokill)
        #se le pasa el sprite del que detecta colision (la bola), con el grupo con el que
        #   chequea (los bloques) y un booleano de si borra el sprite con el que colisiona
        sprites_colisionados = pygame.sprite.spritecollide(self, self.blocks, False)
        #Chequeo si la bola colisiona con el player
        if self.rect.colliderect(self.player.rect):
            sprites_colisionados.append(self.player)
        #Todos los sprites colisionados forman una lista para poder utilizarlos despues

        if sprites_colisionados:
            if direccion == "horizontal":
                for sprite in sprites_colisionados:
                    #Chequea que borde de la bola colisiona con que borde del sprite (player o block)
                    #Utiliza el rect_previo que se define 1 FPS antes para determinar desde donde se viene moviendo 
                    #(evita errores de colision por movimientos rapidos de la bola)
                    if self.rect.right >= sprite.rect.left and self.rect_previo.right <= sprite.rect_previo.left:
                        self.rect.right = sprite.rect.left -1
                        self.pos.x = self.rect.x
                        self.direccion.x *= -1
                    if self.rect.left <= sprite.rect.right and self.rect_previo.left >= sprite.rect_previo.right:
                        self.rect.left = sprite.rect.right + 1
                        self.pos.x = self.rect.x
                        self.direccion.x *= -1
        #Chequea si el sprite con el que colisiona tiene atributo vida, si no lo tiene retorna None
                    if getattr(sprite, "vida", None):
                        sprite.aplicar_daño(1)
        #Si tiene atributo isplayer, esta colisionando con el player y reproduce el sonido propio
                    if getattr(sprite, "isplayer", None):
                        self.reproducir_sonido(SONIDO_GOLPE_PAD)

            if direccion == "vertical":
                for sprite in sprites_colisionados:
                    if self.rect.bottom >= sprite.rect.top and self.rect_previo.bottom <= sprite.rect_previo.top:
                        self.rect.bottom = sprite.rect.top - 1
                        self.pos.y = self.rect.y
                        self.direccion.y *= -1
                    if self.rect.top <= sprite.rect.bottom and self.rect_previo.top >= sprite.rect_previo.bottom:
                        #Agrego 1 pixel a la colision para evitar que colisione doble y la direccion se doble invierta
                        self.rect.top = sprite.rect.bottom + 1
                        self.pos.y = self.rect.y
                        self.direccion.y *= -1
                    if getattr(sprite, "vida", None):
                        sprite.aplicar_daño(1)
                    if getattr(sprite, "isplayer", None):
                        self.reproducir_sonido(SONIDO_GOLPE_PAD)

    #Actualiza la bola
    def update(self, delta_time):
        #Chequea que la bola no este sobre el player
        if self.active:
            #Chequeo que la direccion no este en 0
            if self.direccion.magnitude() != 0:
                self.direccion = self.direccion.normalize()
            #Normaliza el vector, ajustando la magnitud (longitud) a 1 manteniendo la direccion original
            #Hace la velocidad mas consistente, si no al mover en diagonal cambiaria

            #Actualizo el rect previo antes de que se actualice su posicion para mantener la anterior
            self.rect_previo = self.rect.copy()

            #Separo movimiento horizontal de vertical para facilitar las colisiones
            self.pos.x += self.direccion.x * self.velocidad * delta_time
            self.rect.x = round(self.pos.x)
            self.colisiones("horizontal")
            self.colision_con_pantalla("horizontal")

            self.pos.y += self.direccion.y * self.velocidad * delta_time
            self.rect.y = round(self.pos.y)
            self.colisiones("vertical")
            self.colision_con_pantalla("vertical")
        #Si la pelota no fue lanzada actualiza la posicion sobre el player
        else:
            self.rect.midbottom = self.player.rect.midtop
            self.pos = pygame.math.Vector2(self.rect.topleft)

class Block(pygame.sprite.Sprite):
    def __init__(self, tipo_bloque, posicion, groups, crear_mejora, game_instance):
        super().__init__(groups)
        
        #Paso la instancia actual de la clase Game
        self.game_instance = game_instance

        self.vida = int(tipo_bloque)
        self.aplicar_textura(self.vida)
        
        self.rect = self.image.get_rect(topleft = posicion)
        self.rect_previo = self.rect.copy()

        self.crear_mejora = crear_mejora

        self.puntaje = self.vida * PUNTAJE_BASE_BLOQUE
    
    #Aplica la imagen correspondiente segun la vida del bloque
    def aplicar_textura(self, vida):
        #Utiliza el diccionario de referencias de bloque
        textura_bloque = REFERENCIAS_COLORES[str(vida)]
        self.image = pygame.image.load(f"{DIRECTORIO_BASE}graphics/bricks/brick_{textura_bloque}.png")
        self.image = pygame.transform.scale(self.image, (ANCHO_BLOQUES, ALTO_BLOQUES))

    #Aplica 1 de daño al bloque cuando es golpeado por la pelota o el disparo
    def aplicar_daño(self, daño):
        self.vida -= daño
        self.game_instance.reproducir_sonido(SONIDO_GOLPE_BLOQUE)

        #Si el bloque tiene mas de 0 de vida cambia la textura a la que corresponda
        if self.vida > 0:
            self.aplicar_textura(self.vida)
        #Si el bloque no tiene mas vida crea la mejora y lo borra
        else:
            self.crear_mejora(self.rect.center)
            #metodo de sprites para borrarlo de los grupos
            self.kill()
            #Suma el puntaje del bloque en base a la vida inicial
            self.game_instance.sumar_puntaje(self.puntaje)
            #Verifica si el bloque destruido era el ultimo del level
            self.game_instance.check_win()

class Mejoras(pygame.sprite.Sprite):
    def __init__(self, posicion, tipo_mejora, groups):
        super().__init__(groups)

        self.tipo_mejora = tipo_mejora
        self.image = pygame.image.load(f"{DIRECTORIO_BASE}graphics/mejoras/{str(tipo_mejora)}.png").convert_alpha()
        
        self.rect = self.image.get_rect(midtop = posicion)
        self.posicion = pygame.math.Vector2(self.rect.topleft)
        self.velocidad = 300

    def update(self, delta_time):
        self.posicion.y += self.velocidad * delta_time
        self.rect.y = round(self.posicion.y)

        #Si supera la base de la pantalla borro el sprite de su grupo
        if self.rect.top > ALTO_VENTANA + 20:
            self.kill()

class Disparo(pygame.sprite.Sprite):
    def __init__(self, posicion, image, groups):
        super().__init__(groups)
        
        self.image = image
        self.rect = self.image.get_rect(midbottom = posicion)

        self.posicion = pygame.math.Vector2(self.rect.topleft)
        self.velocidad = VELOCIDAD_PELOTA #Test

    def update(self, delta_time):
        self.posicion.y -= self.velocidad * delta_time
        self.rect.y = round(self.posicion.y)

        #Borro los que salen de la pantalla
        if self.rect.bottom <= -20:
            self.kill()