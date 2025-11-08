Descriere

Aplicație Python care simulează automat un joc de tip Match-3 (Candy Crush) pe o grilă de 11×11. Scopul este atingerea pragului de 10.000 puncte în cât mai puține swap-uri. Se rulează 100 de jocuri și se raportează mediile scorurilor și ale swap-urilor.

Mecanism de joc

Detecție formațiuni – se caută linii sau coloane de minimum 3 bomboane identice.

Eliminare și scor – bomboanele din formațiuni se elimină, scorul crește.

Gravitație – bomboanele cad pentru a umple spațiile libere.

Reumplere – se adaugă bomboane noi aleatoare (1–4).

Cascadă – se repetă până când nu mai există formațiuni.

Căutare mișcare (swap) – se încearcă interschimbări adiacente care pot crea formațiuni.

Oprire joc – când scorul ≥ 10.000 puncte sau nu mai există swap valid.

Definiții

Culoare: valoare între 1 și 4.

Formațiune: ≥3 valori identice consecutive pe linie/coloană.

Swap: o singură interschimbare între două celule adiacente ortogonal.

Cascadă: eliminări succesive după o singură mutare validă.

Structura proiectului src/ # codul sursă tests/ # teste unitare simple results/ # summary.csv și loguri docs/ # prezentare și documentație data/ # fișiere opționale de configurare README.md # acest fișier requirements.txt # dependențe

Rulare

Instalare dependențe:

pip install -r requirements.txt

Rulare aplicație:

python src/match3_terminal.py

Rezultatele sunt salvate în results/summary.csv.

Format fișier rezultate JOC SCOR SWAPURI TINTA_ATINSA 1 9870 120 NU 2 10230 95 DA Teste

Se rulează cu:

python -m unittest discover -s tests

Calculul mediilor

avg_points: media scorurilor tuturor jocurilor

avg_swaps: media swap-urilor tuturor jocurilor

moves_to_10000: media swap-urilor doar pentru jocurile cu scor ≥ 10.000