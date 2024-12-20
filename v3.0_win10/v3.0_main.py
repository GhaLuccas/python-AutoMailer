import os
import smtplib
import zipfile
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import subprocess
import tkinter as tk
from tkinter import messagebox, filedialog

# Caminho para o arquivo de configuração
CONFIG_FILE = "config.txt"

# Função para carregar as configurações salvas
def carregar_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            linhas = f.readlines()
            if len(linhas) == 2:
                nome_empresa = linhas[0].strip()
                escritorio_contabil = linhas[1].strip()
                return nome_empresa, escritorio_contabil
    return "", ""

# Função para salvar as configurações
def salvar_config(nome_empresa, escritorio_contabil):
    with open(CONFIG_FILE, 'w') as f:
        f.write(f"{nome_empresa}\n{escritorio_contabil}")

# Função para compactar pasta
def compactar_pasta(caminho_pasta, nome_zip):
    if not os.path.exists(caminho_pasta):
        print(f"A pasta {caminho_pasta} não existe.")
        return
    with zipfile.ZipFile(f"{nome_zip}.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
        for raiz, _, arquivos in os.walk(caminho_pasta):
            for arquivo in arquivos:
                caminho_completo = os.path.join(raiz, arquivo)
                zipf.write(caminho_completo, os.path.relpath(caminho_completo, os.path.dirname(caminho_pasta)))
    print(f"Pasta {caminho_pasta} compactada em {nome_zip}.zip")

# Função para enviar e-mail
def enviar_email(cliente, email_destino, arquivos):
    # Configurações de envio de e-mail (exemplo)
    EMAIL_MASTER_SHOP = os.getenv('EMAIL_MASTER_SHOP', 'sat@mastershop.inf.br')
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'mail.mastershop.inf.br')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USER = os.getenv('SMTP_USER', 'sat@mastershop.inf.br')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '@33772895')

    msg = MIMEMultipart()
    msg['From'] = EMAIL_MASTER_SHOP
    msg['To'] = email_destino
    msg['Subject'] = f'Envio de fechamento - {cliente}'

    # Calcular o período
    agora = datetime.now()
    mes_atual = agora.month
    ano_atual = agora.year
    mes_anterior = mes_atual - 1 if mes_atual > 1 else 12
    if mes_anterior == 12:
        ano_atual -= 1

    primeiro_dia = datetime(ano_atual, mes_anterior, 1)
    ultimo_dia = (primeiro_dia + timedelta(days=31)).replace(day=1) - timedelta(days=1)

    periodo = f"{primeiro_dia.strftime('%d/%m/%Y')} a {ultimo_dia.strftime('%d/%m/%Y')}"
    mensagem = f"Arquivos fiscais de {periodo} Emitidos por {cliente}"

    # Adicionar mensagem ao corpo do email
    msg.attach(MIMEText(mensagem, 'plain'))

    for arquivo in arquivos:
        part = MIMEBase('application', 'octet-stream')
        with open(arquivo, 'rb') as f:
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(arquivo)}')
        msg.attach(part)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        print('E-mail enviado com sucesso!')
        return True
    except Exception as e:
        print(f'Erro ao enviar o e-mail: {e}')
    return False

# Função para criar um arquivo de erro e abrir no Notepad
def criar_arquivo_erro():
    arquivo_erro = "erro.txt"
    with open(arquivo_erro, "w") as f:
        f.write("Operação fracassou")

    try:
        subprocess.Popen([r"C:\Windows\System32\notepad.exe", arquivo_erro])
    except Exception as e:
        print(f"Erro ao abrir o Notepad: {e}")

# Função principal chamada ao clicar no botão "Enviar"
def processar_e_enviar(nome_empresa, escritorio_contabil, caminho_nfe, caminho_sat):
    try:
        agora = datetime.now()
        mes_atual = agora.month
        mes_anterior = mes_atual - 1 if mes_atual > 1 else 12

        # Corrigido para não duplicar o ano
        caminho_nfe_completo = os.path.join(caminho_nfe, f"{mes_anterior:02}")
        caminho_sat_completo = os.path.join(caminho_sat, f"{mes_anterior:02}")

        # Compactar e verificar as pastas de NFe
        arquivos_encontrados_nfe = False
        arquivos_encontrados_sat = False
        arquivos = []

        # NFe
        nome_zip_nfe = f"{caminho_nfe_completo}_fechamento_NFE"
        compactar_pasta(caminho_nfe_completo, nome_zip_nfe)
        if os.path.exists(f"{nome_zip_nfe}.zip"):
            arquivos.append(f"{nome_zip_nfe}.zip")
            arquivos_encontrados_nfe = True

        # SAT
        nome_zip_sat = f"{caminho_sat_completo}_fechamento_SAT"
        compactar_pasta(caminho_sat_completo, nome_zip_sat)
        if os.path.exists(f"{nome_zip_sat}.zip"):
            arquivos.append(f"{nome_zip_sat}.zip")
            arquivos_encontrados_sat = True

        # Enviar e-mails
        if arquivos:
            if enviar_email(nome_empresa, escritorio_contabil, arquivos):
                messagebox.showinfo("Sucesso", "E-mail enviado com sucesso!")
        else:
            mensagem_falta_arquivos = "Sem arquivos este mês de: "
            if not arquivos_encontrados_nfe and not arquivos_encontrados_sat:
                mensagem_falta_arquivos += "NFe e SAT."
            elif not arquivos_encontrados_nfe:
                mensagem_falta_arquivos += "NFe."
            elif not arquivos_encontrados_sat:
                mensagem_falta_arquivos += "SAT."

            enviar_email(nome_empresa, escritorio_contabil, [], mensagem_falta_arquivos)
            messagebox.showinfo("Aviso", mensagem_falta_arquivos)
    except Exception as e:
        criar_arquivo_erro()
        messagebox.showerror("Erro", "Operação fracassou")


# Interface gráfica
def criar_interface():
    root = tk.Tk()
    root.geometry("600x250")
    root.title("Cash - Envio de Fechamento Fiscal")
    root.resizable(False, False)

    # Labels e inputs
    tk.Label(root, text="Nome da Empresa:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
    nome_empresa_entry = tk.Entry(root, width=40)
    nome_empresa_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(root, text="E-mail do Escritório Contábil:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
    email_entry = tk.Entry(root, width=40)
    email_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(root, text="Caminho Base 1:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
    caminho_nfe_entry = tk.Entry(root, width=40)
    caminho_nfe_entry.grid(row=2, column=1, padx=10, pady=10)

    def escolher_diretorio_nfe():
        caminho_nfe = filedialog.askdirectory()
        if caminho_nfe:
            caminho_nfe_entry.delete(0, tk.END)
            caminho_nfe_entry.insert(0, caminho_nfe)

    nfe_button = tk.Button(root, text="Selecionar NFe", command=escolher_diretorio_nfe)
    nfe_button.grid(row=2, column=2, padx=10, pady=10)

    tk.Label(root, text="Caminho Base 2:").grid(row=3, column=0, padx=10, pady=10, sticky="e")
    caminho_sat_entry = tk.Entry(root, width=40)
    caminho_sat_entry.grid(row=3, column=1, padx=10, pady=10)

    def escolher_diretorio_sat():
        caminho_sat = filedialog.askdirectory()
        if caminho_sat:
            caminho_sat_entry.delete(0, tk.END)
            caminho_sat_entry.insert(0, caminho_sat)

    sat_button = tk.Button(root, text="Selecionar SAT", command=escolher_diretorio_sat)
    sat_button.grid(row=3, column=2, padx=10, pady=10)

    # Carregar configurações salvas
    nome_empresa_salvo, escritorio_contabil_salvo = carregar_config()
    if nome_empresa_salvo and escritorio_contabil_salvo:
        nome_empresa_entry.insert(0, nome_empresa_salvo)
        email_entry.insert(0, escritorio_contabil_salvo)

    # Função chamada ao clicar em "Enviar"
    def enviar():
        nome_empresa = nome_empresa_entry.get()
        escritorio_contabil = email_entry.get()
        caminho_nfe = caminho_nfe_entry.get()
        caminho_sat = caminho_sat_entry.get()

        if not nome_empresa or not escritorio_contabil:
            messagebox.showwarning("Atenção", "Por favor, insira o nome da empresa e o e-mail do escritório contábil.")
            return

        salvar_config(nome_empresa, escritorio_contabil)
        processar_e_enviar(nome_empresa, escritorio_contabil, caminho_nfe, caminho_sat)

    enviar_button = tk.Button(root, text="Enviar", command=enviar)
    enviar_button.grid(row=4, column=1, padx=10, pady=20)

    root.mainloop()

if __name__ == "__main__":
    criar_interface()
