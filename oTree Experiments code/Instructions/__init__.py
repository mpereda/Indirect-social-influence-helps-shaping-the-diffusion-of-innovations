from otree.api import *
import random
import networkx as nx
import django
import json
import numpy as np
import time
from statistics import mode

##Models

class C(BaseConstants):
    NAME_IN_URL = 'Instrucciones_Experimento'
    PLAYERS_PER_GROUP = 31
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    preg1 = models.StringField(widget=widgets.RadioSelectHorizontal, verbose_name='¿Qué color ha escogido usted esta ronda?', choices=["Amarillo", "Azul", "No lo podemos saber"])
    preg2 = models.StringField(widget=widgets.RadioSelectHorizontal, verbose_name='¿Qué color tienen sus amigos?', choices=["Amarillo", "Azul", "No lo podemos saber"])
    preg3 = models.StringField(widget=widgets.RadioSelectHorizontal, verbose_name='¿Qué color tienen los amigos de sus amigos, excluyendole a usted?', choices=["Amarillo", "Azul", "No lo podemos saber"])
    preg4 = models.PositiveIntegerField(verbose_name='¿Cuántos jugadores inactivos hay esta ronda?')
    


# FUNCTIONS
def creating_session(subsession: Subsession):
    for p in subsession.get_players():
        p.participant.extra=False
# PAGES

class Instructions(Page):
    timeout_seconds=150

class InstructionsWaitPage(WaitPage):

    title_text = "Gracias por leer las instrucciones"
    body_text = "Cuando todos los participantes hayan terminado, comenzarán las prácticas."

class Practica(Page):
    timeout_seconds=150
    form_model =  'player'
    form_fields = ['preg1', 'preg2', 'preg3', 'preg4']

class ResultadoPractica(Page):
    timeout_seconds=120


page_sequence = [Instructions, Practica, ResultadoPractica]
