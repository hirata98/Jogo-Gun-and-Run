import pygame
import os
import random
import sys
from pygame import mixer


class soldado(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, molotoves):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.vida = 100
        self.scale = scale
        self.vida_max = self.vida
        self.molotoves = molotoves
        self.char_type = char_type
        self.shoot_cooldown = 0
        self.speed = speed
        self.direcao = 1
        self.vel_y = 0
        self.jump = False
        self.noAr = True
        self.flip = False
        self.animation_list = []
        self.index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        # variaves da ai
        self.count_move = 0
        self.ai_visao = pygame.Rect(0, 0, 550, 20)
        self.parado = False
        self.movi_count = 0

        # carrega todas as imagens do inimigo
        animation_types = ['parado', 'running', 'jump', 'morto']
        for animation in animation_types:
            temp_list = []
            # faz a contagem do numero de arquivo em uma pasta(as imagens)
            num_frames = len(os.listdir(f"src/imagens/{self.char_type}/{animation}"))
            for i in range(num_frames):
                imagem = pygame.image.load(f"src/imagens/{self.char_type}/{animation}/{i}.png").convert_alpha()
                imagem = pygame.transform.scale(imagem, (int(imagem.get_width() * scale),
                                                         int(imagem.get_height() * scale)))
                temp_list.append(imagem)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.update_animacao()
        self.esta_vivo()
        # updata cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        # variavel de controle de movimento
        dx = 0
        dy = 0

        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direcao = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direcao = 1

        # jump
        if self.jump:
            self.vel_y = -9
            self.jump = False
            self.noAr = True

        # gravidade
        self.vel_y += GRAVIDADE
        dy += self.vel_y

        # verifica colisao com o chao
        if self.rect.bottom + dy > 635:
            dy = 635 - self.rect.bottom
            self.noAr = False

        # atualiza valor do retangulo da imagem
        self.rect.x += dx
        self.rect.y += dy

    def atirar(self, speed):
        if self.shoot_cooldown == 0:
            tiro_sound.play()
            self.shoot_cooldown = 40
            if self.direcao == 2:
                bullet = Bullet(self.rect.centerx - (self.rect.size[0]),
                                self.rect.centery + 10.0, self.direcao, speed)
            else:
                bullet = Bullet(self.rect.centerx + (1.1 * self.rect.size[0] * self.direcao),
                                self.rect.centery - 10.0, self.direcao, speed)
            bullet_grupo.add(bullet)

    def ai(self):
        if not self.alive:
            self.rect.x -= GAME_SPEED
        if self.alive and player.alive:
            self.rect.x -= GAME_SPEED
            if random.randint(1, 200) == 1 and self.parado == False:
                self.update_action(0)  # 0: parado
                self.parado = True
                self.movi_count = 40
            # verifica se o player esta na area de visao do ai
            if self.ai_visao.colliderect(player.rect):
                self.update_action(0)  # 0: parado
                num = random.randint(1, 20)
                if num == 3:
                    self.atirar(5)
            else:
                if not self.parado:
                    if self.direcao == 1:
                        ai_movendo_direita = True
                    else:
                        ai_movendo_direita = False
                    ai_movendo_esquerda = not ai_movendo_direita
                    self.move(ai_movendo_esquerda, ai_movendo_direita)
                    self.update_action(1)  # 1: run
                    self.count_move += 1
                    # atualiza a visao do ai
                    self.ai_visao.center = (self.rect.centerx + 75 * self.direcao,
                                            self.rect.centery)
                    if self.count_move > TILE_SIZE:
                        self.direcao *= -1
                        self.count_move *= -1
                else:
                    self.movi_count -= 1
                    if self.movi_count <= 0:
                        self.parado = False

    def update_animacao(self):
        ANIMATION_COOLDOWN = 100

        # faz a atualização da imagem de acordo com a frame atual
        self.image = self.animation_list[self.action][self.index]

        # verifica o se passou tempo suficiante para atualizar a frame
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.index += 1
        # se terminou a animação reinicia ela
        if self.index >= len(self.animation_list[self.action]):
            self.index = 0

    def update_action(self, new_act):
        # inicialmente verifica se a nova acao é diferene da anterior
        if new_act != self.action:
            self.action = new_act
            self.index = 0
            self.update_time = pygame.time.get_ticks()

    def esta_vivo(self):
        if self.rect.centerx < 0:
            self.kill()
        if self.vida <= 0:
            self.vida = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        tela.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class Itens_box(pygame.sprite.Sprite):
    def __init__(self, tipo_item, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.tipo_item = tipo_item
        self.image = tipo_box[self.tipo_item]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        # se pegou o item
        if self.rect.x <= 0:
            self.kill()
        self.rect.x -= GAME_SPEED
        if pygame.sprite.collide_rect(self, player):
            iten_sound.play()
            # verifica o tipo de item
            if self.tipo_item == 'vida':
                player.vida += 25
                if player.vida > player.vida_max:
                    player.vida = player.vida_max
            elif self.tipo_item == 'molotove':
                player.molotoves += 2
            self.kill()


class Barra_vida():
    def __init__(self, x, y, vida, vida_max):
        self.x = x
        self.y = y
        self.vida = vida
        self.vida_max = vida_max

    def draw(self, vida):
        # atualiza o tamanho do rect da vida
        self.vida = vida
        ratio = self.vida / self.vida_max
        pygame.draw.rect(tela, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(tela, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(tela, GREEN, (self.x, self.y, 150 * ratio, 20))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direcao, speed):
        pygame.sprite.Sprite.__init__(self)
        self.speed = speed
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direcao = direcao

    def update(self):
        # move bullet
        if self.direcao == 2:
            self.rect.y += (self.direcao * self.speed)
        elif self.direcao == -1:
            self.rect.x += (self.direcao * self.speed * GAME_SPEED)
        else:
            self.rect.x += (self.direcao * self.speed)
        # verifica se a bala saiu da tela
        if self.rect.right < 0 or self.rect.left > tela_width:
            self.kill()
        # verificando colisao com players
        if pygame.sprite.spritecollide(player, bullet_grupo, False):
            if player.alive:
                hit_sound.play()
                player.vida -= 10
                self.kill()
        for inimigo in inimigo_grupo:
            if pygame.sprite.spritecollide(inimigo, bullet_grupo, False):
                if inimigo.alive:
                    inimigo.vida -= 50
                    self.kill()


class Molotove(pygame.sprite.Sprite):
    def __init__(self, x, y, direcao):
        pygame.sprite.Sprite.__init__(self)
        self.tempo = 100
        self.ver_y = -10
        self.speed = 10
        self.image = molotove_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direcao = direcao

    def update(self):
        self.ver_y += GRAVIDADE
        dx = self.direcao * self.speed
        dy = self.ver_y

        # verifica colisao
        if self.rect.bottom + dy > 630:
            dy = 630 - self.rect.bottom
            self.speed = 0
            self.rect.x -= GAME_SPEED

        # verifica se a molotov saiu da tela
        if self.rect.left + dx < 0 or self.rect.right + dx > tela_width:
            self.direcao *= -1

        # atualiza posicao do molotove
        self.rect.x += dx
        self.rect.y += dy

        # count para explosao
        self.tempo -= 1
        if self.tempo <= 0:
            self.kill()
            explosao = Explosao(self.rect.x, self.rect.y, 0.5)
            explosao_grupo.add(explosao)
            # verifica se esta na area de dano
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.vida -= 35
                hit_sound.play()
            for inimigo in inimigo_grupo:
                if abs(self.rect.centerx - inimigo.rect.centerx) < TILE_SIZE * 2 and \
                        abs(self.rect.centery - inimigo.rect.centery) < TILE_SIZE * 2:
                    inimigo.vida -= 100
                    hit_sound.play()


class Explosao(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(0, 7):
            img = pygame.image.load(f"src/imagens/explosao/{num}.png").convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.count = 0

    def update(self):
        velocidade_explosao = 4
        # atualiza a explosao
        self.count += 1

        if self.count >= velocidade_explosao:
            self.count = 0
            self.index += 1
            if self.index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.index]
            explosao_sound.play()


class objs_ceu(pygame.sprite.Sprite):
    def __init__(self, char_type):
        pygame.sprite.Sprite.__init__(self)
        self.x = random.randint(800, 1200)
        self.y = random.randint(50, 600)
        self.speed = 10
        self.char_type = char_type
        self.vida = 100
        self.image = pygame.image.load(f"src/imagens/objsCeu/{self.char_type}.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

    def update(self):
        self.rect.x -= self.speed + GAME_SPEED
        if self.rect.x < -self.rect.width:
            self.rect.x = tela_width + random.randint(2500, 3000)
            self.rect.y = random.randint(50, 550)

    def draw(self, tela):
        tela.blit(self.image, (self.rect.x, self.rect.y))


def draw_text(text, font, Tcolor, x, y):
    img = font.render(text, True, Tcolor)
    tela.blit(img, (x, y))


def main_menu():
    while True:
        if player.alive:
            tela.blit(BG_img, (0, 0))
        mx, my = pygame.mouse.get_pos()

        button_1 = pygame.Rect(300, 250, 200, 50)
        pygame.draw.rect(tela, (255, 0, 0), button_1)
        draw_text('PLAY', font, WHITE, 370, 270)
        if points > 0:
            draw_text('Points: ' + str(points), font, WHITE, 330, 200)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if button_1.collidepoint((mx, my)):
                        return True
        pygame.display.update()
        clock.tick(FPS)


if __name__ == '__main__':
    pygame.init()

    tela_width = 800
    tela_height = int(tela_width * 0.8)

    tela = pygame.display.set_mode((tela_width, tela_height))
    pygame.display.set_caption("theGame")

    # set framerate
    clock = pygame.time.Clock()
    FPS = 60

    # variaveis do game
    global x_pos_bd, y_pos_bd, points
    GAME_SPEED = 3
    GRAVIDADE = 0.75
    TILE_SIZE = 40
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 255)
    x_pos_bd = 0
    y_pos_bd = 0
    points = 0
    font = pygame.font.SysFont('Futura', 30)

    # variaveis do inimigo
    moving_left = False
    moving_right = False
    shoot = False
    molotove = False
    jogou_molotove = False

    # load imagens
    # background
    BG_img = pygame.image.load('src/imagens/background/bd.jpg').convert_alpha()
    # molotove
    molotove_img = pygame.image.load('src/imagens/molotove/molotove.png').convert_alpha()
    # bullet
    bullet_img = pygame.image.load('src/imagens/bullet/bullet.png').convert_alpha()
    # itens
    vida_iten = pygame.image.load('src/imagens/itens/vida.png').convert_alpha()
    molotove_iten = pygame.image.load('src/imagens/itens/molotove.png').convert_alpha()
    tipo_box = {
        'vida': vida_iten,
        'molotove': molotove_iten
    }

    # computa os pontos e printa no canto superior direito
    def score():
        global points, GAME_SPEED
        points += 1
        if points % 1000 == 0:
            GAME_SPEED += 1
        draw_text('Points: ' + str(points), font, WHITE, 600, 20)

    # desenha o fundo e faz movimentacao de efeito correndo
    def background():
        global x_pos_bd, y_pos_bd
        img_width = BG_img.get_width()
        tela.blit(BG_img, (x_pos_bd, y_pos_bd))
        tela.blit(BG_img, (img_width + x_pos_bd, y_pos_bd))
        if x_pos_bd <= -img_width:
            tela.blit(BG_img, (img_width + x_pos_bd, y_pos_bd))
            x_pos_bd = 0
        x_pos_bd -= GAME_SPEED

    def draw_backG():
        tela.fill((120, 201, 200))
        pygame.draw.line(tela, (255, 0, 0), (0, 450), (tela_width, 450))

    # grupo de sprite
    bullet_grupo = pygame.sprite.Group()
    molotove_grupo = pygame.sprite.Group()
    explosao_grupo = pygame.sprite.Group()
    inimigo_grupo = pygame.sprite.Group()
    itens_box_grupo = pygame.sprite.Group()
    objs_ceu_grupo = pygame.sprite.Group()

    # inicia o jogador e a vida
    player = soldado("player", 100, 200, 0.7, 5, 4)
    barra_vida = Barra_vida(10, 10, player.vida, player.vida)

    # load musicas e efeitos sonoros
    pygame.mixer.pre_init(44100, -16, 2, 512)
    hit_sound = pygame.mixer.Sound('src/musica/hit.wav')
    hit_sound.set_volume(0.1)
    bat_sound = pygame.mixer.Sound('src/musica/bat.wav')
    bat_sound.set_volume(0.1)
    iten_sound = pygame.mixer.Sound('src/musica/get_item.wav')
    iten_sound.set_volume(0.1)
    explosao_sound = pygame.mixer.Sound('src/musica/explosao.wav')
    explosao_sound.set_volume(0.3)
    tiro_sound = pygame.mixer.Sound('src/musica/tiro.wav')
    tiro_sound.set_volume(0.06)
    mixer.init()
    mixer.music.load('src/musica/Mbackground.wav')
    mixer.music.set_volume(0.05)
    mixer.music.play(-1)

    run = main_menu()
    while run:
        clock.tick(FPS)
        draw_backG()
        background()
        barra_vida.draw(player.vida)

        draw_text('MOLOTOVS: ', font, WHITE, 10, 35)
        for i in range(player.molotoves):
            tela.blit(molotove_img, (135 + (i * 10), 35))

        player.update()
        player.draw()

        # update grupos
        bullet_grupo.update()
        molotove_grupo.update()
        explosao_grupo.update()
        itens_box_grupo.update()
        objs_ceu_grupo.update()

        bullet_grupo.draw(tela)
        molotove_grupo.draw(tela)
        explosao_grupo.draw(tela)
        itens_box_grupo.draw(tela)
        objs_ceu_grupo.draw(tela)

        for inimigo in inimigo_grupo:
            inimigo.ai()
            inimigo.update()
            inimigo.draw()
        # acao do inimigo
        if player.alive:
            # conta os pontos
            score()
            # tiro nos objetos no ceu
            for obj in objs_ceu_grupo:
                for tiro in bullet_grupo:
                    if obj.rect.colliderect(tiro.rect):
                        obj.vida -= 50
                        obj.rect.x += 5
            # gera inimigos aleatoriamente e gifts
            num = random.randint(1, 800)
            if num == 10:
                objs_ceu_grupo.add(objs_ceu('heli'))
            if num == 8:
                objs_ceu_grupo.add(objs_ceu('aviao'))
            num = random.randint(1, 100)
            if num == 1:
                num = random.randint(800, 1200)
                if len(inimigo_grupo) < 3 and num > player.rect.centerx:
                    inimigo_grupo.add(soldado("inimigo", num, 620, 0.7, 2, 0))
            num = random.randint(1, 1000)
            if num == 2:
                num = random.randint(800, 1200)
                if len(itens_box_grupo) < 2 and num > player.rect.centerx:
                    itens_box_grupo.add(Itens_box('vida', num, 600))
            elif num == 3:
                num = random.randint(800, 1200)
                if len(itens_box_grupo) < 2 and num > player.rect.centerx:
                    itens_box_grupo.add(Itens_box('molotove', num, 600))
            # colidir com inimigo
            for inimigos in inimigo_grupo:
                if player.rect.colliderect(inimigos.rect) and inimigos.alive:
                    hit_sound.play()
                    player.vida -= 35
                    # player.rect.x -= 60
                    inimigos.kill()
            # colidiu com objetos no ceu
            for obs in objs_ceu_grupo:
                if player.rect.colliderect(obs.rect):
                    hit_sound.play()
                    player.vida -= 50
                    obs.kill()
            # atirar
            if shoot:
                player.atirar(7)
            # molotove
            elif molotove and jogou_molotove == False and player.molotoves > 0:
                molotove = Molotove(player.rect.centerx + (0.4 * player.rect.size[0] * player.direcao),
                                    player.rect.top, player.direcao)
                molotove_grupo.add(molotove)
                jogou_molotove = True
                player.molotoves -= 1
            if player.noAr:
                player.update_action(2)  # jump
            else:
                player.update_action(1)  # run
            # else:
            #   player.update_action(0)  # parado
            # player.rect.centerx -= 1
            player.move(moving_left, moving_right)
        # jogo terminou
        else:
            player.update_action(3)  # 3: morto
            run = main_menu()
            if run:
                player.alive = True
                player.vida = 100
                points = 0
                GAME_SPEED = 2
                player.molotoves = 4
                for ini in inimigo_grupo:
                    ini.kill()
                for itens in itens_box_grupo:
                    itens.kill()
                for obj in objs_ceu_grupo:
                    obj.kill()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            # keyboard presses
            if event.type == pygame.KEYDOWN:
                # if event.key == pygame.K_a:
                #   moving_left = True
                # if event.key == pygame.K_d:
                #   moving_right = True
                if event.key == pygame.K_w and player.alive:
                    bat_sound.play()
                    player.jump = True
                if event.key == pygame.K_SPACE:
                    shoot = True
                    player.direcao = 1
                if event.key == pygame.K_m:
                    molotove = True
                if event.key == pygame.K_ESCAPE:
                    run = False
            # keyboard buttun released
            if event.type == pygame.KEYUP:
                # if event.key == pygame.K_a:
                #    moving_left = False
                # if event.key == pygame.K_d:
                #     moving_right = False
                if event.key == pygame.K_SPACE:
                    shoot = False
                if event.key == pygame.K_m:
                    molotove = False
                    jogou_molotove = False
        pygame.display.update()
    pygame.quit()
