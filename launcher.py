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
from mod_manager import ModManager

class PVZFusionLauncher:
    def __init__(self, root):
        self.root = root
<<<<<<< HEAD
        self.root.geometry("800x600")
        self.root.title("PVZ Fusion Launcher")
        self.current_version = "1.0.1"
=======
        self.current_version = "1.0.1"
>>>>>>> 96d10dd068a78d0daec0cb3fa95d75e9632ec0d4
        self.download_queue = Queue()
        
        # Configurações
        self.default_settings = {
            "show_console": True,
            "show_path_info": True,
            "hide_melonconsole": False,
            "launch_without_mods": False,
            "auto_update": True,
            "check_updates_on_start": True,
            "create_backup": True,
            "verify_hashes": True,
            "auto_install_melon": True
        }
        
        self.settings = self.default_settings.copy()
        self.config = {
            "version": self.current_version,
            "game_path": "",
            "mods_path": "",
            "last_update_check": 0
        }
        
        self.load_settings()
        self.load_config()
        self.mod_manager = ModManager(self.config.get('game_path', ''))
        
        self.setup_ui()
        
        self.download_thread = threading.Thread(target=self.process_download_queue, daemon=True)
        self.download_thread.start()
        
        if self.settings['check_updates_on_start']:
            self.root.after(2000, lambda: self.safe_check_updates(show_no_update_msg=False))

    def setup_ui(self):
        """Configura a interface do usuário"""
        try:
            self.style = ttk.Style()
            self.style.theme_use('clam')
            
            main_frame = ttk.Frame(self.root, padding="15")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Header
            header_frame = ttk.Frame(main_frame)
            header_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(header_frame, 
                     text=f"PVZ Fusion Launcher v{self.current_version}",
                     font=('Helvetica', 16)).pack(side=tk.LEFT)
            
            ttk.Label(header_frame,
                     text="EM DESENVOLVIMENTO - ALGUMAS FUNCIONALIDADES PODEM NÃO FUNCIONAR",
                     font=('Helvetica', 8),
                     foreground='red').pack(side=tk.RIGHT, padx=10)
            
            self.game_version_btn = ttk.Button(
                header_frame,
                text="Versão: Desconhecida",
                command=self.check_game_version
            )
            self.game_version_btn.pack(side=tk.RIGHT, padx=5)
            self.update_game_version_display()
            
            self.progress_bar = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=300)
            
            # Controles principais
            control_frame = ttk.Frame(main_frame)
            control_frame.pack(fill=tk.X, pady=10)
            
            buttons = [
                ("Configurar Caminhos", self.setup_paths),
                ("Iniciar Jogo", self.safe_launch),
                ("Gerenciar Mods", self.show_mods_manager),
                ("Abrir Pasta de Mods", self.open_mods_folder),
                ("Atualizar Jogo", self.update_game),
                ("Configurações", self.open_settings),
                ("Verificar Atualizações", lambda: self.safe_check_updates(show_no_update_msg=True)),
                ("Instalar MelonLoader", self.safe_install_melon)
            ]
            
            for i in range(0, len(buttons), 2):
                frame = ttk.Frame(main_frame)
                frame.pack(fill=tk.X, pady=5)
                for text, command in buttons[i:i+2]:
                    ttk.Button(frame, text=text, command=command).pack(side=tk.LEFT, expand=True, padx=2)
            
            # Informações de caminho
            self.path_frame = ttk.Frame(main_frame)
            self.path_frame.pack(fill=tk.X, pady=5)
            self.path_info = ttk.Label(self.path_frame, text="", wraplength=500)
            self.path_info.pack()
            self.update_path_display()
            
            # Console
            self.console_frame = ttk.Frame(main_frame)
            self.console_frame.pack(fill=tk.BOTH, expand=True)
            
            scrollbar = ttk.Scrollbar(self.console_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            self.console = tk.Text(
                self.console_frame, 
                height=10, 
                state='normal',
                bg='black', 
                fg='white',
                yscrollcommand=scrollbar.set
            )
            self.console.pack(fill=tk.BOTH, expand=True)
            scrollbar.config(command=self.console.yview)
            
            self.status_label = ttk.Label(main_frame, text="Pronto", relief=tk.SUNKEN)
            self.status_label.pack(fill=tk.X, pady=5)
            
        except Exception as e:
            self.show_critical_error("Erro na interface", e)

    def update_game(self):
        """Função para atualizar o jogo"""
        self.log("\n=== Iniciando procedimento de atualização do jogo ===")
        messagebox.showinfo("Atualizar Jogo", 
                          "Esta funcionalidade ainda está em desenvolvimento!\n"
                          "Em versões futuras, isso verificará atualizações do jogo no GitHub.",
                          parent=self.root)
        self.log("Funcionalidade de atualização do jogo ainda não implementada")

    def launch_game(self):
        """Inicia o jogo com as configurações atuais"""
        self.log("\n=== Iniciando procedimento de lançamento do jogo ===")
        
        if not self.config.get('game_path'):
            self.log("ERRO: Caminho do jogo não configurado!")
            self.setup_paths()
            return
            
        exe_path = os.path.join(self.config['game_path'], "PlantsVsZombiesRH.exe")
        mods_dir = self.config.get('mods_path', '')
        
        if not os.path.exists(exe_path):
            self.log(f"ERRO: Executável não encontrado em: {exe_path}")
            self.setup_paths()
            return
            
        self.log(f"Executável do jogo encontrado em: {exe_path}")
        
        launch_args = [exe_path]
        self.log(f"Argumentos de lançamento: {launch_args}")
        
        if self.settings['hide_melonconsole']:
            launch_args.append("--melonloader.hideconsole")
            self.log("Adicionado argumento: --melonloader.hideconsole")
            
        if self.settings['launch_without_mods']:
            launch_args.append("--no-mods")
            self.log("Adicionado argumento: --no-mods (mods desativados)")
        else:
            self.log("Mods ativados (padrão)")
        
        if (mods_dir and not os.path.exists(mods_dir)) and not self.settings['launch_without_mods']:
            if self.settings['auto_install_melon']:
                self.log("Pasta de mods não encontrada, iniciando instalação automática do MelonLoader...")
                if self.install_melonloader():
                    self.log("MelonLoader instalado com sucesso, iniciando jogo para finalizar instalação...")
                    try:
                        process = subprocess.Popen(launch_args)
                        self.log(f"Processo do jogo iniciado com PID: {process.pid}")
                        time.sleep(15)
                        process.terminate()
                        self.log("Processo do jogo finalizado após instalação do MelonLoader")
                    except Exception as e:
                        self.log(f"ERRO durante inicialização pós-instalação: {str(e)}")
                    self.log("Instalação do MelonLoader concluída!")
            else:
                self.log("AVISO: Pasta de mods não encontrada mas instalação automática está desativada")
                messagebox.showwarning("Pasta de Mods Não Encontrada", 
                                     "A pasta de mods não foi encontrada e a instalação automática está desativada.",
                                     parent=self.root)
                return
                
        self.log("Iniciando o jogo...")
        try:
            process = subprocess.Popen(launch_args)
            self.log(f"Jogo iniciado com sucesso! PID: {process.pid}")
            
            threading.Thread(target=self.monitor_game_process, args=(process,), daemon=True).start()
            
        except Exception as e:
            self.log(f"ERRO ao iniciar o jogo: {str(e)}")
            self.show_error("Erro ao iniciar jogo", e)
            return
        
        status_text = "Jogo iniciado"
        if self.settings['launch_without_mods']:
            status_text += " (sem mods)"
        self.status_label.config(text=status_text)

    def monitor_game_process(self, process):
        """Monitora o processo do jogo e avisa quando fecha"""
        self.log("Monitorando processo do jogo...")
        process.wait()
        self.log("O jogo foi fechado")
        self.root.after(100, lambda: self.status_label.config(text="Jogo fechado"))
        self.root.after(100, lambda: messagebox.showinfo("Jogo Fechado", 
                                                       "Plants vs Zombies Fusion foi fechado.",
                                                       parent=self.root))

    def install_melonloader(self):
        """Instala o MelonLoader"""
        self.log("\n=== Iniciando instalação do MelonLoader ===")
        try:
            if not self.config.get('game_path'):
                self.log("ERRO: Caminho do jogo não configurado!")
                self.setup_paths()
                return False
                
            melon_url = "https://github.com/LavaGang/MelonLoader/releases/latest/download/MelonLoader.x64.zip"
            self.log(f"URL do MelonLoader: {melon_url}")
            
            self.download_queue.put({
                'type': 'melonloader',
                'url': melon_url
            })
            self.log("Download do MelonLoader adicionado à fila")
            return True
            
        except Exception as e:
            self.log(f"ERRO na instalação: {str(e)}")
            self.show_error("Erro na instalação", e)
            return False

    def download_and_install_melonloader(self, download_url):
        """Baixa e instala o MelonLoader"""
        self.log("\n=== Processando instalação do MelonLoader ===")
        try:
            game_dir = self.config['game_path']
            temp_dir = os.path.join(game_dir, "LauncherTemp")
            
            self.log(f"Diretório do jogo: {game_dir}")
            self.log(f"Criando diretório temporário: {temp_dir}")
            
            os.makedirs(temp_dir, exist_ok=True)
            zip_path = os.path.join(temp_dir, "MelonLoader.zip")
            
            self.log(f"Iniciando download do MelonLoader para: {zip_path}")
            if not self.download_file_with_progress(download_url, zip_path):
                raise Exception("Falha no download do MelonLoader")
            self.log("Download do MelonLoader concluído com sucesso!")
            
            self.log(f"Iniciando extração para: {game_dir}")
            with ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(game_dir)
            self.log("Extração concluída com sucesso!")
            
            mods_dir = os.path.join(game_dir, "Mods")
            self.log(f"Verificando pasta de mods: {mods_dir}")
            os.makedirs(mods_dir, exist_ok=True)
            
            self.config['mods_path'] = mods_dir
            self.save_config()
            self.update_path_display()
            self.log("Pasta de mods configurada e caminho atualizado")
            
            self.log("Removendo arquivos temporários...")
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            self.log("=== Instalação do MelonLoader concluída com sucesso! ===")
            return True
            
        except Exception as e:
            self.log(f"ERRO na instalação do MelonLoader: {str(e)}")
            self.show_error("Erro na instalação do MelonLoader", e)
            return False

    def open_settings(self):
        """Abre a janela de configurações"""
        settings_win = tk.Toplevel(self.root)
        settings_win.title("Configurações")
        settings_win.geometry("400x500")
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
        
        ttk.Checkbutton(
            main_frame,
            text="Instalar MelonLoader automaticamente",
            variable=tk.BooleanVar(value=self.settings['auto_install_melon']),
            command=lambda: self.toggle_setting('auto_install_melon', not self.settings['auto_install_melon'])
        ).pack(anchor=tk.W, pady=(0,10))
        
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

    def show_mods_manager(self):
        """Janela de gerenciamento de mods"""
        if not self.config.get('game_path'):
            messagebox.showwarning("Aviso", "Configure o caminho do jogo primeiro!")
            return
            
        manager = tk.Toplevel(self.root)
        manager.title("Gerenciador de Mods")
        manager.geometry("800x600")
        
        main_frame = ttk.Frame(manager)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        detail_frame = ttk.Frame(main_frame)
        detail_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.mod_listbox = tk.Listbox(
            list_frame,
            width=30,
            height=20,
            selectmode=tk.SINGLE
        )
        self.mod_listbox.pack(fill=tk.BOTH, expand=True)
        self.mod_listbox.bind('<<ListboxSelect>>', self.show_mod_details)
        
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, 
                  text="Ativar/Desativar", 
                  command=self.toggle_selected_mod).pack(side=tk.LEFT, expand=True)
        
        ttk.Button(btn_frame, 
                  text="Atualizar Lista", 
                  command=lambda: self.update_mods_list(manager)).pack(side=tk.LEFT, expand=True)
        
        self.mod_details = tk.Text(
            detail_frame,
            wrap=tk.WORD,
            state='disabled',
            height=10,
            padx=10,
            pady=10
        )
        self.mod_details.pack(fill=tk.BOTH, expand=True)
        
        self.update_mods_list(manager)

    def update_mods_list(self, manager=None):
        """Atualiza a lista de mods na interface"""
        if not hasattr(self, 'mod_listbox'):
            return
            
        self.mod_listbox.delete(0, tk.END)
        mods = self.mod_manager.get_installed_mods()
        
        for mod in mods:
            status = " (Ativo)" if mod['ativo'] else " (Inativo)"
            self.mod_listbox.insert(tk.END, mod['nome'] + status)
        
        if manager:
            manager.title(f"Gerenciador de Mods - {len(mods)} mods encontrados")

    def show_mod_details(self, event):
        """Mostra detalhes do mod selecionado"""
        selection = self.mod_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        mods = self.mod_manager.get_installed_mods()
        
        if index >= len(mods):
            return
            
        mod = mods[index]
        
        self.mod_details.config(state='normal')
        self.mod_details.delete(1.0, tk.END)
        
        details = (
            f"Nome: {mod['nome']}\n"
            f"Status: {'Ativo' if mod['ativo'] else 'Inativo'}\n"
            f"Versão: {mod['versao']}\n"
            f"Autor: {mod['autor']}\n"
            f"Arquivo: {mod['arquivo']}\n\n"
            f"Descrição:\n{mod['descricao']}\n\n"
            f"Dependências: {', '.join(mod['dependencias']) if mod['dependencias'] else 'Nenhuma'}"
        )
        
        self.mod_details.insert(tk.END, details)
        self.mod_details.config(state='disabled')

    def toggle_selected_mod(self):
        """Alterna status do mod selecionado"""
        selection = self.mod_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        mods = self.mod_manager.get_installed_mods()
        
        if index >= len(mods):
            return
            
        mod = mods[index]
        new_state = not mod['ativo']
        
        if self.mod_manager.toggle_mod(mod['nome'], new_state):
            self.log(f"Mod {mod['nome']} {'ativado' if new_state else 'desativado'}!")
            self.update_mods_list()
        else:
            self.log(f"Falha ao alterar mod {mod['nome']}")

    def check_game_version(self):
        """Verifica e exibe a versão do jogo"""
        game_exe = os.path.join(self.config['game_path'], 'PlantsVsZombiesRH.exe')
        if not os.path.exists(game_exe):
            messagebox.showwarning("Aviso", "Arquivo do jogo não encontrado!")
            return
            
        try:
            version_file = os.path.join(self.config['game_path'], '_version.txt')
            if os.path.exists(version_file):
                with open(version_file, 'r') as f:
                    version = f.read().strip()
            else:
                version = "Versão não detectada"
                
            messagebox.showinfo("Versão do Jogo", 
                              f"Versão atual do PVZ Fusion:\n\n{version}")
        except Exception as e:
            self.log(f"Erro ao verificar versão: {str(e)}")
            messagebox.showerror("Erro", "Não foi possível verificar a versão do jogo")

    def update_game_version_display(self):
        """Atualiza o botão com a versão do jogo"""
        if not self.config.get('game_path'):
            self.game_version_btn.config(text="Versão: Não configurado")
            return
            
        try:
            version_file = os.path.join(self.config['game_path'], '_version.txt')
            if os.path.exists(version_file):
                with open(version_file, 'r') as f:
                    version = f.read().strip()
                    self.game_version_btn.config(text=f"Versão: {version}")
            else:
                self.game_version_btn.config(text="Versão: Desconhecida")
        except:
            self.game_version_btn.config(text="Versão: Erro")

    def load_settings(self):
        """Carrega as configurações do usuário de settings.json"""
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as f:
                    loaded_settings = json.load(f)
                    self.settings = {**self.default_settings, **loaded_settings}
            self.save_settings()
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
                    self.config.setdefault("game_path", "")
                    self.config.setdefault("mods_path", "")
                    self.config.setdefault("last_update_check", 0)
            self.save_config()
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
            self.update_game_version_display()
            self.log(f"Caminhos configurados: {game_dir}")
            
            if not os.path.exists(mods_dir) and self.settings['auto_install_melon']:
                self.log("Pasta de mods não encontrada, instalando MelonLoader...")
                self.install_melonloader()
            
        except Exception as e:
            self.show_error("Erro ao configurar caminhos", e)

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
            
            self.log(f"Baixando versão {new_version}...")
            if not self.download_file_with_progress(download_url, zip_path):
                raise Exception("Falha no download")
            
            if self.settings['verify_hashes'] and expected_hash:
                if not self.verify_file_hash(zip_path, expected_hash):
                    raise Exception("Verificação de hash falhou - arquivo pode estar corrompido")
            
            if self.settings['create_backup']:
                self.log("Criando backup...")
                backup_path = os.path.join(os.getcwd(), f"backup_v{self.current_version}.zip")
                self.create_backup(backup_path)
            
            self.log("Instalando atualização...")
            with ZipFile(zip_path, 'r') as zip_ref:
                safe_members = [m for m in zip_ref.namelist() 
                              if not m.startswith(('__MACOSX/', '.DS_Store'))]
                zip_ref.extractall(os.getcwd(), members=safe_members)
            
            self.current_version = new_version
            self.root.title(f"PVZ Fusion Launcher v{self.current_version}")
            
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

    def process_download_queue(self):
        """Processa a fila de downloads em uma thread separada"""
        while True:
            item = self.download_queue.get()
            if item['type'] == 'update':
                self.download_and_install_update(item['url'], item['version'], item.get('hash'))
            elif item['type'] == 'melonloader':
                self.download_and_install_melonloader(item['url'])
            self.download_queue.task_done()

    def update_path_display(self):
        """Atualiza o display de caminhos"""
        if self.config.get('game_path'):
            text = f"Jogo: {self.config['game_path']}\nMods: {self.config.get('mods_path', '')}"
            self.path_info.config(text=text)
        else:
            self.path_info.config(text="Caminhos não configurados")

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

if __name__ == "__main__":
    try:
        root = tk.Tk()
        root.title("PVZ Fusion Launcher")
        app = PVZFusionLauncher(root)
        root.mainloop()
    except Exception as e:
        print(f"Erro fatal: {str(e)}")
        traceback.print_exc()
        messagebox.showerror("Erro Fatal", f"O launcher encontrou um erro:\n{str(e)}")
