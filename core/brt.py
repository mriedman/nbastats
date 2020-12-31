#coding: utf-8
def get_table(x, mode='N'):
    a=x.split('<caption>')[1:]
    b,c={},{}
    for i in a:
        i1=(i.split('</table>')[0]).split('</caption>')
        #print(i1)
        b[i1[0]]=i1[1]
    for i in b:
        #print(i)
        i1=b[i].split('<tr')[1:]
        i2=[]
        for j in i1:
            j1=split2(j,'</th>','</td>')[:-1]
            j2=[]
            for k in j1:
                '''if mode=='PBP':
                    k1=k.split('<')[1:]
                    k2=[l.split('>')[-1] for l in k1]
                    k3=''
                    for l in k2:
                        k3+=l
                    j2.append(k3)'''
                if mode=='PBP':
                    k1=k.split('<')[1:]
                    k2=[l.split('>') for l in k1]
                    k3=''
                    for l in k2:
                        if not l[0][:2] == 'a ':
                            k3+=l[1]
                        else:
                            if '/players/' in l[0]:
                                p_id = l[0].split('/players/')[1].split('.html')[0][2:]
                                p_name = l[1]
                            elif '/coaches/' in l[0]:
                                p_id = l[0].split('/coaches/')[1].split('.html')[0]
                                p_name = l[1]
                            else:
                                raise ValueError('WHAT\'S THE PLAYER ID???')
                            k3+= '$$'+p_id+'$$'+p_name+'$$'
                    j2.append(k3)
                elif mode=='LU' and k==j1[1]: #Lineup
                    k1=k.split('" href="')[:-1]
                    k2=[]
                    for l in k1:
                        k2.append(l.split('data-tip="')[1])
                    j2.append(k2)
                else:
                    k1 = split2(k,'</a>','</strong>')[0].split('>')[-1]
                    j2.append(k1)
                if mode=='Link':
                    if 'href=' in k:
                        k1 = k.split('href=')[1]
                        k2 = k1.split(k1[0])[1]
                        j2.append(k2)
            i2.append(j2)
        c[i]=i2
    return c
def split2(y,*x):
    a0=y.split(x[0])
    a=[i for i in a0]
    for i in x[1:]:
        i0=0
        for j in a:
            k=j.split(i)
            if len(k)>1:
                a=a[:i0]+k+a[i0+1:]
            i0+=1
    return a