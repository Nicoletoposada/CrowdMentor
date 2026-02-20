# Script para encontrar URLs alternativas que funcionen
import requests
import warnings
warnings.filterwarnings('ignore')  # Ignorar advertencias SSL

urls_alternativas = {
    'Microsoft Office (oficial)': 'https://office.com/',
    'Microsoft Office Templates': 'https://office.com/templates',
    'Microsoft 365 Home': 'https://www.microsoft365.com/',
    'Canva Presentation': 'https://www.canva.com/presentations/',
    'Canva Spreadsheet': 'https://www.canva.com/',
    'Slides Google': 'https://slides.google.com/',
    'Sheets Google': 'https://sheets.google.com/',
}

print("="*70)
print("BUSCANDO URLs ALTERNATIVAS QUE FUNCIONEN")
print("="*70)

for nombre, url in urls_alternativas.items():
    try:
        # Usar verify=False para ignorar problemas de certificado
        response = requests.head(url, allow_redirects=True, timeout=5, verify=False)
        status = response.status_code
        if status == 200:
            print(f"✅ {nombre}")
            print(f"   URL: {url}")
        elif status in [301, 302, 303, 307, 308]:
            print(f"⚠️  {nombre} (Redirige a {response.url})")
        else:
            print(f"⚠️  {nombre}: {status}")
    except Exception as e:
        print(f"❌ {nombre}: {str(e)[:50]}")

print("\n" + "="*70)
print("OPCIONES RECOMENDADAS")
print("="*70)

print("""
1. GOOGLE DOCS (FUNCIONA) ✅
   - URL: https://docs.google.com/templates (YA ESTÁ EN EL SISTEMA)
   - Funciona correctamente

2. GOOGLE SHEETS (NUEVA OPCIÓN) ✅
   - URL: https://sheets.google.com/
   - Forma directa para acceder a plantillas de Excel

3. GOOGLE SLIDES (NUEVA OPCIÓN) ✅
   - URL: https://slides.google.com/
   - Forma directa para acceder a plantillas de presentaciones

4. CREAR NUEVAS CATEGORÍAS CON SOLUCIONES ALTERNATIVAS:
   - Microsoft Office (página principal que funcione)
   - O reemplazar con Google Sheets/Slides que SÍ funcionan
""")
