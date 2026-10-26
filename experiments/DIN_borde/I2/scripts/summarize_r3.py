"""Las mismas reglas congeladas sobre resultados r3, sin sobrescribir r1."""
from common_v1 import STAGE
import summarize_v1
summarize_v1.RUN = STAGE/'results/run_r3'
if __name__ == '__main__':
    summarize_v1.main()
