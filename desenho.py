"""Tudo o que aparece na tela: surfista, pranchas, obstáculos, onda, água, cenários
(céu, nuvens, cidade), partículas e pedaços da interface (textos, painéis, botões).
Nenhuma imagem externa é usada: tudo é feito com as formas do pygame.draw."""
import math
import random

import pygame

from config import *


# ===================== Ajudas de cor =====================
def escurece(cor, f=0.7):
    """Deixa a cor mais escura (f=0.7 -> 70% do brilho)."""
    return tuple(int(c * f) for c in cor[:3])


def clareia(cor, f=0.3):
    """Mistura a cor com branco (f=0.3 -> 30% mais clara)."""
    return tuple(int(c + (255 - c) * f) for c in cor[:3])


def mistura(a, b, t):
    """Cor no meio do caminho entre a e b (t=0 -> a, t=1 -> b)."""
    return tuple(int(x + (y - x) * t) for x, y in zip(a, b))


_brilhos = {}


def brilho(cor, raio):
    """Círculo de luz suave. Fica guardado num dicionário para não ser refeito todo frame."""
    if (cor, raio) not in _brilhos:
        img = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
        for k in range(6, 0, -1):
            camada = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
            pygame.draw.circle(camada, (*cor, 32), (raio, raio), raio * k // 6)
            img.blit(camada, (0, 0))
        _brilhos[(cor, raio)] = img
    return _brilhos[(cor, raio)]


# ===================== Interface =====================
def escreve(surf, msg, fonte, cor, pos, ancora="topleft", sombra=True):
    """Escreve um texto. 'ancora' diz qual ponto do texto fica em 'pos' (center, topright...)."""
    img = fonte.render(str(msg), True, cor)
    r = img.get_rect(**{ancora: pos})
    if sombra:
        surf.blit(fonte.render(str(msg), True, (10, 15, 30)), (r.x + 2, r.y + 2))
    surf.blit(img, r)
    return r


def painel(surf, rect, cor=(10, 25, 50), alpha=190, borda=None, raio=14):
    """Retângulo de cantos arredondados e meio transparente."""
    rect = pygame.Rect(rect)
    fundo = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(fundo, (*cor, alpha), fundo.get_rect(), border_radius=raio)
    surf.blit(fundo, rect.topleft)
    if borda:
        pygame.draw.rect(surf, borda, rect, 3, border_radius=raio)


def botao(surf, rect, msg, fonte, mouse, clique, cor=AZUL_UI, destaque=False):
    """Desenha um botão e devolve True se ele foi clicado neste frame."""
    rect = pygame.Rect(rect)
    em_cima = rect.collidepoint(mouse)
    pygame.draw.rect(surf, escurece(cor, 0.5), rect.move(0, 4), border_radius=12)  # sombra
    pygame.draw.rect(surf, clareia(cor, 0.2) if em_cima else cor, rect, border_radius=12)
    borda = DOURADO if destaque else (BRANCO if em_cima else clareia(cor, 0.35))
    pygame.draw.rect(surf, borda, rect, 3, border_radius=12)
    escreve(surf, msg, fonte, BRANCO, rect.center, "center")
    return em_cima and clique


def desenha_cadeado(surf, cx, cy):
    pygame.draw.arc(surf, CINZA, (cx - 10, cy - 22, 20, 24), 0, math.pi, 4)
    pygame.draw.rect(surf, DOURADO, (cx - 14, cy - 10, 28, 22), border_radius=4)
    pygame.draw.circle(surf, escurece(DOURADO, 0.4), (cx, cy), 3)


# ===================== Surfista e prancha =====================
def desenha_prancha(surf, prancha, r):
    """Desenha uma prancha (vista de lado) dentro do retângulo r."""
    pygame.draw.ellipse(surf, prancha["cor"], r)
    esp = max(1, r.height // 4)
    if prancha.get("raio"):  # zigue-zague de raio
        pts = [(r.left + r.width * f, r.centery + (r.height * 0.22 if i % 2 else -r.height * 0.22))
               for i, f in enumerate((0.12, 0.3, 0.45, 0.6, 0.75, 0.88))]
        pygame.draw.lines(surf, prancha["cor2"], False, pts, esp)
    else:
        pygame.draw.line(surf, prancha["cor2"], (r.left + r.width * 0.1, r.centery),
                         (r.right - r.width * 0.1, r.centery), esp)
    quilha = [(r.left + r.width * 0.12, r.bottom - 2), (r.left + r.width * 0.24, r.bottom - 2),
              (r.left + r.width * 0.14, r.bottom + r.height * 0.6)]
    pygame.draw.polygon(surf, (40, 40, 50), quilha)


def cria_surfista(p, prancha, costas=False, escala=1):
    """Desenha o surfista em cima da prancha numa imagem de (50 x 58) * escala.
    De frente vemos o rosto (olhos coloridos e sorriso); de costas vemos a nuca.
    Desenha no dobro do tamanho e depois reduz: assim as bordas ficam suaves."""
    e = escala * 2
    img = pygame.Surface((50 * e, 58 * e), pygame.SRCALPHA)

    def P(x, y):
        return (x * e, y * e)

    def R(x, y, w, h):
        return pygame.Rect(round(x * e), round(y * e), round(w * e), round(h * e))

    def linha(cor, a, b, w):
        pygame.draw.line(img, cor, P(*a), P(*b), max(1, round(w * e)))

    def bola(cor, centro, r):
        pygame.draw.circle(img, cor, P(*centro), max(1, r * e))

    pele, roupa, cabelo, estilo = p["pele"], p["roupa"], p["cabelo"], p["estilo"]
    mulher = p["genero"] == "mulher"

    desenha_prancha(img, prancha, R(0, 44, 50, 8))
    # Pernas (pele) com a bermuda por cima
    linha(pele, (15, 45), (19, 37), 3.4)
    linha(pele, (35, 45), (31, 37), 3.4)
    linha(roupa, (19, 38), (23, 29), 5.5)
    linha(roupa, (31, 38), (27, 29), 5.5)
    # Tronco: mulher de lycra, homem sem camisa
    linha(roupa if mulher else pele, (25, 31), (25, 17), 9)
    pygame.draw.rect(img, roupa, R(20.5, 27, 9, 5))
    # Braços abertos para equilibrar
    for lado in (-1, 1):
        ombro, cotovelo, mao = (25 + 3 * lado, 19), (25 + 12 * lado, 22), (25 + 20 * lado, 18)
        linha(pele, ombro, cotovelo, 3.2)
        linha(pele, cotovelo, mao, 3.2)
        bola(pele, mao, 1.9)
    linha(pele, (25, 17), (25, 14), 3.5)  # pescoço
    # Cabelo que fica atrás da cabeça
    if estilo == "comprido":
        pygame.draw.ellipse(img, cabelo, R(15.5, 3, 19, 21))
    elif estilo == "black":
        bola(cabelo, (25, 8.5), 11)
    if costas:
        bola(cabelo, (25, 10), 8)  # nuca
        if estilo == "curto":
            bola(pele, (17, 11), 2)  # orelhas
            bola(pele, (33, 11), 2)
    else:
        bola(pele, (25, 10), 8)  # rosto
        if estilo == "black":
            pygame.draw.ellipse(img, cabelo, R(15, -1, 20, 8))
        else:
            pygame.draw.ellipse(img, cabelo, R(16.5, 1, 17, 7.5))  # franja
        for ox in (22, 28):  # olhos: branco, íris colorida e pupila
            pygame.draw.ellipse(img, BRANCO, R(ox - 2.1, 8.4, 4.2, 3.2))
            bola(p["olhos"], (ox, 10), 1.35)
            bola(PRETO, (ox, 10), 0.6)
        pygame.draw.arc(img, (130, 40, 40), R(21.5, 10.5, 7, 5), math.pi, 2 * math.pi, max(1, e // 2))
    return pygame.transform.smoothscale(img, (50 * escala, 58 * escala))


_sprites = {}


def sprite(i_personagem, i_prancha, costas=False, escala=1):
    """Imagem do surfista já pronta (cada combinação é desenhada uma vez só)."""
    chave = (i_personagem, i_prancha, costas, escala)
    if chave not in _sprites:
        _sprites[chave] = cria_surfista(PERSONAGENS[i_personagem], PRANCHAS[i_prancha], costas, escala)
    return _sprites[chave]


# ===================== Quilha e obstáculos =====================
def desenha_quilha(surf, x, y, escala=1.0, com_brilho=True):
    """Quilha dourada (é a moeda do jogo)."""
    if com_brilho:
        surf.blit(brilho((255, 220, 60), 26), (x - 14, y - 11))
    forma = [(2, 30), (4, 20), (8, 12), (14, 5), (22, 0), (20, 8), (19, 16), (20, 24), (24, 30)]
    forma = [(x + a * escala, y + b * escala) for a, b in forma]
    pygame.draw.polygon(surf, DOURADO, forma)
    pygame.draw.polygon(surf, BRANCO, forma, 2)


def desenha_predio(surf, o, cen):
    """Prédio com lateral na sombra, beiral, janelas (algumas apagadas) e caixa d'água ou antena."""
    r, s = o["rect"], o["semente"]
    escura = escurece(cen["predio"], 0.7)
    pygame.draw.rect(surf, cen["predio"], r)
    pygame.draw.rect(surf, escura, (r.right - 10, r.top, 10, r.height))
    pygame.draw.rect(surf, escura, (r.left - 3, r.top - 6, r.width + 6, 8))
    if s % 3 == 0:
        pygame.draw.rect(surf, escura, (r.left + 8, r.top - 18, 16, 12))
    elif s % 3 == 1:
        pygame.draw.line(surf, escura, (r.centerx, r.top - 6), (r.centerx, r.top - 30), 2)
        if pygame.time.get_ticks() // 500 % 2:
            pygame.draw.circle(surf, (255, 60, 60), (r.centerx, r.top - 30), 3)
    cores = [cen["janela"], cen.get("janela2", cen["janela"])]
    for i, jx in enumerate(range(r.left + 8, r.right - 16, 16)):
        for j, jy in enumerate(range(r.top + 10, NIVEL_AGUA - 12, 22)):
            acesa = (s + i * 7 + j * 3) % 5 != 0
            pygame.draw.rect(surf, cores[(s + j) % 2] if acesa else escura, (jx, jy, 8, 11))


def desenha_poste(surf, o, cen):
    r = o["rect"]
    pygame.draw.rect(surf, cen["poste"], r)
    pygame.draw.line(surf, cen["poste"], (r.centerx, r.top + 4), (r.centerx - 24, r.top + 4), 5)
    surf.blit(brilho(cen["janela"], 22), (r.centerx - 46, r.top - 12))
    pygame.draw.circle(surf, cen["janela"], (r.centerx - 24, r.top + 10), 6)


def desenha_aviao(surf, o, cen):
    """Avião virado para a esquerda (bico à esquerda, cauda à direita)."""
    r = o["rect"]
    pygame.draw.polygon(surf, CINZA, [(r.right - 18, r.centery), (r.right, r.centery),
                                      (r.right + 2, r.top - 14), (r.right - 8, r.top - 14)])
    pygame.draw.ellipse(surf, BRANCO, r)
    pygame.draw.ellipse(surf, (205, 210, 220), (r.left + 4, r.centery + 2, r.width - 8, r.height // 2 - 2))
    pygame.draw.polygon(surf, CINZA, [(r.centerx - 8, r.centery + 2), (r.centerx + 16, r.centery + 2),
                                      (r.centerx + 6, r.bottom + 14)])
    for i in range(5):
        pygame.draw.circle(surf, (60, 120, 200), (r.left + 22 + i * 9, r.centery - 3), 2)
    pygame.draw.ellipse(surf, (40, 60, 90), (r.left + 5, r.top + 6, 10, 7))  # cabine
    if pygame.time.get_ticks() // 300 % 2:
        pygame.draw.circle(surf, (255, 60, 60), (r.right, r.top - 13), 3)


def desenha_peixe(surf, o, cen):
    """Peixe voador virado para a esquerda, com uma nadadeira grande que parece asa."""
    r = o["rect"]
    pygame.draw.polygon(surf, COR_PEIXE, [(r.right - 4, r.centery), (r.right + 10, r.top - 4), (r.right + 10, r.bottom + 4)])
    pygame.draw.ellipse(surf, COR_PEIXE, r)
    pygame.draw.ellipse(surf, clareia(COR_PEIXE, 0.5), (r.x + 4, r.centery, r.w - 10, r.h // 2 - 1))
    pygame.draw.polygon(surf, BRANCO, [(r.centerx - 4, r.centery), (r.centerx + 10, r.top - 10), (r.centerx + 8, r.centery)])
    pygame.draw.circle(surf, PRETO, (r.left + 6, r.centery - 2), 2)


DESENHOS = {"predio": desenha_predio, "poste": desenha_poste, "aviao": desenha_aviao, "peixe": desenha_peixe}


def desenha_obstaculo(surf, o, cen):
    DESENHOS[o["tipo"]](surf, o, cen)


# ===================== Onda e água =====================
def x_da_onda(y):
    """x da face do tsunami na altura y. A face é curva: deitada perto da água e
    em pé lá em cima (por isso o (1 - t) ** 2)."""
    t = (NIVEL_AGUA - y) / (NIVEL_AGUA - ONDA_TOPO_Y)  # 0 na água, 1 no topo
    t = max(0.0, min(1.0, t))
    return ONDA_BASE_X - (ONDA_BASE_X - ONDA_TOPO_X) * (1 - (1 - t) ** 2)


FACE = [(x_da_onda(y), y) for y in range(ONDA_TOPO_Y, NIVEL_AGUA + 1, 20)]  # do topo até a água
LABIO_FORA = [(0, 30), (50, 19), (110, 11), (175, 13), (235, 25), (280, 46), (308, 76), (318, 108)]
LABIO_DENTRO = [(298, 92), (272, 70), (240, 58), (205, 56), (178, 62), (160, 70)]  # parte de dentro do tubo


def desenha_onda(surf, tempo, cen, dx=0, dy=0):
    """Desenha o tsunami: corpo, faixas mais claras perto da face, correntes subindo,
    espuma na crista e água caindo da ponta. dx/dy deslocam a onda (usado na intro)."""
    o = 4 * math.sin(tempo / 15)  # a crista "respira"
    labio = [(x + dx, y + dy + o) for x, y in LABIO_FORA + LABIO_DENTRO]
    face = [(x + dx, y + dy) for x, y in FACE]
    pygame.draw.polygon(surf, cen["onda"], [(dx, HEIGHT + dy)] + labio + face + [(ONDA_BASE_X + dx, HEIGHT + dy)])
    # Perto da face a água é mais fina e a luz passa: faixas mais claras
    pygame.draw.polygon(surf, mistura(cen["onda"], cen["onda_clara"], 0.5), face + [(x - 80, y) for x, y in reversed(face)])
    pygame.draw.polygon(surf, cen["onda_clara"], face + [(x - 35, y) for x, y in reversed(face)])
    # Correntes de água subindo pela face
    corrente = clareia(cen["onda_clara"], 0.25)
    for i in range(10):
        k = (tempo * 0.006 + i / 10) % 1
        y = NIVEL_AGUA - 20 - k * (NIVEL_AGUA - ONDA_TOPO_Y - 60)
        recuo = 10 + (i % 3) * 18
        pygame.draw.line(surf, corrente, (x_da_onda(y) - recuo + dx, y + dy),
                         (x_da_onda(y - 22) - recuo + dx, y - 22 + dy), 2)
    # Espuma
    pygame.draw.lines(surf, cen["espuma"], False, face, 3)
    for i, (x, y) in enumerate(LABIO_FORA):
        pygame.draw.circle(surf, cen["espuma"], (x + dx, y + dy + o), 9 + 2 * math.sin(tempo / 6 + i))
    px, py = LABIO_FORA[-1]
    for k in range(6):  # cortina de água caindo da ponta da crista
        queda = (tempo * 2 + k * 11) % 70
        pygame.draw.circle(surf, cen["espuma"], (px - 4 + k * 1.5 + dx, py + o + queda + dy), max(1, 4 - queda / 20))


def desenha_espuma_base(surf, tempo, cen, dx=0, dy=0):
    """Espuma branca agitada onde a onda bate na água."""
    for x in range(-10, ONDA_BASE_X + 50, 16):
        y = NIVEL_AGUA + 4 + 3 * math.sin(tempo / 7 + x)
        pygame.draw.circle(surf, cen["espuma"], (x + dx, y + dy), 9 + 4 * math.sin(tempo / 5 + x * 0.7))


def desenha_agua(surf, tempo, cen):
    """Água com ondinhas andando para a esquerda (seno) e reflexos de luz."""
    pts = [(x, NIVEL_AGUA + 6 * math.sin((x + tempo * 3) / 30)) for x in range(0, WIDTH + 20, 20)]
    pygame.draw.polygon(surf, cen["agua"], pts + [(WIDTH, HEIGHT), (0, HEIGHT)])
    reflexo = clareia(cen["agua"], 0.25)
    for i in range(14):
        x = (i * 97 + tempo * 2) % (WIDTH + 60) - 30
        y = NIVEL_AGUA + 16 + (i * 23) % 42
        pygame.draw.line(surf, reflexo, (x, y), (x + 14 + (i % 3) * 6, y), 2)
    pygame.draw.lines(surf, cen["espuma"], False, pts, 3)


def desenha_chuva(surf, tempo):
    for i in range(80):
        x = (i * 61 + tempo * 7) % (WIDTH + 80) - 40
        y = (i * 113 + tempo * 15) % (HEIGHT + 40) - 20
        pygame.draw.line(surf, (185, 195, 215), (x, y), (x - 5, y + 13), 1)


# ===================== Cenário (fundo com parallax) =====================
TOPO_CAMADAS = 200  # as camadas de cidade começam nessa altura (economiza memória)


def cria_ceu(cen):
    """Céu em degradê + estrelas + sol ou lua com brilho."""
    img = pygame.Surface((WIDTH, HEIGHT))
    topo, baixo = cen["ceu"]
    for y in range(HEIGHT):
        img.fill(mistura(topo, baixo, min(1, y / NIVEL_AGUA)), (0, y, WIDTH, 1))
    rnd = random.Random(42)
    if cen.get("estrelas"):
        for _ in range(150):
            x, y = rnd.randrange(WIDTH), rnd.randrange(400)
            pygame.draw.circle(img, mistura(BRANCO, topo, y / 500), (x, y), rnd.choice((1, 1, 1, 2)))
    if cen["astro"]:
        x, y, raio = cen["astro_pos"]
        img.blit(brilho(cen["cor_astro"], raio * 3), (x - raio * 3, y - raio * 3))
        pygame.draw.circle(img, cen["cor_astro"], (x, y), raio)
        if cen["astro"] == "lua":
            for cx, cy, r in ((-10, -8, 7), (9, 6, 5), (-4, 12, 4)):
                pygame.draw.circle(img, escurece(cen["cor_astro"], 0.85), (x + cx, y + cy), r)
    return img


def cria_nuvens(cen, rnd):
    img = pygame.Surface((WIDTH, 260), pygame.SRCALPHA)
    for _ in range(10 if cen.get("chuva") else 5):
        cx, cy = rnd.randint(0, WIDTH), rnd.randint(30, 200)
        bolhas = [(rnd.randint(-55, 45), rnd.randint(-12, 10), rnd.randint(50, 110)) for _ in range(5)]
        for desloc in (0, -WIDTH, WIDTH):  # repete nas bordas para a nuvem não "cortar" ao dar a volta
            for bx, by, larg in bolhas:
                pygame.draw.ellipse(img, (*cen["nuvem"], 170), (cx + bx + desloc, cy + by, larg, larg // 2))
    return img


def cria_cidade(cor, alt_min, alt_max, rnd, janelas=()):
    """Silhueta de prédios para o fundo (começa em y = TOPO_CAMADAS)."""
    img = pygame.Surface((WIDTH, HEIGHT - TOPO_CAMADAS), pygame.SRCALPHA)
    base = NIVEL_AGUA - TOPO_CAMADAS + 10
    x = 0
    while x < WIDTH:
        larg, alt = rnd.randint(40, 95), rnd.randint(alt_min, alt_max)
        topo = base - 10 - alt
        pygame.draw.rect(img, cor, (x, topo, larg, alt + 70))
        if rnd.random() < 0.3:  # antena
            pygame.draw.line(img, cor, (x + larg // 2, topo), (x + larg // 2, topo - rnd.randint(10, 25)), 2)
        if janelas:
            for jx in range(x + 6, x + larg - 8, 12):
                for jy in range(topo + 8, base - 16, 16):
                    if rnd.random() < 0.35:
                        pygame.draw.rect(img, (*rnd.choice(janelas), 140), (jx, jy, 5, 7))
        x += larg + rnd.randint(0, 10)
    return img


def monta_visual(cen, semente):
    """Cria (uma vez só) as imagens de fundo de um cenário."""
    rnd = random.Random(semente)
    janelas = [cen["janela"], cen.get("janela2", cen["janela"])]
    return {"cen": cen,
            "ceu": cria_ceu(cen).convert(),
            "nuvens": cria_nuvens(cen, rnd).convert_alpha(),
            "longe": cria_cidade(cen["longe"], 130, 300, rnd).convert_alpha(),
            "meio": cria_cidade(cen["meio"], 70, 210, rnd, janelas).convert_alpha()}


def desenha_fundo(surf, vis, desloc, fator):
    """Céu parado + 3 camadas andando em velocidades diferentes (parallax).
    'desloc' guarda a posição de cada camada; 'fator' acelera tudo junto."""
    surf.blit(vis["ceu"], (0, 0))
    for camada, vel, y in (("nuvens", 0.25, 0), ("longe", 0.6, TOPO_CAMADAS), ("meio", 1.5, TOPO_CAMADAS)):
        desloc[camada] = (desloc[camada] - vel * fator) % WIDTH
        x = int(desloc[camada])
        surf.blit(vis[camada], (x - WIDTH, y))  # duas cópias lado a lado
        surf.blit(vis[camada], (x, y))          # para nunca aparecer buraco


def miniatura(vis):
    """Foto pequena do cenário para o menu."""
    img = vis["ceu"].copy()
    img.blit(vis["nuvens"], (0, 0))
    img.blit(vis["longe"], (0, TOPO_CAMADAS))
    img.blit(vis["meio"], (0, TOPO_CAMADAS))
    pygame.draw.rect(img, vis["cen"]["agua"], (0, NIVEL_AGUA, WIDTH, HEIGHT - NIVEL_AGUA))
    pygame.draw.line(img, vis["cen"]["espuma"], (0, NIVEL_AGUA), (WIDTH, NIVEL_AGUA), 5)
    if vis["cen"].get("chuva"):
        desenha_chuva(img, 0)
    return pygame.transform.smoothscale(img, (201, 115))


# ===================== Partículas =====================
def solta(lista, x, y, qtd, cor, vel=3.0, vida=30, raio=(2, 4), vx0=0.0, vy0=0.0):
    """Cria 'qtd' partículas (gotas de água, brilhos) saindo do ponto (x, y)."""
    for _ in range(qtd):
        ang = random.uniform(0, 2 * math.pi)
        v = random.uniform(0.3, 1.0) * vel
        lista.append({"x": x, "y": y, "vx": vx0 + math.cos(ang) * v, "vy": vy0 + math.sin(ang) * v,
                      "vida": vida, "max": vida, "r": random.uniform(*raio), "cor": cor})


def atualiza_particulas(surf, lista, mover=True):
    """Move (com gravidade), desenha e apaga as partículas que já acabaram."""
    for p in lista:
        if mover:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.15
            p["vida"] -= 1
        r = p["r"] * p["vida"] / p["max"]
        if r > 0.5:
            pygame.draw.circle(surf, p["cor"], (p["x"], p["y"]), r)
    lista[:] = [p for p in lista if p["vida"] > 0]
