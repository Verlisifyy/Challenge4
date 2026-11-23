import math
import random
import pygame

pygame.init()

WIDTH = 1280
HEIGHT = 720
FPS = 60

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pokemon Tower Defense - Fase 1")

CLOCK = pygame.time.Clock()

FONT_SMALL = pygame.font.SysFont("arial", 20)
FONT_MEDIUM = pygame.font.SysFont("arial", 28, bold=True)
FONT_LARGE = pygame.font.SysFont("arial", 54, bold=True)

# Kleuren
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
DARK_GREY = (55, 55, 55)
LIGHT_GREY = (185, 185, 185)

GRASS_GREEN = (69, 148, 78)
GRASS_DARK = (58, 128, 67)

PATH_BROWN = (184, 151, 101)
PATH_BORDER = (123, 94, 63)

YELLOW = (250, 220, 60)
YELLOW_DARK = (205, 170, 35)

PURPLE = (155, 85, 175)
PURPLE_DARK = (105, 50, 130)

RED = (220, 60, 60)
DARK_RED = (125, 25, 25)

GREEN = (55, 200, 85)
BLUE = (65, 145, 235)

# Gameplay-instellingen
STARTING_MONEY = 350
STARTING_LIVES = 20

TOWER_COST = 100
TOWER_RANGE = 170
TOWER_DAMAGE = 25
TOWER_ATTACK_DELAY = 0.65

PATH_WIDTH = 80
MAX_WAVES = 5

# De route die vijanden volgen
PATH = [
    (-50, 350),
    (210, 350),
    (210, 150),
    (510, 150),
    (510, 520),
    (800, 520),
    (800, 250),
    (1050, 250),
    (1050, 430),
    (1330, 430)
]



def draw_text(surface, text, font, colour, position, center=False):
    """Tekent tekst op het scherm."""
    text_surface = font.render(str(text), True, colour)
    text_rect = text_surface.get_rect()

    if center:
        text_rect.center = position
    else:
        text_rect.topleft = position

    surface.blit(text_surface, text_rect)


def draw_background(surface):
    """Tekent het gras en een eenvoudig tegelpatroon."""
    surface.fill(GRASS_GREEN)

    tile_size = 64

    for row in range(0, HEIGHT, tile_size):
        for column in range(0, WIDTH, tile_size):
            if (row // tile_size + column // tile_size) % 2 == 0:
                tile_rect = pygame.Rect(
                    column,
                    row,
                    tile_size,
                    tile_size
                )
                pygame.draw.rect(surface, GRASS_DARK, tile_rect)


def draw_path(surface):
    """Tekent de route waarover vijanden lopen."""
    pygame.draw.lines(
        surface,
        PATH_BORDER,
        False,
        PATH,
        PATH_WIDTH + 12
    )

    pygame.draw.lines(
        surface,
        PATH_BROWN,
        False,
        PATH,
        PATH_WIDTH
    )

    # Startpunt
    pygame.draw.circle(
        surface,
        BLUE,
        PATH[0],
        26
    )

    # Eindpunt
    pygame.draw.circle(
        surface,
        RED,
        PATH[-1],
        30
    )


def point_to_segment_distance(point, start, end):
    """
    Bereken de kortste afstand tussen een punt en een lijnsegment.
    Wordt gebruikt om torens van het pad af te houden.
    """
    point_vector = pygame.Vector2(point)
    start_vector = pygame.Vector2(start)
    end_vector = pygame.Vector2(end)

    segment = end_vector - start_vector
    segment_length_squared = segment.length_squared()

    if segment_length_squared == 0:
        return point_vector.distance_to(start_vector)

    projection = (
        (point_vector - start_vector).dot(segment)
        / segment_length_squared
    )

    projection = max(0, min(1, projection))
    closest_point = start_vector + segment * projection

    return point_vector.distance_to(closest_point)


def is_position_on_path(position, extra_distance=0):
    """Controleert of een positie te dicht op het pad ligt."""
    minimum_distance = PATH_WIDTH / 2 + extra_distance

    for index in range(len(PATH) - 1):
        distance = point_to_segment_distance(
            position,
            PATH[index],
            PATH[index + 1]
        )

        if distance < minimum_distance:
            return True

    return False


# =========================================================
# VIJAND
# =========================================================

class Enemy(pygame.sprite.Sprite):
    def __init__(
        self,
        path,
        health=100,
        speed=90,
        reward=15,
        radius=20,
        colour=PURPLE,
        name="Rattata"
    ):
        super().__init__()

        self.path = path
        self.path_index = 1

        self.position = pygame.Vector2(path[0])

        self.max_health = health
        self.health = health

        self.speed = speed
        self.reward = reward
        self.radius = radius
        self.colour = colour
        self.name = name

        self.reached_end = False
        self.defeated = False

        image_size = radius * 2 + 8

        self.image = pygame.Surface(
            (image_size, image_size),
            pygame.SRCALPHA
        )

        centre = image_size // 2

        pygame.draw.circle(
            self.image,
            self.colour,
            (centre, centre),
            radius
        )

        pygame.draw.circle(
            self.image,
            BLACK,
            (centre, centre),
            radius,
            3
        )

        # Twee simpele ogen
        pygame.draw.circle(
            self.image,
            WHITE,
            (centre - 7, centre - 4),
            5
        )

        pygame.draw.circle(
            self.image,
            WHITE,
            (centre + 7, centre - 4),
            5
        )

        pygame.draw.circle(
            self.image,
            BLACK,
            (centre - 6, centre - 4),
            2
        )

        pygame.draw.circle(
            self.image,
            BLACK,
            (centre + 6, centre - 4),
            2
        )

        self.rect = self.image.get_rect(center=self.position)

    def update(self, dt):
        """Beweeg naar het volgende waypoint."""
        if self.path_index >= len(self.path):
            self.reached_end = True
            self.kill()
            return

        target = pygame.Vector2(self.path[self.path_index])
        direction = target - self.position

        distance = direction.length()
        movement_distance = self.speed * dt

        if distance <= movement_distance:
            self.position = target
            self.path_index += 1
        elif distance > 0:
            self.position += direction.normalize() * movement_distance

        self.rect.center = (
            round(self.position.x),
            round(self.position.y)
        )

    def take_damage(self, damage):
        """
        Brengt damage toe.

        Geeft True terug als de vijand door deze aanval wordt verslagen.
        """
        if self.defeated:
            return False

        self.health -= damage

        if self.health <= 0:
            self.health = 0
            self.defeated = True
            self.kill()
            return True

        return False

    def get_progress(self):
        """
        Geeft aan hoe ver de vijand op het pad is.
        Wordt gebruikt voor first targeting.
        """
        if self.path_index >= len(self.path):
            return float("inf")

        current_target = pygame.Vector2(self.path[self.path_index])
        distance_to_target = self.position.distance_to(current_target)

        return self.path_index * 10000 - distance_to_target

    def draw_health_bar(self, surface):
        """Tekent een healthbar boven de vijand."""
        bar_width = self.radius * 2
        bar_height = 7

        x = self.rect.centerx - bar_width // 2
        y = self.rect.top - 12

        background_rect = pygame.Rect(
            x,
            y,
            bar_width,
            bar_height
        )

        health_percentage = self.health / self.max_health

        health_rect = pygame.Rect(
            x,
            y,
            round(bar_width * health_percentage),
            bar_height
        )

        pygame.draw.rect(surface, DARK_RED, background_rect)
        pygame.draw.rect(surface, GREEN, health_rect)
        pygame.draw.rect(surface, BLACK, background_rect, 1)


# =========================================================
# PROJECTIEL
# =========================================================

class Projectile(pygame.sprite.Sprite):
    def __init__(self, position, target, damage):
        super().__init__()

        self.position = pygame.Vector2(position)
        self.target = target
        self.damage = damage

        self.speed = 500
        self.radius = 8

        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)

        pygame.draw.circle(
            self.image,
            WHITE,
            (10, 10),
            self.radius + 2
        )

        pygame.draw.circle(
            self.image,
            YELLOW,
            (10, 10),
            self.radius
        )

        pygame.draw.circle(
            self.image,
            YELLOW_DARK,
            (10, 10),
            self.radius,
            2
        )

        self.rect = self.image.get_rect(center=self.position)

    def update(self, dt, game):
        """Vliegt naar het doelwit en doet damage."""
        if not self.target.alive():
            self.kill()
            return

        direction = self.target.position - self.position
        distance = direction.length()

        movement_distance = self.speed * dt

        if distance <= movement_distance + self.target.radius:
            defeated = self.target.take_damage(self.damage)

            if defeated:
                game.money += self.target.reward
                game.score += self.target.reward * 10

            self.kill()
            return

        if distance > 0:
            self.position += direction.normalize() * movement_distance

        self.rect.center = (
            round(self.position.x),
            round(self.position.y)
        )


# =========================================================
# TOREN
# =========================================================

class Tower(pygame.sprite.Sprite):
    def __init__(self, position, projectile_group):
        super().__init__()

        self.position = pygame.Vector2(position)
        self.projectile_group = projectile_group

        self.range = TOWER_RANGE
        self.damage = TOWER_DAMAGE
        self.attack_delay = TOWER_ATTACK_DELAY
        self.cooldown = random.uniform(0, 0.2)

        self.radius = 27

        self.image = pygame.Surface((64, 64), pygame.SRCALPHA)

        # Pikachu-achtige oren
        pygame.draw.polygon(
            self.image,
            YELLOW,
            [(15, 20), (9, 2), (25, 17)]
        )

        pygame.draw.polygon(
            self.image,
            YELLOW,
            [(49, 20), (55, 2), (39, 17)]
        )

        # Hoofd
        pygame.draw.circle(
            self.image,
            YELLOW,
            (32, 34),
            25
        )

        pygame.draw.circle(
            self.image,
            BLACK,
            (32, 34),
            25,
            3
        )

        # Ogen
        pygame.draw.circle(
            self.image,
            BLACK,
            (23, 30),
            4
        )

        pygame.draw.circle(
            self.image,
            BLACK,
            (41, 30),
            4
        )

        # Wangen
        pygame.draw.circle(
            self.image,
            RED,
            (17, 42),
            6
        )

        pygame.draw.circle(
            self.image,
            RED,
            (47, 42),
            6
        )

        self.rect = self.image.get_rect(center=self.position)

    def find_target(self, enemies):
        """Zoekt de vijand die het verst op de route is."""
        possible_targets = []

        for enemy in enemies:
            if enemy.defeated:
                continue

            distance = self.position.distance_to(enemy.position)

            if distance <= self.range:
                possible_targets.append(enemy)

        if not possible_targets:
            return None

        return max(
            possible_targets,
            key=lambda enemy: enemy.get_progress()
        )

    def update(self, dt, enemies):
        """Zoekt en beschiet automatisch een doelwit."""
        self.cooldown -= dt

        if self.cooldown > 0:
            return

        target = self.find_target(enemies)

        if target is not None:
            projectile = Projectile(
                self.position,
                target,
                self.damage
            )

            self.projectile_group.add(projectile)
            self.cooldown = self.attack_delay

    def draw_range(self, surface):
        """Laat het bereik van de toren zien."""
        range_surface = pygame.Surface(
            (self.range * 2, self.range * 2),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            range_surface,
            (255, 255, 255, 35),
            (self.range, self.range),
            self.range
        )

        pygame.draw.circle(
            range_surface,
            (255, 255, 255, 110),
            (self.range, self.range),
            self.range,
            2
        )

        surface.blit(
            range_surface,
            (
                self.position.x - self.range,
                self.position.y - self.range
            )
        )


# =========================================================
# SPEL
# =========================================================

class Game:
    def __init__(self):
        self.enemies = pygame.sprite.Group()
        self.towers = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()

        self.money = STARTING_MONEY
        self.lives = STARTING_LIVES
        self.score = 0

        self.wave = 0
        self.wave_active = False
        self.waves_completed = 0

        self.enemies_to_spawn = 0
        self.spawned_enemies = 0

        self.spawn_timer = 0
        self.spawn_delay = 0.8

        self.game_over = False
        self.game_won = False
        self.paused = False

        self.message = "Druk op SPATIE om wave 1 te starten"
        self.message_timer = 4

        self.selected_tower = None

    def show_message(self, message, duration=2):
        self.message = message
        self.message_timer = duration

    def start_next_wave(self):
        """Start de volgende wave."""
        if self.game_over or self.game_won:
            return

        if self.wave_active:
            self.show_message("De huidige wave is nog bezig")
            return

        if len(self.enemies) > 0:
            self.show_message("Versla eerst alle vijanden")
            return

        if self.wave >= MAX_WAVES:
            return

        self.wave += 1
        self.wave_active = True

        self.spawned_enemies = 0
        self.spawn_timer = 0

        if self.wave == 1:
            self.enemies_to_spawn = 8
            self.spawn_delay = 0.90
        elif self.wave == 2:
            self.enemies_to_spawn = 12
            self.spawn_delay = 0.75
        elif self.wave == 3:
            self.enemies_to_spawn = 16
            self.spawn_delay = 0.62
        elif self.wave == 4:
            self.enemies_to_spawn = 20
            self.spawn_delay = 0.50
        elif self.wave == 5:
            # 14 normale vijanden en daarna één Snorlax-boss
            self.enemies_to_spawn = 15
            self.spawn_delay = 0.65

        self.show_message(f"Wave {self.wave} gestart!", 2)

    def create_enemy(self):
        """Maakt een vijand die bij de huidige wave past."""
        enemy_number = self.spawned_enemies

        # Boss als laatste vijand van wave 5
        if self.wave == 5 and enemy_number == self.enemies_to_spawn - 1:
            return Enemy(
                path=PATH,
                health=900,
                speed=38,
                reward=150,
                radius=34,
                colour=(70, 120, 200),
                name="Snorlax"
            )

        health = 65 + self.wave * 25
        speed = 65 + self.wave * 7
        reward = 10 + self.wave * 2

        # Iedere vijfde vijand is sneller
        if enemy_number > 0 and enemy_number % 5 == 0:
            return Enemy(
                path=PATH,
                health=round(health * 0.7),
                speed=round(speed * 1.65),
                reward=reward + 5,
                radius=17,
                colour=(110, 95, 180),
                name="Zubat"
            )

        return Enemy(
            path=PATH,
            health=health,
            speed=speed,
            reward=reward,
            radius=20,
            colour=PURPLE,
            name="Rattata"
        )

    def handle_spawning(self, dt):
        """Spawnt vijanden tijdens een actieve wave."""
        if not self.wave_active:
            return

        if self.spawned_enemies >= self.enemies_to_spawn:
            return

        self.spawn_timer -= dt

        if self.spawn_timer <= 0:
            enemy = self.create_enemy()
            self.enemies.add(enemy)

            self.spawned_enemies += 1
            self.spawn_timer = self.spawn_delay

    def can_place_tower(self, position):
        """Controleert of een toren op deze positie geplaatst mag worden."""
        x, y = position

        # Houd afstand van schermranden en interface
        if x < 40 or x > WIDTH - 40:
            return False

        if y < 95 or y > HEIGHT - 40:
            return False

        # Torens mogen niet op het pad staan
        if is_position_on_path(position, extra_distance=34):
            return False

        # Torens mogen niet bovenop elkaar staan
        for tower in self.towers:
            if tower.position.distance_to(position) < 75:
                return False

        return True

    def place_tower(self, position):
        """Plaatst een Pikachu-toren."""
        if self.game_over or self.game_won:
            return

        if self.money < TOWER_COST:
            self.show_message("Niet genoeg geld!")
            return

        if not self.can_place_tower(position):
            self.show_message("Je kunt hier geen toren plaatsen")
            return

        tower = Tower(position, self.projectiles)
        self.towers.add(tower)

        self.money -= TOWER_COST
        self.selected_tower = tower

        self.show_message("Pikachu geplaatst!", 1)

    def select_tower(self, position):
        """Selecteert een bestaande toren."""
        selected = None

        for tower in self.towers:
            if tower.rect.collidepoint(position):
                selected = tower
                break

        self.selected_tower = selected
        return selected is not None

    def handle_enemy_results(self):
        """Verwerkt vijanden die het einde hebben bereikt."""
        for enemy in list(self.enemies):
            if enemy.reached_end:
                self.lives -= 1

                # Enemy is normaal al verwijderd door kill(),
                # maar dit voorkomt problemen bij latere wijzigingen.
                enemy.kill()

                if self.lives <= 0:
                    self.lives = 0
                    self.game_over = True
                    self.wave_active = False
                    self.show_message("Game over", 5)

    def check_wave_finished(self):
        """Controleert of alle vijanden van de wave verslagen zijn."""
        all_spawned = (
            self.spawned_enemies >= self.enemies_to_spawn
        )

        no_enemies_left = len(self.enemies) == 0

        if self.wave_active and all_spawned and no_enemies_left:
            self.wave_active = False
            self.waves_completed += 1

            wave_bonus = self.wave * 30
            self.money += wave_bonus
            self.score += wave_bonus * 5

            if self.wave >= MAX_WAVES:
                self.game_won = True
                self.show_message("Alle waves voltooid!", 5)
            else:
                self.show_message(
                    f"Wave voltooid! Bonus: ${wave_bonus}. "
                    f"Druk op SPATIE voor wave {self.wave + 1}",
                    4
                )

    def update(self, dt):
        """Update alle spelobjecten."""
        if self.paused or self.game_over or self.game_won:
            return

        if self.message_timer > 0:
            self.message_timer -= dt

        self.handle_spawning(dt)

        self.enemies.update(dt)

        for tower in self.towers:
            tower.update(dt, self.enemies)

        for projectile in list(self.projectiles):
            projectile.update(dt, self)

        self.handle_enemy_results()
        self.check_wave_finished()

    def draw_interface(self, surface):
        """Tekent de bovenste interface."""
        interface_rect = pygame.Rect(0, 0, WIDTH, 82)
        pygame.draw.rect(surface, (34, 41, 48), interface_rect)
        pygame.draw.line(surface, WHITE, (0, 82), (WIDTH, 82), 2)

        draw_text(
            surface,
            f"Geld: ${self.money}",
            FONT_MEDIUM,
            YELLOW,
            (25, 13)
        )

        draw_text(
            surface,
            f"Levens: {self.lives}",
            FONT_MEDIUM,
            RED,
            (25, 44)
        )

        draw_text(
            surface,
            f"Wave: {self.wave}/{MAX_WAVES}",
            FONT_MEDIUM,
            WHITE,
            (260, 13)
        )

        draw_text(
            surface,
            f"Score: {self.score}",
            FONT_MEDIUM,
            WHITE,
            (260, 44)
        )

        draw_text(
            surface,
            f"Pikachu: ${TOWER_COST}",
            FONT_MEDIUM,
            YELLOW,
            (510, 13)
        )

        draw_text(
            surface,
            "Klik op het gras om te plaatsen",
            FONT_SMALL,
            WHITE,
            (510, 49)
        )

        wave_status = "BEZIG" if self.wave_active else "KLAAR"

        draw_text(
            surface,
            f"Wave-status: {wave_status}",
            FONT_MEDIUM,
            GREEN if self.wave_active else WHITE,
            (900, 13)
        )

        draw_text(
            surface,
            "SPATIE = start wave | P = pauze",
            FONT_SMALL,
            LIGHT_GREY,
            (900, 49)
        )

    def draw_placement_preview(self, surface):
        """Laat zien waar een toren geplaatst wordt."""
        if self.game_over or self.game_won:
            return

        mouse_position = pygame.mouse.get_pos()

        if mouse_position[1] < 82:
            return

        valid = (
            self.can_place_tower(mouse_position)
            and self.money >= TOWER_COST
        )

        preview_colour = (
            (80, 230, 110, 110)
            if valid
            else (230, 65, 65, 110)
        )

        range_surface = pygame.Surface(
            (TOWER_RANGE * 2, TOWER_RANGE * 2),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            range_surface,
            preview_colour,
            (TOWER_RANGE, TOWER_RANGE),
            TOWER_RANGE
        )

        pygame.draw.circle(
            range_surface,
            preview_colour[:3] + (200,),
            (TOWER_RANGE, TOWER_RANGE),
            TOWER_RANGE,
            2
        )

        surface.blit(
            range_surface,
            (
                mouse_position[0] - TOWER_RANGE,
                mouse_position[1] - TOWER_RANGE
            )
        )

        pygame.draw.circle(
            surface,
            YELLOW if valid else RED,
            mouse_position,
            27
        )

        pygame.draw.circle(
            surface,
            BLACK,
            mouse_position,
            27,
            3
        )

    def draw_message(self, surface):
        if self.message_timer <= 0 or not self.message:
            return

        text_surface = FONT_MEDIUM.render(
            self.message,
            True,
            WHITE
        )

        padding = 18

        box_rect = text_surface.get_rect(
            center=(WIDTH // 2, HEIGHT - 45)
        )

        background_rect = box_rect.inflate(
            padding * 2,
            padding
        )

        message_surface = pygame.Surface(
            background_rect.size,
            pygame.SRCALPHA
        )

        message_surface.fill((15, 15, 15, 200))

        surface.blit(
            message_surface,
            background_rect.topleft
        )

        pygame.draw.rect(
            surface,
            WHITE,
            background_rect,
            2,
            border_radius=8
        )

        surface.blit(text_surface, box_rect)

    def draw_end_screen(self, surface):
        """Tekent het win- of game-over-scherm."""
        if not self.game_over and not self.game_won:
            return

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill((0, 0, 0, 190))
        surface.blit(overlay, (0, 0))

        title = (
            "Jij hebt gewonnen!"
            if self.game_won
            else "Game over"
        )

        title_colour = GREEN if self.game_won else RED

        draw_text(
            surface,
            title,
            FONT_LARGE,
            title_colour,
            (WIDTH // 2, HEIGHT // 2 - 90),
            center=True
        )

        draw_text(
            surface,
            f"Eindscore: {self.score}",
            FONT_MEDIUM,
            WHITE,
            (WIDTH // 2, HEIGHT // 2),
            center=True
        )

        draw_text(
            surface,
            f"Waves voltooid: {self.waves_completed}/{MAX_WAVES}",
            FONT_MEDIUM,
            WHITE,
            (WIDTH // 2, HEIGHT // 2 + 45),
            center=True
        )

        draw_text(
            surface,
            "Druk op R om opnieuw te beginnen",
            FONT_MEDIUM,
            YELLOW,
            (WIDTH // 2, HEIGHT // 2 + 105),
            center=True
        )

    def draw_pause_screen(self, surface):
        if not self.paused:
            return

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        draw_text(
            surface,
            "GEPAUZEERD",
            FONT_LARGE,
            WHITE,
            (WIDTH // 2, HEIGHT // 2),
            center=True
        )

        draw_text(
            surface,
            "Druk op P om verder te gaan",
            FONT_MEDIUM,
            YELLOW,
            (WIDTH // 2, HEIGHT // 2 + 70),
            center=True
        )

    def draw(self, surface):
        """Tekent het complete spel."""
        draw_background(surface)
        draw_path(surface)

        if self.selected_tower in self.towers:
            self.selected_tower.draw_range(surface)

        self.draw_placement_preview(surface)

        self.towers.draw(surface)
        self.enemies.draw(surface)
        self.projectiles.draw(surface)

        for enemy in self.enemies:
            enemy.draw_health_bar(surface)

        self.draw_interface(surface)
        self.draw_message(surface)
        self.draw_pause_screen(surface)
        self.draw_end_screen(surface)


# =========================================================
# MAIN GAME LOOP
# =========================================================

def main():
    game = Game()
    running = True

    while running:
        dt = CLOCK.tick(FPS) / 1000

        # Voorkomt grote sprongen als het venster tijdelijk bevriest
        dt = min(dt, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_SPACE:
                    if not game.paused:
                        game.start_next_wave()

                elif event.key == pygame.K_p:
                    if not game.game_over and not game.game_won:
                        game.paused = not game.paused

                elif event.key == pygame.K_r:
                    if game.game_over or game.game_won:
                        game = Game()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not game.paused:
                    if event.pos[1] > 82:
                        clicked_tower = game.select_tower(event.pos)

                        if not clicked_tower:
                            game.place_tower(event.pos)

                elif event.button == 3:
                    game.selected_tower = None

        game.update(dt)
        game.draw(SCREEN)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()