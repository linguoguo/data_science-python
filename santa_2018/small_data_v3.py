#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  7 17:31:07 2019

@author: lin
"""

from matplotlib.collections import LineCollection
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
plt.style.use('seaborn-white')
import seaborn as sns
import random
import math
from concorde.tsp import TSPSolver
import time
import pylab as pl

#---------------- import data ----------------------------
cities =pd.read_csv('cities.csv')
def eratosthenes(n):
    P = [True for i in range(n+1)]
    P[0], P[1] = False, False
    p = 2
    l = np.sqrt(n)
    while p < l:
        if P[p]:
            for i in range(2*p, n+1, p):
                P[i] = False
        p += 1
        
    return P

# find cities that are prime numbers
prime_cities = eratosthenes(max(cities.CityId))
cities['prime'] = prime_cities
b=len(cities)
num=random.sample(range(1,b ), 156)
num.append(0)
df=cities.iloc[num]
df = df.reset_index(drop=True)
len(np.unique(df))
plt.scatter(df.X, df.Y,  c='blue',alpha=0.5,s=1)

#------------------ clustering --------------------------

from sklearn.mixture import GaussianMixture
n_cluster=4
mclusterer = GaussianMixture(n_components=n_cluster, tol=0.01, random_state=66, verbose=1).fit(df[['X', 'Y']].values)
df['mclust'] = mclusterer.predict(df[['X', 'Y']].values)
centers = df.groupby('mclust')['X', 'Y'].agg('mean').reset_index()
clust_c=['#630C3A', '#39C8C6', '#D3500C', '#FFB139']
colors = np.where(df["mclust"]%4==0,'#630C3A','-')
colors[df['mclust']%4==1] = '#39C8C6'
colors[df['mclust']%4==2] = '#D3500C'
colors[df['mclust']%4==3] = '#FFB139' 

    
plt.figure(figsize=(8, 5))
plt.scatter(df.X, df.Y,  color=colors,alpha=0.5,s=5)
for i in range(n_cluster):
    plt.scatter(centers.iloc[i].X, centers.iloc[i].Y, c='black', s=50)    
plt.show()

# ------------------ get the nearest point ---------------

def distance(a, b):
    return math.sqrt((b.X - a.X) ** 2 + (a.Y - b.Y) ** 2)

def nearest_point(df,mean):
    obj= []
    for i in range(len(df)) :
        obj.append(distance(df.iloc[i][['X','Y']],mean))
        dest=df.iloc[obj.index(min(obj))]['CityId']
    print('min=',dest)
    return dest

north_pole = df[df['CityId']==0]
n_p=north_pole[['mclust','X','Y']]
route=n_p.append(centers,ignore_index=True)
route=route.append(n_p,ignore_index=True)
centers = pd.concat([centers,pd.DataFrame(columns=['start_point','end_point'])],sort=False)
solver = TSPSolver.from_data(
    route.X,
    route.Y,
    norm="EUC_2D"
)
#--------------- solver the tsp for centers ---------------------
tour_data = solver.solve(time_bound = 60.0, verbose = True, random_seed = 42)
centers_c=centers.copy() 
for i in range(len(centers)):
    print (tour_data[0][i+1]-1)
    centers.iloc[i]=centers_c.iloc[tour_data[0][i+1]-1]
 
for i in range(1,n_cluster):
    a=int(centers.iloc[i].mclust)
    b=int(centers.iloc[i-1].mclust)
    print ('a',a,'b',b)
    coord=nearest_point(df[df['mclust']==a],centers.iloc[b][['X','Y']])
    centers.loc[i,'start_point']=coord
    
for i in range(0,n_cluster-1): 
    a=int(centers.iloc[i].mclust)
    b=int(centers.iloc[i+1].mclust)
    print ('a',a,'b',b)
    coord=nearest_point(df[df['mclust']==a],centers.iloc[b][['X','Y']])
    centers.loc[i,'end_point']=coord

a=centers.iloc[0].mclust
coord=nearest_point(df[df['mclust']==a],north_pole[['X','Y']])
centers.loc[0,'start_point']=coord

b=centers.iloc[n_cluster-1].mclust
coord=nearest_point(df[df['mclust']==b],north_pole[['X','Y']])
centers.loc[n_cluster-1,'end_point']=coord 

plt.figure(figsize=(8, 5))
plt.scatter(df.X, df.Y,  color=colors,alpha=0.5,s=5)
for i in range(n_cluster):
    plt.scatter(centers.iloc[i].X, centers.iloc[i].Y, c='black', s=50) 
    start=df[df['CityId']==centers.iloc[i].start_point]
    end=df[df['CityId']==centers.iloc[i].end_point]
    plt.scatter(start.X,start.Y,c='red',s=50)
    plt.scatter(end.X,end.Y,c='blue',s=50)
plt.show()

lines=[]
lines.append([(north_pole.X,north_pole.Y),(centers.X[0],centers.Y[0])])
for i in range(0,n_cluster-1):   
    print (i)
    lines.append([(centers.X[i],centers.Y[i]),(centers.X[i+1],centers.Y[i+1])]) 
lines.append([(north_pole.X,north_pole.Y),(centers.X[n_cluster-1],centers.Y[n_cluster-1])])
lc = LineCollection(lines, linewidths=2)
fig, ax = pl.subplots(figsize=(8,5))
#cities.plot.scatter(x='X', y='Y', s=0.07)
ax.scatter(north_pole.X, north_pole.Y, c='red', s=15)
plt.scatter(df.X, df.Y,  color=colors,alpha=0.5,s=1)
plt.scatter(centers.X, centers.Y, c='black', s=15)
for i in range(n_cluster): 
    start=df[df['CityId']==centers.iloc[i].start_point]
    end=df[df['CityId']==centers.iloc[i].end_point]
    plt.scatter(start.X,start.Y,c='green',s=20)
    plt.scatter(end.X,end.Y,c='blue',s=20)
ax.add_collection(lc)
ax.autoscale()
plt.show()

# ---------- solver the tsp by clusters ----------------
def to_end(df,p):
    x=df.iloc[len(df)-1]
    df.iloc[len(df)-1]=df.iloc[p]
    df.iloc[p]=x
    
    
def to_begin(df,p):
    x=df.iloc[0]
    df.iloc[0]=df.iloc[p]
    df.iloc[p]=x 
    
i=0 
df_c=df[df['mclust']==i]
df_c = df_c.reset_index(drop=True)
to_begin(df_c,2)


solver = TSPSolver.from_data(
    df_c.X,
    df_c.Y,
    norm="EUC_2D"
)

tour_c = solver.solve(time_bound = 60.0, verbose = True, random_seed = 44) 
df_r=df_c.copy() 
for i in range(len(df_c)):
    df_c.iloc[i]=df_r.iloc[tour_c[0][i]]


lines_c = [[(df_c.X[j],df_c.Y[j]),(df_c.X[j+1],df_c.Y[j+1])]for j in range(0,len(df_c)-1)]
lc = LineCollection(lines_c, linewidths=2)
fig, ax = pl.subplots(figsize=(8,5))
#ax.scatter(north_pole.X, north_pole.Y, c='red', s=15)
plt.scatter(df_c.X, df_c.Y,  color='grey',alpha=0.5,s=20)
plt.scatter(df_c[df_c['CityId']==a].X,df_c[df_c['CityId']==a].Y,c='black',s=20)
plt.scatter(df_c[df_c['CityId']==b].X,df_c[df_c['CityId']==b].Y,c='red',s=20)
#plt.scatter(centers.X, centers.Y, c='black', s=15) 
ax.add_collection(lc)
ax.autoscale()
plt.show()

def tol(df):
    d=0
    for i in range(0,len(df)-1):
        if (i+1)%10==0:
            d+=1.1*distance(df.iloc[i][['X','Y']],df.iloc[i+1][['X','Y']])
        else:
            d+=distance(df.iloc[i][['X','Y']],df.iloc[i+1][['X','Y']])
        print(i,d)    
    return d
    

print (tol(df_c))

def tol(df):
    d=0
    for i in range(0,len(df)-1):
        #print('/n')
        dis=distance(df.iloc[i][['X','Y']],df.iloc[i+1][['X','Y']])
        #print(i,' ',df.CityId[i],df.prime[i],'->',df.CityId[i+1],df.prime[i+1])
        if (i+1)%10==0 and df['prime'][i]==False:
            d+=1.1*dis
            print(i,df.CityId[i],df.prime[i])
        else:
            d+=dis
            #print(dis)
            
    return d


for i in range(1,2):
    df_r=df_c.copy()
    to_begin(df_r,i)
    solver = TSPSolver.from_data(
            df_r.X,
            df_r.Y,
    norm="EUC_2D"
    )
    tour_c = solver.solve(time_bound = 60.0, verbose = True, random_seed = 44) 
    df_2=df_r.copy() 
    for j in range(len(df_r)):
        df_r.iloc[j]=df_2.iloc[tour_c[0][j]]    
    df_r=df_r.append(df_r.iloc[0])
    df_r = df_r.reset_index(drop=True)
    lines_c = [[(df_r.X[m],df_r.Y[m]),(df_r.X[m+1],df_r.Y[m+1])]for m in range(0,len(df_r)-1)]
    lc = LineCollection(lines_c, linewidths=2)
    fig, ax = pl.subplots(figsize=(8,5))
    #ax.scatter(north_pole.X, north_pole.Y, c='red', s=15)
    plt.scatter(df_r.X, df_r.Y,  color='grey',alpha=0.5,s=20) 
    ax.add_collection(lc)
    ax.autoscale()
    plt.show()
    told=tol(df_r)    
    print(i,' : ',df_r.CityId[0],'->',df_r.CityId[len(df_r)-1],'dist : ',told)
    
a=np.array(range(len(df_c)))
b=a-len(a)
b=np.append(b,a)

        
for i in range(len(a)):
    print(a[b[i:i+len(a)]])     

def tangent(x,y):
    if not(x[0]==x[1]):
        return (y[1]-y[0])/(x[1]-x[0])
    else : 
        return None








i=1 
m=int(centers.iloc[i].mclust)
df_c=df[df['mclust']==m]
df_c = df_c.reset_index(drop=True)
df_c = pd.concat([df_c,pd.DataFrame(columns=['up_down'])],sort=False)
start=df[df['CityId']==centers.iloc[i].start_point]
end=df[df['CityId']==centers.iloc[i].end_point]
x=[float(start.X),float(end.X)]
y=[float(start.Y),float(end.Y)]
a=int(centers[centers['mclust']==m].start_point)    
b=int(centers[centers['mclust']==m].end_point) 
p1=list(df_c.CityId).index(a)
p2=list(df_c.CityId).index(b)
to_begin(df_c,p1)
to_end(df_c,p2)


if not(x[0]==x[1]):
    print ('hoho')
    tan=tangent(x,y)
    plt.figure(figsize=(8, 5))
    plt.scatter(centers.iloc[i].X, centers.iloc[i].Y, c='black', s=50)
    plt.scatter(start.X,start.Y,c='red',s=70)
    plt.plot(x,y,marker = 'o')
    plt.scatter(end.X,end.Y,c='blue',s=70)
    for j in range(1,len(df_c)-1):
        a=df_c.iloc[j].X
        b=df_c.iloc[j].Y
        c=tan*a-tan*x[0]+y[0]-b
        if c>=0:
            df_c.loc[j,'up_down']=0
            plt.scatter(a, b,  c=clust_c[0],alpha=0.5,s=5)
        else :
            plt.scatter(a, b,  c=clust_c[1],alpha=0.5,s=5)
            df_c.loc[j,'up_down']=1
    plt.show()
d_up=start.append(df_c[df_c['up_down']==0],ignore_index=True)
#df_up = df_up.reset_index(drop=True)
df_down=end.append(df_c[df_c['up_down']==1],ignore_index=True)
#df_down = df_down.reset_index(drop=True)


df_r_up=df_up.copy()
solver = TSPSolver.from_data(
        df_up.X,
        df_up.Y,
   norm="EUC_2D"
)
tour_up = solver.solve(time_bound = 60.0, verbose = True, random_seed = 44) 
for j in range(len(df_up)):
    df_up.iloc[j]=df_r_up.iloc[tour_up[0][j]] 
lines_up = [[(df_up.X[m],df_up.Y[m]),(df_up.X[m+1],df_up.Y[m+1])]for m in range(0,len(df_up)-1)]
lup = LineCollection(lines_up, linewidths=2)
fig, ax = pl.subplots(figsize=(8,5))
plt.scatter(df_up.X, df_up.Y,  color='grey',alpha=0.5,s=20)
plt.scatter(start.X,start.Y,c='red',s=70) 
ax.add_collection(lup)
ax.autoscale()
plt.show()
   

df_r_down=df_down.copy()
solver = TSPSolver.from_data(
        df_down.X,
        df_down.Y,
   norm="EUC_2D"
)
tour_down = solver.solve(time_bound = 60.0, verbose = True, random_seed = 44) 
for j in range(len(df_down)):
    df_down.iloc[j]=df_r_down.iloc[tour_down[0][j]] 
lines_down = [[(df_down.X[m],df_down.Y[m]),(df_down.X[m+1],df_down.Y[m+1])]for m in range(0,len(df_down)-1)]
ldown = LineCollection(lines_down, linewidths=2)
fig, ax = pl.subplots(figsize=(8,5))
plt.scatter(df_down.X, df_down.Y,  color='grey',alpha=0.5,s=20) 
plt.scatter(end.X,end.Y,c='blue',s=70)
ax.add_collection(ldown)
ax.autoscale()
plt.show()
   


fig, ax = pl.subplots(figsize=(8,5))
plt.scatter(start.X,start.Y,c='red',s=70)
plt.scatter(end.X,end.Y,c='blue',s=70)
plt.scatter(df_up.X, df_up.Y,  color='grey',alpha=0.5,s=20) 
plt.scatter(df_down.X, df_down.Y,  color='grey',alpha=0.5,s=20)
ldown = LineCollection(lines_down, linewidths=2)
lup = LineCollection(lines_up, linewidths=2)
ax.add_collection(lup)
ax.add_collection(ldown)
ax.autoscale()
plt.show()

