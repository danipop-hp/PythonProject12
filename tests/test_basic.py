import unittest
import sys
import os

# Adaugam folderul principal la sys.path pentru import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.candy_crush import genereaza_tabla, gaseste_formatiuni_si_lungi, aplica_gravitatie

class TestCandyCrush(unittest.TestCase):

    def test_genereaza_tabla_dimensiune(self):
        """Verifica daca tabla generata are 11x11 si valori permise 1..4"""
        tabla = genereaza_tabla()
        self.assertEqual(len(tabla), 11)          # 11 linii
        self.assertEqual(len(tabla[0]), 11)       # 11 coloane
        for linie in tabla:
            for c in linie:
                self.assertIn(c, [1, 2, 3, 4])   # valori permise

    def test_gaseste_formatiuni_linie(self):
        """Verifica detectarea formatiunilor orizontale"""
        tabla = [
            [1, 1, 1] + [2]*8
        ] + [[2]*11 for _ in range(10)]
        set_pozitii, dictionar = gaseste_formatiuni_si_lungi(tabla)
        asteptate = {(0,0),(0,1),(0,2)}
        self.assertTrue(asteptate.issubset(set_pozitii))

    def test_gravitate(self):
        """Verifica daca valorile nenule sunt mutate jos dupa aplicarea gravitatiei"""
        tabla = [
            [0,2,0] + [0]*8,
            [1,0,0] + [0]*8,
            [3,4,0] + [0]*8
        ] + [[1]*11 for _ in range(8)]
        aplica_gravitatie(tabla)
        # verificam ca toate valorile nenule sunt jos
        for j in range(11):
            for i in range(11):
                if tabla[i][j] != 0:
                    for k in range(i, 11):
                        self.assertNotEqual(tabla[k][j], 0)
                    break

if __name__ == "__main__":
    unittest.main()
