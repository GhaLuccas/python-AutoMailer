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
from tkinter import messagebox

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
# Função principal chamada ao clicar no botão "Enviar"
def processar_e_enviar(nome_empresa, escritorio_contabil):
    try:
        agora = datetime.now()
        ano_atual = agora.year
        mes_atual = agora.month
        mes_anterior = mes_atual - 1 if mes_atual > 1 else 12
        if mes_anterior == 12:
            ano_atual -= 1

        # Caminhos para as pastas de NFe e SAT
        caminhos_nfe = [
            fr"C:\cash\NFe\001\{ano_atual:04}\{mes_anterior:02}",
            fr"C:\Autoshop\nfe\NFe\001\{ano_atual:04}\{mes_anterior:02}"
        ]
        caminhos_sat = [
            fr"C:\cash\sat\001\{ano_atual:04}\{mes_anterior:02}",
            fr"C:\Autoshop\nfe\SAT\001\{ano_atual:04}\{mes_anterior:02}"
        ]

        # Compactar e verificar as pastas de NFe
        arquivos_encontrados_nfe = False
        arquivos_encontrados_sat = False
        arquivos = []
        
        for caminho_nfe in caminhos_nfe:
            nome_zip_nfe = f"{caminho_nfe}_fechamento_NFE"
            compactar_pasta(caminho_nfe, nome_zip_nfe)
            if os.path.exists(f"{nome_zip_nfe}.zip"):
                arquivos.append(f"{nome_zip_nfe}.zip")
                arquivos_encontrados_nfe = True

        # Compactar e verificar as pastas de SAT
        for caminho_sat in caminhos_sat:
            nome_zip_sat = f"{caminho_sat}_fechamento_SAT"
            compactar_pasta(caminho_sat, nome_zip_sat)
            if os.path.exists(f"{nome_zip_sat}.zip"):
                arquivos.append(f"{nome_zip_sat}.zip")
                arquivos_encontrados_sat = True

        # Verificar se encontrou algum arquivo
        if arquivos:
            # Enviar os arquivos compactados por e-mail
            if enviar_email(nome_empresa, escritorio_contabil, arquivos):
                messagebox.showinfo("Sucesso", "E-mail enviado com sucesso!")
        else:
            # Se não encontrou nenhum arquivo, enviar e-mail com aviso
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
    root.geometry("500x150")
    root.title("Cash - Envio de Fechamento Fiscal")

    # Ajustar colunas para centralizar os elementos
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)

    # Labels e inputs
    tk.Label(root, text="Nome da Empresa:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
    nome_empresa_entry = tk.Entry(root, width=40)
    nome_empresa_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(root, text="E-mail do Escritório Contábil:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
    email_entry = tk.Entry(root, width=40)
    email_entry.grid(row=1, column=1, padx=10, pady=10)

    # Carregar configurações salvas
    nome_empresa, escritorio_contabil = carregar_config()
    nome_empresa_entry.insert(0, nome_empresa)
    email_entry.insert(0, escritorio_contabil)

    # Função chamada ao clicar em "Enviar"
    def ao_clicar_enviar():
        nome_empresa = nome_empresa_entry.get()
        escritorio_contabil = email_entry.get()
        if nome_empresa and escritorio_contabil:
            # Salvar as configurações antes de enviar
            salvar_config(nome_empresa, escritorio_contabil)
            processar_e_enviar(nome_empresa, escritorio_contabil)
        else:
            messagebox.showwarning("Atenção", "Preencha todos os campos.")

    # Botão de enviar
    enviar_button = tk.Button(root, text="Enviar", command=ao_clicar_enviar)
    enviar_button.grid(row=2, column=1)

    root.mainloop()

# Chamar a interface
criar_interface()

