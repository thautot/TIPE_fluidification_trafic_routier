import pygame
import random as rd
from settings import *
pygame.init()


class Car(pygame.sprite.Sprite):
    """
    Classe permettant de faire apparaître des voitures.

    ...

    Attributes
    ----------
    name : str
        chaîne de caractères correspondant au nom de la voiture
    road : int
        compris entre 0 et 2, signifiant la voie de la voiture
    velocity_init : float
        la vitesse initiale de la voiture
    v0 : float
        la vitesse désirée sur la portion de route
    simu : class
        la simulation qui fait appel à "Car"
    group :pygame.sprite.Group
        groupe auquel la voiture appartient
    x : list
        ensemble des positions en abscisse
    time : list
        ensemble des temps de prélévement des positions
    acceleration : float
        accélération du véhicule
    P : float
        facteur de politesse
    pos : list
        position [x,y]
    rect : pygame.Rect
        dimension du véhicule
    cooldown_change_line : float
        temps entre chaque changement de ligne
    cooldown_time : float
        temps du dernier changement de voie
    display_surface : pygame.display
        fenêtre d'affichage
    leader : Car
        meneur actuel de la voiture
    old_leader : Car
        ancien meneur de la voiture
    s : float
        distance entre la voiture et son meneur

    Methods
    -------
    apply_restrictions():
        Appliquer les restrictions indiquées au début de la simulation.
    get_other_cars(new_road):
        Retourne les différentes voitures misent en jeu.
    get_all_acceleration(new_road, s, l, ps, pl, LvR):
        Retourne les accélérations des différents véhicules mis en jeu.
    test(new_road, s, l, LvR):
        Tests de changement de voie en utilisant le modèle MOBIL.
    change_line():
        Fait changer de ligne la voiture si les conditions le permettent.
    get_acceleration( car, leader):
        Donne l'accélération de car en fonction de son meneur (leader).
    move():
        Change la position, vitesse, accélération de la voiture.
    draw():
        Permet d'afficher la voiture dans la fenêtre.
    update():
        Actualise à chaque image la voiture.
    """

    def __init__(self, name, road, velocity_init, v0, simu, group, x=-CAR_DIM[0]*ALPHA/2):
        """
        Construit tous les  attributs nécessaires pour l'objet voiture.

        Parameters
        ----------
        name : str
            chaîne de caractères correspondant au nom de la voiture
        road : int
            compris entre 0 et 2, signifiant la voie de la voiture
        velocity_init : float
            la vitesse initiale de la voiture
        v0 : float
            la vitesse désirée sur la portion de route
        simu : class
            la simulation qui fait appelle à "Car"
        group :pygame.sprite.Group
            groupe auquel la voiture appartient
        x : float
            abscisse à l'apparition
        """

        super().__init__(group)
        self.group = group
        self.name = name
        self.velocity = velocity_init
        self.v0 = v0
        self.acceleration = 0  # la voiture n'est pas censée manoeuvrer à l'initialisation
        self.road = road        # il peut aller de 0 à 2
        self.voies = 3
        self.P = rd.normalvariate(MOYP, SIGMA)  # facteur de politesse

        self.pos = [x, Y_ROAD[road] * ALPHA] # position en mètre
        self.rect = pygame.Rect(- CAR_DIM[0] / 2, 0, *CAR_DIM)
        self.rect.center = [x/ALPHA, Y_ROAD[road]]         # position en pixel

        # on enregistre les différentes positions
        self.x = [self.pos[0]]
        self.time = [pygame.time.get_ticks() * 1e-3]

        self.simu = simu # utilisé pour enlever la voiture et avoir dt

        self.cooldown_change_line = 2e3 # temps entre chaque changement de voie
        self.cooldown_time = pygame.time.get_ticks()

        # différentes fonctions
        self.display_surface = pygame.display.get_surface()
        # lien avec le leader
        self.leader = None  # leader de la voiture pour le modèle de la voiture suiveuse
        self.old_leader = None
        self.s = WIDTH * ALPHA

    def apply_restrictions(self):
        """
        Appliquer les restrictions indiquées au début de la simulation.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        index = 0
        while index + 1<len(self.simu.restrictions) and self.pos[0]/ALPHA + CAR_DIM[0]/2 > self.simu.restrictions[index + 1][0]:
            index +=1
        self.voies = self.simu.restrictions[index][2]
        self.v0 = self.simu.restrictions[index][1]

    def get_other_cars(self, new_road):
        """
        Retourne les différentes voitures misent en jeu.

        Parameters
        ----------
        new_road : int
            voie sur laquelle on veut prendre les voitures

        Returns
        -------
        ps: Car
            voiture potentielle qui nous suivrait sur cette nouvelle voie
        pl: Car
            voiture potentielle qu'on suivrait sur cette nouvelle voie
        """

        cars_sort = self.simu.cars_sort

        indexcar = cars_sort.index(self)
        ps, pl = None, None
        i = indexcar
        # on récupère ps (potentiel suiveur)
        while i > 0 and (ps is None):
            i -= 1
            specimen = cars_sort[i]
            if specimen.road == new_road:
                ps = specimen
        i = indexcar
        # on récupère pl (potentiel leader)
        while i + 1< len(cars_sort) and (pl is None):
            i += 1
            if cars_sort[i].road == new_road:
                pl = cars_sort[i]
        return ps, pl

    def get_all_acceleration(self, new_road, s, l, ps, pl, LvR):
        """
        retourne les accélérations des différents véhicules mis en jeu

        Parameters
        ----------
        new_road : int
            voie sur laquelle on veut prendre les voitures
        s : Car
            l'actuel suiveur
        l : Car
            l'actuel meneur
        ps: Car
            voiture potentielle qui nous suivrait sur cette nouvelle voie
        pl: Car
            voiture potentielle qu'on suivrait sur cette nouvelle voie
        LvR : bool
            si la voiture veut aller de la gauche vers la droite ou non

        Returns
        -------
        tca : float
            accélération de la voiture si elle change de voie
        ca : float
            accélération de la voiture si elle ne change pas de voie
        tpsa : float
            accélération du potentiel suiveur si la voiture change de voie
        psa : float
            accélération du potentiel suiveur si la voiture ne change pas de voie
        tsa : float
            accélération de l'actuel suiveur si la voiture change de voie
        sa :
            accélération de l'actuel suiveur si la voiture ne change pas de voie
        tceura : float
            accélération de la voiture si elle change de voie modifiée
        ceura : float
            accélération de la voiture si elle ne changeait pas de voie modifiée
        """

        ca = self.get_acceleration(self, l)
        tca = self.get_acceleration(self, pl)
        # modèle MOBIL symétrique
        if SYMETRIQUE:
            if s is None:
                sa = 0
                tsa = 0
            else:
                sa = self.get_acceleration(s, self)
                tsa = self.get_acceleration(s, l)

            if ps is None:
                psa = 0
                tpsa = 0
            else:
                psa = self.get_acceleration(ps, pl)
                tpsa = self.get_acceleration(ps, self)
            return tca, ca, tpsa, psa, tsa, sa
        # modèle MOBIL asymétrique de la gauche vers la droite
        elif LvR:
            if s is None:
                sa = 0
                tsa = 0
            else:
                sa = self.get_acceleration(s, self)
                tsa = self.get_acceleration(s, l)
            if ps is None:
                tpsa = 0
            else:
                tpsa = self.get_acceleration(ps, self)

            if l is None or self.velocity <= l.velocity or l.velocity <= VCRIT:
                tceura =tca
            else:
                tceura = min(tca, ca)

            return tpsa, tceura, ca, tsa, sa
        # modèle MOBIL asymétrique de la droite vers la gauche
        else:
            if ps is None:
                psa = 0
                tpsa = 0
            else:
                psa = self.get_acceleration(ps, pl)
                tpsa = self.get_acceleration(ps, self)

            if pl is None or self.velocity <= pl.velocity or pl.velocity <= VCRIT:
                ceura =ca
            else:
                ceura = min(tca, ca)

            return tca, ceura, tpsa, psa

    def test(self, new_road, s, l, LvR):
        """
        Tests de changement de voie en utilisant le modèle MOBIL.

        Parameters
        ----------
        new_road : int
            voie sur laquelle on veut prendre les voitures
        s : Car
            l'actuel suiveur
        l : Car
            l'actuel meneur
        LvR : bool
            si la voiture veut aller de la gauche vers la droite ou non

        Returns
        -------
        change : bool
            s'il y a un changement de voie ou non
        """

        ps, pl = self.get_other_cars(new_road)

        # on récupère la position de tps et ts
        if ps is None:
            pspos = - CAR_DIM[0] * ALPHA
        else:
            pspos = ps.pos[0]
        if pl is None:
            plpos = DISTANCE + CAR_DIM[0] * ALPHA
        else:
            plpos = pl.pos[0]

        # on regarde si les dimensions des voitures permettent le changement de voie
        if self.pos[0] - pspos <= CAR_DIM[0]*ALPHA or plpos - self.pos[0] <= CAR_DIM[0]*ALPHA:
            return False


        if SYMETRIQUE:
            # pour route symétrique (ex: Amérique)
            tca, ca, tpsa, psa, tsa, sa =self.get_all_acceleration(new_road, s, l, ps, pl, LvR)
            change = tpsa >= - Bsafe and (tca - ca +P * ((tpsa - psa) + (tsa - sa)) > Dath)

        else:
            # pour route asymétrique (ex: France)
            if LvR: # de la gauche vers la droite
                tpsa, tceura, ca, tsa, sa= self.get_all_acceleration(new_road, s, l, ps, pl, LvR)
                change = tpsa >= - Bsafe and (tceura - ca + self.P * (tsa - sa) > Dath - Dabias)
            else:   # de la droite vers la gauche
                tca, ceura, tpsa, psa = self.get_all_acceleration(new_road, s, l, ps, pl, LvR)
                change = tpsa >= - Bsafe and (tca - ceura + self.P * (tpsa - psa) > Dath + Dabias)

        if change:
            # on fait le changement des meneurs des différents véhicules
            self.leader = pl
            if not(ps is None):
                ps.leader = self
            if not(s is None):
                s.leader = l
        return change

    def change_line(self):
        """
        Fait changer de ligne la voiture si les conditions le permettent.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        # si notre meneur a changé de voie on prend un temps d'observation
        if self.leader != self.old_leader:
            self.old_leader = self.leader
            self.cooldown_time = pygame.time.get_ticks()

        # on regarde si on peut changer de voie
        if self.voies!=1 and pygame.time.get_ticks()-self.cooldown_time> self.cooldown_change_line:

            change = False
            # on récupère notre meneur
            l = self.leader
            # on récupère la personne qui nous suit
            s = None
            for car in self.simu.cars_sort:
                if car.leader == self:
                    s = car
            road = self.road
            # on teste les deux voies si on est au centre
            if self.road == 1:
                # on teste si on peut aller à droite
                if self.test(2, s, l, True):
                    road = 2
                    change = True
                # on regarde si on a suffisament de voies
                elif self.voies == 3:
                    # on teste si on peut aller à gauche
                    if self.test(0, s, l, False):
                        road = 0
                        change = True

            elif self.road == 2 and self.test(1, s, l, False):
                # on teste si on peut aller à gauche
                road = 1
                change = True
            elif self.test(1, s, l, True):
                # on teste si on peut aller à droite
                road = 1
                change = True
            if change:
                self.cooldown_time = pygame.time.get_ticks()
                self.road = road
                self.pos[1] = Y_ROAD[road]*ALPHA
                self.rect.centery = Y_ROAD[road]
                self.simu.change_line()

    def get_acceleration(self, car, leader):
        """
        Donne l'accélération de car en fonction de son meneur (leader).

        Parameters
        ----------
        car : Car
            voiture pour laquelle on voudrait l'accélération
        leader : Car
            meneur de car

        Returns
        -------
        float
            accélération de car
        """

        if car is None:
            return 0

        # on calcule le "s" et le "s*" de la formule
        if leader is None:  # cas où le meneur est loin
            deltav = 0
            car.s = DISTANCE  # correspond à dire que son meneur est loin
            setoile = S0
        else:
            deltav = car.velocity - leader.velocity
            car.s = leader.pos[0] - car.pos[0] - CAR_DIM[0] * ALPHA  # on remet en mètre
            setoile = S0 + max(0, car.velocity * (T + deltav * INVERTED2SQRTAB))

        return max(MB, A * (1 - (car.velocity / car.v0) ** D - (setoile / car.s) ** 2))

    def move(self):
        """
        Change la position, vitesse, accélération de la voiture.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        dt = self.simu.dt
        # on fait bouger la position
        self.pos[0] = self.pos[0] + self.velocity * dt / ALPHA + (self.acceleration * dt ** 2) / 2
        # puis la vitesse
        self.velocity = max(0,self.velocity + self.acceleration * dt)
        # et enfin l'accélération
        self.acceleration = self.get_acceleration(self, self.leader)
        # on applique la position au rectangle associé
        self.rect.centerx = self.pos[0] / ALPHA
        # et on ajoute la dernière position dans la liste pour la visualiser
        self.x.append(self.pos[0])
        self.time.append(pygame.time.get_ticks() * 1e-3)

        if self.rect.topleft[0] > WIDTH:
            self.simu.remove(self)

    def draw(self):
        """
        Permet d'afficher la voiture dans la fenêtre.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        if self.name == "end":
            pygame.draw.rect(self.display_surface, COLOR['end'], self.rect)
        else:
            pygame.draw.rect(self.display_surface, COLOR['car'], self.rect)

    def update(self):
        """
        Actualise à chaque image la voiture.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        if self.name != "end":
            self.apply_restrictions()
            self.change_line()
            self.move()
        self.draw()