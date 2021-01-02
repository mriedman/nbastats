#coding: utf-8
from core.brt import *
from core.playtypes import *
def pbp1(x0, v=0):
    def getplayer(s, isviolation = False):
        if '$$' not in s:
            if s == 'Team':
                if not ishome:
                    return 'team2' # Road team
                else:
                    return 'team1' # Home team
            if s == '':
                # IDK why they have it this way
                # Go see Game 6 of 2019 NBA finals (Draymond illegal timeout)
                # or PHI vs DET 1/17/20 Q1 3:02 (6 players on the floor)
                # It's only under the wrong column for violations, not turnovers
                # CHO vs BRK 12/27/20 5 sec
                # MIN vs SAC 1/27/20 8 sec
                if ishome ^ isviolation:
                    return 'team1' # Home team
                else:
                    return 'team2' # Road team
            elif v == 0:
                return s[:9]
            return s
        if v == 0:
            return s.split('$$')[1]
        elif v == 1 or v!= 0.5:
            return s.split('$$')[2]
        else:
            return s
    def shot(x):
        def st(y):
            y1=[]
            if 'ft' in y:
                f0=y.index('ft')-1
            elif 'at rim' in y:
                f0=y.index('at rim')+6
            else:
                f0=-1
                print(y)
                print(x)
                raise ValueError('Shot distance not found')
            if y[:3]=='lay':
                y1=['layup',y[11:f0]]
            elif y[:3]=='jum':
                y1=['jump shot',y[15:f0]]
            elif y[:3]=='hoo':
                y1=['hook shot',y[15:f0]]
            elif y[:3]=='dun':
                return ['dunk',y[10:f0]]
            else:
                print(x)
                print(y)
                raise ValueError
                return y
            if not '(' in y:
                return y1
            f=y.index('(')
            if y[f+1:f+4]=='ass':
                y1.append('assist')
                y1.append(getplayer(y[f+11:-1]))
                return y1
            elif y[f+1:f+4]=='blo':
                y1.append('block')
                y1.append(getplayer(y[f+10:-1]))
                return y1
            else:
                print(x)
                print(y[f:])
                raise ValueError
                return y1
        if x[:3] == 'fre':
            #print(['1','FT',x[11],x[16]])
            return ['1','FT',x[11],x[16], 'free throw']
        elif x[:3]=='2-p':
            #print(['2']+st(x[5:]))
            return ['2']+st(x[5:])
        elif x[:3]=='3-p':
            #print(['3']+st(x[5:]))
            return ['3']+st(x[5:])
        elif x[:3]=='cle':
            #print(['1','FT', x[22], x[27],'Clear Path'])
            return ['1', 'FT', x[22], x[27],'clear path']
        elif x[:3]=='tec':
            #print(['1','FT','1','1','Tech'])
            return ['1','FT','1','1','technical']
        elif x[:3]=='fla':
            return ['1','FT',x[-6],x[-1], 'flagrant']
        elif x[:7] == 'no shot':
            return ['1','FT','1','1','unknown']
        else:
            print(x)
            raise ValueError('Weird shot type')
            return [x]
    def foul(x):
        foultype = x[:x.index('foul') - 1]
        if foultype not in foultypelist:
            print(x)
            raise ValueError('Foul type not in list: '+foultype)
        if foultype == 'Flagrant':
            return ['foul', x[:x.index(' by')], getplayer(x[x.index('foul') + 15:])]
        elif '(' in x:
            return ['foul', foultype, getplayer(x[x.index('foul') + 8:x.index('(')]), getplayer(x[x.index('wn by ') + 6:-1])]
        elif foultype in ['Technical', 'Def 3 sec tech', 'Clear path']:
            return ['foul', foultype, getplayer(x[x.index('foul') + 8:])]
        elif foultype == 'Double personal':
            return ['foul', foultype, getplayer(x[x.index('foul') + 8:x.index(' and')]), getplayer(x[x.index(' and') + 5:])]
        else:
            print(foultype)
            raise ValueError('Weird foul type')
    def turnover(x):
        xf = x.index('(')
        x1 = ['turnover', getplayer(x[12:xf - 1])]
        if ';' in x:
            totype = x[xf + 1:x.index(';')]
            if totype not in tosclist:
                print(x)
                raise ValueError(totype + ' not in list: ' + str(tosclist))
            x1.append(totype)
            x1.append(getplayer(x[x.index(';') + 11:-1]))
        else:
            totype = x[xf + 1:-1]
            if totype not in tonosclist:
                print(x)
                raise ValueError(totype + ' not in list: ' + str(tonosclist))
            x1.append(totype)
            x1.append('NONE')
        # print(x1)
        return x1
    if len(x0)<2:
        # print([x0,1])
        if ' Q' in x0[0]:
            return ['quarter', int(x0[0][0])]
        elif ' OT' in x0[0]:
            return ['quarter', 4 + int(x0[0][0])]
        print(x0)
        raise ValueError
        return [0] #Help
    if x0[1]!='&nbsp;':
        x=x0[1]
        ishome = False
    else:
        x=x0[-1]
        ishome = True
    if x[0] == 'Time':
        return ['NULL']
    try:
        if ' enters the game for ' in x:
            a=x.index(' enters the game for ')
            # x[1] enters for x[2]
            return ['enters for',getplayer(x[:a]),getplayer(x[a+21:])]
        elif ' makes ' in x:
            a=x.index(' makes ')
            return ['made shot', getplayer(x[:a])]+shot(x[a+7:])
        elif ' misses ' in x:
            a=x.index(' misses ')
            return ['missed shot', getplayer(x[:a])]+shot(x[a+8:])
        elif 'Defensive re' in x:
            return ['DRB', getplayer(x[21:])]
        elif 'Offensive re' in x:
            return ['ORB', getplayer(x[21:])]
        elif 'timeout' in x:
            if 'full' in x:
                return ['timeout', 'full', 'team1' if ishome else 'team2']
            elif x == 'Official timeout':
                return ['timeout', 'official', 'official']
            elif '20 second' in x:
                return ['timeout', '20 second', 'team1' if ishome else 'team2']
            else:
                print([x[:x.index('time')-1]],'TO')
                raise ValueError('Weird timeout')
                return ['timeout', 'full', x[:x.index('time')-1]]
        elif 'Turnover' in x:
            return turnover(x)
        elif 'foul' in x:
            if '(' in x or True:
                #print([x[x.index('foul')+8:x.index('(')],'foul',x[:x.index('foul')-1],x[x.index('wn by ')+6:]])
                #return [getplayer(x[x.index('foul')+8:x.index('(')]),'foul',x[:x.index('foul')-1],getplayer(x[x.index('wn by ')+6:-1])]
                return foul(x)
            else:
                #print([x[x.index('foul')+8:],'foul',x[:x.index('foul')-1]])
                # Doesn't work for double personals (Double personal foul by L. Scola and J. Noah)
                return [getplayer(x[x.index('foul')+8:]),'foul',x[:x.index('foul')-1]]
        elif 'Violation' in x:
            vtype = x[x.index('(')+1:-1]
            if vtype not in violationtypelist:
                print(x)
                print([vtype,violationtypelist])
                raise ValueError('Violation type not found')
            else:
                return ['violation', getplayer(x[13:x.index('(')-1], isviolation=True), vtype]
        elif 'Jump ball' in x:
            x1 = ['jump ball', getplayer(x[11:x.index(' vs')])]
            if v > 0:
                x1.append('vs.')
            if '(' in x:
                x1.append(getplayer(x[x.index('vs. ')+4:x.index('(')-1]))
                x1.append(getplayer(x[x.index('(')+1:x.index('gains')-1]))
            else:
                x1.append(getplayer(x[x.index('vs. ')+4:]))
                if v == 0:
                    x1.append('NONE')
            return x1
        elif 'Instant Replay' in x:
            if x == 'Instant Replay':
                return ['NULL'] # QQQQQQQQQQ
            x1 = ['instant replay']
            if x[16:24] == 'Request:':
                x1.append('official review')
            elif x[16:26] == 'Challenge:':
                x1.append('coach challenge')
            else:
                print(x)
                raise ValueError('Unknown instant replay')
            # IDK why it works this way but it does
            if x[-14:-1] == 'Ruling Stands':
                x1.append('overturned')
            elif x[-7:-1] == 'Stands':
                x1.append('upheld')
            else:
                print(x)
                raise ValueError('Unknown instant replay')
            return x1
        elif 'ejected' in x:
            if x[-18:] == ' ejected from game':
                return ['ejected', getplayer(x[:-18])]
            else:
                print(x)
                raise ValueError('Weird ejection')
        else:
            if len(x0) >= 0:
                return ['NULL']
            print(x)
            raise ValueError('')
            return [x]
    except:
        print(x)
        raise ValueError('Something\'s wrong here')
def pbp2(x):
    a={}
    a['time']=x[0]
    a['score']=x[3]
    a1=pbp1(x)
    if type(a)!=list:
        return a
    a.player=a1[0]
    a.act=a1[1]
    if a.act=='enters for':
        a.player2=a1[2]
    if a.act=='makes' or a.act=='misses':
        a.value=int(a1[2])
    else:
        a.value=0
    if a.act=='foul':
        a.ftype=a1[2]
        a.player2=a1[3]
def csc(x):
    # Clock, Score
    try:
        a0i=x[0].index(':')
        a0j=x[0].index('.')
        a0=int(x[0][:a0i])*600+int(x[0][a0i+1:a0j])*10+int(x[0][a0j+1:])
        a1i=x[3].index('-')
        a1=[int(x[3][:a1i]),int(x[3][a1i+1:])]
        return [a0]+a1
    except:
        return [-1,-1,-1]
def binpbp(x0, pnumlist, ishome):
    pnumget = lambda x: [pnumlist[x][0]] if x in pnumlist else [192] + [ord(i) for i in x]
    reqpnums = ['official', 'team1', 'team2', 'NONE']
    for i in reqpnums:
        if i not in pnumlist:
            raise ValueError(i+' not in pnumlist: '+str(pnumlist))
    pbplist = []
    # print([pbp1(x, v=0) for x in x0])
    currqsecs = 7200
    for x in x0:
        p = pbp1(x, v=0)
        c = csc(x)
        if p == ['NULL']:
            continue
        if p[0] == 'quarter':
            if p[1] <= 4:
                currqsecs = p[1] * 7200
            else:
                currqsecs = 4 * 7200 + p[1] * 3000
            continue
        currtime = currqsecs - c[0]
        x1 = []
        start = 0
        if p[0] == 'enters for':
            x1 += [start, *pnumget(p[1]), *pnumget(p[2])]
        start += 1
        if p[0] in ['made shot', 'missed shot']:
            x1 += [start - 1 + int(p[2]) + 3 * (len(p) > 5) + 6 * (p[0] == 'missed shot'), *pnumget(p[1])]
            if p[3] == 'FT':
                x1.append((int(p[4])<<5) + (int(p[5])<<3) + freethrowlist.index(p[6]))
            else:
                # print([x,p])
                x1.append(shottypelist.index(p[3]))
                x1.append(0 if p[4] == 'm' else int(p[4]))
                if len(p) == 7:
                    x1.append(['assist', 'block'].index(p[5]))
                    x1 += [*pnumget(p[6])]
            if p[0] == 'made shot':
                x1 += c[1:]
        start += 12
        if p[0] == 'foul':
            x1.append(start + foultypelist.index(p[1]))
            for player in p[2:]:
                x1 += [*pnumget(player)]
        start += len(foultypelist)
        if p[0] == 'turnover':
            if p[3] == 'NONE':
                x1.append(start + tonosclist.index(p[2]))
            else:
                x1.append(start + len(tonosclist) + tosclist.index(p[2]))
            x1 += [*pnumget(p[1])]
        start += len(tonosclist) + len(tosclist)
        if p[0] == 'DRB':
            x1 += [start, *pnumget(p[1])]
        start += 1
        if p[0] == 'ORB':
            x1 += [start, *pnumget(p[1])]
        start += 1
        if p[0] == 'timeout':
            x1.append(start + timeoutlist.index(p[1]))
            if len(x) > 2:
                x1 += [*pnumget(p[2])]
        start += len(timeoutlist)
        if p[0] == 'violation':
            x1.append(start + violationtypelist.index(p[2]))
            x1 += [*pnumget(p[1])]
        start += len(violationtypelist)
        if p[0] == 'jump ball':
            x1.append(start)
            for i in p[1:]:
                x1 += [*pnumget(i)]
        start += 1
        if p[0] == 'instant replay':
            num = start + 2 * ['official review', 'coach challenge'].index(p[1]) + ['overturned', 'upheld'].index(p[2])
            x1.append(num)
        start += 4
        if p[0] == 'ejected':
            x1 += [start, *pnumget(p[1])]
        start += 1
        x1 += [currtime//255, currtime%255, 255]
        if any(type(i) == list for i in x1):
            print([x,p])
            raise ValueError('List in the wrong place')
        if x1 == []:
            print([x,p])
            raise ValueError('Binary format not found')
        pbplist += x1
        # print(x1)
    return pbplist




'''g1=Team('BRK')
#g1.newseason('2020')
a=[]
for i0 in range(16):
    # g1.szns['2020'][i0].gpbp()
    gbxsc=g1.seasons['2020'][i0].pbp()
    print(gbxsc)
    a1=[]
    for i in gbxsc['Play-By-Play Table']:
        print(i)
        print(pbp1(i))
        print(csc(i))
        a1.append(csc(i)+pbp1(i))
    with open('data/BRK/season/2020/g'+str(i0)+'.csv', mode='w') as csvf:
        csvw = csv.writer(csvf)
        for j in a1:
            csvw.writerow(j)'''