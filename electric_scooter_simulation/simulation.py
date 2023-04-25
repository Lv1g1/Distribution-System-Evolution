import random, math, time
import matplotlib.pyplot as plt

# numero stazioni
STAZIONI = 5

# numero di posti in ogni stazione
POSTAZIONI = 9

# numero totale dei monopattini
MONOPATTINI = STAZIONI*POSTAZIONI # metà delle postazioni disponibili

# puntica rtesiani pos stazioni
POSIZIONE_STAZIONI = [(0.0, 0.0), (0.5,0.5),(1,1),(1,0),(0,1)]

# tempo scandito da tick ogni tot secondi
TICK = 30

# durata simulazione in tick
SIMULATION_TIME = 1000

# numero di utenti generati ogni tick
MIN_UTENTI_PER_TICK = 0
MAX_UTENTI_PER_TICK = 10

# generazione casuale di un consumo percentuale tra minimo e massimo
# negativo consuma meno di quello calcolato in media, positivo consuma di più di quello calcolato in media
CONSUMO_MINIMO = -0.05
CONSUMO_MASSIMO = 0.1

# velocità 18 km/h -> 18/3600 km/s
VELOCITA_MEDIA = 18/3600*TICK # km

# ricarica monopattino
CHARGER = 3 # massimo numero di monopattini caricati contemporaneamente

MAX_BATTERY = 0.9 # priorità minima se è sopra lo 0.9
MIN_BATTERY = 0.8 # batteria minima per sbloccare

CHARGER_POWER = 3000  # 3 kWh
BATTERY_CAPACITY = 80 # 80 Wh
EFFICIENCY = 0.9 # 90% inventata non la so
# Time = Battery Capacity / (Charger Power x Charging Efficiency)
CHARGE_PER_TICK = TICK * CHARGER_POWER/3600/CHARGER * EFFICIENCY

AUTONOMIA = 7  
CONSUMO_PER_TICK = VELOCITA_MEDIA/AUTONOMIA*BATTERY_CAPACITY # batteria consumata dal monopattino ad ogni tick

PRINT = False # set True for detailed informations at every tick, will slow down the program

# SimulationPlotter
PLOTTER = True # will slow the simulation
SIZE_STAZIONI = 30
SIZE_MONOPATTINI = 10
COLOR_STAZIONI = 'gray'
COLOR_BATTERY = 'royalblue'
MAX_BATTERY_COLOR = 'darkgreen'
MIN_BATTERY_COLOR = 'darkred'

class SimulationPlotter:
    def __init__(self) -> None:
        self.lines = {} # variabile per salvarsi l'oggetto monopattino disegnato
        self.monopattini = [] # variabile per salvarsi i dati dei monopattini
        
        # Create new Figure and an Axes which fills it.
        self.fig = plt.figure(num='Simulation',figsize=(12, 8), layout="constrained")
        self.ax_dict = self.fig.subplot_mosaic(
            [
                ["bar", "simulation", "simulation"],
            ],
        )

        # Set title for the subplots
        self.ax_dict["simulation"].set_title('Map')
        self.ax_dict["bar"].set_title('Scooters Battery')

        #self.ax_dict["simulation"].set_xlim(-0.1, 1.1)
        self.ax_dict["simulation"].set_xticks([])
        #self.ax_dict["simulation"].set_ylim(-0.1, 1.1)
        self.ax_dict["simulation"].set_yticks([])

        # plot stazioni
        self.stazioni = [] 
        for i in range(STAZIONI):
            x, y = POSIZIONE_STAZIONI[i]
            color = COLOR_STAZIONI
            
            s,= self.ax_dict["simulation"].plot(x, y, marker='8',
                    markersize=SIZE_STAZIONI,
                    mfc= color)
            self.stazioni.append(s)

        # disegna l'istogramma per i livelli di batteria
        y = [i for i in range(MONOPATTINI)]
        id = [i for i in range(MONOPATTINI)]
        battery = [100 for i in range(MONOPATTINI)] # inizialmente carichi

        self.bar = self.ax_dict["bar"].barh(y=y, width=battery, tick_label=id, color=COLOR_BATTERY)

        # linee verticali per segnali livelli importanti di batteria
        self.ax_dict["bar"].axvline(MIN_BATTERY*100, color=MIN_BATTERY_COLOR) # minima batteria per partire
        self.ax_dict["bar"].axvline(MAX_BATTERY*100, color=MAX_BATTERY_COLOR) # priorità minima di ricarica se superiore

        self.battery = self.bar.get_children() # lista dei rettangoli che formano l'istogramma per facilitare la modifica
    
    def update(self):
        # aggiorna posizione monopattino
        id_to_remove = []
        for id,dx,dy,ax,ay in self.monopattini:
            m = self.lines[id]
            x = m.get_xdata()[0]
            y = m.get_ydata()[0]
            
            x += dx
            y += dy

            # se arrivato a destinazione rimuovilo
            if dx > 0 and x >= ax or dx < 0 and x <= ax or dy > 0 and y >= ay or dy < 0 and y <= ay:
                m.remove()
                del self.lines[id]
                id_to_remove.append(id)
            
            else: # altrimenti aggiorna i dati
                m.set_xdata(x)
                m.set_ydata(y)

        for id in id_to_remove:
            for i in range(len(self.monopattini)):
                if self.monopattini[i][0] == id:
                    self.monopattini.pop(i)
                    break

        # update
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def monopattino_partito(self, id, partenza, arrivo):
        px,py = POSIZIONE_STAZIONI[partenza]
        ax,ay = POSIZIONE_STAZIONI[arrivo]

        # disegna il monopattino
        line, = self.ax_dict["simulation"].plot(px, py,marker=f'${id}$',
                        markersize=SIZE_MONOPATTINI)

        self.lines[id] = line
        
        dist = math.sqrt((px-ax)*(px-ax)+(py-ay)*(py-ay))
        cos = (ax-px)/dist
        sin = (ay-py)/dist

        dx = VELOCITA_MEDIA*cos
        dy = VELOCITA_MEDIA*sin

        # per evitare problemi di approssimazione, probabilmente non serve
        ax += (px-ax)/1000
        ay += (py-ay)/1000

        self.monopattini.append((id,dx,dy,ax,ay))

    def change_battery(self, battery):
        # aggiorna i livelli di batteria
        for i in range(MONOPATTINI):
            self.battery[i].set_width(battery[i]*100)

    def end_simulation(self):
        plt.close(self.fig)
        plt.ioff()
                
class Utente:
    def __init__(self, id, partenza = None, arrivo = None) -> None:
        self.id = id
    
        # se non forniti generazione casuale di partenza e arrivo
        if partenza == None or arrivo == None: 
            self.partenza = random.randint(0,STAZIONI-1)
            self.arrivo = random.randint(0, STAZIONI-2)
            if self.arrivo >= self.partenza:
                self.arrivo += 1
        else:
            self.partenza = partenza
            self.arrivo = arrivo

        self.tempo_richiesta = None
        self.tempo_partenza = None
        self.tempo_attesa = None

        self.spostamento = None
        self.tempo_destinazione = None

        self.monopattino = None

    def richiesta(self, tempo):
        self.tempo_richiesta = tempo
    
    def partito(self, tempo)->None:
        self.tempo_partenza = tempo
        self.tempo_attesa = tempo - self.tempo_richiesta
        self.tempo_destinazione = self.spostamento/VELOCITA_MEDIA

    def consumo_batteria(self):
        disturbo = random.uniform(CONSUMO_MINIMO, CONSUMO_MASSIMO)
        self.monopattino.consumo(disturbo)

class Monopattino:
    def __init__(self, id, battery):
        self.id = id
        self.battery = battery
        self.perc = battery/BATTERY_CAPACITY # livello percentuale batteria

        self.priority = None

    # carica la batteria e ritorna la percentuale della batteria
    def charge(self) -> float:
        self.battery += CHARGE_PER_TICK
        
        if self.battery >= BATTERY_CAPACITY:
            self.charged = True
            self.battery = BATTERY_CAPACITY
            self.perc = 1
        else:
            self.perc = self.battery/BATTERY_CAPACITY

        return self.perc
    
    # calcola il consumo della batteria
    def consumo(self, disturbo):
        self.battery -= CONSUMO_PER_TICK*(1 + disturbo)
        self.perc = self.battery/BATTERY_CAPACITY

# lista ordinata per priorità
class PriorityList:
    def __init__(self) -> None:
        self.list = []

    # inserisce i monopattini in ordine decrescente di priorità 
    def add(self, m: Monopattino):
        for i in range(len(self.list)):
            if self.list[i].priority < m.priority:
                self.list.insert(i, m)
                break
            elif i == len(self.list) - 1:
                self.list.append(m)

        if len(self.list) == 0:
            self.list.append(m)

    # rimuove e ritorna l'elemento con priorità minima
    def pop(self):
        if len(self.list)>0:
            return self.list.pop()
        
        return None
    
    # rimuove e ritorna l'elemento con priorità massima
    def pop_first(self):
        if len(self.list)>0:
            return self.list.pop(0)
        
        return None
    
    # rimuove e ritorna il monopattino con la batteria più alta
    def pop_max_charged(self):
        if len(self.list) > 0:
            j = 0
            best = self.list[0].perc
            
            for i in range(1, len(self.list)):
                if self.list[i].perc > best:
                    j = i
                    best = self.list[i].perc

            return self.list.pop(j)
        return None
        
    # ritorna in ordine decrescente di pirorità i monopattini con la priorità più alta
    def ret_max_priority(self, n:int) -> list:
        if len(self.list) <= n:
            return self.list
        else:
            return self.list[0:n]

    # ritorna in ordine decrescente di priorità i monopattini con la priorità più bassa
    def ret_min_priority(self, n:int) -> list:
        if len(self.list) <= n:
            return self.list
        else:
            return self.list[-n:]

class Stazione: # stazione reale, fisica
    def __init__(self, id) -> None:
        self.id = id
        self.in_stazione = PriorityList()

    # rimuove e ritorna un mopattino da quelli in stazione
    def sblocco(self):
        return self.in_stazione.pop_max_charged()
    
    # chiamata all'arrivo di un monopattino in stazione
    # ritorna 1 se è subito disponibile per partire altrimenti ritorna 0
    def arrivo(self, monopattino:Monopattino):
        self.calc_priority(monopattino)
        self.in_stazione.add(monopattino)

        if monopattino.perc >= MIN_BATTERY:
            return 1
        return 0

    # carica i monopattini con priorità più alta
    # ritorna il numero di monopattini passati da non_carichi a carichi
    def charge(self) -> list:
        nuovi_carichi = 0
        in_charge = self.in_stazione.ret_max_priority(CHARGER)
        for monopattino in in_charge:
            non_carico = False
            if monopattino.perc < MIN_BATTERY:
                non_carico = True
                
            battery = monopattino.charge()

            if non_carico and battery >= MIN_BATTERY:
                nuovi_carichi += 1

        return nuovi_carichi

    # calcola la priorità dei monopattini
    def calc_priority(self, m:Monopattino): # priorità = batteria, se è sopra il 90% diventa negativa
        if m.perc >= MAX_BATTERY:
            m.priority = -m.perc
        else:
            m.priority = m.perc

class ModelloStazione: # modello della stazione usato dal cloud per la gestione degli spostamenti
    def __init__(self, stazione:Stazione, pos) -> None:
        self.stazione = stazione
        
        self.x, self.y = pos
        
        self.liberi = POSTAZIONI # posti liberi
        self.disponibili = 0     # monopattini disponibili

        self.in_stazione = []
        self.in_arrivo = []

        self.arrivi = []   # id utenti che richiedono di partire da questa stazione
        self.partenze = [] # id utenti che richiedono di arrivare in questa stazione

class Cloud:
    def __init__(self, stazioni, posizioni) -> None:
        self.stazioni = {stazioni[i].id: ModelloStazione(stazioni[i],posizioni[i]) for i in range(len(stazioni))}

        self.richieste = {} # richieste non ancora soddisfatte

    # ritorna risultato, lista utenti
    # risultato: intero se 1 successo altrimenti fallimento (se fallimento gli altri paremetri sono None)
    # lista utenti: lista utenti le quali richieste sono state soddisfatte
    def richiesta_utente(self, richiedente:Utente)->tuple:
        id_utente = richiedente.id
        id_arrivo = richiedente.arrivo
        id_partenza = richiedente.partenza

        liberi = self.stazioni[id_arrivo].liberi
        disponibile = self.check_sblocco(id_partenza)
        
        if liberi > 0 and disponibile:
            richiedente.monopattino = self.sblocco(id_partenza)
            self.stazioni[id_arrivo].in_arrivo.append(richiedente.monopattino.id)
            richiedente.spostamento = self.distanza(id_partenza, id_arrivo)
            self.stazioni[id_arrivo].liberi -= 1
            return 1,[richiedente] # successo
        
        elif liberi > 0: # monopattino non disponibile in stazione
            self.stazioni[id_arrivo].arrivi.append(id_utente)
            self.stazioni[id_partenza].partenze.append(id_utente)
            self.richieste[id_utente] = richiedente # la richiesta verrà riesaminata quando ci saranno monopattini disponibili
            return -1,None # fallimento non è disponibile un monopattino nella stazione di partenza
        
        elif disponibile: # non ci sono posti nella stazione di arrivo
            utenti = self.trova_percorso(id_partenza, id_arrivo) # algortimo di ricerca
            if utenti != None: # percorso trovato
                # partenza utente richiesta
                richiedente.spostamento = self.distanza(id_partenza, id_arrivo)
                richiedente.monopattino = self.sblocco(id_partenza)
                self.stazioni[id_arrivo].in_arrivo.append(richiedente.monopattino.id)
                
                self.stazioni[id_arrivo].liberi -= 1
                
                # partenza resto degli utenti
                for utente in utenti:
                    partenza = utente.partenza
                    arrivo =  utente.arrivo

                    utente.spostamento = self.distanza(partenza, arrivo)
                    utente.monopattino = self.sblocco(partenza)
                    self.stazioni[arrivo].in_arrivo.append(utente.monopattino.id)
                    
                    self.stazioni[arrivo].liberi -= 1
                    
                    del self.richieste[utente.id] # rimuove la richiesta dalla lista di richieste in sospeso
                    self.stazioni[partenza].partenze.remove(utente.id) # rimozione dalle partenze
                    self.stazioni[arrivo].arrivi.remove(utente.id) # rimozione dagli arrivi

                utenti.insert(0,richiedente) # aggiunto richiedente alla lista degli utenti
                
                return 1,utenti # successo
            
            # percorso non trovato
            for utente in self.stazioni[id_arrivo].arrivi:
                if utente == id_utente:
                    break
            else:
                self.stazioni[id_arrivo].arrivi.append(id_utente)
                self.stazioni[id_partenza].partenze.append(id_utente)
                self.richieste[id_utente] = richiedente # la richiesta verra riesaminata quando ci saranno partenze/richieste dalla stazione di arrivo
            return -2,None # fallimento non ci sono posti nella stazione di arrivo
            
        else: # non ci sono posti nella stazione di arrivo e nemmeno monopattini in quella di partenza
            self.stazioni[id_arrivo].arrivi.append(id_utente)
            self.stazioni[id_partenza].partenze.append(id_utente)
            self.richieste[id_utente] = richiedente # la richiesta deve prima diventare -1 o -2 per poter essere riesaminata
            return -3,None # fallimento non ci sono posti nella stazione di arrivo e nemmeno monopattini in quella di partenza

    # verifica la presenza di monopattini disponibili
    def check_sblocco(self, id_stazione):
        if self.stazioni[id_stazione].disponibili > 0:
            return True
        return False

    # sblocca un monopattino
    def sblocco(self, id_stazione): # da per scontato che sia possibile sbloccare (controllato precedentemente con check_sblocco)
        monopattino = self.stazioni[id_stazione].stazione.sblocco()
        self.stazioni[id_stazione].liberi += 1
        self.stazioni[id_stazione].disponibili -= 1
        self.stazioni[id_stazione].in_stazione.remove(monopattino.id)

        return monopattino

    # calcola la distanza tra 2 stazioni
    def distanza(self, id_1, id_2)->float:
        x_1 = self.stazioni[id_1].x
        y_1 = self.stazioni[id_1].y
        x_2 = self.stazioni[id_2].x
        y_2 = self.stazioni[id_2].y

        diff_x = x_1 - x_2
        diff_y = y_1 - y_2

        return math.sqrt(diff_x*diff_x+diff_y*diff_y)
    
    # consideriamo caso in cui ci sono monopattini disponibili nella stazione di partenza e i posti di quella di arrivo sono tutti occupati
    # ritorna la lista di utenti per completare il percorso dalla stazione di arrivo a quella di partenza
    def trova_percorso(self, id_partenza, id_arrivo):
        if len(self.stazioni[id_arrivo].partenze) > 0 and self.check_sblocco(id_arrivo):
            # ricerca se c'è qualcuno nella stazione di arrivo che vuole andare in qeulla di partenza
            for id in self.stazioni[id_arrivo].partenze:
                ultimo_utente = self.richieste[id]
                prossima = ultimo_utente.arrivo
                if prossima == id_partenza: # se la trova ritorna l'utente 
                    return [ultimo_utente]

            stazione_visitate = [id_arrivo]
            percorsi = [self.stazioni[id_arrivo].partenze.copy()]
            soluzione = []

            # si interrompe quando sono finiti tutti i possibili percorsi
            while len(percorsi) > 0:
                if len(percorsi[-1]) > 0:
                    utente = self.richieste[percorsi[-1].pop(0)]
                    arrivo = utente.arrivo

                    if arrivo not in stazione_visitate:
                        stazione_visitate.append(arrivo)
                        # se non ci sono partenze o non ci sono monopattini in stazione è inutile aggiungere
                        if len(self.stazioni[arrivo].partenze) > 0 and self.check_sblocco(arrivo):
                            soluzione.append(utente)
                            # ricerca della stazione di partenza per concludere il percorso
                            for id in self.stazioni[arrivo].partenze:
                                ultimo_utente = self.richieste[id]
                                prossima = ultimo_utente.arrivo
                                if prossima == id_partenza: # se la trova ritorna la lista di utenti 
                                    soluzione.append(ultimo_utente)
                                    return soluzione
                            
                            percorsi.append(self.stazioni[arrivo].partenze.copy())

                else:
                    percorsi.pop()
                    if len(soluzione)>0:
                        soluzione.pop()
        return None

    # chiamata ogni volta che un monopattino arriva a destinazione
    # per semplicità della simulazione il cloud viene chiamato appena un utente arriva a destinazione e avvisa la stazione,
    # dovrebbe essere il contrario, la stazione rileva un monopattino e avvisa il cloud
    def utente_arrivato(self, utente:Utente):
        stazione = utente.arrivo
        self.stazioni[stazione].in_stazione.append(utente.monopattino.id) # modello stazione
        self.stazioni[stazione].in_arrivo.remove(utente.monopattino.id) # è arrivato
        disponibile = self.stazioni[stazione].stazione.arrivo(utente.monopattino) # stazione reale
        
        if disponibile == 1: # se il monopattino arrivato è carico
            return self.monopattino_disponibile(stazione)
        return 0, None
    
    # chiamata ogni volta che un monopattino da non_carico passa a carico
    def monopattino_disponibile(self, stazione):
        self.stazioni[stazione].disponibili += 1
        
        res = 0
        utenti_soddisfatti = []
        id = 0

        for id in self.stazioni[stazione].partenze:
            richiesta = self.richieste[id]
            res, utenti_soddisfatti = self.richiesta_utente(richiesta)
            if res == 1:
                break # monopattino usato
            
        if res == 1:
            # rimozione nel ciclo non è possibile perchè stiamo iterando le partenze quindi va fatta dopo
            richiesta = self.richieste[id]
            del self.richieste[id] # rimuove la richiesta dalla lista di richieste in sospeso
            self.stazioni[richiesta.arrivo].arrivi.remove(id)
            self.stazioni[richiesta.partenza].partenze.remove(id)

        return res, utenti_soddisfatti

    # serve solo nel setup della simulazione ad aggiungere monopattini
    def add_monopattino(self, stazione, monopattino:Monopattino):
        self.stazioni[stazione].liberi -= 1
        self.stazioni[stazione].disponibili += 1
        self.stazioni[stazione].in_stazione.append(monopattino.id) # modello stazione
        self.stazioni[stazione].stazione.arrivo(monopattino) # stazione reale

    def printa_stazioni(self):
        print('id stazine - posti liberi - mon disponibili - mon in stazione - batteria - mon in arrivo')
        keys = self.stazioni.keys()
        for k in keys:
            lista = [int(m.perc*100) for m in self.stazioni[k].stazione.in_stazione.list]
            print(k,self.stazioni[k].liberi,self.stazioni[k].disponibili,self.stazioni[k].in_stazione,lista,self.stazioni[k].in_arrivo)

# genera un numero casuale di utenti
def genera_utenti(id):
    utenti = []
    n = random.randint(MIN_UTENTI_PER_TICK,MAX_UTENTI_PER_TICK)
    for i in range(n):
        utenti.append(Utente(id + i))
    return id+n, utenti

# simulazione
def simulazione():
    # inizializziamo le stazioni
    stazioni = []
    for i in range(STAZIONI):
        stazioni.append(Stazione(i))

    # inizializzazione cloud
    cloud = Cloud(stazioni, POSIZIONE_STAZIONI)

    # inizializzazione monopattini
    monopattini = [Monopattino(i, BATTERY_CAPACITY) for i in range(MONOPATTINI)]

    # aggiunta dei monopattini
    for m in monopattini:
        s = m.id % STAZIONI
        cloud.add_monopattino(s, m)

    # inizializzazione tempo
    t = 0

    utenti_a_destinazione = []
    utenti_in_viaggio = []
    utenti_in_attesa = {} # utenti con richieste non ancora completate

    id = 0 # id prossimo utente

    if PLOTTER: # parte grafica
        plt.ion() 
        plotter = SimulationPlotter()

    # variabile per valutare la performance
    attese = 0 # numero di utenti che hanno atteso
    tot_attesa = 0 # tick totali di attesa
    lista_tick_attesa = [] # lista tick inizio attese
    lista_attese = [] # lista utenti in attesa ad ogni singolo tick

    # ciclo
    while t < SIMULATION_TIME:
        # fa avanzare il tempo
        t += 1
        if t%1000==0:
            print(t)

        if PLOTTER:
            # aggiorna la simulazione
            plotter.update()
            time.sleep(0.1)
        
        # parametri per la valutazione della simulazione
        tot_attesa += len(utenti_in_attesa)
        lista_attese.append(len(utenti_in_attesa))

        # consumo batteria monopattini
        for utente in utenti_in_viaggio:
            utente.consumo_batteria()

        # caricamento monopattini
        to_add = []
        to_remove = []
        for stazione in stazioni:
            disponibili = stazione.charge()

            for i in range(disponibili): # se ci sono dei monopattini disponibili
                result, utenti_soddisfatti = cloud.monopattino_disponibile(stazione.id)
                if result == 1:
                    for i in range(len(utenti_soddisfatti)):
                        utenti_soddisfatti[i].partito(t)
                        del utenti_in_attesa[utenti_soddisfatti[i].id]
                        to_add.append(utenti_soddisfatti[i])

                        if PLOTTER:
                            plotter.monopattino_partito(utenti_soddisfatti[i].monopattino.id, utenti_soddisfatti[i].partenza, utenti_soddisfatti[i].arrivo)

        for utente in to_remove:
            utenti_in_viaggio.remove(utente)

        for utente in to_add:
            utenti_in_viaggio.append(utente)

        if PLOTTER:
            # display livello batterie
            plotter.change_battery([m.perc for m in monopattini])

        # utenti in viaggio
        to_add = []
        to_remove = []
        for utente in utenti_in_viaggio:
            utente.tempo_destinazione -= 1 # decremento tick di tempo mancante per l'arrivo
            if utente.tempo_destinazione <= 0:
                # utente arrivato a destinazione
                result, utenti_soddisfatti = cloud.utente_arrivato(utente)
                if result == 1: # potrebbe essere che appena arriva un monopattino qualcuno riparta subito
                    for i in range(len(utenti_soddisfatti)):
                        utenti_soddisfatti[i].partito(t)
                        del utenti_in_attesa[utenti_soddisfatti[i].id]
                        to_add.append(utenti_soddisfatti[i])

                        if PLOTTER:
                            plotter.monopattino_partito(utenti_soddisfatti[i].monopattino.id, utenti_soddisfatti[i].partenza, utenti_soddisfatti[i].arrivo)

                #utenti_a_destinazione.append(utente)
                to_remove.append(utente)
        
        for utente in to_remove:
            utenti_in_viaggio.remove(utente)

        for utente in to_add:
            utenti_in_viaggio.append(utente)

        # creazione di nuovi utenti
        id, utenti = genera_utenti(id)
        
        # nuovi utenti mandano richieste al cloud
        for utente in utenti:
            utente.richiesta(t)
            
            result, utenti_soddisfatti = cloud.richiesta_utente(utente)

            if result == 1:
                utente.partito(t)
                utenti_in_viaggio.append(utente)
                
                if PLOTTER:
                    plotter.monopattino_partito(utente.monopattino.id, utente.partenza, utente.arrivo)
                
                for i in range(1, len(utenti_soddisfatti)):
                    utenti_soddisfatti[i].partito(t)
                    del utenti_in_attesa[utenti_soddisfatti[i].id]
                    utenti_in_viaggio.append(utenti_soddisfatti[i])
                    
                    if PLOTTER:
                        plotter.monopattino_partito(utenti_soddisfatti[i].monopattino.id, utenti_soddisfatti[i].partenza, utenti_soddisfatti[i].arrivo)
            else:
                utenti_in_attesa[utente.id] = utente

                # parametri per valutare la simulazione
                attese += 1
                lista_tick_attesa.append(t)

        if PRINT:
            print(f'\n   time {t}\n')
            cloud.printa_stazioni()
            # print(f'arrivati : {len(utenti_a_destinazione), [u.id for u in utenti_a_destinazione]}')
            # print(f'in viaggio : {len(utenti_in_viaggio), [u.id for u in utenti_in_viaggio]}')
            print(f'\nutenti totali : {id}')
            print(f'utenti in attesa: {len(utenti_in_attesa)}')
            print(f'partenza, arrivo : {[(utenti_in_attesa[key].partenza, utenti_in_attesa[key].arrivo) for key in utenti_in_attesa.keys()]}')

    # Simulazione conclusa
    if PLOTTER: # chiusura del simulation_plotter
        plotter.end_simulation() 

    # Calcolo di paremetri per valutare la performance del sistema
    prob_attesa = attese/id
    attesa_media_per_utente = tot_attesa/id
    lunghezza_media_attesa = tot_attesa/attese
    print(
f"""
Numero Utenti: {id}
Numero Attese: {attese}
Attesa totale: {tot_attesa}
Lunghezza media attesa: {lunghezza_media_attesa}
Attesa media per utente: {attesa_media_per_utente}
Probabilità di rimanere in attesa: {prob_attesa*100}
""")

    #return id,attese,tot_attesa,lunghezza_media_attesa,attesa_media_per_utente,prob_attesa
    # grafici per mostrare la conclusione
    fig = plt.figure(num='Conclusions', figsize=(12, 8), layout="constrained")
    ax_dict = fig.subplot_mosaic(
        [
            ["graph"],
            #["bar"]
        ],
    )

    # Set title for the subplots axes
    #ax_dict["bar"].set_ylabel('nuove attese')
    ax_dict["graph"].set_ylabel('utenti in attesa')

    # istogramma
    ticks = [i for i in range(SIMULATION_TIME)]
    # nuove_attese = [0 for i in range(SIMULATION_TIME)]
    # for tick in lista_tick_attesa:
    #     nuove_attese[tick-1] += 1

    # ax_dict["bar"].bar(ticks, height=nuove_attese)

    # grafico
    ax_dict["graph"].plot(ticks,lista_attese)

    plt.show()

if __name__ == '__main__':
    simulazione()
#     utenti = attese = tot_attesa = lunghezza_media_attesa = attesa_media_per_utente = prob_attesa = 0
#     for i in range(100):
#         ut,att,tot_a,lunghezza_m,attesa_m,p = simulazione()
#         utenti += ut
#         attese += att
#         tot_attesa += tot_a
#         lunghezza_media_attesa += lunghezza_m
#         attesa_media_per_utente += attesa_m
#         prob_attesa += p

#     print(
# f"""
# Numero Utenti: {utenti/100}
# Numero Attese: {attese/100}
# Attesa totale: {tot_attesa/100}
# Lunghezza media attesa: {lunghezza_media_attesa/100}
# Attesa media per utente: {attesa_media_per_utente/100}
# Probabilità di rimanere in attesa: {prob_attesa}
# """)

    
