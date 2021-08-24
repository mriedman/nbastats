from core.brt import *
from urllib import request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

t = str(request.urlopen('https://www.basketball-reference.com/teams/', context=ctx).read())
tables = get_table(t, mode='Link')
nameyears = {}
abbrtocode = {}
abbrtoname = {}
nametocode = {}
for i in tables['Active Franchises Table']+tables['Defunct Franchises Table']:
    print(i)
    if i[1][0] == '/':
        names = set()
        t1 = str(request.urlopen('https://www.basketball-reference.com' + i[1], context=ctx).read())
        tables1 = get_table(t1,mode = 'Link')
        for i in tables1:
            currname = tables1[i][1][1].split('/')[2]
            nameyears[currname] = {}
            for j in tables1[i]:
                if '/' in j[1]:
                    name = j[1].split('/')[2]
                    names.add((name,j[4]))
                    abbrtocode[name] = currname
                    abbrtoname[name] = j[4]
                    nametocode[j[4]] = currname
                    nameyears[currname][str(int(j[0][:4])+1)] = name
with open('teamcodes.py','w') as file:
    file.write('nameyears = '+str(nameyears))
    file.write('\nabbrtocode = '+str(abbrtocode))
    file.write('\nabbrtoname = ' + str(abbrtoname))
    file.write('\nnametocode = ' + str(nametocode))
    file.write('\nnametoabbr = {v: k for k, v in abbrtoname.items()}\n')
