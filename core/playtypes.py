# Lists containing all types of plays from BBRef database

# Turnover types that can appear without ;
tonosclist = ['illegal screen', 'traveling', '3 sec', 'offensive foul', 'shot clock', 'out of bounds lost ball',
              'bad pass', 'step out of bounds', '5 sec', '8 sec', 'inbound', 'off goaltending', 'offensive goaltending',
              'palming', 'illegal assist', 'double dribble', 'illegal pick', 'illegal screen', 'discontinued dribble',
              'dbl dribble', 'back court', 'turnover', 'lost ball', 'lane violation', 'no', 'punched ball',
              'kicked ball', 'jump ball violation.', '5 sec inbounds']
# Turnover types that appear with ;
tosclist = ['bad pass', 'lost ball', 'turnover']
# Shot types
shottypelist = ['layup', 'hook shot', 'dunk', 'jump shot', 'tip-in']
# Free throw types
freethrowlist = ['clear path', 'technical', 'flagrant', 'free throw', 'unknown']
# Foul types
# Tea is actually from Teamfoul but the m is cut off
foultypelist = ['Double personal', 'Personal', 'Shooting', 'Offensive', 'Technical', 'Personal block', 'Personal take',
                'Offensive charge', 'Loose ball', 'Flagrant foul type 1', 'Flagrant foul type 2', 'Def 3 sec tech',
                'Away from play', 'Flagrant', 'Clear path', 'Tea', 'Shooting block', 'Hanging tech', 'Inbound']
# Violation types
violationtypelist = ['delay of game', 'def goaltending', 'kicked ball', 'jump ball',
                     'illegal defense', 'lane', 'double lane']
# Timeout types
timeoutlist = ['full', '20 second', 'official']
unknownlist = {'Violation': ['violation']}