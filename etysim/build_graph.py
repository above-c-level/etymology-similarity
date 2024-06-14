from article_parsing import INDEX
import bz2
import time


start = time.perf_counter()
with bz2.open(INDEX, 'rt', encoding='utf-8') as f:
    indices = f.readlines()
end = time.perf_counter()
print(f'Loaded {len(indices)} indices in {end - start:.2f} seconds.')
