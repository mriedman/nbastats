from core.brt import *
from urllib import request
import csv
import os,sys
import ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
def gs(tm,yr):
    s=str(request.urlopen("https://www.basketball-reference.com/teams/"+tm+"/"+yr+"_games.html",context=ctx).read())
    # Get relevant bits of team game log page
    tm2=s.split('-'+yr[2:]+' ')[1].split(' Sched')[0]
    s1=get_table(s, mode='Link')
    s2=s1['Regular Season Table']
    print(1)
    bxscfile = open('data/'+tm+'/season/'+yr+'/boxscore.txt','wb')
    pbpfile = open('data/'+tm+'/season/'+yr+'/pbp.txt','wb')
    ct=0
    for i in s2:
        print(ct)
        ct+=1
        if i[0]=='G':
            # Header line
            continue
        g=str(request.urlopen("https://www.basketball-reference.com"+i[6],context=ctx).read())
        g1=get_table(g, mode='Link')
        tmbx=0
        for j in g1:
            if tm2 in j and j[len(tm2)+2]!='H' and j[len(tm2)+2]!='Q':
                # Full Game (not Half/Quarter)
                tmbx=j
        # Add BBRef box score link ending (e.g. /boxscores/202010230BRK)
        g00=[1]+[ord(j) for j in i[6]]
        g00+=[255]*(31-len(g00))
        #print(bytes(g00))
        bxscfile.write(bytes(g00))
        for j in g1[tmbx]:
            g2=[0]
            if len(j)<15 or j[1]=='MP' or j[0]=='Team Totals':
                continue
            for k in range(len(j)):
                if k==0:
                    continue
                if k==1:
                    # Add player ID (e.g. duranke01)
                    k1=j[k].split('/')[-1][:-5]
                    k2=[ord(l) for l in k1]
                    while len(k2)<9:
                        k2.append(255)
                    g2+=k2
                elif k==2:
                    # MP ([Minutes, Seconds])
                    g2+=[int(i) for i in j[k].split(':')]
                elif j[k]=='':
                    # 255 for null values
                    g2.append(255)
                elif k in [5,8,11]:
                    # Shooting %ages
                    g2.append(int(254*float(j[k])))
                elif k==21:
                    # +/-
                    g2.append(int(j[k])+128)
                else:
                    g2.append(int(j[k]))
            #print(j)
            #print(g2)
            #print(bytes(g2))
            #print(len(g2))#31
            bxscfile.write(bytes(g2))
    bxscfile.close()
#Regular Season Table
#['1', 'Tue, Oct 16, 2018', '/boxscores/index.cgi?month=10&amp;day=16&amp;year=2018', '10:30p', '', 'Box Score', '/boxscores/201810160GSW.html', '', 'Oklahoma City Thunder', '/teams/OKC/2019.html', 'W', '', '108', '100', '1', '0', 'W 1', '']
#TYPE[0] PLAYER[1-9] MIN:SEC[10-11] FG FGA FG%[14] 3P 3PA 3P%[17] FT FTA FT%[20] ORB DRB TRB[23] AST STL BLK[26] TOV PF PTS +/-[30]
#Playoffs Table

gs('BRK','2020')