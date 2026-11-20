import pygame

# ===== Inicialização =====
pygame.init()
WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Nome do Jogo")
clock = pygame.time.Clock()
FPS = 60

# ===== Loop principal =====
game = True
while game:
    clock.tick(FPS)

    # 1) Trata eventos (teclado, mouse, fechar a janela)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game = False

    # 2) Atualiza o estado do jogo (movimentos, colisões, pontuação)

    # 3) Desenha na tela
    window.fill((20, 20, 40))      # limpa a tela
    pygame.display.update()        # mostra o novo frame

# ===== Finalização =====
pygame.quit()