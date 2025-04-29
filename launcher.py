import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import requests
import json
from zipfile import ZipFile
import webbrowser

class PVZFusionLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("PVZ Fusion Launcher")
        self.root.geometry("500x400")
        
        # Carrega configurações
        self.config = self.load_config()
        
        # Configuração de estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configura ícone (se existir)
        if os.path.exists("resources/icon.ico"):
            self.root.iconbitmap("resources/icon.ico")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title = ttk.Label(main_frame, text="PVZ Fusion Launcher", font=('Helvetica', 16))
        title.pack(pady=10)
        
        # Botão Launch Game
        btn_launch = ttk.Button(main_frame, text="Iniciar Jogo", command=self.launch_game)
        btn_launch.pack(pady=10, fill=tk.X)
        
        # Botão Mods
        btn_mods = ttk.Button(main_frame, text="Abrir Pasta de Mods", command=self.open_mods_folder)
        btn_mods.pack(pady=10, fill=tk.X)
        
        # Botão Verificar Atualizações
        btn_update = ttk.Button(main_frame, text="Verificar Atualizações", command=self.check_updates)
        btn_update.pack(pady=10, fill=tk.X)
        
        # Botão Instalar MelonLoader
        btn_melon = ttk.Button(main_frame, text="Instalar MelonLoader", command=self.install_melonloader)
        btn_melon.pack(pady=10, fill=tk.X)
        
        # Área de status
        self.status_label = ttk.Label(main_frame, text="Pronto", relief=tk.SUNKEN)
        self.status_label.pack(pady=20, fill=tk.X)
    
    # ============== FUNÇÕES PRINCIPAIS ==============
    
    def launch_game(self):
        try:
            game_path = os.path.join(self.config['game_path'], "PlantsVsZombies.exe")
            
            if os.path.exists(game_path):
                subprocess.Popen(game_path)
                self.update_status(f"Jogo iniciado: {game_path}")
            else:
                messagebox.showerror("Erro", "Executável do jogo não encontrado!")
        except Exception as e:
            self.show_error("Falha ao iniciar o jogo", e)
    
    def open_mods_folder(self):
        try:
            mods_path = self.config['mods_path']
            
            if os.path.exists(mods_path):
                os.startfile(mods_path)
                self.update_status(f"Pasta de mods aberta: {mods_path}")
            else:
                messagebox.showwarning("Aviso", "Pasta de mods não encontrada!")
        except Exception as e:
            self.show_error("Falha ao abrir pasta de mods", e)
    
    def check_updates(self):
        try:
            self.update_status("Verificando atualizações...")
            
            repo_url = "https://api.github.com/repos/seu-usuario/pvz-fusion/releases/latest"
            response = requests.get(repo_url)
            
            if response.status_code == 200:
                latest_release = response.json()
                latest_version = latest_release['tag_name']
                
                if latest_version > self.config['version']:
                    if messagebox.askyesno(
                        "Atualização Disponível", 
                        f"Versão {latest_version} disponível!\nDeseja baixar agora?"
                    ):
                        self.download_update(latest_release)
                else:
                    messagebox.showinfo("Sem Atualizações", "Você já tem a versão mais recente!")
                    self.update_status("Versão atual: " + self.config['version'])
            else:
                messagebox.showerror("Erro", "Não foi possível conectar ao GitHub")
                self.update_status("Falha na verificação")
        except Exception as e:
            self.show_error("Erro ao verificar atualizações", e)
    
    def install_melonloader(self):
        try:
            self.update_status("Baixando MelonLoader...")
            
            temp_dir = "temp"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            melon_url = "https://github.com/LavaGang/MelonLoader/releases/latest/download/MelonLoader.x64.zip"
            file_path = os.path.join(temp_dir, "MelonLoader.zip")
            
            # Baixa o arquivo
            self.download_file(melon_url, file_path)
            
            # Extrai para a pasta do jogo
            self.update_status("Instalando MelonLoader...")
            with ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(self.config['game_path'])
            
            messagebox.showinfo("Sucesso", "MelonLoader instalado com sucesso!")
            self.update_status("MelonLoader instalado")
        except Exception as e:
            self.show_error("Falha ao instalar MelonLoader", e)
    
    # ============== FUNÇÕES AUXILIARES ==============
    
    def download_update(self, release):
        try:
            temp_dir = "temp"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            download_url = release['assets'][0]['browser_download_url']
            file_path = os.path.join(temp_dir, "update.zip")
            
            self.update_status("Baixando atualização...")
            self.download_file(download_url, file_path)
            
            self.update_status("Instalando atualização...")
            with ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(self.config['game_path'])
            
            # Atualiza a versão no config
            self.config['version'] = release['tag_name']
            self.save_config(self.config)
            
            messagebox.showinfo("Sucesso", "Atualização instalada com sucesso!")
            self.update_status(f"Versão {release['tag_name']} instalada")
        except Exception as e:
            self.show_error("Falha ao instalar atualização", e)
    
    def download_file(self, url, save_path):
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
    
    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update()
    
    def show_error(self, title, exception):
        messagebox.showerror(title, f"Erro: {str(exception)}")
        self.update_status(f"Erro: {title}")
    
    # ============== MANIPULAÇÃO DE CONFIG ==============
    
    def load_config(self):
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except:
            # Configuração padrão se o arquivo não existir
            default_config = {
                "version": "1.0",
                "game_path": "C:/Program Files/PVZ_Fusion",
                "mods_path": "C:/Program Files/PVZ_Fusion/Mods"
            }
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config):
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)

# Ponto de entrada do programa
if __name__ == "__main__":
    root = tk.Tk()
    app = PVZFusionLauncher(root)
    root.mainloop()
