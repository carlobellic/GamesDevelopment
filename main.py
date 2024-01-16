import pygame
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE, K_SPACE, MOUSEBUTTONDOWN
from sys import exit
import random

# Initialize Pygame
pygame.init()

# Set up window
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mankind's Expiration")

# Load images
background = pygame.transform.scale(pygame.image.load("game_map.png").convert(), (WIDTH, HEIGHT))
player_image_original = pygame.image.load("player.png").convert_alpha()
bullet_image_original = pygame.image.load("bullet.png").convert_alpha()
zombie_image_original = pygame.image.load("zombie.png").convert_alpha()
powerup_image_original = pygame.image.load("speedboost.png").convert_alpha()

# Resize images
player_image = pygame.transform.scale(player_image_original, (150, 150))
bullet_image = pygame.transform.scale(bullet_image_original, (20, 10))
zombie_image = pygame.transform.scale(zombie_image_original, (50, 50))
powerup_image = pygame.transform.scale(powerup_image_original, (30, 30))

# Flip the player image horizontally
flipped_player_image = pygame.transform.flip(player_image, True, False)

# Set up player
player_rect = flipped_player_image.get_rect()
player_rect.center = (WIDTH // 2, HEIGHT // 2)
player_speed = 5

# Set up bullets
bullets = []

# Bullet speed and cooldown
bullet_speed = 10
bullet_cooldown = 30
bullet_timer = 0

# Set up zombies
zombies = []
wave = 1
zombie_speed = 2
zombies_per_wave = 2
total_waves = 10
waves_completed = 0

# Set up health bar
player_health = 100
font = pygame.font.Font(None, 36)

# Cooldown for collisions with zombies
collision_cooldown = 30
collision_timer = 0

# Load power-up image
powerup_image_original = pygame.image.load("speedboost.png").convert_alpha()
powerup_image = pygame.transform.scale(powerup_image_original, (30, 30))

# Power-up attributes
powerup_rect = powerup_image.get_rect()
powerup_active = False

# Power-up cooldown
powerup_cooldown = 30
powerup_timer = 0

# Score variables
score = 0
score_font = pygame.font.Font(None, 36)

# Set the new damage value
damage_taken = 5

# Main menu loop
menu_font = pygame.font.Font(None, 72)
menu_title = menu_font.render("Mankind's Expiration", True, (255, 255, 255))
menu_title_rect = menu_title.get_rect(center=(WIDTH // 2, HEIGHT // 4))
play_button_font = pygame.font.Font(None, 48)
play_button_text = play_button_font.render("Play", True, (255, 255, 255))
play_button_rect = play_button_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

menu_active = True

while menu_active:
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            exit()
        if event.type == MOUSEBUTTONDOWN:
            if play_button_rect.collidepoint(event.pos):
                menu_active = False

    screen.blit(background, (0, 0))
    screen.blit(menu_title, menu_title_rect)
    pygame.draw.rect(screen, (0, 0, 0), play_button_rect)
    screen.blit(play_button_text, play_button_rect.topleft)

    pygame.display.update()

# Main game loop
clock = pygame.time.Clock()

game_over = False

while not game_over:
    while waves_completed < total_waves and player_health > 0:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                exit()

        # Get the mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Calculate the angle between the player and the mouse
        angle = pygame.math.Vector2(mouse_x - player_rect.centerx, mouse_y - player_rect.centery).angle_to((1, 0))

        # Handle player movement within boundaries
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and player_rect.top > 0:
            player_rect.y -= player_speed
        if keys[pygame.K_s] and player_rect.bottom < HEIGHT:
            player_rect.y += player_speed
        if keys[pygame.K_a] and player_rect.left > 0:
            player_rect.x -= player_speed
        if keys[pygame.K_d] and player_rect.right < WIDTH:
            player_rect.x += player_speed

        # Shooting bullets
        if keys[K_SPACE] and bullet_timer <= 0:
            bullet_rect = bullet_image.get_rect()
            bullet_rect.center = player_rect.center
            bullets.append((bullet_rect, angle))
            bullet_timer = bullet_cooldown

        # Update bullet positions
        bullets = [(bullet_rect, angle) for bullet_rect, angle in bullets if bullet_rect.colliderect(screen.get_rect())]
        for bullet in bullets:
            bullet_rect, bullet_angle = bullet
            bullet_vector = pygame.math.Vector2(1, 0).rotate(-bullet_angle)
            bullet_rect.x += bullet_vector.x * bullet_speed
            bullet_rect.y += bullet_vector.y * bullet_speed

        # Decrease bullet cooldown timer
        if bullet_timer > 0:
            bullet_timer -= 1

        # Spawn zombies
        if not zombies:
            zombies_per_wave += 1
            for _ in range(zombies_per_wave):
                zombie_rect = zombie_image.get_rect()
                side = random.choice(["top", "bottom", "left", "right"])
                if side == "top":
                    zombie_rect.topleft = (random.randint(0, WIDTH - zombie_rect.width), 0)
                elif side == "bottom":
                    zombie_rect.topleft = (random.randint(0, WIDTH - zombie_rect.width), HEIGHT - zombie_rect.height)
                elif side == "left":
                    zombie_rect.topleft = (0, random.randint(0, HEIGHT - zombie_rect.height))
                elif side == "right":
                    zombie_rect.topleft = (WIDTH - zombie_rect.width, random.randint(0, HEIGHT - zombie_rect.height))

                zombies.append(zombie_rect)

        # Update zombie positions
        for zombie_rect in zombies[:]:
            zombie_vector = pygame.math.Vector2(player_rect.centerx - zombie_rect.centerx,
                                                player_rect.centery - zombie_rect.centery)
            if zombie_vector.length() > 0:
                zombie_vector.normalize_ip()
                zombie_rect.x += zombie_vector.x * zombie_speed
                zombie_rect.y += zombie_vector.y * zombie_speed

        # Check for collisions between bullets and zombies
        bullets_to_remove = []
        zombies_to_remove = []

        for bullet in bullets:
            bullet_rect, _ = bullet
            for zombie_rect in zombies[:]:
                # Adjust the size of the zombie hitbox
                if bullet_rect.colliderect(zombie_rect.inflate(-5, -5)):  # Make the hitbox smaller by 5 pixels
                    bullets_to_remove.append(bullet)
                    zombies_to_remove.append(zombie_rect)
                    score += 5  # Increment the score for each killed zombie

        # Remove collided bullets
        bullets = [bullet for bullet in bullets if bullet not in bullets_to_remove]

        # Remove collided zombies
        zombies = [zombie for zombie in zombies if zombie not in zombies_to_remove]

        # Check for collisions between player and zombies
        for zombie_rect in zombies:
            if player_rect.colliderect(zombie_rect):
                if collision_timer <= 0:
                    player_health -= damage_taken
                    print(f"Player Health: {player_health}")
                    collision_timer = collision_cooldown

        # Decrease collision cooldown timer
        if collision_timer > 0:
            collision_timer -= 1

        # Rotate the player image with the correct anchor point and scale
        rotated_image = pygame.transform.rotozoom(flipped_player_image, angle, 0.2)
        rotated_rect = rotated_image.get_rect(center=player_rect.center)

        # Spawn power-up once every wave
        if waves_completed > 0 and len(zombies) == 0 and len(bullets) == 0 and powerup_timer <= 0:
            powerup_rect.topleft = (random.randint(50, WIDTH - powerup_rect.width - 50),
                                    random.randint(50, HEIGHT - powerup_rect.height - 50))
            powerup_active = True

        # Check for collisions between player and power-up
        if powerup_active and player_rect.colliderect(powerup_rect):
            bullet_cooldown /= 2
            powerup_active = False
            powerup_timer = powerup_cooldown

        # Decrease power-up cooldown timer
        if powerup_timer > 0:
            powerup_timer -= 1

        # Update screen
        screen.blit(background, (0, 0))

        # Draw bullets
        for bullet in bullets:
            bullet_rect, _ = bullet
            screen.blit(bullet_image, bullet_rect.topleft)

        # Draw zombies
        for zombie_rect in zombies:
            screen.blit(zombie_image, zombie_rect.topleft)

        # Draw power-up
        if powerup_active:
            screen.blit(powerup_image, powerup_rect.topleft)

        # Draw rotated player image
        screen.blit(rotated_image, rotated_rect.topleft)

        # Draw health bar
        pygame.draw.rect(screen, (255, 0, 0), (10, 10, 200, 20))
        pygame.draw.rect(screen, (0, 255, 0), (10, 10, player_health * 2, 20))

        # Draw score
        score_text = score_font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 40))

        # Display current wave count
        wave_text = font.render(f"Wave: {wave}/{total_waves}", True, (255, 255, 255))
        screen.blit(wave_text, (WIDTH - 150, 10))

        pygame.display.update()
        clock.tick(60)

        # Check if all zombies are defeated
        if len(zombies) == 0 and len(bullets) == 0:
            waves_completed += 1
            wave += 1  # Increment wave count
            print(f"Wave {waves_completed} completed!")

    # Game over screen
    screen.fill((0, 0, 0))  # Fill the screen with black

    # Display game over text
    game_over_text = font.render("Game Over", True, (255, 0, 0))
    game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    screen.blit(game_over_text, game_over_rect)

    # Display final score
    final_score_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
    final_score_rect = final_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
    screen.blit(final_score_text, final_score_rect)

    # Update the display
    pygame.display.update()

    # Wait for a key press to exit or restart
    waiting_for_key = True
    while waiting_for_key:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                exit()
            if event.type == KEYDOWN:
                waiting_for_key = False

    # Reset game variables for a new game
    player_health = 100
    bullets = []
    zombies = []
    waves_completed = 0
    wave = 1  # Reset wave count
    score = 0

# Game over
pygame.quit()
exit()
