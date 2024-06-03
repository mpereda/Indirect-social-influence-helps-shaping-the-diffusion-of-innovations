from otree.api import *
import re


##Models

class C(BaseConstants):
    NAME_IN_URL = 'Datos_participante'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    Correo = models.StringField(verbose_name='Indique el correo electrónico asociado a su cuenta de paypal para realizar el pago de sus ganancias:')
    Repite = models.BooleanField(choices=[
    [True,'Quiero participar en otra sesión de este experimento'],
    [False,'No quiero participar en más sesiones de este experimento y únicamente recibir el pago por presentarme'],
    ])

##Functions

def creating_session(subsession: Subsession):
    subsession.session.canceled=False
    for p in subsession.get_players():
        p.Repite=False

#These functions are used to chech if the email format is correct (and different from @paypal.me)    
def Correo_error_message(Player,value):
    print(value)
    if (check(value))==0:
        return 'Introduzca un correo válido'
    else: 
        if (checkformat(value))==0:
            return 'Los correos @paypal.me no son aceptados.' 


def check(s):
    pat = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.fullmatch(pat,s):
        return 1
    else:
        return 0

def checkformat(s):
    pat = r'\b[A-Za-z0-9._%+-]+@paypal.me'
    if re.fullmatch(pat,s):
        return 0
    else:
        return 1

# PAGES
class Repeticion(Page):
    form_model = 'player'
    form_fields = ['Repite']
    
    def is_displayed(player):
    	return (player.participant.extra or player.session.canceled)
    
    def vars_for_template(player):
        participant=player.participant
        return dict(real_payoff= participant.payoff.to_real_world_currency(player.session))
	

class EndPage(Page):
    pass

class Formulario(Page):
    form_model =  'player'
    form_fields = ['Correo']
    
    def is_displayed(player):
    	return not(player.Repite)

    def vars_for_template(player):
        participant=player.participant
        return dict(real_payoff= participant.payoff.to_real_world_currency(player.session))


page_sequence = [Repeticion, Formulario, EndPage]
