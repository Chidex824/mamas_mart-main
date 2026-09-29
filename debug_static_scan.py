import os
root = r'C:\Users\chide\OneDrive\Desktop\mamas_mart-main\mamas_mart-main\static'
invalid = []
for dp, _, files in os.walk(root):
    for name in files:
        if any(ch in name for ch in ['<', '>', ':', '"', '|', '?', '*']):
            invalid.append(os.path.join(dp, name))
        if name in {'CON', 'PRN', 'AUX', 'NUL'}:
            invalid.append(os.path.join(dp, name))
print('INVALID_COUNT', len(invalid))
for path in invalid:
    print(path)
