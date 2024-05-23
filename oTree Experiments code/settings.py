from os import environ

environ['OTREE_PRODUCTION'] = "1"
AUTH_LEVEL = environ.get('OTREE_AUTH_LEVEL')

if environ.get('OTREE_PRODUCTION') not in {None, '', '0'}:
    DEBUG = False
else:
    DEBUG = True

ADMIN_USERNAME = 'valencia'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

SERVER_URL = 'https://valencia.ibsen-h2020.eu/'


SESSION_CONFIGS = [
        dict(
         name='StartPlayers',
         app_sequence=['StartExperiment','CancellExperimentMorePlayers','Block','Data','LatePeople'],
         num_demo_participants=40,
    ),
        dict(
         name='egonetwork_1_2_3_4',
         app_sequence=['Instructions','egonetworkChoiceAmAz','egonetworkChoiceVerMag','egonetworkChoiceRojNar','egonetworkChoiceLilMor', 'Data'],
         num_demo_participants=31,
         grafo='_static/global/Amistad.txt',
         Innovadores = 4,
    ),
        dict(
            name='egonetwork_1_3_2_4',
            app_sequence=['Instructions','egonetworkChoiceAmAz','egonetworkChoiceRojNar','egonetworkChoiceVerMag','egonetworkChoiceLilMor', 'Data'],
            num_demo_participants=31,
            grafo='_static/global/Amistad.txt',
            Innovadores = 4,
        ),
        dict(
            name='egonetwork_1_4_2_3',
            app_sequence=['Instructions','egonetworkChoiceAmAz','egonetworkChoiceLilMor','egonetworkChoiceVerMag','egonetworkChoiceRojNar', 'Data'],
            num_demo_participants=31,
            grafo='_static/global/Amistad.txt',
            Innovadores = 4,
        ),
        dict(
            name='egonetwork_1_4_3_2',
            app_sequence=['Instructions','egonetworkChoiceAmAz','egonetworkChoiceLilMor','egonetworkChoiceRojNar','egonetworkChoiceVerMag', 'Data'],
            num_demo_participants=31,
            grafo='_static/global/Amistad.txt',
            Innovadores = 4,
        ),
        dict(
            name='egonetwork_1_2_4_3',
            app_sequence=['Instructions','egonetworkChoiceAmAz','egonetworkChoiceVerMag','egonetworkChoiceLilMor','egonetworkChoiceRojNar', 'Data'],
            num_demo_participants=31,
            grafo='_static/global/Amistad.txt',
            Innovadores = 4,
        ),
        dict(
            name='egonetwork_1_3_4_2',
            app_sequence=['Instructions','egonetworkChoiceAmAz','egonetworkChoiceRojNar','egonetworkChoiceLilMor','egonetworkChoiceVerMag', 'Data'],
            num_demo_participants=31,
            grafo='_static/global/Amistad.txt',
            Innovadores = 4,
        ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=0.04, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = [
    'consensus',
    'wait_page_arrival',
    'extra',
    'full',
]
SESSION_FIELDS = [
    'canceled',
    'passed',
    'block',
]

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'es'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'EUR'
USE_POINTS = True

ROOMS = [
    dict(
        name='econ101',
        display_name='Econ 101 class',
        participant_label_file='_rooms/econ101.txt',
    ),
    dict(
        name='live_demo', display_name='Room for live demo (no participant labels)'
    ),
]


DEMO_PAGE_INTRO_HTML = """
Here are some oTree games.
"""


SECRET_KEY = '5039424909079'

INSTALLED_APPS = ['otree']
