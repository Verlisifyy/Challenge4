from pathlib import Path
import random
import pygame

pygame.init()

# Venster instellen
breedte = 800
hoogte = 600
scherm = pygame.display.set_mode((breedte, hoogte))
pygame.display.set_caption("Flappy Bird")
klok = pygame.time.Clock()


# Vogelafbeelding laden
afbeelding_pad = Path(__file__).with_name("flappy.png")
vogel_afbeelding = pygame.image.load(str(afbeelding_pad)).convert_alpha()
vogel_afbeelding = pygame.transform.scale(vogel_afbeelding, (48, 48))

groot_lettertype = pygame.font.Font(None, 70)
klein_lettertype = pygame.font.Font(None, 32)
score_lettertype = pygame.font.Font(None, 45)

# Instellingen van de vogel
vogel_x = 100
vogel_y = 250
snelheid_y = 0
zwaartekracht = 0.5
sprongkracht = -9

# Instellingen van de pijpen
pijp_x = breedte
pijp_breedte = 80
pijp_snelheid = 4
opening_grootte = 180
opening_y = random.randint(120, 300)

score = 0
punt_gegeven = False
game_over = False
programma_draait = True

while programma_draait:

    # Besturing
    for gebeurtenis in pygame.event.get():

        if gebeurtenis.type == pygame.QUIT:
            programma_draait = False

        if gebeurtenis.type == pygame.KEYDOWN:

            # Springen met spatie
            if gebeurtenis.key == pygame.K_SPACE and not game_over:
                snelheid_y = sprongkracht

            # Spel resetten met L
            if gebeurtenis.key == pygame.K_l and game_over:
                vogel_y = 250
                snelheid_y = 0
                pijp_x = breedte
                opening_y = random.randint(120, 300)
                score = 0
                punt_gegeven = False
                game_over = False

    if not game_over:

        # Zwaartekracht en beweging van de vogel
        snelheid_y += zwaartekracht
        vogel_y += snelheid_y

        # Pijpen naar links bewegen
        pijp_x -= pijp_snelheid

        # Pijpen opnieuw rechts plaatsen
        if pijp_x + pijp_breedte < 0:
            pijp_x = breedte
            opening_y = random.randint(120, 300)
            punt_gegeven = False

        # Onzichtbare rechthoeken voor botsingen
        vogel_vak = pygame.Rect(
            vogel_x,
            int(vogel_y),
            vogel_afbeelding.get_width(),
            vogel_afbeelding.get_height()
        )

        bovenste_pijp = pygame.Rect(
            pijp_x,
            0,
            pijp_breedte,
            opening_y
        )

        onderste_pijp_y = opening_y + opening_grootte

        onderste_pijp = pygame.Rect(
            pijp_x,
            onderste_pijp_y,
            pijp_breedte,
            hoogte - onderste_pijp_y
        )

        # Botsing met het dak of de bodem
        if vogel_y <= 0:
            vogel_y = 0
            snelheid_y = 0
            game_over = True

        if vogel_y + vogel_afbeelding.get_height() >= hoogte:
            vogel_y = hoogte - vogel_afbeelding.get_height()
            snelheid_y = 0
            game_over = True

        # Botsing met de pijpen
        if vogel_vak.colliderect(bovenste_pijp):
            game_over = True

        if vogel_vak.colliderect(onderste_pijp):
            game_over = True

        # Punt geven wanneer de vogel de pijp passeert
        if pijp_x + pijp_breedte < vogel_x and not punt_gegeven:
            score += 1
            punt_gegeven = True

    # Pijpen maken voor het tekenen
    bovenste_pijp = pygame.Rect(
        pijp_x,
        0,
        pijp_breedte,
        opening_y
    )

    onderste_pijp_y = opening_y + opening_grootte

    onderste_pijp = pygame.Rect(
        pijp_x,
        onderste_pijp_y,
        pijp_breedte,
        hoogte - onderste_pijp_y
    )

    # Spel tekenen
    scherm.fill((135, 206, 235))

    pygame.draw.rect(scherm, (40, 180, 60), bovenste_pijp)
    pygame.draw.rect(scherm, (40, 180, 60), onderste_pijp)

    pygame.draw.rect(scherm, (20, 100, 35), bovenste_pijp, 4)
    pygame.draw.rect(scherm, (20, 100, 35), onderste_pijp, 4)

    scherm.blit(vogel_afbeelding, (vogel_x, vogel_y))

    score_tekst = score_lettertype.render(
        f"Score: {score}",
        True,
        (255, 255, 255)
    )
    scherm.blit(score_tekst, (20, 20))

    # Game-overtekst tonen
    if game_over:
        game_over_tekst = groot_lettertype.render(
            "GAME OVER",
            True,
            (220, 30, 30)
        )

        reset_tekst = klein_lettertype.render(
            "Druk op L om opnieuw te beginnen",
            True,
            (30, 30, 30)
        )

        game_over_vak = game_over_tekst.get_rect(
            center=(breedte // 2, hoogte // 2)
        )

        reset_vak = reset_tekst.get_rect(
            center=(breedte // 2, hoogte // 2 + 60)
        )

        scherm.blit(game_over_tekst, game_over_vak)
        scherm.blit(reset_tekst, reset_vak)

    pygame.display.flip()
    klok.tick(60)

pygame.quit()