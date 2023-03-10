from .disco import disco
from .sistema_arquivos import sistema_arquivos
from .usuario import usuario
import os
import hashlib


class sistema_operacional:
    def __init__(self):
        self.disco = disco(256, 4, 1, self)
        if os.path.exists('disco.txt'):
            print('Disco encontrado. Carregando...')
            self.disco.carregar('disco.txt')
        self.arquivos = sistema_arquivos(self.disco, self)
        self.usuarios = []
        self.usuario_atual = None

    def criar_usuario(self, nome: str, senha: str):
        for _usuario in self.usuarios:
            if _usuario.nome == nome:
                print("Já existe um usuário com esse nome. Tente novamente.")
                return False
        self.usuarios.append(usuario(nome, senha))
        return True

    def senha_para_hash(self, senha: str) -> str:
        return hashlib.sha256(senha.encode()).hexdigest()

    def logar(self, nome: str, senha: str):
        for _usuario in self.usuarios:
            if _usuario.nome == nome and _usuario.senha == senha:
                self.usuario_atual = _usuario
                print(senha)
                return True
        print("Usuário ou senha incorretos. Tente novamente.")
        return False

    def buscar_usuario(self, nome: str) -> usuario:
        for _usuario in self.usuarios:
            if _usuario.nome == nome:
                return _usuario
        return None

    def deslogar(self):
        self.usuario_atual = None

    def converter_caminho_para_lista(self, caminho: str) -> list:
        if caminho == '':
            return ['']
        if "/" in caminho:
            novo_caminho = []
            if caminho[0] == "/":
                novo_caminho.append('/')
            caminho = caminho.split("/")
            caminho = list(filter(None, caminho))
            novo_caminho.extend(caminho)
            caminho = novo_caminho
        else:
            caminho = [caminho]
        return caminho
