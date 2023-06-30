import pygame
import pyautogui

pygame.init()

# paramêtres qui peuvent être changer
DISTANCE = 1500  # distance en mêtre que vaudrait la portion de route (donc largeur fenêtre)
V0 = 90 / 3.6  # vitesse initiale
VCRIT = 70 / 3.6   # vitesse de congestionnement

# booléen pour uné génération de voie par défaut (évite de rentrer les restrictions)
DEFAULT = False

# données pour IDM
T = 1.5  # s: temps minimal pour faire une manoeuvre d'urgence
S0 = 0.1  # m: distance minimale entre 2 véhicules
A = 0.8  # m/s**2: accélération maximale
D = 4.0  # /: coefficient d'accélération
B = 3  # m/s**2: décélération confortable
INVERTED2SQRTAB = 1 / (2 * (A * B) ** 0.5) # limite le calcul de racines
MB = -9.0 # m/s**2: décélération maximale
DT = 1.5


#données pour MOBI
SYMETRIQUE = False
MOYP = 0.2      # moyenne coefficient d'amabilité sans unité
SIGMA = 0.1     # écart type du coefficient d'amabilité
Bsafe = 3.0     # décélération de sécurité (m.s-2)
Dath= 0.5       # seuil de changement (m.s-2)
Dabias = 0.3    # biais pour la ligne de droite (m.s-2)

# paramètres de la fenêtre de visualisation
WIDTH, HEIGHT = pyautogui.size()[0], 400
FPS = 30

ROAD_BEG = [(0, V0, 2)]     # défini les conditions initiales de la route
ALPHA = DISTANCE / WIDTH    # distance_mêtre = ALPHA * distance_pixel
SIZE_ROAD = int(5 / ALPHA)  # largeur de la route en pixels
CAR_DIM = (5 / ALPHA, SIZE_ROAD + 1)  # dimensions d'une voiture ramenées en pixels


# y des différentes routes
Y_ROAD= [HEIGHT // 2 + SIZE_ROAD * 1.5, HEIGHT // 2, HEIGHT // 2 - SIZE_ROAD * 1.5]

# distance pour le repère
if DISTANCE >=800:
    DIST_REP = max(1,int(DISTANCE/1000))* 100
else:
    DIST_REP = max(1,int(DISTANCE/100)) * 10

# visuel
COLOR = {
    'road': (250, 250, 250),
    'background': (25, 25, 25),
    'car': (250, 25, 27),
    'end':(25,27,250),
    'linechange' : "#606060"
}
SLICE = "\n_.~~~~~~~~~~~~~~~~~~~~~---------------~~~~~~~~~~~~~~~~~~~~~._"
ERREUR = "                         /!\ ERREUR"

FONT = pygame.font.Font(None, 30)

def load():
    """
    Lire le fichier d'apparition et renvoyer les différents paramètres.

    Parameters
    ----------
    None

    Returns
    -------
    time : list
        contient les numéros d'image où apparaît chaque voiture
    speed: list
        contient la vitesse initiale de chaque voiture
    -road: list
        contient la voie sur laquelle la voiture apparaît
    """

    # certaines voitures étaient présente avant le début on doit les enlever
    crop = 6
    with open("assets/apparition.csv", "r") as f:
        # temps d'apparition des voitures
        time = f.readline()[:-1]
        time = [int(i) for i in time.split(",")]

        # vitesse quand la voiture apparaît en mètres par seconde
        speed = f.readline()[:-1]
        speed = [float(i) for i in speed.split(",")]

        # de quel côté la voiture apparaît
        road =f.readline()
        road = [int(i) for i in road.split(",")]
    return tuple(time[crop:]), tuple(speed[crop:]), tuple(road[crop:])

def restriction():
    """
    Permet de définir les restrictions sur la route.

    Parameters
    ----------
    None

    Returns
    -------
    res: list
        ensemble de listes contenant la distance, la vitesse et le nombre de
        voies de chaque changement ex: [[0m, 90km/h, 3],[200m, 120km/h, 2]]
    """

    res = ROAD_BEG
    print(SLICE)
    restr = int(input("voulez-vous des restrictions sur la route ?\n1- oui\n0- non\n"))
    if restr == 1:
        finish = False
        while not finish:
            print(SLICE)
            dist = int(input("à quelle distance ? (en mêtres)\n"))
            print(SLICE)
            change_vit = int(input("changer la vitesse ?\n1-oui\n0-non\n"))
            print(SLICE)
            change_road = int(input("changer le nombre de voies ?\n1-oui\n0-non\n"))
            if dist < DISTANCE:
                if change_vit == 1:
                    print(SLICE)
                    vit = float(input("nouvelle vitesse en km/h :\n"))
                else:
                    vit = res[-1][1] *3.6
                if change_road == 1:
                    print(SLICE)
                    road = int(input("nombre de voies (entre 1 et 3) :\n"))
                else:
                    road = res[-1][2]
                res.append((dist/ALPHA, vit / 3.6, road))
            finish = not(bool(input("si fini pressez entrée, sinon écrivez n'importe quoi\n")))
    res.sort(key=lambda x: x[0])
    print("la simulation se lance")
    return res
