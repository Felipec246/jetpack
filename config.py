"""Configurações do Tsunami Surf.

Aqui ficam os números que controlam o jogo (tela, física, dificuldade) e as listas
de personagens, pranchas e cenários. Mudando um valor aqui, o jogo inteiro muda junto.
"""
import os

# ===== Pastas e arquivos =====
PASTA = os.path.dirname(os.path.abspath(__file__))   # pasta onde está o jogo
ASSETS = os.path.join(PASTA, "assets")
ARQUIVO_SAVE = os.path.join(PASTA, "save.json")      # quilhas, pranchas e recordes

# ===== Tela =====
WIDTH, HEIGHT = 800, 600
FPS = 60

# ===== Física do surfista =====
GRAVIDADE = 0.5   # a cada frame puxa o surfista um pouco para baixo
IMPULSO = -1.0    # segurando ESPAÇO (negativo = para cima)
VEL_MAXIMA = 9    # velocidade vertical máxima

# ===== Onda =====
# A face do tsunami é uma curva: deitada perto da água e quase em pé lá em cima.
NIVEL_AGUA = HEIGHT - 60              # y da superfície da água
ONDA_TOPO_X, ONDA_TOPO_Y = 150, 80    # ponto mais alto da face
ONDA_BASE_X = 360                     # onde a face encontra a água
TOPO_PADRAO = 215                     # y mais alto que os pés alcançam com a prancha inicial

# ===== Dificuldade =====
VEL_INICIAL = 6          # velocidade dos obstáculos no começo (pixels por frame)
VEL_MAX_JOGO = 17        # velocidade máxima
ACELERACAO = 0.12        # quanto a velocidade sobe a cada segundo de jogo
DURACAO_FASE = 25        # segundos de cada fase (a cada fase os pontos valem +0.5x)
ESPACO_OBSTACULOS = 480  # distância (pixels) entre obstáculos na fase 1

# ===== Cores (R, G, B) =====
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
CINZA = (185, 190, 200)
DOURADO = (255, 200, 30)
VERDE = (60, 200, 110)
AZUL_UI = (30, 105, 185)
COR_PEIXE = (150, 190, 210)

# ===== Personagens =====
# estilo do cabelo: "curto", "comprido" ou "black"
PERSONAGENS = [
    {"nome": "Léo", "genero": "homem", "estilo": "curto",
     "pele": (243, 205, 175), "cabelo": (235, 195, 90), "olhos": (50, 120, 230), "roupa": (220, 50, 50)},
    {"nome": "Bia", "genero": "mulher", "estilo": "comprido",
     "pele": (245, 210, 185), "cabelo": (200, 85, 35), "olhos": (40, 160, 80), "roupa": (30, 170, 210)},
    {"nome": "Davi", "genero": "homem", "estilo": "curto",
     "pele": (198, 140, 95), "cabelo": (35, 25, 18), "olhos": (110, 65, 25), "roupa": (240, 130, 30)},
    {"nome": "Luna", "genero": "mulher", "estilo": "comprido",
     "pele": (192, 135, 92), "cabelo": (95, 55, 28), "olhos": (175, 120, 40), "roupa": (235, 80, 150)},
    {"nome": "Kaio", "genero": "homem", "estilo": "curto",
     "pele": (105, 66, 42), "cabelo": (18, 12, 8), "olhos": (55, 30, 15), "roupa": (250, 190, 30)},
    {"nome": "Nina", "genero": "mulher", "estilo": "black",
     "pele": (98, 60, 38), "cabelo": (25, 16, 10), "olhos": (90, 175, 165), "roupa": (140, 80, 220)},
]

# ===== Pranchas (loja) =====
# agilidade: multiplica a força para subir e a velocidade vertical
# altura: quantos pixels a mais o surfista consegue subir na onda
PRANCHAS = [
    {"nome": "Pranchinha", "preco": 0, "desc": "Para começar", "agilidade": 1.0, "altura": 0,
     "cor": (250, 205, 70), "cor2": (230, 90, 40)},
    {"nome": "Fish", "preco": 20, "desc": "Sobe e desce rápido", "agilidade": 1.15, "altura": 25,
     "cor": (70, 200, 225), "cor2": BRANCO},
    {"nome": "Longboard", "preco": 50, "desc": "Sobe bem mais alto", "agilidade": 1.1, "altura": 55,
     "cor": (235, 90, 80), "cor2": (255, 235, 200)},
    {"nome": "Gun", "preco": 100, "desc": "Rápida e alta", "agilidade": 1.3, "altura": 80,
     "cor": (150, 95, 235), "cor2": (255, 220, 80)},
    {"nome": "Relâmpago", "preco": 200, "desc": "A lendária!", "agilidade": 1.5, "altura": 110,
     "cor": (40, 40, 50), "cor2": (255, 215, 0), "raio": True},
]

# ===== Cenários =====
# req = pontuação (recorde) necessária para liberar o cenário
CENARIOS = [
    {"nome": "Cidade", "req": 0,
     "ceu": ((80, 150, 220), (190, 225, 245)), "nuvem": (255, 255, 255),
     "longe": (150, 175, 205), "meio": (115, 135, 165), "predio": (90, 95, 115),
     "janela": (250, 230, 140), "poste": (50, 50, 60),
     "agua": (25, 115, 175), "onda": (18, 90, 155), "onda_clara": (45, 140, 200), "espuma": (235, 245, 255),
     "astro": "sol", "astro_pos": (650, 90, 38), "cor_astro": (255, 245, 180)},
    {"nome": "Pôr do Sol", "req": 1500,
     "ceu": ((70, 45, 125), (255, 160, 95)), "nuvem": (255, 175, 150),
     "longe": (150, 85, 115), "meio": (105, 60, 95), "predio": (70, 45, 75),
     "janela": (255, 205, 110), "poste": (45, 30, 50),
     "agua": (70, 70, 140), "onda": (50, 50, 120), "onda_clara": (110, 95, 175), "espuma": (255, 225, 215),
     "astro": "sol", "astro_pos": (560, 330, 60), "cor_astro": (255, 200, 90)},
    {"nome": "Noite Neon", "req": 4000,
     "ceu": ((5, 5, 25), (45, 25, 85)), "nuvem": (60, 50, 100),
     "longe": (35, 30, 70), "meio": (25, 22, 55), "predio": (30, 26, 58),
     "janela": (0, 255, 220), "janela2": (255, 60, 200), "poste": (20, 20, 35),
     "agua": (20, 30, 85), "onda": (15, 25, 75), "onda_clara": (70, 45, 150), "espuma": (170, 220, 255),
     "astro": "lua", "astro_pos": (640, 90, 32), "cor_astro": (235, 235, 255), "estrelas": True},
    {"nome": "Tempestade", "req": 8000,
     "ceu": ((40, 45, 55), (115, 125, 130)), "nuvem": (75, 80, 90),
     "longe": (95, 105, 110), "meio": (70, 78, 85), "predio": (58, 64, 72),
     "janela": (240, 240, 180), "poste": (35, 38, 42),
     "agua": (45, 80, 90), "onda": (32, 62, 72), "onda_clara": (70, 105, 115), "espuma": (225, 235, 235),
     "astro": None, "chuva": True},
]
