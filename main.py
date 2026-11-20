import pygame
import random

# ===== Inicialização =====
pygame.init()
WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jetpack Escape")
clock = pygame.time.Clock()
FPS = 60
fonte = pygame.font.SysFont(None, 48)

# ===== Constantes do jogo =====
GRAVIDADE = 0.5          # a cada frame, puxa o jogador um pouco para baixo
IMPULSO = -1.0           # força do jetpack (negativo = para cima)
VEL_MAXIMA = 10          # velocidade vertical máxima (para não ficar rápido demais)
VEL_OBSTACULO = 6        # quantos pixels os obstáculos andam para a esquerda por frame
INTERVALO_OBSTACULO = 90 # a cada 90 frames (1,5 segundo) nasce um obstáculo

# ===== Estado do jogo =====
player = pygame.Rect(100, HEIGHT // 2, 40, 40)  # x, y, largura, altura
player_y = player.y   # posição y "de verdade" (com casas decimais)
vel_y = 0             # velocidade vertical do jogador
obstaculos = []       # lista de retângulos (pygame.Rect)
contador = 0          # conta frames até criar o próximo obstáculo
pontos = 0
game_over = False


def novo_obstaculo():
    """Cria um obstáculo na borda direita da tela, com altura e posição aleatórias."""
    altura = random.randint(100, 250)
    y = random.randint(0, HEIGHT - altura)
    return pygame.Rect(WIDTH, y, 30, altura)


# ===== Loop principal =====
game = True
while game:
    clock.tick(FPS)

    # 1) Trata eventos (teclado, mouse, fechar a janela)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game = False
        # Apertar R depois de perder recomeça o jogo
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r and game_over:
            player_y = HEIGHT // 2
            vel_y = 0
            obstaculos = []
            contador = 0
            pontos = 0
            game_over = False

    # 2) Atualiza o estado do jogo (só enquanto não perdeu)
    if not game_over:
        # Jetpack: segurando ESPAÇO, a velocidade vai para cima
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            vel_y += IMPULSO
        vel_y += GRAVIDADE  # a gravidade age sempre

        # Limita a velocidade
        if vel_y > VEL_MAXIMA:
            vel_y = VEL_MAXIMA
        if vel_y < -VEL_MAXIMA:
            vel_y = -VEL_MAXIMA

        # Move o jogador
        player_y += vel_y

        # Não deixa sair pelo teto nem pelo chão
        if player_y < 0:
            player_y = 0
            vel_y = 0
        if player_y > HEIGHT - player.height:
            player_y = HEIGHT - player.height
            vel_y = 0
        player.y = int(player_y)

        # Cria obstáculos de tempos em tempos
        contador += 1
        if contador >= INTERVALO_OBSTACULO:
            obstaculos.append(novo_obstaculo())
            contador = 0

        # Move os obstáculos para a esquerda
        for obs in obstaculos:
            obs.x -= VEL_OBSTACULO

        # Remove o obstáculo mais antigo quando ele sai da tela
        if len(obstaculos) > 0 and obstaculos[0].right < 0:
            obstaculos.pop(0)

        # Colisão: se encostar em qualquer obstáculo, perde
        for obs in obstaculos:
            if player.colliderect(obs):
                game_over = True

        # Pontuação: ganha 1 ponto por frame vivo
        pontos += 1

    # 3) Desenha na tela (o que vem depois fica por cima)
    window.fill((20, 20, 40))                          # fundo
    pygame.draw.rect(window, (80, 220, 255), player)   # jogador
    for obs in obstaculos:
        pygame.draw.rect(window, (230, 60, 60), obs)   # obstáculos

    texto_pontos = fonte.render(f"Distancia: {pontos // 10} m", True, (255, 255, 255))
    window.blit(texto_pontos, (10, 10))

    if game_over:
        texto_fim = fonte.render("GAME OVER - aperte R", True, (255, 220, 0))
        window.blit(texto_fim, (WIDTH // 2 - texto_fim.get_width() // 2, HEIGHT // 2))

    pygame.display.update()

# ===== Finalização =====
pygame.quit()
