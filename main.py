"""Tsunami Surf - jogo em Pygame para a disciplina Design de Software (Insper).

O jogo tem três telas, cada uma é uma função com o seu próprio loop:
    tela_menu()  -> lobby: nome, personagem, loja de pranchas, cenários e recordes
    tela_intro() -> a cidade tranquila... e chega o tsunami!
    tela_jogo()  -> surfa até bater em alguma coisa
Cada função devolve o nome da próxima tela ("menu", "intro", "jogo" ou "sair").
"""
import math
import os
import random

import pygame

import save
import sons
from config import *
from desenho import *

# ===== Inicialização =====
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tsunami Surf")
clock = pygame.time.Clock()
# Tudo é desenhado nesta superfície e depois copiado para a janela.
# Assim dá para "tremer" a tela inteira só mudando onde ela é copiada.
tela = pygame.Surface((WIDTH, HEIGHT))

F_PEQ = pygame.font.Font(None, 24)
F_MED = pygame.font.Font(None, 32)
F_GRA = pygame.font.Font(None, 48)
F_ENORME = pygame.font.Font(None, 80)
F_TITULO = pygame.font.Font(None, 104)

# Na primeira vez o jogo cria a música do menu e os efeitos (demora uns segundos)
window.fill((10, 30, 60))
escreve(window, "Preparando as ondas...", F_MED, BRANCO, (WIDTH // 2, HEIGHT // 2), "center")
pygame.display.flip()
sons.gera_sons(ASSETS)


# ===== Sons =====
class SemSom:
    """Usado quando o computador não tem saída de áudio: play() não faz nada."""
    def play(self):
        pass


def carrega_som(arquivo, volume):
    try:
        som = pygame.mixer.Sound(os.path.join(ASSETS, arquivo))
        som.set_volume(volume)
        return som
    except (pygame.error, FileNotFoundError):
        return SemSom()


SOM_QUILHA = carrega_som("coletavel.mp3.mp3", 0.7)
SOM_MORTE = carrega_som("morte.mp3.mp3", 0.8)
SOM_FASE = carrega_som("fase.wav", 0.6)
SOM_COMPRA = carrega_som("compra.wav", 0.6)
SOM_ERRO = carrega_som("erro.wav", 0.5)
SOM_TROVAO = carrega_som("trovao.wav", 0.8)
musica_atual = None


def toca_musica(arquivo, volume):
    """Troca a música de fundo (se já estiver tocando essa, só ajusta o volume)."""
    global musica_atual
    try:
        if arquivo != musica_atual:
            pygame.mixer.music.load(os.path.join(ASSETS, arquivo))
            pygame.mixer.music.play(-1, fade_ms=800)
            musica_atual = arquivo
        pygame.mixer.music.set_volume(volume)
    except pygame.error:
        pass


# ===== Dados e imagens prontas =====
dados = save.carrega()
VISUAIS = [monta_visual(c, i) for i, c in enumerate(CENARIOS)]
MINIATURAS = [miniatura(v) for v in VISUAIS]
fundo = {"nuvens": 0.0, "longe": 0.0, "meio": 0.0}  # posição de cada camada do fundo
AREA = pygame.Rect(300, 100, 480, 480)              # painel da direita do menu


def mostra(tremor=0):
    """Copia a tela para a janela (com um deslocamento aleatório se estiver tremendo)."""
    tremor = int(tremor)
    window.fill(PRETO)
    window.blit(tela, (random.randint(-tremor, tremor), random.randint(-tremor, tremor)))
    pygame.display.flip()


def formata_tempo(segundos):
    segundos = int(segundos)
    return f"{segundos // 60}:{segundos % 60:02d}"


def escreve_transparente(msg, fonte, cor, centro, alpha):
    img = fonte.render(msg, True, cor)
    img.set_alpha(max(0, min(255, int(alpha))))
    tela.blit(img, img.get_rect(center=centro))


# =====================================================================
# ============================== MENU =================================
# =====================================================================
letras_titulo = []


def desenha_titulo(t):
    """'TSUNAMI SURF' com as letras balançando como uma onda."""
    if not letras_titulo:
        for letra in "TSUNAMI SURF":
            letras_titulo.append((F_TITULO.render(letra, True, (10, 40, 90)),
                                  F_TITULO.render(letra, True, (60, 190, 255)),
                                  F_TITULO.render(letra, True, BRANCO)))
    x = WIDTH // 2 - sum(l[2].get_width() for l in letras_titulo) // 2
    for i, (sombra, cor, img) in enumerate(letras_titulo):
        y = 14 + 5 * math.sin(t / 12 + i * 0.6)
        tela.blit(sombra, (x + 5, y + 6))
        tela.blit(cor, (x + 2, y + 3))
        tela.blit(img, (x, y))
        x += img.get_width()


def painel_inicio(t):
    escreve(tela, "COMO JOGAR", F_GRA, DOURADO, (AREA.centerx, AREA.y + 32), "center")
    img = sprite(dados["personagem"], dados["prancha"], False, 3)
    tela.blit(img, img.get_rect(center=(AREA.x + 95, AREA.y + 215 + 6 * math.sin(t / 20))))
    escreve(tela, PERSONAGENS[dados["personagem"]]["nome"], F_MED, BRANCO, (AREA.x + 95, AREA.y + 320), "center")
    escreve(tela, PRANCHAS[dados["prancha"]]["nome"], F_PEQ, CINZA, (AREA.x + 95, AREA.y + 345), "center")
    dicas = [("Segure ESPAÇO (ou o mouse)", BRANCO), ("para subir na onda", CINZA),
             ("Desvie dos obstáculos:", BRANCO), ("prédios, postes, peixes, aviões", CINZA),
             ("Pegue as QUILHAS douradas", DOURADO), ("e compre pranchas na loja", CINZA),
             ("A cada fase fica mais rápido", BRANCO), ("e os pontos multiplicam!", CINZA),
             ("Recordes liberam cenários", BRANCO), ("P = pausa", CINZA)]
    for i, (texto, cor) in enumerate(dicas):
        escreve(tela, texto, F_PEQ, cor, (AREA.x + 185, AREA.y + 78 + i * 28))


def painel_personagem(mouse, clique):
    escreve(tela, "ESCOLHA SEU SURFISTA", F_GRA, DOURADO, (AREA.centerx, AREA.y + 32), "center")
    for i, p in enumerate(PERSONAGENS):
        card = pygame.Rect(AREA.x + 15 + (i % 3) * 152, AREA.y + 62 + (i // 3) * 205, 142, 195)
        em_cima = card.collidepoint(mouse)
        painel(tela, card, cor=(30, 60, 100) if em_cima else (20, 45, 80), alpha=230,
               borda=DOURADO if dados["personagem"] == i else None, raio=10)
        img = sprite(i, dados["prancha"], False, 2)
        tela.blit(img, img.get_rect(midtop=(card.centerx, card.y + 8)))
        escreve(tela, p["nome"], F_MED, BRANCO, (card.centerx, card.y + 137), "center")
        escreve(tela, p["desc"][0], F_PEQ, CINZA, (card.centerx, card.y + 160), "center")
        escreve(tela, p["desc"][1], F_PEQ, CINZA, (card.centerx, card.y + 179), "center")
        if em_cima and clique:
            dados["personagem"] = i
            save.salva(dados)


def painel_pranchas(mouse, clique):
    """Loja: compra com quilhas e equipa pranchas. Devolve uma mensagem (ou None)."""
    escreve(tela, "LOJA DE PRANCHAS", F_GRA, DOURADO, (AREA.centerx, AREA.y + 32), "center")
    msg = None
    for i, pr in enumerate(PRANCHAS):
        linha = pygame.Rect(AREA.x + 12, AREA.y + 62 + i * 82, AREA.w - 24, 74)
        equipada = dados["prancha"] == i
        painel(tela, linha, cor=(20, 45, 80), alpha=220, borda=DOURADO if equipada else None, raio=10)
        desenha_prancha(tela, pr, pygame.Rect(linha.x + 12, linha.y + 28, 110, 16))
        escreve(tela, pr["nome"], F_MED, BRANCO, (linha.x + 135, linha.y + 8))
        escreve(tela, pr["desc"], F_PEQ, CINZA, (linha.x + 135, linha.y + 33))
        barras = (("VEL", (pr["agilidade"] - 0.8) / 0.7), ("ALT", (pr["altura"] + 25) / 135))
        for j, (rotulo, valor) in enumerate(barras):
            bx = linha.x + 135 + j * 95
            escreve(tela, rotulo, F_PEQ, CINZA, (bx, linha.y + 52), sombra=False)
            pygame.draw.rect(tela, (40, 55, 80), (bx + 36, linha.y + 56, 50, 8), border_radius=4)
            pygame.draw.rect(tela, VERDE, (bx + 36, linha.y + 56, int(50 * valor), 8), border_radius=4)
        bt = pygame.Rect(linha.right - 128, linha.y + 17, 116, 40)
        if equipada:
            pygame.draw.rect(tela, (40, 150, 80), bt, border_radius=12)
            escreve(tela, "EQUIPADA", F_PEQ, BRANCO, bt.center, "center")
        elif i in dados["pranchas"]:
            if botao(tela, bt, "EQUIPAR", F_MED, mouse, clique):
                dados["prancha"] = i
                save.salva(dados)
        else:
            pode = dados["quilhas"] >= pr["preco"]
            if botao(tela, bt, f"    {pr['preco']}", F_MED, mouse, clique, cor=(190, 140, 20) if pode else (95, 85, 70)):
                if pode:
                    dados["quilhas"] -= pr["preco"]
                    dados["pranchas"].append(i)
                    dados["prancha"] = i
                    save.salva(dados)
                    SOM_COMPRA.play()
                    msg = f"Você comprou a {pr['nome']}!"
                else:
                    SOM_ERRO.play()
                    msg = f"Faltam {pr['preco'] - dados['quilhas']} quilhas!"
            desenha_quilha(tela, bt.x + 16, bt.y + 9, escala=0.75, com_brilho=False)
    return msg


def painel_cenarios(mouse, clique):
    melhor = save.melhor_pontuacao(dados)
    escreve(tela, "CENÁRIOS", F_GRA, DOURADO, (AREA.centerx, AREA.y + 32), "center")
    escreve(tela, f"Melhor pontuação: {melhor}", F_PEQ, CINZA, (AREA.centerx, AREA.y + 62), "center")
    msg = None
    for i, cen in enumerate(CENARIOS):
        card = pygame.Rect(AREA.x + 20 + (i % 2) * 225, AREA.y + 82 + (i // 2) * 195, 215, 185)
        liberado = melhor >= cen["req"]
        escolhido = dados["cenario"] == i
        em_cima = card.collidepoint(mouse)
        painel(tela, card, cor=(30, 60, 100) if em_cima else (20, 45, 80), alpha=230,
               borda=DOURADO if escolhido else None, raio=10)
        foto = pygame.Rect(card.x + 7, card.y + 7, 201, 115)
        tela.blit(MINIATURAS[i], foto)
        if not liberado:
            sombra = pygame.Surface(foto.size, pygame.SRCALPHA)
            sombra.fill((0, 0, 0, 160))
            tela.blit(sombra, foto)
            desenha_cadeado(tela, foto.centerx, foto.centery)
        escreve(tela, cen["nome"], F_MED, BRANCO, (card.centerx, card.y + 142), "center")
        if escolhido:
            status, cor = "SELECIONADO", DOURADO
        elif liberado:
            status, cor = "clique para usar", VERDE
        else:
            status, cor = f"faça {cen['req']} pontos", (255, 130, 110)
        escreve(tela, status, F_PEQ, cor, (card.centerx, card.y + 167), "center")
        if em_cima and clique:
            if liberado:
                dados["cenario"] = i
                save.salva(dados)
            else:
                SOM_ERRO.play()
                msg = f"Faça {cen['req']} pontos para liberar: {cen['nome']}"
    return msg


def painel_recordes():
    escreve(tela, "RECORDES", F_GRA, DOURADO, (AREA.centerx, AREA.y + 32), "center")
    lista = dados["recordes"][:8]
    if not lista:
        escreve(tela, "Ninguém surfou ainda...", F_MED, BRANCO, AREA.center, "center")
        escreve(tela, "Seja o primeiro!", F_MED, DOURADO, (AREA.centerx, AREA.centery + 35), "center")
        return
    y0 = AREA.y + 70
    for texto, x, ancora in (("#", 30, "topleft"), ("NOME", 70, "topleft"),
                             ("PONTOS", 330, "topright"), ("TEMPO", 440, "topright")):
        escreve(tela, texto, F_PEQ, CINZA, (AREA.x + x, y0), ancora)
    medalhas = [DOURADO, (210, 210, 225), (210, 130, 60)]  # ouro, prata, bronze
    for i, r in enumerate(lista):
        y = y0 + 32 + i * 42
        if r["nome"].lower() == dados["nome"].lower():  # destaca o jogador atual
            painel(tela, (AREA.x + 15, y - 8, AREA.w - 30, 38), cor=(60, 120, 200), alpha=90, raio=8)
        cor = medalhas[i] if i < 3 else BRANCO
        escreve(tela, i + 1, F_MED, cor, (AREA.x + 30, y))
        escreve(tela, r["nome"], F_MED, cor, (AREA.x + 70, y))
        escreve(tela, r["pontos"], F_MED, cor, (AREA.x + 330, y), "topright")
        escreve(tela, formata_tempo(r.get("tempo", 0)), F_MED, cor, (AREA.x + 440, y), "topright")
    proximos = [c for c in CENARIOS if c["req"] > save.melhor_pontuacao(dados)]
    if proximos:
        escreve(tela, f"Próximo cenário: {proximos[0]['nome']} com {proximos[0]['req']} pontos",
                F_PEQ, CINZA, (AREA.centerx, AREA.bottom - 25), "center")


def tela_menu():
    toca_musica("menu.wav", 0.5)
    aba = "inicio"
    editando = dados["nome"] == ""  # caixa do nome recebendo letras
    aviso, aviso_t = "", 0
    t = 0
    while True:
        clock.tick(FPS)
        t += 1
        mouse = pygame.mouse.get_pos()
        clique = jogar = False
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                save.salva(dados)
                return "sair"
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                clique = True
            elif editando and ev.type == pygame.TEXTINPUT:
                dados["nome"] = (dados["nome"] + ev.text)[:12]
            elif ev.type == pygame.KEYDOWN:
                if editando:
                    if ev.key == pygame.K_BACKSPACE:
                        dados["nome"] = dados["nome"][:-1]
                    elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        dados["nome"] = dados["nome"].strip()
                        editando = dados["nome"] == ""
                        save.salva(dados)
                elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    jogar = True
                elif ev.key == pygame.K_ESCAPE:
                    aba = "inicio"

        vis = VISUAIS[dados["cenario"]]
        desenha_fundo(tela, vis, fundo, 0.5)
        desenha_agua(tela, t, vis["cen"])
        desenha_titulo(t)

        # ----- Coluna da esquerda: nome, botões e quilhas
        painel(tela, (20, 100, 260, 480))
        escreve(tela, "JOGADOR", F_PEQ, CINZA, (38, 112))
        caixa = pygame.Rect(35, 132, 230, 40)
        if clique:
            if caixa.collidepoint(mouse):
                editando = True
            elif editando and dados["nome"].strip():
                dados["nome"] = dados["nome"].strip()
                editando = False
                save.salva(dados)
        pygame.draw.rect(tela, BRANCO if editando else (210, 220, 235), caixa, border_radius=8)
        pygame.draw.rect(tela, DOURADO if editando else AZUL_UI, caixa, 3, border_radius=8)
        if dados["nome"]:
            cursor = "|" if editando and t // 30 % 2 == 0 else ""
            escreve(tela, dados["nome"] + cursor, F_MED, (20, 30, 60), (caixa.x + 10, caixa.centery), "midleft", False)
        else:
            escreve(tela, "Digite seu nome", F_MED, (140, 140, 160), (caixa.x + 10, caixa.centery), "midleft", False)

        if botao(tela, (35, 185, 230, 56), "JOGAR", F_GRA, mouse, clique, cor=(40, 165, 90)):
            jogar = True
        abas = [("PERSONAGEM", "personagem"), ("PRANCHAS", "pranchas"), ("CENÁRIOS", "cenarios"),
                ("RECORDES", "recordes"), ("COMO JOGAR", "inicio")]
        for i, (rotulo, nome_aba) in enumerate(abas):
            if botao(tela, (35, 255 + i * 52, 230, 44), rotulo, F_MED, mouse, clique, destaque=aba == nome_aba):
                aba = nome_aba
        desenha_quilha(tela, 42, 527, escala=0.9, com_brilho=False)
        escreve(tela, f"{dados['quilhas']} quilhas", F_MED, DOURADO, (75, 541), "midleft")

        # ----- Painel da direita (muda conforme a aba)
        painel(tela, AREA)
        msg = None
        if aba == "inicio":
            painel_inicio(t)
        elif aba == "personagem":
            painel_personagem(mouse, clique)
        elif aba == "pranchas":
            msg = painel_pranchas(mouse, clique)
        elif aba == "cenarios":
            msg = painel_cenarios(mouse, clique)
        else:
            painel_recordes()
        if msg:
            aviso, aviso_t = msg, 150

        if jogar:
            if dados["nome"].strip():
                dados["nome"] = dados["nome"].strip()
                save.salva(dados)
                return "intro"
            editando = True
            aviso, aviso_t = "Digite seu nome antes de jogar!", 150
            SOM_ERRO.play()

        if aviso_t > 0:  # mensagem rápida embaixo da tela
            aviso_t -= 1
            caixa_aviso = pygame.Rect(0, 0, 460, 42)
            caixa_aviso.center = (AREA.centerx, HEIGHT - 45)
            painel(tela, caixa_aviso, cor=(0, 0, 0), alpha=210, borda=DOURADO, raio=10)
            escreve(tela, aviso, F_PEQ, BRANCO, caixa_aviso.center, "center")
        mostra()


# =====================================================================
# ============================== INTRO ================================
# =====================================================================
def tela_intro():
    """Cena de abertura: cidade tranquila, alerta, o tsunami subindo e levando o surfista."""
    toca_musica("musica.mp3.mp3", 0.4)
    vis = VISUAIS[dados["cenario"]]
    cen = vis["cen"]
    frente = sprite(dados["personagem"], dados["prancha"])
    costas = pygame.transform.flip(sprite(dados["personagem"], dados["prancha"], True), True, False)
    particulas = []
    DURACAO = 300
    for f in range(DURACAO):
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                save.salva(dados)
                return "sair"
            if ev.type == pygame.MOUSEBUTTONDOWN or (
                    ev.type == pygame.KEYDOWN and ev.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE)):
                return "jogo"
        if f == 85:
            SOM_TROVAO.play()

        # A onda sobe (de baixo e da esquerda) entre os frames 90 e 210, freando no final
        k = min(1.0, max(0.0, (f - 90) / 120))
        k = 1 - (1 - k) ** 3
        dx, dy = -520 * (1 - k), 330 * (1 - k)
        tremor = 7 * math.sin(math.pi * (f - 85) / 145) if 85 <= f < 230 else 0

        # Surfista: boiando -> rema até a onda -> a onda leva ele para cima e ele desce
        if f < 200:
            x, pes, img, ang = 470, NIVEL_AGUA + 4 + 2 * math.sin(f / 10), frente, 0
        elif f < 240:
            x, pes, img, ang = 470 - 110 * (f - 200) / 40, NIVEL_AGUA + 4, costas, 0
        else:
            k2 = (f - 240) / (DURACAO - 240)
            pes = NIVEL_AGUA + 5 - 170 * math.sin(math.pi * k2)
            x = x_da_onda(pes)
            img = costas if k2 < 0.5 else frente
            ang = 22 * abs(math.cos(math.pi * k2))
            solta(particulas, x - 12, pes - 2, 2, cen["espuma"], vel=1.2, vida=22, raio=(1.5, 3.5), vx0=-2, vy0=-1.5)

        desenha_fundo(tela, vis, fundo, 0.4 if f < 240 else 1.0)
        desenha_onda(tela, f, cen, dx, dy)
        desenha_agua(tela, f, cen)
        desenha_espuma_base(tela, f, cen, dx, dy)
        girado = pygame.transform.rotozoom(img, -ang, 1)
        tela.blit(girado, girado.get_rect(center=(x, pes - 26)))
        atualiza_particulas(tela, particulas)
        if cen.get("chuva"):
            desenha_chuva(tela, f)

        if 15 <= f < 95:
            escreve_transparente("Mais um dia tranquilo na cidade...", F_GRA, BRANCO, (WIDTH // 2, 200),
                                 255 * min(1, (f - 15) / 20, (95 - f) / 20))
        elif 95 <= f < 205:
            if f // 10 % 2 == 0:
                escreve(tela, "ALERTA DE TSUNAMI!", F_ENORME, (255, 70, 60), (WIDTH // 2, 200), "center")
        elif f < 265:
            escreve(tela, "Segure ESPAÇO para surfar!", F_GRA, DOURADO, (WIDTH // 2, 200), "center")
        else:
            escreve(tela, "VAI!", F_ENORME, BRANCO, (WIDTH // 2, 200), "center")
        escreve(tela, "ESPAÇO pula a intro", F_PEQ, CINZA, (WIDTH - 12, HEIGHT - 12), "bottomright")
        mostra(tremor)
    return "jogo"


# =====================================================================
# ============================== JOGO =================================
# =====================================================================
def novo_obstaculo(tipo, topo_pes, fase):
    """Cria um obstáculo na borda direita. Cada tipo fica numa parte da onda:
    avião em cima, peixe no meio, prédio e poste embaixo."""
    if tipo == "predio":
        topo = NIVEL_AGUA - random.randint(80, 190)
        rect = pygame.Rect(WIDTH, topo, random.randint(55, 85), HEIGHT - topo)
    elif tipo == "poste":
        topo = NIVEL_AGUA - random.randint(100, 180)
        rect = pygame.Rect(WIDTH, topo, 14, HEIGHT - topo)
    elif tipo == "aviao":  # pode aparecer até no ponto mais alto que a prancha alcança
        rect = pygame.Rect(WIDTH, random.randint(topo_pes - 45, 230), 80, 26)
    else:  # peixe: sobe e desce em volta de uma altura central
        rect = pygame.Rect(WIDTH, 0, 30, 14)
    return {"tipo": tipo, "rect": rect, "x": float(WIDTH), "semente": random.randint(0, 999),
            "centro": random.randint(250, 380), "amp": min(60, 30 + 8 * (fase - 1))}


def termina_partida(pontos, segundos, pegas, fase):
    """Guarda quilhas e recorde. Devolve um dicionário com o resultado da partida."""
    antes = save.melhor_pontuacao(dados)
    dados["quilhas"] += pegas
    pessoal = save.registra_recorde(dados, dados["nome"] or "Surfista", int(pontos), int(segundos))
    liberados = [c["nome"] for c in CENARIOS if antes < c["req"] <= int(pontos)]
    save.salva(dados)
    return {"pontos": int(pontos), "segundos": int(segundos), "pegas": pegas, "fase": fase,
            "recorde": int(pontos) > antes, "pessoal": pessoal, "liberados": liberados,
            "espera": 45, "giro": 0, "queda": 0}


def desenha_hud(pontos, pegas, fase, segundos, recorde, t):
    mult = 1 + 0.5 * (fase - 1)
    # Pontos e quilhas (direita)
    escreve(tela, "PONTOS", F_PEQ, CINZA, (WIDTH - 15, 10), "topright")
    escreve(tela, int(pontos), F_GRA, BRANCO, (WIDTH - 15, 28), "topright")
    if pontos > recorde > 0:
        if t // 15 % 2:
            escreve(tela, "NOVO RECORDE!", F_PEQ, DOURADO, (WIDTH - 15, 66), "topright")
    else:
        escreve(tela, f"RECORDE {recorde}", F_PEQ, CINZA, (WIDTH - 15, 66), "topright")
    desenha_quilha(tela, WIDTH - 95, 90, escala=0.8, com_brilho=False)
    escreve(tela, f"x {pegas}", F_MED, DOURADO, (WIDTH - 15, 96), "topright")
    # Fase, multiplicador e barra até a próxima fase (centro)
    caixa = pygame.Rect(WIDTH // 2 - 90, 10, 180, 50)
    painel(tela, caixa, alpha=150, raio=12)
    escreve(tela, f"FASE {fase}", F_MED, BRANCO, (caixa.x + 12, caixa.y + 8))
    escreve(tela, f"x{mult:g}", F_MED, DOURADO, (caixa.right - 12, caixa.y + 8), "topright")
    barra = pygame.Rect(caixa.x + 12, caixa.y + 34, 156, 7)
    pygame.draw.rect(tela, (40, 50, 70), barra, border_radius=4)
    progresso = (segundos % DURACAO_FASE) / DURACAO_FASE
    pygame.draw.rect(tela, DOURADO, (barra.x, barra.y, int(barra.w * progresso), barra.h), border_radius=4)
    escreve(tela, formata_tempo(segundos), F_PEQ, CINZA, (caixa.centerx, caixa.bottom + 12), "center")


def tela_jogo():
    """Uma partida. Devolve "jogo" (jogar de novo), "menu" ou "sair"."""
    toca_musica("musica.mp3.mp3", 0.4)
    vis = VISUAIS[dados["cenario"]]
    cen = vis["cen"]
    prancha = PRANCHAS[dados["prancha"]]
    agilidade = prancha["agilidade"]
    topo_pes = TOPO_PADRAO - prancha["altura"]  # pranchas melhores sobem mais na onda
    frente = sprite(dados["personagem"], dados["prancha"])
    costas = pygame.transform.flip(sprite(dados["personagem"], dados["prancha"], True), True, False)
    recorde = save.melhor_pontuacao(dados)

    player = pygame.Rect(0, 0, 40, 40)         # hitbox (o x é calculado pela onda)
    player_y = NIVEL_AGUA - player.height + 5  # y "de verdade" (com casas decimais)
    vel_y = angulo = 0.0
    subindo = False
    obstaculos, quilhas, particulas, textos = [], [], [], []
    contador, quilha_feita = 0, False
    frames = t = 0         # frames jogados / relógio das animações
    pontos, pegas, fase = 0.0, 0, 1
    velocidade = VEL_INICIAL
    banner = tremor = flash = 0
    pausado = False
    fim = None             # vira um dicionário com o resultado quando o surfista cai

    while True:
        clock.tick(FPS)
        mouse = pygame.mouse.get_pos()
        clique = False
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                save.salva(dados)
                return "sair"
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                clique = True
            if ev.type == pygame.KEYDOWN:
                if fim:
                    if fim["espera"] <= 0 and ev.key in (pygame.K_r, pygame.K_RETURN):
                        return "jogo"
                    if fim["espera"] <= 0 and ev.key in (pygame.K_m, pygame.K_ESCAPE):
                        return "menu"
                elif ev.key in (pygame.K_p, pygame.K_ESCAPE):
                    pausado = not pausado
                elif pausado and ev.key == pygame.K_m:
                    return "menu"

        segundos = frames / FPS
        mult = 1 + 0.5 * (fase - 1)
        if not pausado:
            t += 1

        # ===== Atualiza o jogo (só enquanto está surfando) =====
        if not pausado and not fim:
            frames += 1
            # Fases: a cada DURACAO_FASE segundos fica mais difícil e os pontos valem mais
            nova_fase = 1 + int(segundos // DURACAO_FASE)
            if nova_fase > fase:
                fase, banner, flash = nova_fase, 150, 5
                SOM_FASE.play()
            velocidade = min(VEL_MAX_JOGO, VEL_INICIAL + ACELERACAO * segundos)
            espaco = max(300, ESPACO_OBSTACULOS - 30 * (fase - 1))
            intervalo = max(18, int(espaco / velocidade))  # frames entre um obstáculo e outro

            # Física: segurando ESPAÇO/mouse sobe; a gravidade puxa sempre
            teclas = pygame.key.get_pressed()
            if teclas[pygame.K_SPACE] or teclas[pygame.K_UP] or pygame.mouse.get_pressed()[0]:
                vel_y += IMPULSO * agilidade
            vel_y += GRAVIDADE
            vel_max = VEL_MAXIMA * agilidade
            vel_y = max(-vel_max, min(vel_max, vel_y))
            player_y += vel_y
            if player_y < topo_pes - player.height:  # não passa do ponto mais alto da prancha
                player_y, vel_y = topo_pes - player.height, 0
            if player_y > NIVEL_AGUA - player.height + 5:  # nem afunda na água
                player_y, vel_y = NIVEL_AGUA - player.height + 5, 0
            player.y = int(player_y)
            player.centerx = int(x_da_onda(player.bottom))  # encosta na face da onda
            if vel_y < 0:
                subindo = True
            elif vel_y > 0:
                subindo = False
            angulo += (min(30, abs(vel_y) * 3.5) - angulo) * 0.25  # inclina suavemente

            # Gotinhas saindo de trás da prancha
            if random.random() < 0.6 + abs(vel_y) * 0.05:
                solta(particulas, player.centerx - 12, player.bottom - 2, 1 + (abs(vel_y) > 4), cen["espuma"],
                      vel=1.2, vida=24, raio=(1.5, 3.5), vx0=-velocidade * 0.4, vy0=-1.5 - abs(vel_y) * 0.2)

            # Cria obstáculos. A partir da fase 2 podem vir em dupla (avião + prédio/poste)
            contador += 1
            if contador >= intervalo:
                contador, quilha_feita = 0, False
                if fase >= 2 and random.random() < min(0.5, 0.2 * (fase - 1)):
                    obstaculos.append(novo_obstaculo("aviao", topo_pes, fase))
                    obstaculos.append(novo_obstaculo(random.choice(["predio", "poste"]), topo_pes, fase))
                else:
                    tipo = random.choice(["predio", "poste", "aviao", "aviao", "peixe", "peixe"])
                    obstaculos.append(novo_obstaculo(tipo, topo_pes, fase))
            # A quilha nasce no meio do caminho entre dois obstáculos (nunca fica dentro de um).
            # Algumas nascem bem no alto: só pranchas melhores alcançam!
            if not quilha_feita and contador >= intervalo // 2:
                y = random.randint(TOPO_PADRAO - 130, NIVEL_AGUA - 35)
                quilhas.append({"tipo": "quilha", "rect": pygame.Rect(WIDTH, y, 24, 30), "x": float(WIDTH)})
                quilha_feita = True

            # Move tudo para a esquerda na mesma velocidade
            for o in obstaculos + quilhas:
                o["x"] -= velocidade
                o["rect"].x = int(o["x"])
                if o["tipo"] == "peixe":
                    o["rect"].y = int(o["centro"] + o["amp"] * math.sin(o["x"] / 40))
            obstaculos = [o for o in obstaculos if o["rect"].right > -60]

            # Quilhas: as que o surfista pegou viram brilho; as que saíram da tela somem
            alcance = player.inflate(14, 14)
            restantes = []
            for q in quilhas:
                if alcance.colliderect(q["rect"]):
                    pegas += 1
                    SOM_QUILHA.play()
                    solta(particulas, q["rect"].centerx, q["rect"].centery, 14, DOURADO, vel=4)
                    textos.append({"x": q["rect"].centerx, "y": q["rect"].y, "vida": 45})
                elif q["rect"].right > 0:
                    restantes.append(q)
            quilhas = restantes

            # Colisão (hitbox um pouco menor que o desenho, para ser justo)
            corpo = player.inflate(-14, -10)
            for o in obstaculos:
                caixa = o["rect"].inflate(-6, -6) if o["tipo"] == "aviao" else o["rect"]
                if corpo.colliderect(caixa):
                    SOM_MORTE.play()
                    solta(particulas, player.centerx, player.centery, 40, cen["espuma"], vel=6, vida=45, raio=(2, 5))
                    tremor = 18
                    pygame.mixer.music.set_volume(0.15)
                    fim = termina_partida(pontos, segundos, pegas, fase)
                    break

            # Quanto mais rápido, mais pontos (e ainda multiplica pela fase)
            pontos += velocidade * mult * 0.1

        # Raios na tempestade
        if cen.get("chuva") and not pausado and random.random() < 0.003:
            flash = 10
            SOM_TROVAO.play()

        # ===== Desenha (o que vem depois fica por cima) =====
        fator = 0 if pausado or fim else velocidade / VEL_INICIAL
        desenha_fundo(tela, vis, fundo, fator)
        for o in obstaculos:
            desenha_obstaculo(tela, o, cen)
        for q in quilhas:
            desenha_quilha(tela, q["rect"].x, q["rect"].y + int(4 * math.sin(t / 8)))
        desenha_onda(tela, t, cen)
        if fim:  # o surfista caiu: gira e afunda (desenhado antes da água)
            if not pausado:
                fim["giro"] += 9
                fim["queda"] = min(70, fim["queda"] + 1.5)
                fim["espera"] -= 1
            img = pygame.transform.rotozoom(frente, fim["giro"], 1)
            tela.blit(img, img.get_rect(center=(player.centerx, player.bottom - 26 + fim["queda"])))
        desenha_agua(tela, t, cen)
        desenha_espuma_base(tela, t, cen)
        if not fim:
            img = pygame.transform.rotozoom(costas if subindo else frente, -angulo, 1)
            tela.blit(img, img.get_rect(center=(player.centerx, player.bottom - 26)))
        atualiza_particulas(tela, particulas, mover=not pausado)
        for tx in textos:  # "+1" subindo quando pega quilha
            if not pausado:
                tx["y"] -= 1
                tx["vida"] -= 1
            escreve_transparente("+1", F_MED, DOURADO, (tx["x"], tx["y"]), tx["vida"] * 8)
        textos = [tx for tx in textos if tx["vida"] > 0]
        if cen.get("chuva"):
            desenha_chuva(tela, t)
        if flash > 0:
            clarao = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            clarao.fill((255, 255, 255, flash * 18))
            tela.blit(clarao, (0, 0))
            flash -= 1

        desenha_hud(pontos, pegas, fase, segundos, recorde, t)
        if banner > 0 and not fim:  # aviso de fase nova
            alpha = min(255, banner * 6)
            y = 200 - max(0, banner - 130) * 3
            escreve_transparente(f"FASE {fase}!", F_ENORME, DOURADO, (WIDTH // 2, y), alpha)
            escreve_transparente(f"Mais rápido... pontos x{mult:g}!", F_MED, BRANCO, (WIDTH // 2, y + 50), alpha)
            if not pausado:
                banner -= 1

        if pausado:
            escuro = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            escuro.fill((0, 0, 0, 140))
            tela.blit(escuro, (0, 0))
            escreve(tela, "PAUSADO", F_ENORME, BRANCO, (WIDTH // 2, 220), "center")
            if botao(tela, (290, 290, 220, 50), "CONTINUAR (P)", F_MED, mouse, clique):
                pausado = False
            if botao(tela, (290, 355, 220, 50), "MENU (M)", F_MED, mouse, clique, cor=(120, 70, 160)):
                return "menu"

        if fim:
            caixa = pygame.Rect(170, 110, 460, 390)
            painel(tela, caixa, alpha=225, borda=DOURADO)
            escreve(tela, "WIPEOUT!", F_ENORME, (255, 90, 70), (WIDTH // 2, 165), "center")
            escreve(tela, f"Pontos: {fim['pontos']}", F_GRA, BRANCO, (WIDTH // 2, 225), "center")
            escreve(tela, f"Tempo: {formata_tempo(fim['segundos'])}    Fase: {fim['fase']}", F_MED, CINZA,
                    (WIDTH // 2, 265), "center")
            escreve(tela, f"Quilhas: +{fim['pegas']}  (total {dados['quilhas']})", F_MED, DOURADO,
                    (WIDTH // 2, 300), "center")
            if fim["recorde"] and fim["pontos"] > 0:
                if t // 15 % 2:
                    escreve(tela, "NOVO RECORDE!", F_GRA, DOURADO, (WIDTH // 2, 342), "center")
            elif fim["pessoal"]:
                escreve(tela, "Seu melhor resultado!", F_MED, VERDE, (WIDTH // 2, 342), "center")
            for i, nome in enumerate(fim["liberados"]):
                escreve(tela, f"Cenário liberado: {nome}!", F_PEQ, (120, 230, 255), (WIDTH // 2, 375 + i * 22), "center")
            if fim["espera"] <= 0:
                if botao(tela, (190, 430, 200, 50), "DE NOVO (R)", F_MED, mouse, clique, cor=(40, 165, 90)):
                    return "jogo"
                if botao(tela, (410, 430, 200, 50), "MENU (M)", F_MED, mouse, clique, cor=(120, 70, 160)):
                    return "menu"

        mostra(tremor)
        if tremor > 0:
            tremor -= 1


# ===== Loop das telas =====
def main():
    estado = "menu"
    while estado != "sair":
        if estado == "menu":
            estado = tela_menu()
        elif estado == "intro":
            estado = tela_intro()
        else:
            estado = tela_jogo()
    save.salva(dados)
    pygame.quit()


if __name__ == "__main__":
    main()
