import csv
import re
from pathlib import Path

src = Path('data/official/official_sale.txt')
lines = [line.strip() for line in src.open(encoding='utf-8') if line.strip()]
skip = {'Едностайни','Двустайни','Тристайни','Район','Цена','€/кв.м','Общо'}
clean = [line for line in lines if not any(token in line for token in skip)]
num_re = re.compile(r'\d+')
records = []
i = 0
while i < len(clean):
    district = clean[i]
    i += 1
    block = clean[i:i+6]
    i += 6
    vals = ['-'] * 7
    for idx, line in enumerate(block):
        if not line or line.strip() == '-':
            continue
        tokens = num_re.findall(line.replace('\t', ' '))
        if not tokens:
            continue
        if idx < 5:
            vals[idx] = ''.join(tokens)
        else:
            vals[5] = ''.join(tokens[:1])
            vals[6] = ''.join(tokens[1:2]) if len(tokens) > 1 else vals[5]
    records.append([district] + vals)

out = Path('data/official/official_sale_flat_final.csv')
with out.open('w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['district','price_1','ppm2_1','price_2','ppm2_2','price_3','ppm2_3','ppm2_all'])
    writer.writerows(records)
print('wrote', len(records), 'rows to', out)
