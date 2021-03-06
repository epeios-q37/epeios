# coding: utf-8

import sys
sys.path.append(".")
from workshop.fr.z_3 import *

from random import randint


DICTIONNAIRE = [
    "armoire",
    "boucle",
    "buisson",
    "bureau",
    "chaise",
    "carton",
    "couteau",
    "fichier",
    "garage",
    "glace",
    "journal",
    "kiwi",
    "lampe",
    "liste",
    "montagne",
    "remise",
    "sandale",
    "taxi",
    "vampire",
    "volant",
]


class Pendu:
    def raz(self):
        self.nbErreurs = 0
        self.bonnesPioches = []
        self.motSecret = ""

    def __init__(self):
        self.raz()


PENDU = [P_TETE, P_CORPS, P_BRAS_GAUCHE,
         P_BRAS_DROIT, P_PIED_GAUCHE, P_PIED_DROIT]


def obtenirMot():
    return DICTIONNAIRE[randint(0, len(DICTIONNAIRE)-1)]


def majDessin(nbErreurs):
    if (nbErreurs):
        dessinePendu(PENDU[nbErreurs-1])


def majMasque(motSecret, bonnesPioches):
    masque = ("_" * len(motSecret))

    for i in range(len(motSecret)):
        if motSecret[i] in bonnesPioches:
            masque = masque[:i] + motSecret[i] + masque[i + 1:]

    effaceEtAffiche(masque)


def raz(pendu):
    redessine()
    pendu.raz()
    pendu.motSecret = obtenirMot()
    print(pendu.motSecret)
    majMasque(pendu.motSecret, pendu.bonnesPioches)


def connexion(pendu):
    raz(pendu)


def pioche(pendu, pioche):
    if pioche in pendu.motSecret:
        pendu.bonnesPioches.append(pioche)

        exact = 0

        for i in range(len(pendu.motSecret)):
            if pendu.motSecret[i] in pendu.bonnesPioches:
                exact += 1

        majMasque(pendu.motSecret, pendu.bonnesPioches)

        if exact == len(pendu.motSecret):
            alerte("Tu as gagné ! Félicitations !")
            raz(pendu)
            return
    else:
        pendu.nbErreurs += 1
        majDessin(pendu.nbErreurs)

    if pendu.nbErreurs >= len(PENDU):
        dessinePendu(P_VISAGE)
        alerte("\nPerdu !\nErreurs : " + str(pendu.nbErreurs) +
               " ; bonnes pioches : " + str(len(pendu.bonnesPioches)) +
               "\n\nLe mot à deviner était : '" + pendu.motSecret + "'.")
        raz(pendu)


def redemarrer(pendu):
    if (pendu.motSecret != ""):
        alerte("Erreurs : " + str(pendu.nbErreurs) +
               " ; bonnes pioches : " + str(len(pendu.bonnesPioches)) +
               "\n\nLe mot à deviner était : '" + pendu.motSecret + "'.")

    raz(pendu)


go(globals())
