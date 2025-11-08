# match3_terminal.py
# Simulare automata match-3 in terminal.
# Scris "manual" cu concepte de anul I: liste, for, while, if, functii, random.

import random
import time
import os
import csv

# ---------- Setari ----------
LINII = 11
COLOANE = 11
CULORI = 4            # culori 1..4
PRAG_PUNCTE = 10000
NUMAR_JOCURI = 100

# Daca vrei reproductibilitate, seteaza un seed
# random.seed(0)

# Animatie: True = arata pas-cu-pas; False = doar rezumat.
# Pentru a nu ingreuna timpul total, animatie va fi activata doar pentru primul joc.
ANIMATIE_PENTRU_PRIMUL_JOC = True
PAUZA_INTRE_PASI = 0.25   # secunde (0.25 = lent; mareste daca vrei mai lent)

# ---------- Functii utile ----------
def curata_ecran():
    """Curata ecranul terminalului pentru 'animație'."""
    os.system('cls' if os.name == 'nt' else 'clear')

def afiseaza_tabla(tabla, scor_curent, swapuri, arata_animatie):
    """Afiseaza tabla cu indici si info despre scor si swap-uri.
       Daca arata_animatie este True, sterge ecranul si face o pauza pentru efect vizual."""
    if arata_animatie:
        curata_ecran()
    print("SCOR:", scor_curent, " | SWAP-URI:", swapuri)
    # antet coloane
    header = "    "
    for j in range(COLOANE):
        header += "{:2d} ".format(j)
    print(header)
    # linii
    for i in range(LINII):
        linie_text = "{:2d}: ".format(i)
        for j in range(COLOANE):
            linie_text += " {:d} ".format(tabla[i][j])
        print(linie_text)
    print()
    if arata_animatie:
        time.sleep(PAUZA_INTRE_PASI)

# ---------- Generare initiala ----------
def genereaza_tabla():
    """Returneaza o tabla LINII x COLOANE cu valori random 1..CULORI."""
    tabla = []
    for i in range(LINII):
        rand = []
        for j in range(COLOANE):
            rand.append(random.randint(1, CULORI))
        tabla.append(rand)
    return tabla

# ---------- Detectare formatiuni ----------
def gaseste_formatiuni_si_lungi(tabla):
    """
    Gaseste toate pozitiile care fac parte din formatiuni orizontale sau verticale.
    Returneaza:
      - set_pozitii: set de tuple (i,j) care trebuie eliminate
      - dictionar_lungimi: pozitie -> lungimea maxima a formațiunii di care face parte acea pozitie
    Aceasta permite regula anti-dublare: daca pozitia este in doua formatiuni, retinem lungimea maxima.
    """
    set_pozitii = set()
    dictionar_lungimi = {}  # (i,j) -> lungime_max

    # Orizontal
    for i in range(LINII):
        j = 0
        while j < COLOANE:
            val = tabla[i][j]
            k = j + 1
            while k < COLOANE and tabla[i][k] == val:
                k += 1
            lungime = k - j
            if val != 0 and lungime >= 3:
                for col in range(j, k):
                    set_pozitii.add((i, col))
                    veche = dictionar_lungimi.get((i, col), 0)
                    if lungime > veche:
                        dictionar_lungimi[(i, col)] = lungime
            j = k

    # Vertical
    for j in range(COLOANE):
        i = 0
        while i < LINII:
            val = tabla[i][j]
            k = i + 1
            while k < LINII and tabla[k][j] == val:
                k += 1
            lungime = k - i
            if val != 0 and lungime >= 3:
                for lin in range(i, k):
                    set_pozitii.add((lin, j))
                    veche = dictionar_lungimi.get((lin, j), 0)
                    if lungime > veche:
                        dictionar_lungimi[(lin, j)] = lungime
            i = k

    return set_pozitii, dictionar_lungimi

# ---------- Punctaj ----------
def punct_per_bomboana_dupa_lungime(lungime):
    """Intoarce punctul acordat unei bomboane in functie de lungimea formațiunii din care face parte."""
    if lungime == 3:
        return 20
    elif lungime == 4:
        return 30
    else:  # lungime >= 5
        return 40

def calculeaza_puncte_din_dictionar_lungimi(dictionar_lungimi):
    """Calculeaza punctele totale din dictionarul pozitie->lungime_max (suma punctelor per bomboana)."""
    total = 0
    for poz, lung in dictionar_lungimi.items():
        total += punct_per_bomboana_dupa_lungime(lung)
    return total

# ---------- Eliminare + Gravitate + Reumplere ----------
def elimina_formatiuni(tabla):
    """Marcheaza si sterge formatiunile curente. Returneaza (puncte_obtinute, s_a_eliminat_bool, dictionar_lungimi)."""
    set_pozitii, dictionar_lungimi = gaseste_formatiuni_si_lungi(tabla)
    if not set_pozitii:
        return 0, False, {}
    # Setam la 0
    for (i, j) in set_pozitii:
        tabla[i][j] = 0
    # calcul puncte conform regulii anti-dublare
    puncte = calculeaza_puncte_din_dictionar_lungimi(dictionar_lungimi)
    return puncte, True, dictionar_lungimi

def aplica_gravitatie(tabla):
    """Face bomboanele sa cada: pentru fiecare coloana, muta valorile nenule jos si mentine 0 sus."""
    for j in range(COLOANE):
        colo = []
        for i in range(LINII):
            if tabla[i][j] != 0:
                colo.append(tabla[i][j])
        # numar goluri
        goluri = LINII - len(colo)
        # construim coloana noua: goluri (0) sus, apoi valorile nenule
        noua_colo = [0]*goluri + colo
        for i in range(LINII):
            tabla[i][j] = noua_colo[i]

def reumple(tabla):
    """Inlocuieste 0-urile cu valori aleatoare 1..CULORI (de sus in jos)."""
    for i in range(LINII):
        for j in range(COLOANE):
            if tabla[i][j] == 0:
                tabla[i][j] = random.randint(1, CULORI)

# ---------- Cascade ----------
def proceseaza_toate_cascadele(tabla, scor_curent, swapuri, arata_animatie):
    """
    Aplica repetat: detectare formatiuni -> eliminare -> punctaj -> gravitate -> reumplere,
    pana cand nu mai exista formatiuni.
    Returneaza scor_updatat.
    Afiseaza pas-cu-pas daca arata_animatie este True.
    """
    while True:
        afiseaza_tabla(tabla, scor_curent, swapuri, arata_animatie)
        puncte, s_a_eliminat, dictionar = elimina_formatiuni(tabla)
        if not s_a_eliminat:
            break
        # afisam detaliu eliminare daca animatie
        if arata_animatie:
            print("Eliminare detectata. Pozitii eliminate:", len(dictionar), " -> +", puncte, "p")
            time.sleep(PAUZA_INTRE_PASI)
        scor_curent += puncte
        aplica_gravitatie(tabla)
        if arata_animatie:
            afiseaza_tabla(tabla, scor_curent, swapuri, arata_animatie)
        reumple(tabla)
        if arata_animatie:
            afiseaza_tabla(tabla, scor_curent, swapuri, arata_animatie)
    return scor_curent

# ---------- Simulare swap pentru evaluare ----------
def simuleaza_swap_pentru_evaluare(tabla, i1, j1, i2, j2):
    """Simuleaza swap pe o copie a tablei si aplica toate cascadele; returneaza punctele obtinute."""
    copie = [rand[:] for rand in tabla]
    # swap
    copie[i1][j1], copie[i2][j2] = copie[i2][j2], copie[i1][j1]
    puncte_total = 0
    while True:
        puncte, s_a_eliminat, dictionar = elimina_formatiuni(copie)
        if not s_a_eliminat:
            break
        puncte_total += puncte
        aplica_gravitatie(copie)
        reumple(copie)
    return puncte_total

# ---------- Gasire cel mai bun swap ----------
def gaseste_cel_mai_bun_swap(tabla):
    """
    Parcurge toate swap-urile ortogonale (dreapta si jos pentru fiecare pozitie),
    simuleaza fiecare swap si alege swap-ul cu cele mai multe puncte simulate.
    Returneaza (i1,j1,i2,j2,puncte_simulate) sau None daca niciun swap nu produce puncte.
    """
    cel_mai_bun = None
    cel_mai_bun_puncte = 0
    for i in range(LINII):
        for j in range(COLOANE):
            # swap dreapta
            if j + 1 < COLOANE:
                puncte = simuleaza_swap_pentru_evaluare(tabla, i, j, i, j+1)
                if puncte > cel_mai_bun_puncte:
                    cel_mai_bun_puncte = puncte
                    cel_mai_bun = (i, j, i, j+1, puncte)
            # swap jos
            if i + 1 < LINII:
                puncte = simuleaza_swap_pentru_evaluare(tabla, i, j, i+1, j)
                if puncte > cel_mai_bun_puncte:
                    cel_mai_bun_puncte = puncte
                    cel_mai_bun = (i, j, i+1, j, puncte)
    return cel_mai_bun

# ---------- Rulare unui singur joc ----------
def joaca_un_joc(arata_animatie):
    """
    Ruleaza un joc complet:
      - genereaza tabla
      - aplica eliminari initiale (cascade)
      - apoi: cauta cel mai bun swap, daca exista il executa (contorizand 1 swap),
        apoi aplica cascade; repeta pana cand atinge PRAG_PUNCTE sau nu mai exista swap-uri.
    Returneaza: (scor_final, numar_swapuri, atins_prag_bool)
    """
    tabla = genereaza_tabla()
    scor = 0
    swapuri = 0

    # aplicam orice eliminari initiale
    scor = proceseaza_toate_cascadele(tabla, scor, swapuri, arata_animatie)
    if scor >= PRAG_PUNCTE:
        return scor, swapuri, True

    # bucla principala
    while True:
        # gasim cel mai bun swap care genereaza puncte
        rezultat = gaseste_cel_mai_bun_swap(tabla)
        if rezultat is None:
            # nu exista niciun swap care sa genereze formatiuni -> jocul se opreste
            return scor, swapuri, (scor >= PRAG_PUNCTE)
        i1, j1, i2, j2, puncte_asteptate = rezultat
        # efectuam swap-ul
        tabla[i1][j1], tabla[i2][j2] = tabla[i2][j2], tabla[i1][j1]
        swapuri += 1
        if arata_animatie:
            print("Se efectueaza swap: ({},{}) <-> ({},{})  (estimare puncte: {})".format(i1, j1, i2, j2, puncte_asteptate))
            afiseaza_tabla(tabla, scor, swapuri, arata_animatie)
        # aplicam toate cascadele rezultate
        scor = proceseaza_toate_cascadele(tabla, scor, swapuri, arata_animatie)
        if scor >= PRAG_PUNCTE:
            return scor, swapuri, True
import csv

def ruleaza_simulari():
    # Creăm folderul /results dacă nu există
    if not os.path.exists("results"):
        os.makedirs("results")

    # Pregătim summary.csv
    summary_file = "results/summary.csv"
    with open(summary_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["joc", "scor", "swapuri", "prag_atins"])

    total_scor = 0
    total_swapuri = 0
    jocuri_cu_prag = 0
    total_swapuri_jocuri_cu_prag = 0

    start_time = time.time()

    for idx in range(NUMAR_JOCURI):
        arata_animatie = (ANIMATIE_PENTRU_PRIMUL_JOC and idx == 0)
        if arata_animatie:
            print("ANIMATIE: se arata pas-cu-pas doar pentru primul joc.")
            time.sleep(1)
        scor, swapuri, atins = joaca_un_joc(arata_animatie)
        total_scor += scor
        total_swapuri += swapuri
        if atins:
            jocuri_cu_prag += 1
            total_swapuri_jocuri_cu_prag += swapuri

        # Salvam in summary.csv
        with open(summary_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([idx+1, scor, swapuri, atins])

        # Salvam log detaliat pentru fiecare joc
        log_file = f"results/joc_{idx+1}.log"
        with open(log_file, "w") as f:
            f.write(f"Joc {idx+1}\n")
            f.write(f"Scor final: {scor}\n")
            f.write(f"Swap-uri: {swapuri}\n")
            f.write(f"Prag atins: {atins}\n")

        # afisam sumarul pentru acest joc (nu aglomereaza cand animatie e activa pentru primul joc)
        print("Joc {:3d}: scor = {:6d}, swap-uri = {:3d}{}".format(idx+1, scor, swapuri, "  (prag atins)" if atins else ""))

    durata = time.time() - start_time
    avg_points = total_scor / float(NUMAR_JOCURI)
    avg_swaps = total_swapuri / float(NUMAR_JOCURI)
    if jocuri_cu_prag > 0:
        moves_to_10000 = total_swapuri_jocuri_cu_prag / float(jocuri_cu_prag)
    else:
        moves_to_10000 = None

    print("\n--- STATISTICI FINALE PE {} JOCURI ---".format(NUMAR_JOCURI))
    print("Timp total rulare: {:.2f} sec".format(durata))
    print("Scor total (toate jocurile):", total_scor)
    print("avg_points (media punctelor pe joc): {:.2f}".format(avg_points))
    print("avg_swaps  (media swap-urilor pe joc): {:.2f}".format(avg_swaps))
    print("Jocuri care au atins {} puncte: {}".format(PRAG_PUNCTE, jocuri_cu_prag))
    if moves_to_10000 is not None:
        print("moves_to_10000 (media swap-urilor doar pentru jocurile care au atins pragul): {:.2f}".format(moves_to_10000))
    else:
        print("moves_to_10000: - (niciun joc nu a atins pragul de {})".format(PRAG_PUNCTE))


# ---------- punctul de intrare ----------
if __name__ == "__main__":
    print("Pornesc simularea match-3 in terminal.")
    print("Tabla: {}x{}, culori 1..{}, numar jocuri = {}, prag puncte = {}".format(
        LINII, COLOANE, CULORI, NUMAR_JOCURI, PRAG_PUNCTE))
    if ANIMATIE_PENTRU_PRIMUL_JOC:
        print("Animatie: activata pentru primul joc (pauza intre pasi = {} s).".format(PAUZA_INTRE_PASI))
    else:
        print("Animatie: dezactivata.")
    print("Incepe rularea...")
    time.sleep(1)
    ruleaza_simulari()
