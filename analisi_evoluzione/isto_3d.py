import math, time
import matplotlib.pyplot as plt
import numpy as np

STAZIONI = 3
NUM_RICHIESTE = 10
VISIBILI = 10

def genera_richieste():
    richieste = []
    for p in range(STAZIONI):
        for a in range(STAZIONI):
            if p != a:
                richieste.append((p,a))
    return richieste

def var(c):
    variance = 0
    for i in range(STAZIONI):
        variance += c[i]**2
    return variance

def uguali(c1, c2):
    for i in range(STAZIONI):
        if c1[i] != c2[i]:
            return False
    return True

conf = [[0,0,0,1]]
nuova_conf = []

richieste = genera_richieste()

plt.ion()
fig = plt.figure()
ax = fig.add_subplot(projection='3d')

casi = 1
for r in range(NUM_RICHIESTE):
    casi *= 6
    for c in conf:
        for p,a in richieste:
            copia = c.copy()
            copia[p] -= 1
            copia[a] += 1
            nuova_conf.append(copia)

    # accorpa le configurazioni uguali
    conf = []

    while len(nuova_conf)>0:
        c = nuova_conf.pop()
        counter = c[-1]
        to_pop = []
        for i in range(len(nuova_conf)):
            if uguali(c,nuova_conf[i]):
                counter += nuova_conf[i][-1]
                to_pop.append(i)
        l = len(to_pop)
        for i in range(l):
            nuova_conf.pop(to_pop[l - i - 1])
        
        c[-1] = counter
        conf.append(c)

    somma = 0
    for c in conf:
        somma += c[-1]*var(c)

    varianza_attesa = somma/casi
    print(f'R:{r+1}')
    print(f'Varianza attesa: {varianza_attesa}')
    print(f'Dev standard: {math.sqrt(varianza_attesa)}')

    # istogramma
    ax.clear()
    ax.axes.set_zlim3d(bottom = 0, top = 0.20)

    x = []
    y = []
    weights = []

    for c in conf:
        for i in range(STAZIONI-1):
            if c[i] > VISIBILI/2 and c[i] < -VISIBILI/2:
                break
        else:
            x.append(c[0])
            y.append(c[1])
            weights.append(c[3])

    xbins = np.arange(start=-VISIBILI/2, stop=VISIBILI/2+2, step=1) - 0.25
    ybins = np.arange(start=-VISIBILI/2, stop=VISIBILI/2+2, step=1) - 0.25

    hist, xedges, yedges = np.histogram2d(x, y, bins = [xbins, ybins], weights=weights, density=True)

    # Construct arrays for the anchor positions of the bars
    xpos, ypos = np.meshgrid(xedges[:-1], yedges[:-1], indexing="ij")
    xpos = xpos.ravel()
    ypos = ypos.ravel()
    zpos = 0

    # Construct arrays with the dimensions for the bars.
    dx = dy = 0.5 * np.ones_like(zpos)
    dz = hist.ravel()

    ax.bar3d(xpos, ypos, zpos, dx, dy, dz, zsort='average')

    fig.canvas.draw()
    fig.canvas.flush_events()

plt.ioff()
plt.show()
