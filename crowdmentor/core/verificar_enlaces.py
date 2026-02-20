# Script para verificar que los enlaces funcionen antes de agregarlos
import requests
import time

def verificar_url(url, titulo):
    """Verifica si una URL está disponible"""
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        if response.status_code < 400:
            print(f"✓ OK [{response.status_code}]: {titulo}")
            return True
        else:
            print(f"✗ ERROR [{response.status_code}]: {titulo}")
            print(f"  URL: {url}")
            return False
    except Exception as e:
        print(f"✗ FALLO: {titulo}")
        print(f"  Error: {str(e)}")
        print(f"  URL: {url}")
        return False

# URLs a verificar
urls_plantillas = [
    ("https://www.oepm.es/es/index.html", "OEPM España"),
    ("https://www.emprendedores.es/gestion/modelo-canvas/", "Modelo Canvas"),
    ("https://www.canva.com/es_mx/plantillas/presentaciones/pitch/", "Pitch Deck Canva"),
]

urls_articulos = [
    ("https://www.emprendedores.es/crear-una-empresa/a23782/como-hacer-pitch-perfecto/", "Pitch Perfecto"),
    ("https://grow.google/intl/es/courses-and-tools/", "Google Actívate"),
    ("https://www.emprendedores.es/crear-una-empresa/validar-idea-negocio/", "Validación Ideas"),
    ("https://www.emprendedores.es/gestion/aspectos-legales-crear-empresa/", "Aspectos Legales"),
    ("https://www.emprendedores.es/gestion/finanzas-basicas-emprendedores/", "Finanzas"),
]

urls_videos = [
    ("https://www.youtube.com/watch?v=k1W1guccVDI", "Validar Idea"),
    ("https://www.youtube.com/watch?v=QCUHZKts-O0", "Finanzas"),
    ("https://www.youtube.com/watch?v=xvnEAQ0P1hY", "Pitch Inversión"),
]

urls_herramientas = [
    ("https://www.canva.com/es_mx/", "Canva Español"),
    ("https://trello.com/es", "Trello Español"),
    ("https://workspace.google.com/intl/es/", "Google Workspace"),
    ("https://mailchimp.com/es/", "Mailchimp"),
    ("https://www.notion.so/es-es", "Notion"),
    ("https://analytics.google.com/analytics/web/?hl=es", "Google Analytics"),
    ("https://www.hubspot.es/products/crm", "HubSpot CRM"),
]

print("="*70)
print("VERIFICANDO PLANTILLAS Y DOCUMENTOS")
print("="*70)
for url, titulo in urls_plantillas:
    verificar_url(url, titulo)
    time.sleep(1)

print("\n" + "="*70)
print("VERIFICANDO ARTÍCULOS Y GUÍAS")
print("="*70)
for url, titulo in urls_articulos:
    verificar_url(url, titulo)
    time.sleep(1)

print("\n" + "="*70)
print("VERIFICANDO VIDEOS")
print("="*70)
for url, titulo in urls_videos:
    verificar_url(url, titulo)
    time.sleep(1)

print("\n" + "="*70)
print("VERIFICANDO HERRAMIENTAS")
print("="*70)
for url, titulo in urls_herramientas:
    verificar_url(url, titulo)
    time.sleep(1)

print("\n" + "="*70)
print("VERIFICACIÓN COMPLETADA")
print("="*70)
