# multiprocessing test area

import multiprocessing as mp

print(mp.cpu_count())  # twelve on this machine, 2 on server

pool = mp.Pool(mp.cpu_count())
