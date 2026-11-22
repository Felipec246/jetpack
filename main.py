import pygame
import random
import math

# ===== Inicialização =====
pygame.init()
WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tsunami Surf")
clock = pygame.time.Clock()
FPS = 60
fonte = pygame.font.SysFont(None, 36)
fonte_grande = pygame.font.SysFont(None, 48)
pygame.mixer.init()

pygame.mixer.music.load("assets/musica.mp3.mp3")
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(-1)

som_quilha = pygame.mixer.Sound("assets/coletavel.mp3.mp3")
som_morte = pygame.mixer.Sound("assets/morte.mp3.mp3")
som_quilha.set_volume(0.7)
som_morte.set_volume(0.8)

# ===== Constantes do jogo =====
GRAVIDADE = 0.5          # a cada frame, puxa o surfista um pouco para baixo
IMPULSO = -1.0           # força para subir (negativo = para cima)
VEL_MAXIMA = 10          # velocidade vertical máxima
VEL_INICIAL = 6          # velocidade inicial dos obstáculos (pixels por frame)
INTERVALO_OBSTACULO = 80 # frames entre um obstáculo e outro (no começo)
INTERVALO_MINIMO = 50    # o intervalo nunca fica menor que isso
NIVEL_AGUA = HEIGHT - 60 # y da superfície da água (o "chão" do surfista)

# Face do tsunami: uma rampa reta do ponto mais alto (topo) até a água (base).
# O surfista sempre fica em cima dessa rampa.
ONDA_TOPO_X, ONDA_TOPO_Y = 150, 170   # ponto mais alto que o surfista alcança
ONDA_BASE_X = 280                     # onde a face da onda encontra a água

# ===== Cores (R, G, B) =====
COR_CEU = (110, 130, 160)
COR_CIDADE_FUNDO = (90, 105, 135)
COR_PREDIO = (90, 90, 100)
COR_JANELA = (240, 220, 120)
COR_POSTE = (50, 50, 55)
COR_PEIXE = (150, 190, 210)
COR_AGUA = (20, 90, 150)
COR_TSUNAMI = (15, 70, 130)
COR_ESPUMA = (235, 245, 255)
COR_QUILHA = (255, 200, 30)
BRANCO = (255, 255, 255)
CINZA = (180, 180, 190)
PRETO = (0, 0, 0)
COR_PELE = (200, 150, 110)
COR_ROUPA = (20, 20, 20)
COR_CABELO = (30, 20, 10)


# ===== Funções que criam imagens (feitas uma vez só, antes do loop) =====
def cria_corpo():
    """Desenha a prancha e o corpo do surfista (sem a cabeça) numa imagem 50x50 transparente."""
    img = pygame.Surface((50, 50), pygame.SRCALPHA)  # SRCALPHA = fundo transparente
    pygame.draw.ellipse(img, (250, 200, 60), (0, 40, 50, 9))      # prancha
    pygame.draw.line(img, COR_ROUPA, (16, 41), (22, 30), 5)       # perna de trás
    pygame.draw.line(img, COR_ROUPA, (34, 41), (28, 30), 5)       # perna da frente
    pygame.draw.line(img, COR_ROUPA, (25, 31), (25, 18), 8)       # tronco
    pygame.draw.line(img, COR_PELE, (6, 23), (44, 21), 4)         # braços abertos
    return img


def cria_surfista_frente():
    """Surfista olhando para fora da onda: dá para ver o rosto (olhos e sorriso)."""
    img = cria_corpo()
    pygame.draw.circle(img, COR_PELE, (25, 10), 8)                # cabeça
    pygame.draw.ellipse(img, COR_CABELO, (16, 1, 18, 7))          # cabelo (só em cima)
    pygame.draw.circle(img, PRETO, (22, 10), 2)                   # olho esquerdo
    pygame.draw.circle(img, PRETO, (28, 10), 2)                   # olho direito
    pygame.draw.arc(img, PRETO, (21, 10, 8, 6), math.pi, 2 * math.pi, 1)  # sorriso
    return img


def cria_surfista_costas():
    """Surfista virado para a onda: vemos só a nuca (cabeça toda de cabelo)."""
    img = cria_corpo()
    pygame.draw.circle(img, COR_CABELO, (25, 10), 8)              # cabeça vista de trás
    pygame.draw.circle(img, COR_PELE, (17, 11), 2)                # orelha esquerda
    pygame.draw.circle(img, COR_PELE, (33, 11), 2)                # orelha direita
    return img


def cria_brilho():
    """Círculo amarelo meio transparente que fica atrás da quilha (mostra que é para pegar)."""
    img = pygame.Surface((50, 50), pygame.SRCALPHA)
    pygame.draw.circle(img, (255, 230, 60, 110), (25, 25), 24)    # o 4º número é a transparência
    pygame.draw.circle(img, (255, 245, 150, 170), (25, 25), 16)   # (0 = invisível, 255 = sólido)
    return img


def cria_cidade_fundo():
    """Desenha silhuetas de prédios distantes numa imagem do tamanho da tela."""
    img = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    x = 0
    while x < WIDTH:
        largura = random.randint(40, 90)
        altura = random.randint(80, 280)
        pygame.draw.rect(img, COR_CIDADE_FUNDO, (x, NIVEL_AGUA - altura, largura, altura))
        x += largura + random.randint(0, 15)
    return img


# ===== Funções que criam obstáculos e quilhas =====
def novo_predio():
    """Cria um prédio baixo saindo da água."""
    altura_visivel = random.randint(80, 190)
    largura = random.randint(50, 80)
    topo = NIVEL_AGUA - altura_visivel
    return pygame.Rect(WIDTH, topo, largura, HEIGHT - topo)


def novo_poste():
    """Cria um poste fino saindo da água."""
    altura_visivel = random.randint(100, 180)
    topo = NIVEL_AGUA - altura_visivel
    return pygame.Rect(WIDTH, topo, 14, HEIGHT - topo)


def novo_aviao():
    """Cria um avião na parte de CIMA da onda (para o topo não ser um lugar seguro)."""
    y = random.randint(ONDA_TOPO_Y - 45, 220)
    return pygame.Rect(WIDTH, y, 80, 26)


def novo_peixe():
    """Cria um peixe voador. Ele é um dicionário: o retângulo e a altura central do voo
    (o peixe sobe e desce em volta dessa altura)."""
    altura_central = random.randint(220, 380)   # parte do MEIO da onda
    return {"rect": pygame.Rect(WIDTH, altura_central, 30, 14), "altura_central": altura_central}


def nova_quilha():
    """Cria uma quilha numa altura que o surfista consegue alcançar."""
    y = random.randint(ONDA_TOPO_Y - 35, NIVEL_AGUA - 35)
    return pygame.Rect(WIDTH, y, 24, 30)


def x_da_onda(y):
    """Diz em qual x está a face do tsunami na altura y (interpolação linear na rampa)."""
    fracao = (y - ONDA_TOPO_Y) / (NIVEL_AGUA - ONDA_TOPO_Y)  # 0 no topo, 1 na água
    return ONDA_TOPO_X + (ONDA_BASE_X - ONDA_TOPO_X) * fracao


# ===== Funções de desenho =====
def desenha_predio(predio):
    """Desenha um prédio cinza com janelas acesas."""
    pygame.draw.rect(window, COR_PREDIO, predio)
    for jx in range(predio.left + 10, predio.right - 10, 20):
        for jy in range(predio.top + 10, NIVEL_AGUA - 12, 25):
            pygame.draw.rect(window, COR_JANELA, (jx, jy, 10, 12))


def desenha_poste(poste):
    """Desenha um poste com um braço e uma lâmpada acesa na ponta."""
    pygame.draw.rect(window, COR_POSTE, poste)
    pygame.draw.line(window, COR_POSTE, (poste.centerx, poste.top + 4), (poste.centerx - 22, poste.top + 4), 5)
    pygame.draw.circle(window, COR_JANELA, (poste.centerx - 22, poste.top + 10), 6)


def desenha_aviao(aviao):
    """Desenha um avião virado para a esquerda (bico à esquerda, cauda à direita)."""
    pygame.draw.ellipse(window, BRANCO, aviao)  # corpo
    asa = [(aviao.centerx - 5, aviao.centery),
           (aviao.centerx + 15, aviao.centery),
           (aviao.centerx + 5, aviao.bottom + 12)]
    pygame.draw.polygon(window, CINZA, asa)
    cauda = [(aviao.right - 15, aviao.centery),
             (aviao.right, aviao.centery),
             (aviao.right, aviao.top - 12)]
    pygame.draw.polygon(window, CINZA, cauda)
    for i in range(4):  # janelinhas
        pygame.draw.circle(window, (60, 120, 200), (aviao.left + 15 + i * 10, aviao.centery - 3), 3)


def desenha_peixe(peixe):
    """Desenha um peixe voador virado para a esquerda, com uma nadadeira grande que parece asa."""
    r = peixe["rect"]
    pygame.draw.ellipse(window, COR_PEIXE, r)                                     # corpo
    rabo = [(r.right - 4, r.centery), (r.right + 10, r.top - 4), (r.right + 10, r.bottom + 4)]
    pygame.draw.polygon(window, COR_PEIXE, rabo)
    asa = [(r.centerx - 4, r.centery), (r.centerx + 10, r.top - 10), (r.centerx + 8, r.centery)]
    pygame.draw.polygon(window, BRANCO, asa)                                      # "asa"
    pygame.draw.circle(window, PRETO, (r.left + 6, r.centery - 2), 2)             # olho


def desenha_quilha(quilha, tempo):
    """Desenha uma quilha dourada com brilho, balançando para cima e para baixo."""
    balanco = int(4 * math.sin(tempo / 8))  # só o desenho balança; a hitbox fica parada
    x = quilha.x
    y = quilha.y + balanco
    window.blit(BRILHO, (quilha.centerx - 25, quilha.centery - 25 + balanco))
    # Formato de quilha: base reta embaixo, frente curva subindo até a ponta lá atrás
    forma = [(x + 2, y + 30), (x + 4, y + 20), (x + 8, y + 12), (x + 14, y + 5), (x + 22, y),
             (x + 20, y + 8), (x + 19, y + 16), (x + 20, y + 24), (x + 24, y + 30)]
    pygame.draw.polygon(window, COR_QUILHA, forma)
    pygame.draw.polygon(window, BRANCO, forma, 2)  # contorno branco


def desenha_agua(deslocamento):
    """Desenha a água com ondinhas que andam para a esquerda (usando seno)."""
    pontos_onda = []
    for x in range(0, WIDTH + 10, 10):
        y = NIVEL_AGUA + 6 * math.sin((x + deslocamento) / 30)
        pontos_onda.append((x, y))
    pygame.draw.polygon(window, COR_AGUA, pontos_onda + [(WIDTH, HEIGHT), (0, HEIGHT)])
    pygame.draw.lines(window, COR_ESPUMA, False, pontos_onda, 3)  # espuma na superfície


def desenha_tsunami(tempo):
    """Desenha a onda gigante: a crista curvada em cima e a face onde o surfista desliza."""
    o = 5 * math.sin(tempo / 15)  # faz só a crista "respirar" (a face fica parada)
    forma = [(0, HEIGHT), (0, 90 + o), (60, 60 + o), (130, 55 + o), (190, 70 + o),
             (230, 95 + o), (240, 125 + o),                     # ponta da crista
             (215, 110 + o), (185, 105 + o), (160, 125 + o),    # parte de dentro do tubo
             (ONDA_TOPO_X, ONDA_TOPO_Y),                        # topo da face
             (ONDA_BASE_X, NIVEL_AGUA), (ONDA_BASE_X, HEIGHT)]  # base da face
    pygame.draw.polygon(window, COR_TSUNAMI, forma)
    # Espuma na crista
    for (x, y) in [(20, 85), (60, 62), (100, 55), (140, 58), (180, 68), (215, 85), (236, 112)]:
        pygame.draw.circle(window, COR_ESPUMA, (x, y + o), 9)
    # Linha de espuma descendo pela face
    pygame.draw.line(window, COR_ESPUMA, (ONDA_TOPO_X, ONDA_TOPO_Y), (ONDA_BASE_X, NIVEL_AGUA), 3)


def desenha_surfista(player, vel_y, subindo):
    """Desenha o surfista: de costas e virado para a esquerda quando sobe a onda,
    de frente (rosto visível) e virado para a direita quando desce."""
    if subindo:
        img = pygame.transform.flip(SURFISTA_COSTAS, True, False)  # espelha na horizontal
    else:
        img = SURFISTA_FRENTE
    # Quanto mais rápido, mais inclinado (no máximo 30 graus).
    angulo = min(30, abs(vel_y) * 4)
    img = pygame.transform.rotate(img, -angulo)
    window.blit(img, img.get_rect(center=player.center))


# ===== Imagens prontas =====
SURFISTA_FRENTE = cria_surfista_frente()
SURFISTA_COSTAS = cria_surfista_costas()
BRILHO = cria_brilho()
CIDADE_FUNDO = cria_cidade_fundo()

# ===== Estado do jogo =====
player = pygame.Rect(0, NIVEL_AGUA - 40, 40, 40)  # hitbox do surfista (o x é calculado pela onda)
player_y = player.y   # posição y "de verdade" (com casas decimais)
vel_y = 0
subindo = False       # True quando está subindo a onda (de costas)
predios = []
postes = []
avioes = []
peixes = []           # lista de dicionários {"rect": Rect, "altura_central": número}
quilhas = []
contador = 0          # conta frames até criar o próximo obstáculo
pontos = 0
quilhas_coletadas = 0
fundo_x = 0           # posição horizontal da cidade do fundo
tempo = 0             # conta frames desde o início (usado nas animações)
game_over = False


# ===== Loop principal =====
game = True
while game:
    clock.tick(FPS)
    tempo += 1

    # 1) Trata eventos (teclado, mouse, fechar a janela)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game = False
        # Apertar R depois de perder recomeça o jogo
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r and game_over:
            player_y = NIVEL_AGUA - player.height
            vel_y = 0
            predios = []
            postes = []
            avioes = []
            peixes = []
            quilhas = []
            contador = 0
            pontos = 0
            quilhas_coletadas = 0
            game_over = False

    # 2) Atualiza o estado do jogo (só enquanto não perdeu)
    if not game_over:
        # Dificuldade: quanto maior a distância, mais rápido e mais obstáculos
        velocidade = int(VEL_INICIAL + pontos / 900)
        intervalo = max(INTERVALO_MINIMO, INTERVALO_OBSTACULO - pontos // 120)

        # Segurando ESPAÇO, a velocidade vai para cima
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            vel_y += IMPULSO
        vel_y += GRAVIDADE  # a gravidade age sempre

        # Limita a velocidade
        if vel_y > VEL_MAXIMA:
            vel_y = VEL_MAXIMA
        if vel_y < -VEL_MAXIMA:
            vel_y = -VEL_MAXIMA

        # Move o surfista
        player_y += vel_y

        # Não deixa passar do topo da onda nem afundar na água
        if player_y < ONDA_TOPO_Y - player.height:
            player_y = ONDA_TOPO_Y - player.height
            vel_y = 0
        if player_y > NIVEL_AGUA - player.height + 5:
            player_y = NIVEL_AGUA - player.height + 5
            vel_y = 0
        player.y = int(player_y)
        # Encosta o surfista na face da onda: o x depende da altura dos pés (player.bottom)
        player.centerx = int(x_da_onda(player.bottom))

        # Subindo (vel_y < 0) = de costas; descendo (vel_y > 0) = de frente.
        # Se vel_y for 0 (parado no topo ou na água), continua como estava.
        if vel_y < 0:
            subindo = True
        if vel_y > 0:
            subindo = False

        # Cria um obstáculo quando o contador chega no intervalo (sorteia qual)
        contador += 1
        if contador >= intervalo:
            # Cada zona da onda tem seu obstáculo: avião em cima, peixe no meio,
            # prédio e poste embaixo. Repetir um nome na lista aumenta a chance dele.
            tipo = random.choice(["predio", "poste", "aviao", "aviao", "peixe", "peixe"])
            if tipo == "predio":
                predios.append(novo_predio())
            elif tipo == "poste":
                postes.append(novo_poste())
            elif tipo == "aviao":
                avioes.append(novo_aviao())
            else:
                peixes.append(novo_peixe())
            contador = 0
        # A quilha nasce na METADE do intervalo: sempre no meio do caminho entre dois
        # obstáculos. Como tudo anda na mesma velocidade, ela nunca fica dentro de um.
        if contador == intervalo // 2:
            quilhas.append(nova_quilha())

        # Move tudo para a esquerda na mesma velocidade
        for predio in predios:
            predio.x -= velocidade
        for poste in postes:
            poste.x -= velocidade
        for aviao in avioes:
            aviao.x -= velocidade
        for peixe in peixes:
            peixe["rect"].x -= velocidade
            # O peixe sobe e desce 30 pixels em volta da altura central (seno do x)
            peixe["rect"].y = int(peixe["altura_central"] + 30 * math.sin(peixe["rect"].x / 40))
        for quilha in quilhas:
            quilha.x -= velocidade

        # Remove o obstáculo mais antigo de cada lista quando ele sai da tela
        if len(predios) > 0 and predios[0].right < 0:
            predios.pop(0)
        if len(postes) > 0 and postes[0].right < 0:
            postes.pop(0)
        if len(avioes) > 0 and avioes[0].right < 0:
            avioes.pop(0)
        if len(peixes) > 0 and peixes[0]["rect"].right < 0:
            peixes.pop(0)

        # Quilhas: as que o surfista pegou somem e contam ponto; as que saíram da tela somem
        restantes = []
        for quilha in quilhas:
            if player.colliderect(quilha):
                som_quilha.play()
                quilhas_coletadas += 1
            elif quilha.right > 0:
                restantes.append(quilha)
        quilhas = restantes

        # Colisão: se encostar em qualquer obstáculo, perde
        for obs in predios + postes + avioes:
            if player.colliderect(obs):
                som_morte.play()
                game_over = True
        for peixe in peixes:
            if player.colliderect(peixe["rect"]):
                som_morte.play()
                game_over = True

        # Cidade do fundo anda devagar (parece estar longe)
        fundo_x -= 1
        if fundo_x <= -WIDTH:
            fundo_x = 0

        pontos += 1

    # 3) Desenha na tela (o que vem depois fica por cima)
    window.fill(COR_CEU)                                 # céu
    window.blit(CIDADE_FUNDO, (fundo_x, 0))              # cidade do fundo (2 cópias lado a lado,
    window.blit(CIDADE_FUNDO, (fundo_x + WIDTH, 0))      # para nunca aparecer um buraco)
    for predio in predios:
        desenha_predio(predio)
    for poste in postes:
        desenha_poste(poste)
    for aviao in avioes:
        desenha_aviao(aviao)
    for peixe in peixes:
        desenha_peixe(peixe)
    for quilha in quilhas:
        desenha_quilha(quilha, tempo)
    desenha_tsunami(tempo)                               # onda gigante (engole o que já passou)
    desenha_agua(tempo * 3)                              # água por cima da base dos prédios
    desenha_surfista(player, vel_y, subindo)

    texto_pontos = fonte.render(f"Distancia: {pontos // 10} m", True, BRANCO)
    window.blit(texto_pontos, (WIDTH - texto_pontos.get_width() - 10, 10))
    texto_quilhas = fonte.render(f"Quilhas: {quilhas_coletadas}", True, COR_QUILHA)
    window.blit(texto_quilhas, (WIDTH - texto_quilhas.get_width() - 10, 40))

    if game_over:
        texto_fim = fonte_grande.render("GAME OVER - aperte R", True, (255, 220, 0))
        window.blit(texto_fim, (WIDTH // 2 - texto_fim.get_width() // 2, HEIGHT // 2))

    pygame.display.update()

# ===== Finalização =====
pygame.quit()
