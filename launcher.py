import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os
import json
from zipfile import ZipFile
import time
import sys
import traceback
import requests
import webbrowser
import shutil
from packaging import version
import hashlib
import threading
from queue import Queue

class PVZFusionLauncher:
    def __init__(self, root):
        self.root = root
        self.current_version = "1.1"
        self.download_queue = Queue()
        
        # Inicializa configurações padrão
        self.default_settings = {
            "show_console": True,
            "show_path_info": True,
            "hide_melonconsole": False,
            "launch_without_mods": False,
            "auto_update": True,
            "check_updates_on_start": True,
            "create_backup": True,
            "verify_hashes": True
        }
        
        # Inicializa estruturas de dados
        self.settings = self.default_settings.copy()
        self.config = {
            "version": self.current_version,
            "game_path": "",
            "mods_path": "",
            "last_update_check": 0
        }
        
        # Carrega configurações reais
        self.load_settings()
        self.load_config()
        
        # Configura interface
        self.setup_ui()
        
        # Inicia thread para downloads
        self.download_thread = threading.Thread(target=self.process_download_queue, daemon=True)
        self.download_thread.start()
        
        # Verificação de atualização inicial
        if self.settings['check_updates_on_start']:
            self.root.after(2000, lambda: self.safe_check_updates(show_no_update_msg=False))

    def load_settings(self):
        """Carrega as configurações do usuário de settings.json"""
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as f:
                    loaded_settings = json.load(f)
                    self.settings = {**self.default_settings, **loaded_settings}
            self.save_settings()  # Garante que o arquivo exista
        except Exception as e:
            print(f"Erro ao carregar configurações: {str(e)}")
            self.settings = self.default_settings.copy()

    def save_settings(self):
        """Salva as configurações do usuário"""
        try:
            with open('settings.json', 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Erro ao salvar configurações: {str(e)}")

    def load_config(self):
        """Carrega a configuração principal de config.json"""
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r') as f:
                    self.config = json.load(f)
                    # Garante que campos essenciais existam
                    self.config.setdefault("game_path", "")
                    self.config.setdefault("mods_path", "")
                    self.config.setdefault("last_update_check", 0)
            self.save_config()  # Garante que o arquivo exista
        except Exception as e:
            print(f"Erro ao carregar configuração principal: {str(e)}")
            self.config = {
                "version": self.current_version,
                "game_path": "",
                "mods_path": "",
                "last_update_check": 0
            }

    def save_config(self):
        """Salva a configuração principal"""
        try:
            with open('config.json', 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Erro ao salvar configuração principal: {str(e)}")

    def setup_ui(self):
        """Configura todos os elementos da interface"""
        try:
            # Configuração de estilo
            self.style = ttk.Style()
            self.style.theme_use('clam')
            
            # Frame principal
            main_frame = ttk.Frame(self.root, padding="15")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Título
            title = ttk.Label(main_frame, text=f"PVZ Fusion Launcher v{self.current_version}", 
                            font=('Helvetica', 16))
            title.pack(pady=10)
            
            # Barra de progresso (inicialmente oculta)
            self.progress_bar = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, 
                                              length=300, mode='determinate')
            
            # Frame de botões principais
            btn_frame = ttk.Frame(main_frame)
            btn_frame.pack(fill=tk.X, pady=5)
            
            ttk.Button(btn_frame, text="Configurar Caminhos", 
                      command=self.setup_paths).pack(side=tk.LEFT, expand=True, padx=2)
            ttk.Button(btn_frame, text="Configurações", 
                      command=self.open_settings).pack(side=tk.LEFT, expand=True, padx=2)
            
            # Informações de caminho
            self.path_frame = ttk.Frame(main_frame)
            self.path_info = ttk.Label(self.path_frame, text="", wraplength=550)
            self.path_info.pack()
            
            # Frame de ações principais
            action_frame = ttk.Frame(main_frame)
            action_frame.pack(fill=tk.X, pady=5)
            
            ttk.Button(action_frame, text="Iniciar Jogo", 
                      command=self.safe_launch).pack(side=tk.LEFT, expand=True, padx=2)
            ttk.Button(action_frame, text="Abrir Mods", 
                      command=self.safe_open_mods).pack(side=tk.LEFT, expand=True, padx=2)
            
            # Frame de ações secundárias
            secondary_frame = ttk.Frame(main_frame)
            secondary_frame.pack(fill=tk.X, pady=5)
            
            ttk.Button(secondary_frame, text="Verificar Atualizações", 
                      command=lambda: self.safe_check_updates(show_no_update_msg=True)).pack(side=tk.LEFT, expand=True, padx=2)
            ttk.Button(secondary_frame, text="Instalar MelonLoader", 
                      command=self.safe_install_melon).pack(side=tk.LEFT, expand=True, padx=2)
            
            # Status
            self.status_label = ttk.Label(main_frame, text="Pronto", relief=tk.SUNKEN)
            self.status_label.pack(pady=10, fill=tk.X)
            
            # Console de log
            self.console_frame = ttk.Frame(main_frame)
            scrollbar = ttk.Scrollbar(self.console_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            self.console = tk.Text(self.console_frame, height=8, state='disabled', 
                                 bg='black', fg='white', yscrollcommand=scrollbar.set)
            self.console.pack(fill=tk.BOTH, expand=True)
            
            scrollbar.config(command=self.console.yview)
            
            self.apply_visibility_settings()
            
        except Exception as e:
            self.show_critical_error("Erro na interface", e)

    def open_settings(self):
        """Abre a janela de configurações"""
        settings_win = tk.Toplevel(self.root)
        settings_win.title("Configurações")
        settings_win.geometry("400x450")
        settings_win.resizable(False, False)
        
        main_frame = ttk.Frame(settings_win, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Configurações", font=('Helvetica', 14)).pack(pady=5)
        
        # Seção de interface
        ttk.Label(main_frame, text="Interface:", font=('Helvetica', 10, 'bold')).pack(anchor=tk.W)
        
        ttk.Checkbutton(
            main_frame, 
            text="Mostrar Console de Log",
            variable=tk.BooleanVar(value=self.settings['show_console']),
            command=lambda: self.toggle_setting('show_console', not self.settings['show_console'])
        ).pack(anchor=tk.W)
        
        ttk.Checkbutton(
            main_frame, 
            text="Mostrar Caminhos do Jogo",
            variable=tk.BooleanVar(value=self.settings['show_path_info']),
            command=lambda: self.toggle_setting('show_path_info', not self.settings['show_path_info'])
        ).pack(anchor=tk.W)
        
        # Seção de jogo
        ttk.Label(main_frame, text="Jogo:", font=('Helvetica', 10, 'bold')).pack(pady=(10,2), anchor=tk.W)
        
        ttk.Checkbutton(
            main_frame,
            text="Esconder Console do MelonLoader",
            variable=tk.BooleanVar(value=self.settings['hide_melonconsole']),
            command=lambda: self.toggle_setting('hide_melonconsole', not self.settings['hide_melonconsole'])
        ).pack(anchor=tk.W)
        
        ttk.Checkbutton(
            main_frame,
            text="Iniciar jogo sem mods",
            variable=tk.BooleanVar(value=self.settings['launch_without_mods']),
            command=lambda: self.toggle_setting('launch_without_mods', not self.settings['launch_without_mods'])
        ).pack(anchor=tk.W)
        
        # Seção de atualização
        ttk.Label(main_frame, text="Atualizações:", font=('Helvetica', 10, 'bold')).pack(pady=(10,2), anchor=tk.W)
        
        ttk.Checkbutton(
            main_frame,
            text="Atualização Automática",
            variable=tk.BooleanVar(value=self.settings['auto_update']),
            command=lambda: self.toggle_setting('auto_update', not self.settings['auto_update'])
        ).pack(anchor=tk.W)
        
        ttk.Checkbutton(
            main_frame,
            text="Verificar atualizações ao iniciar",
            variable=tk.BooleanVar(value=self.settings['check_updates_on_start']),
            command=lambda: self.toggle_setting('check_updates_on_start', not self.settings['check_updates_on_start'])
        ).pack(anchor=tk.W)
        
        ttk.Checkbutton(
            main_frame,
            text="Criar backup antes de atualizar",
            variable=tk.BooleanVar(value=self.settings['create_backup']),
            command=lambda: self.toggle_setting('create_backup', not self.settings['create_backup'])
        ).pack(anchor=tk.W)
        
        ttk.Checkbutton(
            main_frame,
            text="Verificar hashes de segurança",
            variable=tk.BooleanVar(value=self.settings['verify_hashes']),
            command=lambda: self.toggle_setting('verify_hashes', not self.settings['verify_hashes'])
        ).pack(anchor=tk.W)
        
        ttk.Button(main_frame, text="Fechar", command=settings_win.destroy).pack(pady=10)

    def process_download_queue(self):
        """Processa a fila de downloads em uma thread separada"""
        while True:
            item = self.download_queue.get()
            if item['type'] == 'update':
                self.download_and_install_update(item['url'], item['version'], item.get('hash'))
            elif item['type'] == 'melonloader':
                self.download_and_install_melonloader(item['url'])
            self.download_queue.task_done()

    def download_file_with_progress(self, url, dest_path):
        """Baixa um arquivo com exibição de progresso"""
        try:
            self.progress_bar.pack(pady=10)
            self.progress_bar['value'] = 0
            self.root.update()
            
            with requests.get(url, stream=True, timeout=30) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                downloaded = 0
                
                with open(dest_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            progress = (downloaded / total_size) * 100
                            self.progress_bar['value'] = progress
                            self.root.update()
            
            self.progress_bar.pack_forget()
            return True
            
        except Exception as e:
            self.progress_bar.pack_forget()
            self.show_error("Download falhou", e)
            return False

    def verify_file_hash(self, file_path, expected_hash):
        """Verifica o hash SHA-256 de um arquivo"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest() == expected_hash
        except Exception as e:
            self.log(f"Erro ao verificar hash: {str(e)}")
            return False

    def check_updates(self, show_no_update_msg=True):
        """Verifica e aplica atualizações"""
        try:
            self.log("Verificando atualizações no GitHub...")
            api_url = "https://api.github.com/repos/shelugon/PvZ-Fusion-Launcher/releases/latest"
            response = requests.get(api_url, timeout=15)
            response.raise_for_status()
            
            release_data = response.json()
            latest_version = release_data['tag_name'].strip('vV')
            download_url = None
            expected_hash = None
            
            # Encontra o asset .zip e hash na release
            for asset in release_data.get('assets', []):
                if asset['name'].lower().endswith('.zip'):
                    download_url = asset['browser_download_url']
                elif asset['name'].lower().endswith('.sha256'):
                    hash_url = asset['browser_download_url']
                    hash_response = requests.get(hash_url)
                    if hash_response.status_code == 200:
                        expected_hash = hash_response.text.strip()
            
            if not download_url:
                raise Exception("Arquivo de atualização não encontrado")
            
            self.log(f"Versão atual: {self.current_version} | Disponível: {latest_version}")
            
            if version.parse(latest_version) > version.parse(self.current_version):
                if self.settings['auto_update']:
                    self.download_queue.put({
                        'type': 'update',
                        'url': download_url,
                        'version': latest_version,
                        'hash': expected_hash
                    })
                    return True
                else:
                    return self.prompt_for_update(latest_version, download_url, expected_hash)
            elif show_no_update_msg:
                self.log("Você já tem a versão mais recente")
                messagebox.showinfo("Sem Atualizações", "Você já está usando a versão mais recente!", parent=self.root)
            return False
                
        except Exception as e:
            self.log(f"Erro ao verificar atualizações: {str(e)}")
            if show_no_update_msg:
                messagebox.showerror("Erro", f"Não foi possível verificar atualizações:\n{str(e)}", parent=self.root)
            return False

    def download_and_install_update(self, download_url, new_version, expected_hash=None):
        """Baixa e instala a atualização"""
        try:
            temp_dir = os.path.join(os.getcwd(), "launcher_temp_update")
            os.makedirs(temp_dir, exist_ok=True)
            zip_path = os.path.join(temp_dir, "update.zip")
            
            # 1. Baixa a atualização
            self.log(f"Baixando versão {new_version}...")
            if not self.download_file_with_progress(download_url, zip_path):
                raise Exception("Falha no download")
            
            # 2. Verifica hash se configurado
            if self.settings['verify_hashes'] and expected_hash:
                if not self.verify_file_hash(zip_path, expected_hash):
                    raise Exception("Verificação de hash falhou - arquivo pode estar corrompido")
            
            # 3. Cria backup se configurado
            if self.settings['create_backup']:
                self.log("Criando backup...")
                backup_path = os.path.join(os.getcwd(), f"backup_v{self.current_version}.zip")
                self.create_backup(backup_path)
            
            # 4. Extrai os arquivos
            self.log("Instalando atualização...")
            with ZipFile(zip_path, 'r') as zip_ref:
                safe_members = [m for m in zip_ref.namelist() 
                              if not m.startswith(('__MACOSX/', '.DS_Store'))]
                zip_ref.extractall(os.getcwd(), members=safe_members)
            
            # 5. Atualiza a versão
            self.current_version = new_version
            self.root.title(f"PVZ Fusion Launcher v{self.current_version}")
            
            # 6. Limpeza
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            self.log("Atualização concluída com sucesso!")
            if messagebox.askyesno(
                "Atualização Completa",
                f"O launcher foi atualizado para v{new_version}!\n\n"
                "Deseja reiniciar agora para aplicar as mudanças?",
                parent=self.root
            ):
                self.restart_launcher()
            return True
            
        except Exception as e:
            self.log(f"Falha na atualização: {str(e)}")
            messagebox.showerror(
                "Erro na Atualização",
                f"Não foi possível completar a atualização:\n{str(e)}\n"
                "Seu launcher pode estar corrompido. Restaure do backup se necessário.",
                parent=self.root
            )
            return False

    def install_melonloader(self):
        """Instala o MelonLoader"""
        try:
            if not self.config.get('game_path'):
                self.setup_paths()
                return False
                
            melon_url = "https://github.com/LavaGang/MelonLoader/releases/latest/download/MelonLoader.x64.zip"
            
            self.download_queue.put({
                'type': 'melonloader',
                'url': melon_url
            })
            return True
            
        except Exception as e:
            self.show_error("Erro na instalação", e)
            return False

    def download_and_install_melonloader(self, download_url):
        """Baixa e instala o MelonLoader"""
        try:
            game_dir = self.config['game_path']
            temp_dir = os.path.join(game_dir, "LauncherTemp")
            os.makedirs(temp_dir, exist_ok=True)
            zip_path = os.path.join(temp_dir, "MelonLoader.zip")
            
            # 1. Baixa o MelonLoader
            self.log("Baixando MelonLoader...")
            if not self.download_file_with_progress(download_url, zip_path):
                raise Exception("Falha no download do MelonLoader")
            
            # 2. Extrai os arquivos
            self.log("Instalando MelonLoader...")
            with ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(game_dir)
            
            # 3. Cria pasta de mods se não existir
            mods_dir = os.path.join(game_dir, "Mods")
            os.makedirs(mods_dir, exist_ok=True)
            
            self.config['mods_path'] = mods_dir
            self.save_config()
            self.update_path_display()
            
            # 4. Limpeza
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            self.log("MelonLoader instalado com sucesso!")
            return True
            
        except Exception as e:
            self.show_error("Erro na instalação do MelonLoader", e)
            return False

    def launch_game(self):
        """Inicia o jogo com as configurações atuais"""
        if not self.config.get('game_path'):
            self.setup_paths()
            return
            
        exe_path = os.path.join(self.config['game_path'], "PlantsVsZombiesRH.exe")
        mods_dir = self.config.get('mods_path', '')
        
        if not os.path.exists(exe_path):
            self.log("Executável não encontrado!")
            self.setup_paths()
            return
            
        # Prepara argumentos de lançamento
        launch_args = [exe_path]
        
        if self.settings['hide_melonconsole']:
            launch_args.append("--melonloader.hideconsole")
            
        if self.settings['launch_without_mods']:
            launch_args.append("--no-mods")
            self.log("Iniciando jogo SEM mods")
        else:
            self.log("Iniciando jogo COM mods")
        
        # Se não tem pasta de mods, instala MelonLoader primeiro
        if mods_dir and not os.path.exists(mods_dir) and not self.settings['launch_without_mods']:
            self.log("Instalando MelonLoader...")
            if self.install_melonloader():
                self.log("Iniciando jogo para finalizar instalação...")
                process = subprocess.Popen(launch_args)
                time.sleep(15)
                process.terminate()
                self.log("Instalação completa!")
                
        self.log(f"Iniciando jogo: {' '.join(launch_args)}")
        subprocess.Popen(launch_args)
        
        status_text = "Jogo iniciado"
        if self.settings['launch_without_mods']:
            status_text += " (sem mods)"
        self.status_label.config(text=status_text)

    def open_mods_folder(self):
        """Abre a pasta de mods"""
        if not self.config.get('mods_path'):
            self.setup_paths()
            return
            
        mods_dir = self.config['mods_path']
        
        if not os.path.exists(mods_dir):
            self.log("Pasta de mods não existe, instalando MelonLoader...")
            if self.install_melonloader():
                os.startfile(mods_dir)
        else:
            os.startfile(mods_dir)
            
        self.status_label.config(text="Pasta de mods aberta")

    def create_backup(self, backup_path):
        """Cria um backup zip do launcher atual"""
        try:
            with ZipFile(backup_path, 'w') as backup_zip:
                for root, dirs, files in os.walk(os.getcwd()):
                    if 'launcher_temp_update' in root or '.git' in root:
                        continue
                    for file in files:
                        if file.endswith(('.zip', '.log', '.tmp')):
                            continue
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, os.getcwd())
                        backup_zip.write(file_path, arcname)
            self.log(f"Backup criado em: {backup_path}")
            return True
        except Exception as e:
            self.log(f"Erro ao criar backup: {str(e)}")
            return False

    def restart_launcher(self):
        """Reinicia o launcher"""
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def update_path_display(self):
        """Atualiza o display de caminhos"""
        if self.config.get('game_path'):
            text = f"Jogo: {self.config['game_path']}\nMods: {self.config.get('mods_path', '')}"
            self.path_info.config(text=text)
        else:
            self.path_info.config(text="Caminhos não configurados")

    def setup_paths(self):
        """Configura os caminhos do jogo"""
        try:
            exe_path = filedialog.askopenfilename(
                title="Selecione PlantsVsZombiesRH.exe",
                filetypes=[("Executável", "*.exe")]
            )
            
            if not exe_path:
                return
                
            if not exe_path.lower().endswith('.exe'):
                messagebox.showerror("Erro", "Por favor, selecione um arquivo .exe válido")
                return
            
            if os.path.basename(exe_path) != "PlantsVsZombiesRH.exe":
                messagebox.showwarning("Aviso", "O arquivo selecionado não é o PlantsVsZombiesRH.exe")
                return
                
            game_dir = os.path.dirname(exe_path)
            mods_dir = os.path.join(game_dir, "Mods")
            
            self.config.update({
                "game_path": game_dir,
                "mods_path": mods_dir
            })
            
            self.save_config()
            self.update_path_display()
            self.log(f"Caminhos configurados: {game_dir}")
            
            if not os.path.exists(mods_dir):
                self.log("Pasta de mods não encontrada, instalando MelonLoader...")
                self.install_melonloader()
            
        except Exception as e:
            self.show_error("Erro ao configurar caminhos", e)

    def show_error(self, title, error):
        """Mostra erro genérico"""
        error_msg = f"{title}:\n{str(error)}"
        self.log(f"ERRO: {error_msg}")
        messagebox.showerror(title, error_msg)
        self.status_label.config(text=f"Erro: {title}")

    def show_critical_error(self, title, error):
        """Mostra erro crítico e encerra"""
        error_msg = f"{title}:\n{str(error)}"
        print(f"ERRO CRÍTICO: {error_msg}")
        traceback.print_exc()
        messagebox.showerror(title, "Ocorreu um erro crítico. O launcher será fechado.\n\n" + error_msg)
        self.root.destroy()
        sys.exit(1)

    def log(self, message):
        """Adiciona mensagem ao console"""
        try:
            self.console.config(state='normal')
            self.console.insert(tk.END, message + "\n")
            self.console.config(state='disabled')
            self.console.see(tk.END)
            self.root.update()
        except:
            print(message)

    def safe_launch(self):
        """Versão segura de launch_game"""
        try:
            self.launch_game()
        except Exception as e:
            self.show_error("Erro ao iniciar jogo", e)

    def safe_open_mods(self):
        """Versão segura de open_mods_folder"""
        try:
            self.open_mods_folder()
        except Exception as e:
            self.show_error("Erro ao abrir mods", e)

    def safe_install_melon(self):
        """Versão segura de install_melonloader"""
        try:
            self.install_melonloader()
        except Exception as e:
            self.show_error("Erro ao instalar MelonLoader", e)

    def safe_check_updates(self, show_no_update_msg=True):
        """Versão segura de check_updates"""
        try:
            self.check_updates(show_no_update_msg)
        except Exception as e:
            self.show_error("Erro ao verificar atualizações", e)

    def toggle_setting(self, setting, value):
        """Atualiza uma configuração e aplica as mudanças"""
        self.settings[setting] = value
        self.save_settings()
        self.apply_visibility_settings()

    def apply_visibility_settings(self):
        """Aplica as configurações de visibilidade"""
        if self.settings['show_console']:
            self.console_frame.pack(fill=tk.BOTH, expand=True)
        else:
            self.console_frame.pack_forget()
        
        if self.settings['show_path_info']:
            self.path_frame.pack(fill=tk.X, pady=5)
        else:
            self.path_frame.pack_forget()

    def prompt_for_update(self, new_version, download_url, expected_hash=None):
        """Pergunta ao usuário sobre a atualização"""
        answer = messagebox.askyesno(
            "Atualização Disponível",
            f"Versão {new_version} disponível!\n\n"
            "Deseja atualizar agora? (Recomendado)\n\n"
            "Nota: Será criado um backup automático",
            parent=self.root
        )
        if answer:
            self.download_queue.put({
                'type': 'update',
                'url': download_url,
                'version': new_version,
                'hash': expected_hash
            })
            return True
        return False

if __name__ == "__main__":
    try:
        root = tk.Tk()
        root.title("PVZ Fusion Launcher")  # Título correto da janela
        app = PVZFusionLauncher(root)
        root.mainloop()
    except Exception as e:
        print(f"Erro fatal: {str(e)}")
        traceback.print_exc()
        messagebox.showerror("Erro Fatal", f"O launcher encontrou um erro:\n{str(e)}")
