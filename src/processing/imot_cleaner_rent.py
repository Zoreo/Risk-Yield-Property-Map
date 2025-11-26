import csv
from pathlib import Path
src = Path('data/official/official_rent.txt')
lines = [line.strip() for line in src.open(encoding='utf-8') if line.strip()]
skip = {'Едностайни','Двустайни','Тристайни','Район','Цена','€/кв.м','Общо'}
clean = [line for line in lines if not any(token in line for token in skip)]
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
        tokens = [tok.replace(',', '.') for tok in line.replace('\t', ' ').split() if any(ch.isdigit() for ch in tok)]
        if not tokens:
            continue
        if idx < 5:
            vals[idx] = tokens[0]
        else:
            vals[5] = tokens[0]
            vals[6] = tokens[1] if len(tokens) > 1 else tokens[0]
    records.append([district] + vals)

out = Path('data/official/official_rent_flat_final.csv')
with out.open('w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['district','rent_1','rent_ppm2_1','rent_2','rent_ppm2_2','rent_3','rent_ppm2_3','rent_ppm2_all'])
    writer.writerows(records)
print('wrote', len(records), 'rows to', out)
