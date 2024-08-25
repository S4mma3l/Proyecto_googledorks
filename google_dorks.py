import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import requests
import re
import webbrowser
from ttkthemes import ThemedTk  # Cambiar importación

def get_google_results(query, dorks, location=None, advanced_params=None):
    api_key = 'serpapi_key'
    query = query.strip()
    if not query:
        print("La consulta no puede estar vacía.")
        return []
    
    url = f"https://serpapi.com/search.json?q={query} {dorks}&api_key={api_key}"
    
    if location:
        url += f"&location={location}"
    if advanced_params:
        if 'start' in advanced_params and advanced_params['start']:
            url += f"&start={advanced_params['start']}"
        if 'num' in advanced_params and advanced_params['num']:
            url += f"&num={advanced_params['num']}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get('organic_results', [])
    except requests.exceptions.RequestException as err:
        print(f"Error occurred: {err}")
    return []

def search_tor(query):
    proxies = {
        'http': 'socks5h://localhost:9050',
        'https': 'socks5h://localhost:9050'
    }
    url = f"http://3g2upl4pq6kufc4m.onion/search?q={query}"
    try:
        response = requests.get(url, proxies=proxies)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error al realizar la búsqueda en Tor: {e}")
        return None

def check_breach(email):
    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
    headers = {'User-Agent': 'Python'}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            print(f"El correo electrónico {email} no ha sido encontrado en brechas de seguridad.")
            return None
        else:
            print(f"Error al verificar brechas de seguridad: {response.status_code} {response.reason}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error al verificar brechas de seguridad: {e}")
        return None

def extract_information(text, info_type):
    patterns = {
        'emails': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        'phone_numbers': r'\+?\d[\d -]{8,}\d',
        'ids': r'\b[A-Z0-9]{8,}\b',
        'nicknames': r'\b[A-Za-z0-9_]{3,}\b',
        'files': r'http[s]?://[^\s/$.?#].[^\s]*\.(pdf|docx|xlsx|csv)',
        'images': r'http[s]?://[^\s/$.?#].[^\s]*\.(jpg|jpeg|png|gif)',
        'videos': r'http[s]?://[^\s/$.?#].[^\s]*\.(mp4|avi|mov|wmv)',
        'documents': r'http[s]?://[^\s/$.?#].[^\s]*\.(pdf|docx|pptx|txt)',
        'cameras': r'http[s]?://[^\s/$.?#].[^\s]*\.(jpg|jpeg|png|mp4)',
        'government': r'http[s]?://[^\s/$.?#].[^\s]*\.(gov|edu)',
        'breach': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    }
    
    pattern = patterns.get(info_type, '')
    return re.findall(pattern, text)

def get_dorks(info_type, file_type):
    dorks = {
        'emails': 'filetype:xls OR filetype:csv',
        'phone_numbers': 'filetype:pdf',
        'ids': 'site:gov OR site:org',
        'nicknames': 'intitle:"index of"',
        'files': f'filetype:{file_type}',
        'images': 'filetype:jpg OR filetype:jpeg OR filetype:png',
        'videos': 'filetype:mp4 OR filetype:avi OR filetype:mov',
        'documents': 'filetype:pdf OR filetype:docx OR filetype:pptx',
        'cameras': 'inurl:cam OR inurl:view OR inurl: CCTV OR inurl:ipcamera',
        'government': 'site:gov',
        'breach': 'site:haveibeenpwned.com'
    }
    return dorks.get(info_type, '')

def reset_fields():
    info_type_var.set('')
    file_type_var.set('')
    query_entry.delete(0, tk.END)
    location_entry.delete(0, tk.END)
    start_entry.delete(0, tk.END)
    num_results_entry.delete(0, tk.END)
    result_text.delete(1.0, tk.END)

def search_google():
    info_type = info_type_var.get()
    file_type = file_type_var.get() if info_type == 'files' else ''
    query = query_entry.get()
    dorks = get_dorks(info_type, file_type)
    location = location_entry.get() if location_entry.get() else None
    advanced_params = {
        'start': start_entry.get() if start_entry.get() else None,
        'num': num_results_entry.get() if num_results_entry.get() else None
    }
    results = get_google_results(query, dorks, location, advanced_params)
    result_text.delete(1.0, tk.END)
    if results:
        result_text.insert(tk.END, f"Resultados de Google para {info_type}:\n")
        for result in results:
            title = result.get('title', 'No title')
            link = result.get('link', 'No link')
            result_text.insert(tk.END, f"{title}\n{link}\n\n")
            result_text.tag_add(f'link_{link}', f"{result_text.index('end-3l')}", f"{result_text.index('end-2l')}")
            result_text.tag_config(f'link_{link}', foreground='blue', underline=True)
        result_text.bind("<Button-1>", open_link)
    else:
        result_text.insert(tk.END, "No se obtuvieron resultados.")

def search_tor_network():
    info_type = info_type_var.get()
    query = query_entry.get()
    results = search_tor(query)
    if results:
        extracted_info = extract_information(results, info_type)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Resultados de la red Tor para {info_type}:\n")
        for item in extracted_info:
            result_text.insert(tk.END, f"{item}\n")
            result_text.tag_add('link', '1.0', 'end')
            result_text.tag_config('link', foreground='blue', underline=True)
        result_text.bind("<Button-1>", open_link)
    else:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "No se obtuvieron resultados de la red Tor.")

def check_email_breach():
    email = email_entry.get()
    if not email:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "El campo del correo electrónico está vacío.")
        return
    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
    headers = {'User-Agent': 'Python'}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            breaches = response.json()
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, f"El correo electrónico {email} ha sido encontrado en las siguientes brechas:\n")
            for breach in breaches:
                result_text.insert(tk.END, f"{breach['Name']}: {breach['BreachDate']}\n")
        elif response.status_code == 404:
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, f"El correo electrónico {email} no ha sido encontrado en brechas de seguridad.")
        else:
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, f"Error al verificar brechas de seguridad: {response.status_code} {response.reason}")
    except requests.exceptions.RequestException as e:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Error al verificar brechas de seguridad: {e}")

def open_link(event):
    try:
        index = result_text.index("@%s,%s" % (event.x, event.y))
        tag = result_text.tag_names(index)
        for t in tag:
            if t.startswith("link_"):
                link = t.split("_", 1)[1]
                webbrowser.open(link)
                break
    except Exception as e:
        print(f"Error al abrir el enlace: {e}")

def abrir_ayuda():
    webbrowser.open("https://www.pentestercr.com/")

# Crear la ventana principal con un tema
root = ThemedTk(theme="yaru")  # Aplicar el tema deseado

# Configurar colores
bg_color = "#F5F7F8"  # Color de fondo principal
fg_color = "#1F316F"  # Color de texto
btn_bg_color = "#F5F7F8"  # Color de fondo de botones
btn_fg_color = "#071952"  # Color de texto de botones
result_bg_color = "#EBF4F6"  # Color de fondo de resultados
result_fg_color = "#071952"  # Color de texto de resultados

root.title("Herramienta de Búsqueda Avanzada(Google Dorks) PentesterCR")
root.configure(bg=bg_color)

info_type_var = tk.StringVar()
file_type_var = tk.StringVar()

frame1 = ttk.Frame(root, style="TFrame")
frame1.pack(padx=2, pady=2, fill=tk.X)

# Estilo para etiquetas y entradas
style = ttk.Style()
style.configure("TLabel", background=bg_color, foreground=fg_color)
style.configure("TEntry", fieldbackground=fg_color)
style.configure("TCombobox", fieldbackground=fg_color, background=fg_color)
style.configure("TButton", background=btn_bg_color, foreground=btn_fg_color)

query_label = ttk.Label(frame1, text="Consulta:")
query_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
query_entry = ttk.Entry(frame1, width=50)
query_entry.grid(row=0, column=1, padx=5, pady=5)

info_type_label = ttk.Label(frame1, text="Tipo de información:")
info_type_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
info_type_combobox = ttk.Combobox(frame1, textvariable=info_type_var, values=[
    'emails', 'phone_numbers', 'ids', 'nicknames', 'files', 'images', 'videos', 'documents', 'cameras', 'government', 'breach'
])
info_type_combobox.grid(row=1, column=1, padx=5, pady=5)

file_type_label = ttk.Label(frame1, text="Tipo de archivo (si aplica):")
file_type_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
file_type_combobox = ttk.Combobox(frame1, textvariable=file_type_var, values=[
    'pdf', 'docx', 'xlsx', 'csv'
])
file_type_combobox.grid(row=2, column=1, padx=5, pady=5)

location_label = ttk.Label(frame1, text="Ubicación (opcional):")
location_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
location_entry = ttk.Entry(frame1, width=50)
location_entry.grid(row=3, column=1, padx=5, pady=5)

start_label = ttk.Label(frame1, text="Inicio de resultados (opcional):")
start_label.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
start_entry = ttk.Entry(frame1, width=50)
start_entry.grid(row=4, column=1, padx=5, pady=5)

num_results_label = ttk.Label(frame1, text="Número de resultados (opcional):")
num_results_label.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
num_results_entry = ttk.Entry(frame1, width=50)
num_results_entry.grid(row=5, column=1, padx=5, pady=5)

email_label = ttk.Label(frame1, text="Correo electrónico (para brechas):")
email_label.grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
email_entry = ttk.Entry(frame1, width=50)
email_entry.grid(row=6, column=1, padx=5, pady=5)

search_google_button = ttk.Button(frame1, text="Buscar en Google", command=search_google)
search_google_button.grid(row=7, column=0, padx=5, pady=5)

search_tor_button = ttk.Button(frame1, text="Buscar en Tor", command=search_tor_network)
search_tor_button.grid(row=7, column=1, padx=5, pady=5)

check_breach_button = ttk.Button(frame1, text="Verificar brechas", command=check_email_breach)
check_breach_button.grid(row=7, column=2, padx=5, pady=5)

result_text = ScrolledText(root, wrap=tk.WORD, height=10, width=80, bg=result_bg_color, fg=result_fg_color, selectbackground="light blue", selectforeground="black")
result_text.pack(padx=10, pady=10)

version_label = ttk.Label(root, text="Versión 1.0")
version_label.pack(side=tk.BOTTOM, anchor=tk.E, padx=10, pady=10)

reset_button = ttk.Button(frame1, text="Restablecer", command=reset_fields)
reset_button.grid(row=8, column=2, columnspan=5, padx=5, pady=5)

help_button = ttk.Button(root, text="Desarrollado por S4mma3l", command=abrir_ayuda)
help_button.pack(side=tk.BOTTOM, anchor=tk.E, padx=10, pady=10)

root.mainloop()