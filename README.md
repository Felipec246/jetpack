# Tsunami Surf

Jogo feito em Python com **Pygame** (versão `pygame-ce`) para a disciplina **Design de Software** (Insper, 2026).

## Grupo

- Felipe Issa Cevasco (GitHub: Felipec246)
- Ricardo Castro e Silva (GitHub: RicardoCastro08)
- José Porto (GitHub: jose-porto)

## Sobre o jogo

Um tsunami invadiu a cidade e você está surfando na face da onda! **Segure ESPAÇO para subir**; ao soltar, a gravidade puxa o surfista de volta para a água. Desvie de prédios, postes, aviões e peixes voadores que vêm da direita e pegue as **quilhas** douradas.

- A velocidade aumenta com o tempo e, a cada fase (25 s), o jogo fica mais difícil e os pontos valem mais (multiplicador).
- As quilhas coletadas viram moeda: na loja do menu dá para comprar pranchas melhores (mais rápidas e que sobem mais alto na onda).
- Fazer recorde libera novos cenários: Cidade, Pôr do Sol, Noite Neon e Tempestade (com chuva e trovões).
- O progresso (nome, quilhas, pranchas, personagem, cenário e ranking) é salvo no arquivo `save.json`.

## Telas

1. **Menu (lobby):** nome do jogador, escolha de personagem, loja de pranchas, cenários e ranking de recordes.
2. **Abertura:** pequena cena animada da cidade tranquila até a chegada do tsunami (pode ser pulada).
3. **Partida:** o jogo em si, com pausa. Ao bater, aparece a tela de fim com os resultados, onde dá para jogar de novo ou voltar ao menu.

## Controles

| Tecla / mouse | O que faz |
|---|---|
| ESPAÇO, seta para cima ou botão esquerdo do mouse (segurar) | Sobe na onda |
| P ou ESC | Pausa / continua |
| M (na pausa ou na tela de fim) | Volta ao menu |
| R ou ENTER (na tela de fim) | Joga de novo |
| ENTER ou ESPAÇO (no menu) | Começa a jogar |
| Mouse | Navega pelo menu e pela loja |

## Como rodar

1. Instale o Python 3.
2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
3. Rode o jogo:
   ```
   python main.py
   ```

Na primeira vez o jogo demora alguns segundos ("Preparando as ondas...") porque gera a música do menu e alguns efeitos sonoros por código.

## Estrutura do projeto

| Arquivo | Conteúdo |
|---|---|
| `main.py` | Telas do jogo (menu, abertura e partida) e o loop principal |
| `config.py` | Constantes: tela, física, dificuldade, personagens, pranchas e cenários |
| `desenho.py` | Funções que desenham surfista, onda, água, obstáculos, fundo e efeitos |
| `sons.py` | Gera a música do menu e alguns efeitos por síntese de som |
| `save.py` | Salva e carrega o progresso em `save.json` |
| `assets/` | Arquivos de som e música |

## Vídeo do jogo

(https://drive.google.com/file/d/1_uJIDRA247KX5thHjKHRo4gIHaPTBINc/view?usp=sharing)

## Créditos dos sons e da música

- Música (`musica.mp3.mp3`): Pixabay, [Pixabay Music](https://pixabay.com/music/).
- Efeitos sonoros (`coletavel.mp3.mp3` e `morte.mp3.mp3`): Pixabay, [Pixabay Sound Effects](https://pixabay.com/sound-effects/).

Os efeitos `.wav` adicionais são gerados pelo próprio jogo em `sons.py`. Os links individuais e os nomes dos autores dos arquivos baixados não foram registrados.

## Uso de IA

(usada por todos os integrantes do grupo para ajudar na lógica do código e ajudar a utilizar as funções e módulos)
