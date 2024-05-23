from otree.api import *
import random
import networkx as nx
import django
import json
import numpy as np
import time
from collections import Counter

##Models

class C(BaseConstants):
    NAME_IN_URL = 'Egonetworks_Vecinos2'
    PLAYERS_PER_GROUP = None
    NET_SIZE = 31 #Tamaño de la red
    NUM_ROUNDS = 15
    radio_amigos=2
    plus=15 #Puntos que se suman al payoff si hay consenso

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    egonetwork_data = models.LongStringField()
    action = models.StringField(widget=widgets.RadioSelectHorizontal)
    node = models.IntegerField()
    bot = models.BooleanField()
    botcolor = models.StringField()
    initialnetwork = models.LongStringField()
    initialcolor = models.StringField()
    color_neighbors_shown = models.LongStringField()
    color_friends_shown  = models.LongStringField()
    max_rounds = models.IntegerField()

def action_choices(Player):
	choices=[["#67e96e", "Verde"], ["#c700ac", "Magenta"]]
	random.shuffle(choices)
	return choices


# FUNCTIONS
def creating_session(group: Group):
    if group.round_number == 1:
        initialize_network= ["#67e96e" for i in range(C.NET_SIZE)]
        starting_minority = np.random.choice(range(C.NET_SIZE), group.session.config['Innovadores'], replace=False)
        for i in starting_minority:
            initialize_network[i] = "#c700ac"

        random_rounds=random.randint(13,15)

        nodeshuffle= list(range(1,C.NET_SIZE+1))
        random.shuffle(nodeshuffle)
        for i,p in enumerate(group.get_players()):
            if i<C.NET_SIZE:
                p.node= nodeshuffle[i]
                p.initialcolor = initialize_network[p.node-1]
                p.max_rounds = random_rounds
    else:
        for i,p in enumerate(group.get_players()):
            if i<C.NET_SIZE:
                prev_player = p.in_round(p.round_number-1)
                p.node= prev_player.node
                p.max_rounds = prev_player.max_rounds       


def set_payoff(group: Group):
    # Create the graph as a networkx graph
    g = nx.read_edgelist( group.session.config['grafo'],create_using=nx.Graph(), nodetype = int)

    # Create a dictionary of positions for each of the egonetworks
    distances = dict(nx.all_pairs_shortest_path_length(g))
    pos = {}
    dispx = 100
    dispy = -100
    angle = [np.pi/2]
    for ident in range(1,len(g.nodes())+1):
        radio = max(distances[ident].values())
        pos[ident] = {}
        for l in range(0,radio+1):
            lista =[]
            for i in range(1,len(distances[ident])+1):
                if (distances[ident][i] == l):
                    lista.append(i)
            for i in range(len(lista)):
                pos[ident][lista[i]] = { 'x' : dispx*(1+l*np.cos(angle[l%len(angle)]+2*np.pi*i/len(lista))), 'y' : dispy*(1+l*np.sin(angle[l%len(angle)]+2*np.pi*i/len(lista)))}
                
    players = group.get_players()
    colors = {}
    bots = np.zeros(C.NET_SIZE+1)
    zero_color_list = []
    # Create a list of those users that were inactive last round
    for p in players:
        colors[int(p.node)] = str(p.action)
        bots[int(p.node)] = int(p.bot)
        if not p.bot:
            zero_color_list.append(p.action)
    for p in players:
        # Pay if there is consensus
        if len(set(zero_color_list)) == 1:
            p.participant.consensus=True
            if p.round_number > 1:
                prev_player = p.in_round(p.round_number-1)
            else: 
                prev_player = p.in_round(p.round_number)
            if not (p.bot & prev_player.bot):
                if set(zero_color_list)=="#c700ac":
                    p.in_round(p.max_rounds).payoff += 5*(15+1-p.round_number)+C.plus
                else:
                    p.in_round(p.max_rounds).payoff += 5*(15+1-p.round_number)
        else:
            if not p.bot:
                p.in_round(p.max_rounds).payoff += 1

    for p in players:
        #Assign an egonetwork to each player in JSON format
        egonetwork = {}
        # egonetwork = nx.cytoscape_data(nx.minimum_spanning_tree(nx.ego_graph(g,int(p.node),radius=nx.diameter(g))))    ## This option creates the complete ego tree
        egonetwork = nx.cytoscape_data(nx.ego_graph(g,int(p.node),radius=nx.diameter(g)))     ## This option creates the complete ego graph

        ##In each egonetwork we store the style that the elements should show
        neighbors = []
        neighbors_with_bots = []
        friends = []
        friends_with_bots = []
        friends_shown = []
        for i in range(0,len(egonetwork['elements']['nodes'])):
            if (int(egonetwork['elements']['nodes'][i]['data']['id'])==int(p.node)):
                    egonetwork['elements']['nodes'][i]['style'] = {'width': 50, 'height': 50,'background-color': p.action, 'label' : 'USTED ESTÁ AQUÍ', 'z-index': '8', 'border-width' : 2}  
                    egonetwork['elements']['nodes'][i]['renderedPosition'] = pos[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]
                    if p.bot:
                        egonetwork['elements']['nodes'][i]['style'] = {'width': 50, 'height': 50,'background-color': p.action, 'label' : 'USTED ESTÁ AQUÍ', 'z-index': '8', 'border-width' : 2,'shape' : 'triangle'}    
            else:
                if distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]==1:
                    neighbors_with_bots.append(i)   
                    if not(bots[int(egonetwork['elements']['nodes'][i]['data']['id'])]):
                        neighbors.append(i) 
                elif distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]==C.radio_amigos:
                    friends_with_bots.append(i)   
                    if not(bots[int(egonetwork['elements']['nodes'][i]['data']['id'])]):
                        friends.append(i) 
                else:
                    egonetwork['elements']['nodes'][i]['renderedPosition'] = pos[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]
                    egonetwork['elements']['nodes'][i]['style'] = {'background-color': 'black','z-index': '8', 'border-width' : 2,'width': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4), 'height': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4)}
                    if bots[int(egonetwork['elements']['nodes'][i]['data']['id'])]:
                        egonetwork['elements']['nodes'][i]['style'] = {'width': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4), 'height': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4),'background-color': 'black','z-index': '8', 'border-width' : 2,'shape' : 'triangle'}

        if len(neighbors) >=2:
            neighbors_shown=np.random.choice(neighbors,2, replace=False)
        elif len(neighbors)==1:
            bot_to_show = random.choice([bot for bot in neighbors_with_bots if bot not in neighbors])
            neighbors_shown = [neighbors[0], bot_to_show]
        else:
            neighbors_shown=np.random.choice(neighbors_with_bots,2, replace=False)
        p.color_neighbors_shown=str([colors[int(egonetwork['elements']['nodes'][i]['data']['id'])] for i in neighbors_shown])
        if len(friends) >=2:
            friends_shown=np.random.choice(friends,2, replace=False)
        elif len(friends)==1:
            bot_to_show = random.choice([bot for bot in friends_with_bots if bot not in friends])
            friends_shown = [friends[0], bot_to_show]
        else:
            if len(friends_with_bots)>=2:
                friends_shown=np.random.choice(friends_with_bots,2, replace=False)
        if friends_shown != []:
            p.color_friends_shown=str([colors[int(egonetwork['elements']['nodes'][i]['data']['id'])] for i in friends_shown])

        p.color_neighbors_shown=str([colors[int(egonetwork['elements']['nodes'][i]['data']['id'])] for i in neighbors_shown])
        if friends_shown != []:
            p.color_friends_shown=str([colors[int(egonetwork['elements']['nodes'][i]['data']['id'])] for i in friends_shown])

        seencolor = [colors[int(egonetwork['elements']['nodes'][i]['data']['id'])] for i in neighbors_shown] + [colors[int(egonetwork['elements']['nodes'][i]['data']['id'])] for i in friends_shown]
        c=Counter(seencolor)
        if c["#67e96e"] < c["#c700ac"]:
            p.botcolor = "#c700ac"
        elif c["#67e96e"] > c["#c700ac"]:
            p.botcolor = "#67e96e"
        else:
            p.botcolor = np.random.choice(["#67e96e", "#c700ac"])

        for i in neighbors_with_bots:
            if i in neighbors_shown:
                egonetwork['elements']['nodes'][i]['renderedPosition'] = pos[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]
                egonetwork['elements']['nodes'][i]['style'] = {'background-color': str(colors[int(egonetwork['elements']['nodes'][i]['data']['id'])]),'z-index': '8', 'border-width' : 2,'width': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4), 'height': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4)}
                if bots[int(egonetwork['elements']['nodes'][i]['data']['id'])]: 
                    egonetwork['elements']['nodes'][i]['style'] = {'width': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4), 'height': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4),'background-color': str(colors[int(egonetwork['elements']['nodes'][i]['data']['id'])]),'z-index': '8', 'border-width' : 2,'shape' : 'triangle'}
            else:
                egonetwork['elements']['nodes'][i]['renderedPosition'] = pos[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]
                egonetwork['elements']['nodes'][i]['style'] = {'background-color': 'black','z-index': '8', 'border-width' : 2,'width': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4), 'height': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4)}
                if bots[int(egonetwork['elements']['nodes'][i]['data']['id'])]:
                    egonetwork['elements']['nodes'][i]['style'] = {'width': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4), 'height': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4),'background-color': 'black','z-index': '8', 'border-width' : 2,'shape' : 'triangle'}

        for i in friends_with_bots:
            if i in friends_shown:
                egonetwork['elements']['nodes'][i]['renderedPosition'] = pos[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]
                egonetwork['elements']['nodes'][i]['style'] = {'background-color': str(colors[int(egonetwork['elements']['nodes'][i]['data']['id'])]),'z-index': '8', 'border-width' : 2,'width': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4), 'height': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4)}
                if bots[int(egonetwork['elements']['nodes'][i]['data']['id'])]: 
                    egonetwork['elements']['nodes'][i]['style'] = {'width': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4), 'height': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4),'background-color': str(colors[int(egonetwork['elements']['nodes'][i]['data']['id'])]),'z-index': '8', 'border-width' : 2,'shape' : 'triangle'}
            else:
                egonetwork['elements']['nodes'][i]['renderedPosition'] = pos[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]
                egonetwork['elements']['nodes'][i]['style'] = {'background-color': 'black','z-index': '8', 'border-width' : 2,'width': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4), 'height': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4)}
                if bots[int(egonetwork['elements']['nodes'][i]['data']['id'])]:
                    egonetwork['elements']['nodes'][i]['style'] = {'width': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4), 'height': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4),'background-color': 'black','z-index': '8', 'border-width' : 2,'shape' : 'triangle'}




        egonetwork['style'] = {'z-index-compare': 'manual'}
        c=len(egonetwork['elements']['nodes'])
        for edge in egonetwork['elements']['edges']:
            c=c+1
            edge['data']['id'] = c
            edge['style'] = {'line-style': 'solid', 'z-index': '8'}
        ## Create concentric cicles that show the distance between the central self node and each of the other nodes
        for outcirc in range(max(distances[p.node].values())):
            c=c+1
            egonetwork['elements']['nodes'].append({ 'data': { 'id': str(c) }, 'renderedPosition': { 'x': 100, 'y': -100 }, 'style' : {'background-color':'black', 'background-opacity': '0.15', 'width': 300+outcirc*200, 'height': 300+outcirc*200, 'z-index': '7' }, 'classes': ['foo'] })
        p.egonetwork_data = json.dumps(egonetwork) 

def set_network_initial(group: Group):
       # Create the graph as a networkx graph
    g = nx.read_edgelist( group.session.config['grafo'],create_using=nx.Graph(), nodetype = int)
    # Create a dictionary of positions for each of the egonetworks
    distances = dict(nx.all_pairs_shortest_path_length(g))
    pos = {}
    dispx = 100
    dispy = -100
    angle = [np.pi/2]
    for ident in range(1,len(g.nodes())+1):
        radio = max(distances[ident].values())
        pos[ident] = {}
        for l in range(0,radio+1):
            lista =[]
            for i in range(1,len(distances[ident])+1):
                if (distances[ident][i] == l):
                    lista.append(i)
            for i in range(len(lista)):
                pos[ident][lista[i]] = { 'x' : dispx*(1+l*np.cos(angle[l%len(angle)]+2*np.pi*i/len(lista))), 'y' : dispy*(1+l*np.sin(angle[l%len(angle)]+2*np.pi*i/len(lista)))}
                
    players = group.get_players()
    colors = {}
    bots = np.zeros(C.NET_SIZE+1)
    # Create a list of those users that were inactive last round
    for p in players:
        colors[int(p.node)] = p.initialcolor
        bots[int(p.node)] = int(p.bot)
        p.participant.consensus = False

    for p in players:
        #Assign an egonetwork to each player in JSON format
        egonetwork = {}
        # egonetwork = nx.cytoscape_data(nx.minimum_spanning_tree(nx.ego_graph(g,int(p.node),radius=nx.diameter(g))))    ## This option creates the complete ego tree
        egonetwork = nx.cytoscape_data(nx.ego_graph(g,int(p.node),radius=nx.diameter(g)))     ## This option creates the complete ego graph

        ##In each egonetwork we store the style that the elements should show
        neighbors = []
        neighbors_with_bots = []
        neighbors_shown = []
        friends = []
        friends_with_bots = []
        friends_shown=[]
        for i in range(0,len(egonetwork['elements']['nodes'])):
            if (int(egonetwork['elements']['nodes'][i]['data']['id'])==int(p.node)):
                    egonetwork['elements']['nodes'][i]['style'] = {'width': 50, 'height': 50,'background-color': colors[p.node], 'label' : 'USTED ESTÁ AQUÍ', 'z-index': '8', 'border-width' : 2}  
                    egonetwork['elements']['nodes'][i]['renderedPosition'] = pos[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]
                    if p.bot:
                        egonetwork['elements']['nodes'][i]['style'] = {'width': 50, 'height': 50,'background-color': colors[p.node], 'label' : 'USTED ESTÁ AQUÍ', 'z-index': '8', 'border-width' : 2,'shape' : 'triangle'}    
            else:
                if distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]==1:
                    neighbors_with_bots.append(i)   
                    if not(bots[int(egonetwork['elements']['nodes'][i]['data']['id'])-1]):
                        neighbors.append(i) 
                elif distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]==C.radio_amigos:
                    friends_with_bots.append(i)   
                    if not(bots[int(egonetwork['elements']['nodes'][i]['data']['id'])-1]):
                        friends.append(i) 
                else:
                    egonetwork['elements']['nodes'][i]['renderedPosition'] = pos[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]
                    egonetwork['elements']['nodes'][i]['style'] = {'background-color': 'black','z-index': '8', 'border-width' : 2,'width': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4), 'height': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4)}
                    if bots[int(egonetwork['elements']['nodes'][i]['data']['id'])]:
                        egonetwork['elements']['nodes'][i]['style'] = {'width': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4), 'height': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4),'background-color': 'black','z-index': '8', 'border-width' : 2,'shape' : 'triangle'}

        if len(neighbors) >=2:
            neighbors_shown=np.random.choice(neighbors,2, replace=False)
        elif len(neighbors)==1:
            bot_to_show = random.choice([bot for bot in neighbors_with_bots if bot not in neighbors])
            neighbors_shown = [neighbors[0], bot_to_show]
        else:
            neighbors_shown=np.random.choice(neighbors_with_bots,2, replace=False)
        if len(friends) >=2:
            friends_shown=np.random.choice(friends,2, replace=False)
        elif len(friends)==1:
            bot_to_show = random.choice([bot for bot in friends_with_bots if bot not in friends])
            friends_shown = [friends[0], bot_to_show]
        else:
            if len(friends_with_bots)>=2:
                friends_shown=np.random.choice(friends_with_bots,2, replace=False)


        for i in neighbors_with_bots:
            if i in neighbors_shown:
                egonetwork['elements']['nodes'][i]['renderedPosition'] = pos[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]
                egonetwork['elements']['nodes'][i]['style'] = {'width': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4), 'height': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4),'background-color': str(colors[int(egonetwork['elements']['nodes'][i]['data']['id'])]),'z-index': '8', 'border-width' : 2}
                if bots[int(egonetwork['elements']['nodes'][i]['data']['id'])]: 
                    egonetwork['elements']['nodes'][i]['style'] = {'width': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4), 'height': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4),'background-color': str(colors[int(egonetwork['elements']['nodes'][i]['data']['id'])]),'z-index': '8', 'border-width' : 2,'shape' : 'triangle'}
            else:
                egonetwork['elements']['nodes'][i]['renderedPosition'] = pos[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]
                egonetwork['elements']['nodes'][i]['style'] = {'width': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4), 'height': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4),'background-color': 'black','z-index': '8', 'border-width' : 2,'width': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4), 'height': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4)}
                if bots[int(egonetwork['elements']['nodes'][i]['data']['id'])]:
                    egonetwork['elements']['nodes'][i]['style'] = {'width': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4), 'height': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4),'background-color': 'black','z-index': '8', 'border-width' : 2,'shape' : 'triangle'}

        for i in friends_with_bots:
            if i in friends_shown:
                egonetwork['elements']['nodes'][i]['renderedPosition'] = pos[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]
                egonetwork['elements']['nodes'][i]['style'] = {'width': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4), 'height': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4),'background-color': str(colors[int(egonetwork['elements']['nodes'][i]['data']['id'])]),'z-index': '8', 'border-width' : 2}
                if bots[int(egonetwork['elements']['nodes'][i]['data']['id'])]: 
                    egonetwork['elements']['nodes'][i]['style'] = {'width': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4), 'height': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4),'background-color': str(colors[int(egonetwork['elements']['nodes'][i]['data']['id'])]),'z-index': '8', 'border-width' : 2,'shape' : 'triangle'}
            else:
                egonetwork['elements']['nodes'][i]['renderedPosition'] = pos[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]
                egonetwork['elements']['nodes'][i]['style'] = {'width': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4), 'height': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4),'background-color': 'black','z-index': '8', 'border-width' : 2,'width': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4), 'height': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4)}
                if bots[int(egonetwork['elements']['nodes'][i]['data']['id'])]:
                    egonetwork['elements']['nodes'][i]['style'] = {'width': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4), 'height': 50/np.power((distances[int(p.node)][int(egonetwork['elements']['nodes'][i]['data']['id'])]),3/4),'background-color': 'black','z-index': '8', 'border-width' : 2,'shape' : 'triangle'}




        egonetwork['style'] = {'z-index-compare': 'manual'}
        c=len(egonetwork['elements']['nodes'])
        for edge in egonetwork['elements']['edges']:
            c=c+1
            edge['data']['id'] = c
            edge['style'] = {'line-style': 'solid', 'z-index': '8'}
        ## Create concentric cicles that show the distance between the central self node and each of the other nodes
        for outcirc in range(max(distances[p.node].values())):
            c=c+1
            egonetwork['elements']['nodes'].append({ 'data': { 'id': str(c) }, 'renderedPosition': { 'x': 100, 'y': -100 }, 'style' : {'background-color':'black', 'background-opacity': '0.15', 'width': 300+outcirc*200, 'height': 300+outcirc*200, 'z-index': '7' }, 'classes': ['foo'] })
        p.initialnetwork = json.dumps(egonetwork)     


# PAGES

class Explanation(Page):
    timeout_seconds = 60
    def is_displayed(player):
        return player.round_number == 1
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.bot = True
        else:
            player.bot=False
        
class Network(Page):
    form_model = 'player'
    timeout_seconds = 40

    def is_displayed(player):
        return (player.participant.consensus==False)&(player.max_rounds>=player.round_number)
    
    def vars_for_template(player: Player):
        network = player.egonetwork_data
        return {'ego_network': network, 'player node' : player.node, 'player action' : player.action}
    

class Choose(Page):
    form_model = 'player'
    form_fields = ['action']
    timeout_seconds = 15

    def is_displayed(player):
        return (player.participant.consensus==False)&(player.max_rounds>=player.round_number)

    def before_next_page(player, timeout_happened):
        if timeout_happened:
            # We treat the player as a bot (randomly chosen if it's first round, then 50% to follow majority of its lookable nodes and 50% to choose randomly)
            player.bot = True
            if (player.round_number == 1):
                player.action = random.choice(['#67e96e', '#c700ac'])
            else:
                prev_player = player.in_round(player.round_number-1)
                player.action = random.choice([str(random.choice(['#67e96e', '#c700ac'])),str(prev_player.botcolor)])
        else:
            player.bot=False

                

class ResultsWaitPage(WaitPage):
    title_text = "Muchas gracias por su decisión"
    body_text = "Por favor, espere a que el resto de participantes tome la suya."
    form_model = 'player'
    after_all_players_arrive = set_payoff

    def is_displayed(player):
        return (player.participant.consensus==False)&(player.max_rounds>=player.round_number)

class Consenso(Page):
    timeout_seconds = 30
    def is_displayed(player):
        return player.max_rounds==player.round_number

class StartingWaitPage(WaitPage):
    title_text = "Espere por favor"
    boy_text = "En breve empezará la siguiente fase del experimento"
    form_model = 'player'
    after_all_players_arrive = set_network_initial

    def is_displayed(player):
        return player.round_number==1

class StartingNetwork(Page):
    form_model = 'player'
    timeout_seconds = 60

    def is_displayed(player):
        return player.round_number==1
    
    def vars_for_template(player: Player):
        return {'initial_network': player.initialnetwork}


page_sequence = [Explanation, StartingWaitPage, StartingNetwork, Choose, ResultsWaitPage, Network, Consenso]
