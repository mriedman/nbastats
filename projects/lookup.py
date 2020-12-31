from brt import *
from urllib import request
import csv
import os,sys
import ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
#s=request.urlopen("https://www.basketball-reference.com/play-index/pgl_finder.cgi?request=1&match=game&is_playoffs=N&age_min=0&age_max=99&season_start=1&season_end=-1&pos_is_g=Y&pos_is_gf=Y&pos_is_f=Y&pos_is_fg=Y&pos_is_fc=Y&pos_is_c=Y&pos_is_cf=Y&c1stat=pts&c1comp=gt&c1val=30&c2stat=trb&c2comp=gt&c2val=20&order_by=date_game",context=ctx)
s=request.urlopen("https://www.basketball-reference.com/play-index/pgl_finder.cgi?request=1&player_id=&match=game&year_min=1947&year_max=2019&age_min=0&age_max=99&team_id=&opp_id=&season_start=1&season_end=-1&is_playoffs=N&draft_year=&round_id=&game_num_type=&game_num_min=&game_num_max=&game_month=&game_day=&game_location=&game_result=&is_starter=&is_active=&is_hof=&pos_is_g=Y&pos_is_gf=Y&pos_is_f=Y&pos_is_fg=Y&pos_is_fc=Y&pos_is_c=Y&pos_is_cf=Y&c1stat=pts&c1comp=gt&c1val=30&c1val_orig=30&c2stat=trb&c2comp=gt&c2val=20&c2val_orig=20&c3stat=&c3comp=&c3val=&c3val_orig=&c4stat=&c4comp=&c4val=&c4val_orig=&is_dbl_dbl=&is_trp_dbl=&order_by=date_game&order_by_asc=&offset=900",context=ctx)
print(1)
t=str(s.read())
a=get_table(t)["Query Results Table"]
def strremove(x,y):
    a=''
    for i in x:
        if i!=y:
            a+=i
    return a
z=0
for i in a[1:]:
    if i[0]!='Rk':
        print(z)
        z+=1
        try:
            s1=request.urlopen('https://www.basketball-reference.com/boxscores/'+strremove(i[4],'-')+'0'+(i[5] if i[6]=='' else i[7])+'.html',context=ctx)
        except:
            try:
                s1 = request.urlopen('https://www.basketball-reference.com/boxscores/' + strremove(i[4],'-') + '0' + (
                    i[7] if i[6] == '' else i[5]) + '.html', context=ctx)
            except:
                print(i[4]+','+i[5] +','+i[6]+','+i[7]+',')
                continue
        t1=str(s1.read())
        a1=get_table(t1)
        for j in a1:
            if '(' in j:
                if any(x[0]==i[1] for x in a1[j]):
                    for k in a1[j][1:]:
                        try:
                            if all(int(k[x])>=10 for x in [13,14,19]) and k[0]!='Team Totals' and k[0]!=i[1]:
                                print('')
                                print(k[0])
                                print(i[1])
                        except:
                            pass

