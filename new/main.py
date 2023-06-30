import pygame
import matplotlib.pyplot as plt
from settings import *
from Car import Car
pygame.init()


class Simulation:
    """
    Classe prennant en charge l'affichage et génère le rendu

    ...

    Attributes
    ----------
    None

    Methods
    -------
    initialise():
        Créée tous les attributs à chaque début de simulation.

    """

    def  __init__(self):
        """
        Construit tous les  attributs nécessaires pour l'objet voiture.

        Parameters
        ----------
        None
        """

        # affichage
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.frame = 0
        self.dt = 0

        # gestion d'apparition des voitures
        time, speed, road = load()
        self.apparition = {"time": time, "speed": speed, "road": road}
        self.rest = True

        self.initialise()

    def initialise(self):
        """
        Créée tous les attributs à chaque début de simulation.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        # lié au temps
        self.clock = pygame.time.Clock()
        self.frame = 0
        # pour le graph
        self.list_x = []
        self.list_t = []
        self.changeline = []

        # groupes de cars
        self.cars = pygame.sprite.Group()  # groupe des voitures
        self.cars_sort = []
        if self.rest:
            if DEFAULT:
                self.restrictions = ROAD_BEG
            else:
                self.restrictions = restriction()

        # pour le tracer des routes
        self.road = [((0, Y_ROAD[1]),(WIDTH, Y_ROAD[1]))]
        last_2 = True
        dist_2 = 0
        last_0 = True
        dist_0 = 0
        for rest in self.restrictions:
            # si on passe de 3 à moins de voies
            if rest[2]<3 and last_0:
                self.end_line(rest[0],0)
                last_0 = False
                self.road.append(((dist_0, Y_ROAD[0]), (rest[0], Y_ROAD[0])))
            # si on repasse à 3 voies
            elif rest[2]==3 and not last_0:
                last_0 = True
                dist_0 = rest[0]
            # si on passe de 2 à 1 voie
            if rest[2] < 2 and last_2:
                self.end_line(rest[0],2)
                last_2  = False
                self.road.append(((dist_2, Y_ROAD[2]), (rest[0], Y_ROAD[2])))
            # si la 2ème voie est de nouveau présente
            elif rest[2]>=2 and not last_2:
                last_2 = True
                dist_2 = rest[0]
        if last_0:
            self.road.append(((dist_0, Y_ROAD[0]), (WIDTH, Y_ROAD[0])))
        if last_2:
            self.road.append(((dist_2, Y_ROAD[2]), (WIDTH, Y_ROAD[2])))

    def end_line(self, x, road):
        """
        Créée une voiture morte au bout d'une fin de voie

        Parameters
        ----------
        x : float
            abscisse de la voiture
        road : int
            voie sur laquelle on voudrait la positionner

        Returns
        -------
        None
        """

        end = Car("end",road, 1, 1, self,[self.cars], (x + CAR_DIM[0] / 2) * ALPHA)
        self.cars_sort.append(end)

    def spawn(self):
        """
        """
        # on regarde si on doit faire apparaitre une voiture
        if not self.frame in self.apparition["time"]:
            return None
        name = self.apparition["time"].index(self.frame)
        car = Car(name,
                  self.apparition["road"][name],
                  self.apparition["speed"][name],
                  V0,
                  self,
                  [self.cars])
        self.cars_sort.append(car)
        self.get_leader(car)

    def get_leader(self, car):
        """
        On donne à la voiture qui vient d'être créée un meneur.

        Parameters
        ----------
        car : Car
            voiture pour laquelle on cherche un meneur

        Returns
        -------
        None
        """

        i = 0
        while i < len(self.cars_sort) and car.leader is None:
            specimen = self.cars_sort[i]
            if specimen.road == car.road and car!=specimen: # on n'a pas besoin de vérifier si le spécimen est devant
                car.leader = specimen
            i+=1

    def remove(self, car):
        """
        Enlève une voiture de la simulation.

        Parameters
        ----------
        car : Car
            voiture qu'on souhaiterait supprimer

        Returns
        -------
        None
        """

        self.list_x.append([car.x[i] for i in range(len(car.x)) if i % 5 == 0])
        self.list_t.append((car.name, [car.time[i] for i in range(len(car.time)) if i % 5 == 0]))

        # on le supprime de l'ensemble des voitures
        self.cars.remove(car)
        # on le supprime dans la liste des voitures classées
        del self.cars_sort[self.cars_sort.index(car)]

        # on l'enlève comme meneur pour la voiture qui l'avait
        for car2 in self.cars:
            if car2.leader == car:
                car2.leader = None

    def change_line(self):
        """
        Enregistre un changement de voie.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        self.changeline.append(pygame.time.get_ticks()*1e-3) # on enregistre un changement de voie

    def show_graph(self):
        """
        Affiche la courbe en position des voitures ainsi que les changements de voies.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        # on affiche la position (x) en fonction du temps
        for i in self.changeline:
            plt.figure(1)
            plt.plot([i,i], [0, DISTANCE], "--", color= COLOR["linechange"], alpha=0.5)
        for i in range(len(self.list_t)):
            plt.figure(1)
            plt.plot(self.list_t[i][1], self.list_x[i], '-', label=self.list_t[i][0])
        for car in self.cars:
            plt.figure(1)
            plt.plot(car.time, car.x, '-', label=car.name)
        plt.ylim(0, DISTANCE)
        plt.grid()
        plt.legend()
        plt.show()

    def draw(self):
        """
        Affiche l'environnement, un repère ainsi que les voitures dans la fenêtre.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        # on dessine d'abord le fond
        self.screen.fill(COLOR['background'])

        # on dessine un repère
        pygame.draw.line(self.screen, COLOR['road'],(10,120),(DIST_REP/ALPHA,120), 3)
        pygame.draw.line(self.screen, COLOR['road'],(10,125),(10,115), 3)
        pygame.draw.line(self.screen, COLOR['road'],(DIST_REP/ALPHA,125),(DIST_REP/ALPHA,115), 3)
        surf = FONT.render(str(f"{DIST_REP}m"), True, 'White')
        rect = surf.get_rect(topleft=(10, 90))
        self.screen.blit(surf,rect)

        # puis les routes
        for pos in self.road:
            pygame.draw.line(self.screen, COLOR['road'],*pos, SIZE_ROAD)

    def update(self):
        """
        Actualise à chaque image les voitures.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        self.cars.update()

    def run(self):
        """
        Boucle permettant l'affichage et l'acquisition des différents événements

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        cooldown = 1e3
        time = 0
        print(SLICE)
        print("pour quitter la simulation:          échap")
        print("pour relancer la simulation:         r")
        print("pour voir les résultats et autre:    espace")
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or pygame.key.get_pressed()[pygame.K_ESCAPE]:
                    pygame.quit()
                elif pygame.key.get_pressed()[pygame.K_SPACE]:
                    print(SLICE)
                    print("/!\ les résultats suivants ceux-ci seront inutilisables,")
                    print("il est conseillé de relancer la simulation (appuyer sur 'r')")
                    self.show_graph()
                elif pygame.key.get_pressed()[pygame.K_r]:
                    if pygame.time.get_ticks()-time > cooldown:
                        if not DEFAULT:
                            print(SLICE)
                            self.rest = bool(input("si vous voulez les mêmes restrictions appuyez sur entrée sinon écrivez n'importe quoi\n"))
                        self.initialise()
                        time = pygame.time.get_ticks()
            self.spawn()
            self.cars_sort.sort(key=lambda x: x.pos[0]) # on trie la liste
            self.draw()
            self.update()
            pygame.display.update()  # rafraichissement de la page
            self.dt = self.clock.tick(FPS) * 1e-3  # temps entre chaque actualisation en seconde
            self.frame +=1

if __name__ == '__main__':
    # lancement du programme
    simu = Simulation()
    simu.run()

