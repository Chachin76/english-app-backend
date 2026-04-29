f = open('main.py', encoding='utf-8')
c = f.read()
f.close()

# Encontrar la primera ocurrencia de max_tokens=2048 en el endpoint leccion
# y cambiarla a 4096
idx = c.find('@app.post("/leccion")')
if idx > 0:
    parte = c[idx:]
    parte_nueva = parte.replace('max_tokens=2048,', 'max_tokens=4096,', 1)
    c = c[:idx] + parte_nueva
    f = open('main.py', 'w', encoding='utf-8')
    f.write(c)
    f.close()
    print('Listo')
else:
    print('No encontrado')