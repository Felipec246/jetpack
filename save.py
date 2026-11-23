"""Salva e carrega o progresso (quilhas, pranchas compradas, escolhas e recordes)
no arquivo save.json, para nada se perder quando o jogo fecha."""
import json

from config import ARQUIVO_SAVE, CENARIOS, PERSONAGENS, PRANCHAS


def novo():
    """Progresso de quem nunca jogou."""
    return {"nome": "", "quilhas": 0, "pranchas": [0], "prancha": 0,
            "personagem": 0, "cenario": 0, "recordes": []}


def carrega():
    """Lê o save.json. Se ele não existir (ou estiver estragado), começa do zero."""
    try:
        with open(ARQUIVO_SAVE, encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    except (OSError, ValueError):
        dados = {}
    if not isinstance(dados, dict):
        dados = {}
    for chave, valor in novo().items():
        if type(dados.get(chave)) is not type(valor):
            dados[chave] = valor
    # Corrige números fora das listas (por exemplo, se o arquivo foi editado à mão)
    dados["pranchas"] = [i for i in dados["pranchas"] if isinstance(i, int) and 0 <= i < len(PRANCHAS)]
    if 0 not in dados["pranchas"]:
        dados["pranchas"].insert(0, 0)
    if dados["prancha"] not in dados["pranchas"]:
        dados["prancha"] = 0
    if not 0 <= dados["personagem"] < len(PERSONAGENS):
        dados["personagem"] = 0
    if not 0 <= dados["cenario"] < len(CENARIOS):
        dados["cenario"] = 0
    dados["recordes"] = [r for r in dados["recordes"] if isinstance(r, dict) and "nome" in r and "pontos" in r]
    return dados


def salva(dados):
    try:
        with open(ARQUIVO_SAVE, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=2)
    except OSError:
        print("Não foi possível salvar o progresso.")


def registra_recorde(dados, nome, pontos, tempo):
    """Guarda o melhor resultado de cada jogador. Devolve True se for recorde pessoal."""
    for r in dados["recordes"]:
        if r["nome"].lower() == nome.lower():
            if pontos <= r["pontos"]:
                return False
            r.update(nome=nome, pontos=pontos, tempo=tempo)
            break
    else:  # o for não achou o nome: jogador novo
        dados["recordes"].append({"nome": nome, "pontos": pontos, "tempo": tempo})
    dados["recordes"].sort(key=lambda r: r["pontos"], reverse=True)
    return True


def melhor_pontuacao(dados):
    """Maior pontuação de todos os jogadores (é ela que libera os cenários)."""
    return max((r["pontos"] for r in dados["recordes"]), default=0)


# ===== Modo demonstração =====
NOME_DEMO = "john john"


def modo_demo(dados):
    """True se o nome do jogador é o da demonstração: aí todas as pranchas e cenários ficam liberados.
    Nada disso é gravado no save; é decidido na hora, só olhando o nome."""
    return dados["nome"].strip().lower() == NOME_DEMO


def tem_prancha(dados, i):
    """O jogador pode usar a prancha i? (comprou ou está no modo demonstração)"""
    return modo_demo(dados) or i in dados["pranchas"]


def cenario_liberado(dados, cenario):
    """O cenário está liberado? (recorde suficiente ou modo demonstração)"""
    return modo_demo(dados) or melhor_pontuacao(dados) >= cenario["req"]


def ajusta_escolhas(dados):
    """Se o jogador escolheu uma prancha ou um cenário que não pode usar
    (por exemplo, saiu do modo demonstração trocando de nome), volta para os iniciais."""
    if not tem_prancha(dados, dados["prancha"]):
        dados["prancha"] = 0
    if not cenario_liberado(dados, CENARIOS[dados["cenario"]]):
        dados["cenario"] = 0
