"""Cria a música do menu e alguns efeitos sonoros por código (síntese de som)
e salva como .wav na pasta assets. Só demora na primeira vez que o jogo abre."""
import math
import os
import random
import wave
from array import array

TAXA = 22050  # amostras por segundo


def _forma_onda(forma, fase):
    """Valor de uma onda (entre -1 e 1) numa fase entre 0 e 1."""
    if forma == "quadrada":
        return 1.0 if fase < 0.5 else -1.0
    if forma == "triangulo":
        return 4 * abs(fase - 0.5) - 1
    return math.sin(2 * math.pi * fase)


def sintetiza(caminho, faixas, bpm):
    """faixas = lista de (notas, forma, volume).
    notas = lista de (nota MIDI ou None para pausa, duração em batidas)."""
    seg_batida = 60 / bpm
    total = max(sum(d for _, d in notas) for notas, _, _ in faixas)
    n = int(total * seg_batida * TAXA)
    mix = [0.0] * n
    for notas, forma, volume in faixas:
        pos = 0
        for nota, duracao in notas:
            tam = int(duracao * seg_batida * TAXA)
            if nota is not None:
                freq = 440 * 2 ** ((nota - 69) / 12)
                fase = ruido = 0.0
                for i in range(min(tam, n - pos)):
                    if forma == "bumbo":        # tambor grave: frequência caindo rápido
                        fase += (45 + 90 * math.exp(-i / 600)) / TAXA
                        v = math.sin(2 * math.pi * fase) * math.exp(-i / 2500)
                    elif forma == "chimbal":    # chiado curtinho
                        v = random.uniform(-1, 1) * math.exp(-i / 300)
                    elif forma == "ronco":      # ruído grave (trovão / tsunami chegando)
                        ruido += 0.04 * (random.uniform(-1, 1) - ruido)
                        v = ruido * 4 * math.sin(math.pi * i / tam)
                    else:                       # nota musical com ataque rápido e decaimento
                        fase += freq / TAXA
                        v = _forma_onda(forma, fase % 1) * min(1, i / 80) * math.exp(-2.5 * i / tam)
                    mix[pos + i] += v * volume
            pos += tam
    amostras = array("h", [int(max(-1.0, min(1.0, s)) * 30000) for s in mix])
    with wave.open(caminho, "wb") as arquivo:
        arquivo.setnchannels(1)
        arquivo.setsampwidth(2)
        arquivo.setframerate(TAXA)
        arquivo.writeframes(amostras.tobytes())


# Melodia do menu (notas MIDI: 60 = Dó central). 8 compassos de 4 batidas.
MELODIA = [(76, 1), (79, 1), (81, .5), (79, .5), (76, 1),
           (72, 1), (76, 1), (74, 1), (72, 1),
           (69, 1), (72, 1), (74, .5), (72, .5), (69, 1),
           (67, 1.5), (69, .5), (71, 1), (74, 1),
           (76, .5), (76, .5), (79, 1), (84, 1), (81, 1),
           (79, 1), (76, 1), (72, 1), (76, 1),
           (77, 1), (76, 1), (74, 1), (72, 1),
           (74, 1), (71, 1), (72, 2)]


def gera_sons(pasta):
    """Cria os .wav que ainda não existem na pasta."""
    baixo = []
    for raiz in [48, 45, 41, 43] * 2:  # acordes Dó, Lá menor, Fá, Sol (duas vezes)
        baixo += [(raiz, 1), (raiz + 7, 1), (raiz + 12, 1), (raiz + 7, 1)]
    receitas = {
        "menu.wav": ([(MELODIA, "quadrada", 0.15), (baixo, "triangulo", 0.4),
                      ([(36, 1), (None, 1)] * 16, "bumbo", 0.55),
                      ([(None, .5), (90, .5)] * 32, "chimbal", 0.07)], 140),
        "fase.wav": ([([(72, .5), (76, .5), (79, .5), (84, 1.5)], "quadrada", 0.25),
                      ([(60, .5), (64, .5), (67, .5), (72, 1.5)], "triangulo", 0.35)], 360),
        "compra.wav": ([([(83, .5), (88, 2)], "quadrada", 0.25)], 400),
        "erro.wav": ([([(45, 1), (41, 2)], "quadrada", 0.22)], 300),
        "trovao.wav": ([([(1, 8)], "ronco", 0.9)], 120),
    }
    for nome, (faixas, bpm) in receitas.items():
        caminho = os.path.join(pasta, nome)
        if not os.path.exists(caminho):
            try:
                sintetiza(caminho, faixas, bpm)
            except OSError:
                pass  # sem permissão para gravar: o jogo funciona sem esse som
