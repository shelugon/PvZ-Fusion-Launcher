import os
import shutil
from pathlib import Path

class ModManager:
    def __init__(self, game_path):
        """
        Inicializa o gerenciador de mods
        :param game_path: Caminho da instalação do jogo
        """
        self.game_path = Path(game_path) if game_path else None
        self.mods_dir = self.game_path / 'Mods' if self.game_path else None
        self.disabled_dir = self.mods_dir / '_disabled' if self.mods_dir else None

        # Cria as pastas necessárias
        self._create_dirs()

        # DLLs que devem ser ignoradas (não são mods)
        self.system_dlls = [
            'MelonLoader.dll',
            'UnityEngine.dll',
            'Assembly-CSharp.dll'
        ]

    def _create_dirs(self):
        """Cria as pastas necessárias se não existirem"""
        if self.mods_dir and not self.mods_dir.exists():
            self.mods_dir.mkdir()
        if self.disabled_dir and not self.disabled_dir.exists():
            self.disabled_dir.mkdir()

    def get_installed_mods(self):
        """
        Retorna lista de mods instalados
        :return: Lista de dicionários com {nome, ativo}
        """
        if not self.mods_dir or not self.mods_dir.exists():
            return []

        mods = []

        # Mods ativos
        for dll in self.mods_dir.glob('*.dll'):
            if dll.name not in self.system_dlls:
                mods.append({
                    'nome': dll.stem,
                    'ativo': True,
                    'arquivo': dll.name
                })

        # Mods desativados
        if self.disabled_dir and self.disabled_dir.exists():
            for dll in self.disabled_dir.glob('*.dll'):
                if dll.name not in self.system_dlls:
                    mods.append({
                        'nome': dll.stem,
                        'ativo': False,
                        'arquivo': dll.name
                    })

        return sorted(mods, key=lambda x: x['nome'].lower())

    def toggle_mod(self, mod_name, activate=True):
        """
        Ativa/desativa um mod
        :param mod_name: Nome do mod (sem extensão)
        :param activate: True para ativar, False para desativar
        :return: True se bem-sucedido
        """
        try:
            if not self.mods_dir or not self.disabled_dir:
                return False

            dll_name = f"{mod_name}.dll"
            active_path = self.mods_dir / dll_name
            disabled_path = self.disabled_dir / dll_name

            if activate:
                # Ativar: mover de _disabled para Mods
                if not disabled_path.exists():
                    return False
                shutil.move(str(disabled_path), str(active_path))
            else:
                # Desativar: mover de Mods para _disabled
                if not active_path.exists():
                    return False
                shutil.move(str(active_path), str(disabled_path))

            return True
        except Exception as e:
            print(f"Erro ao alternar mod {mod_name}: {str(e)}")
            return False

    def open_mods_folder(self):
        """Abre a pasta de mods no explorador de arquivos"""
        if self.mods_dir and self.mods_dir.exists():
            os.startfile(self.mods_dir)
            return True
        return False