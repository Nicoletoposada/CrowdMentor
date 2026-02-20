# Script para verificar URLs de plantillas
import requests
from urllib.parse import urljoin

urls_a_verificar = {
    'Google Docs Templates': 'https://docs.google.com/templates',
    'PowerPoint Microsoft': 'https://templates.office.com/es-es/plantillas-para-PowerPoint',
    'Excel Microsoft': 'https://templates.office.com/es-es/plantillas-para-Excel',
}

print("="*70)
print("VERIFICANDO URLs DE PLANTILLAS")
print("="*70)

for nombre, url in urls_a_verificar.items():
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        status = response.status_code
        if status == 200:
            print(f"✅ {nombre}: {status} (OK)")
        elif status in [301, 302, 303, 307, 308]:
            print(f"⚠️  {nombre}: {status} (Redirección) -> {response.url}")
        else:
            print(f"❌ {nombre}: {status} (NO FUNCIONA)")
    except Exception as e:
        print(f"❌ {nombre}: Error - {str(e)}")

print("\n" + "="*70)
print("ALTERNATIVAS QUE FUNCIONAN:")
print("="*70)

alternativas = {
    'Google Docs (forma alternativa)': 'https://docs.google.com/document/u/0/?tgif=d#create',
    'Microsoft Office Home': 'https://office.com/templates',
    'Microsoft Templates (EN)': 'https://templates.office.com/templates',
}

for nombre, url in alternativas.items():
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        status = response.status_code
        if status == 200:
            print(f"✅ {nombre}: {status} (OK)")
        else:
            print(f"⚠️  {nombre}: {status}")
    except Exception as e:
        print(f"❌ {nombre}: Error - {str(e)}")
