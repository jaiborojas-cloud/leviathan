"""CLI intacta del sujeto bajo guarda de lectura; no modifica su namespace."""
import runpy
import sys
from support_v1 import SOURCES, guard

if __name__ == '__main__':
    guard()
    target = SOURCES/'analisis_C1_v1.py'
    sys.argv[0] = str(target)
    runpy.run_path(str(target), run_name='__main__')
