from .disco import disco
from .inode import inode
from .usuario import usuario
from . import sistema_operacional


from colorama import Fore, Style


class sistema_arquivos:
    def __init__(self, disco: disco, so: sistema_operacional):
        self.disco = disco
        self.root = inode('/', 'root', None, self.disco, apontador_blocos=None)
        if len(self.disco.bitmap_inodes) > 0:
            for _inode, bit in self.disco.bitmap_inodes.items():
                self.root = _inode
                break
        else:
            self.disco.adicionar_inode(self.root)
        self.diretorio_atual = self.root
        self.so = so
        # print(self.diretorio_atual.apontador_inodes)


    def set_root(self, _inode: inode):
        self.root = _inode
        
    def alterar_diretorio_atual(self, _inode: inode):  # PRONTA
        if _inode is None:
            return False
        self.diretorio_atual = _inode

    def procurar_inode(self, inode_destino: inode, nome: str) -> inode:  # PRONTA
        return inode_destino.get_inode(nome)

    def remover_diretorio(self, caminho: list):
        if len(caminho) == 0:
            print("rmdir: caminho vazio ou inválido")
            return False
        diretorio_a_remover = caminho[-1]
        caminho = caminho[:-1]
        diretorio_onde_remover = self.encontrar_inode(caminho)
        if diretorio_onde_remover is False:
            print("bash: rmdir: " + '/'.join(caminho) +
                  ": Diretório inexistente")
            return False
        if (filho := self.procurar_inode(diretorio_onde_remover, diretorio_a_remover)) is not None:
            if filho is not False:
                if filho.apontador_inode_pai is diretorio_onde_remover:
                    if filho.tipo != 'd':
                        print("bash: rmdir: " + '/'.join(caminho) +
                              ": Diretório inexistente")
                        return False
                    if not filho.dir_vazio():
                        print("bash: rmdir: " + '/'.join(caminho) +
                              ": Diretório não vazio")
                        return False
                    diretorio_onde_remover.remover_inode(filho)
                    return True
        print("bash: rmdir: " + '/'.join(caminho) + ": Diretório inexistente")
        return False

    def criar_inode(self, caminho: list, criador: str, tipo: str) -> inode:  # PRONTA
        if len(caminho) == 0:
            print("mkdir: caminho vazio ou inválido")
            return False
        inode_a_criar = caminho[-1]
        caminho = caminho[:-1]
        diretorio_onde_criar = self.encontrar_inode(caminho)
        if diretorio_onde_criar is False:
            print("bash: mkdir: " + '/'.join(caminho) +
                  ": Arquivo ou diretório inexistente")
            return False
        if (filho := self.procurar_inode(diretorio_onde_criar, inode_a_criar)) is not None:
            if filho is not False:
                if filho.apontador_inode_pai is diretorio_onde_criar:
                    print("bash: mkdir: " + '/'.join(caminho) +
                          ": Arquivo ou diretório já existente")
                    return False
        novo_inode = None
        if tipo == 'd':
            novo_inode = inode(inode_a_criar, criador, diretorio_onde_criar, self.disco, apontador_blocos=None)
        elif tipo == 'a':
            novo_inode = inode(inode_a_criar, criador, diretorio_onde_criar, self.disco, apontador_inodes=None)
        else:
            print("bash: mkdir: " + '/'.join(caminho) +
                  ": Tipo de inode inválido")
            return False
        diretorio_onde_criar.adicionar_inode(novo_inode)
        self.disco.adicionar_inode(novo_inode)
        return novo_inode

    def encontrar_inode(self, caminho: list) -> inode:  # PRONTA
        diretorio_inicial = self.diretorio_atual
        for diretorio in caminho:
            if diretorio == '.':
                continue
            if diretorio == '/':
                diretorio = self.root
            elif diretorio == '..':
                if self.diretorio_atual.apontador_inode_pai is None:
                    self.alterar_diretorio_atual(diretorio_inicial)
                    return False
                diretorio = self.diretorio_atual.apontador_inode_pai
            else:
                diretorio = self.procurar_inode(
                    self.diretorio_atual, diretorio)
                if diretorio is False or diretorio is None:
                    self.alterar_diretorio_atual(diretorio_inicial)
                    return False
                if diretorio.apontador_inode_pai is not self.diretorio_atual:
                    self.alterar_diretorio_atual(diretorio_inicial)
                    return False
            self.alterar_diretorio_atual(diretorio)
        inode_encontrado = self.diretorio_atual
        self.alterar_diretorio_atual(diretorio_inicial)
        return inode_encontrado

    def trocar_diretorio(self, caminho: list):  # PRONTA
        diretorio_destino = self.encontrar_inode(caminho)
        if diretorio_destino is False:
            print("bash: cd: " + '/'.join(caminho) +
                  ": Arquivo ou diretório inexistente")
            return False
        if diretorio_destino.tipo != 'd':
            print("bash: cd: " + '/'.join(caminho) + ": Não é um diretório")
            return False
        self.alterar_diretorio_atual(diretorio_destino)
        return True

    def listar_diretorio(self, usuario_atual : str, caminho: list = None) -> bool:  # PRONTA
        if caminho is None:
            caminho = ['.']
        diretorio_a_listar = self.encontrar_inode(caminho)
        if diretorio_a_listar is False:
            print("bash: ls: " + '/'.join(caminho) +
                  ": Arquivo ou diretório inexistente")
            return False
        if usuario_atual != diretorio_a_listar.dono:
            if 'r' not in diretorio_a_listar.permissao_outros:
                print("bash: ls: " + '/'.join(caminho) +
                      ": Permissão negada")
                return False
        if usuario_atual == diretorio_a_listar.dono:
            if 'r' not in diretorio_a_listar.permissao_dono:
                print("bash: ls: " + '/'.join(caminho) +
                      ": Permissão negada")
                return False
        filhos = diretorio_a_listar.listar()
        filho: inode
        for filho in filhos:
            if filho.apontador_inode_pai is not diretorio_a_listar:
                continue
            if filho.tipo == 'd':
                print(f"{Fore.BLUE}{filho.nome}{Style.RESET_ALL}")
            else:
                print(filho.nome)
        return True

    def renomear_arquivo_ou_diretorio(self, caminho: list, novo_caminho: str, usuario_atual : str): # ACREDITO QUE ESTEJA PRONTA, MAS NÃO TESTEI MUITO
        inode_a_renomear = self.encontrar_inode(caminho)
        if inode_a_renomear is False:
            print("bash: mv: " + '/'.join(caminho) +
                  ": Arquivo ou diretório inexistente")
            return False
        if inode_a_renomear.apontador_inode_pai is None:
            print("bash: mv: " + '/'.join(caminho) +
                  ": Arquivo ou diretório inexistente")
            return False
        pai_novo_nome = self.encontrar_inode(novo_caminho[:-1])
        if pai_novo_nome is False:
            print("bash: mv: " + '/'.join(caminho) +
                  ": Arquivo ou diretório inexistente")
            return False
        if inode_a_renomear.dono != usuario_atual:
            if 'w' not in inode_a_renomear.permissao_outros:
                print("bash: mv: " + '/'.join(caminho) +
                      ": Permissão negada")
                return False
        if inode_a_renomear.dono == usuario_atual:
            if 'w' not in inode_a_renomear.permissao_dono:
                print("bash: mv: " + '/'.join(caminho) +
                      ": Permissão negada")
                return False
        filho_novo_nome = self.procurar_inode(pai_novo_nome, novo_caminho[-1])
        if filho_novo_nome is not None and filho_novo_nome is not False:
            # Filho com mesmo nome já existe
            # Se filho estiver vazio, remover, senão, retornar erro
            if inode_a_renomear.apontador_inode_pai is pai_novo_nome:
                # Se o pai for o mesmo, colocar o filho_novo_nome dentro do inode_a_renomear
                inode_a_renomear.mover(filho_novo_nome, inode_a_renomear.nome)
                return True
            if filho_novo_nome.apontador_inode_pai is pai_novo_nome:
                if not filho_novo_nome.dir_vazio():
                    print("bash: mv: " + '/'.join(caminho) +
                          ": Diretório já existente")
                    return False
                else:
                    pai_novo_nome.remover_inode(filho_novo_nome)
                    self.disco.remover_inode(filho_novo_nome)
        inode_a_renomear.mover(pai_novo_nome, novo_caminho[-1])
        return True

    def remover_arquivo(self, caminho: list, usuario_atual : str): ## PRONTO?? DA UMA OLHADA JAEGER
        inode_a_remover = self.encontrar_inode(caminho)
        if inode_a_remover is False:
            print("bash: rm: " + '/'.join(caminho) +
                  ": Arquivo inexistente")
            return False
        if inode_a_remover.apontador_inode_pai is None:
            print("bash: rm: " + '/'.join(caminho) +
                  ": Arquivo inexistente")
            return False
        if inode_a_remover.tipo == 'd':
            print("bash: rm: " + '/'.join(caminho) +
                  ": Não é um arquivo")
            return False
        if inode_a_remover.dono != usuario_atual:
            if 'w' not in inode_a_remover.permissao_outros:
                print("bash: rm: " + '/'.join(caminho) +
                      ": Permissão negada")
                return False
        if inode_a_remover.dono == usuario_atual:
            if 'w' not in inode_a_remover.permissao_dono:
                print("bash: rm: " + '/'.join(caminho) +
                      ": Permissão negada")
                return False
        inode_a_remover.apontador_inode_pai.remover_inode(inode_a_remover)
        self.disco.remover_inode(inode_a_remover)
        return True


    def escrever_arquivo(self, caminho: list, conteudo: str, usuario: str):
        inode_a_escrever = self.encontrar_inode(caminho)
        if inode_a_escrever is False:
            print("bash: echo: " + '/'.join(caminho) +
                  ": Arquivo ou diretório inexistente")
            return False
        if inode_a_escrever.tipo != 'a':
            print("bash: echo: " + '/'.join(caminho) +
                  ": Não é um arquivo")
            return False        
        ## tentando algo com usuarios
        if usuario != inode_a_escrever.dono:
            if 'w' not in inode_a_escrever.permissao_outros:
                print("bash: echo: " + '/'.join(caminho) +
                      ": Permissão negada")
                return False
        if usuario == inode_a_escrever.dono:
            if 'w' not in inode_a_escrever.permissao_dono:
                print("bash: echo: " + '/'.join(caminho) +
                      ": Permissão negada")
                return False
        return inode_a_escrever.escrever(conteudo)
    
    def ler_arquivo(self, caminho: list, usuario: str):
        inode_a_ler = self.encontrar_inode(caminho)
        if inode_a_ler is False:
            print("bash: cat: " + '/'.join(caminho) +
                  ": Arquivo ou diretório inexistente")
            return False
        if inode_a_ler.tipo != 'a':
            print("bash: cat: " + '/'.join(caminho) +
                  ": Não é um arquivo")
            return False
        if usuario != inode_a_ler.dono:
            if 'r' not in inode_a_ler.permissao_outros:
                print("bash: cat: " + '/'.join(caminho) +
                      ": Permissão negada")
                return False
        if usuario == inode_a_ler.dono:
            if 'r' not in inode_a_ler.permissao_dono:
                print("bash: cat: " + '/'.join(caminho) +
                      ": Permissão negada")
                return False
        conteudo_arquivo = inode_a_ler.ler()
        if conteudo_arquivo is False or conteudo_arquivo is None:
            return False
        print(conteudo_arquivo)
        return True

    def alterar_usuario(self, caminho: list, usuario: str, usuario_atual: str):
        usuario = self.so.buscar_usuario(usuario)
        if usuario is None:
            print("bash: chown"  +
                  ": Usuário inexistente")
            return False
        inode_a_alterar = self.encontrar_inode(caminho)
        if inode_a_alterar is False:
            print("bash: chown: " + '/'.join(caminho) +
                  ": Arquivo ou diretório inexistente")
            return False
        if inode_a_alterar.apontador_inode_pai is None:
            print("bash: chown: " + '/'.join(caminho) +
                  ": Arquivo ou diretório inexistente")
            return False
        if usuario_atual != inode_a_alterar.dono:
            print("bash: chown: " + '/'.join(caminho) +
                    ": Permissão negada")
            return False
        inode_a_alterar.dono = usuario
        return True

    def alterar_permissao(self, caminho: list, permissao: str, usuario_a_alterar: str, usuario_atual: str):        
        inode_a_alterar = self.encontrar_inode(caminho)
        if inode_a_alterar is False:
            print("bash: chmod: " + '/'.join(caminho) +
                  ": Arquivo ou diretório inexistente")
            return False
        if inode_a_alterar.apontador_inode_pai is None:
            print("bash: chmod: " + '/'.join(caminho) +
                  ": Arquivo ou diretório inexistente")
            return False
        if len(permissao) > 2:
            print("bash: chmod: " + '/'.join(caminho) +
                  ": Permissão inválida")
            return False
        if usuario_atual != inode_a_alterar.dono:
            print("bash: chmod: " + '/'.join(caminho) +
                    ": Permissão negada")
            return False
        for i in permissao:
            if i not in ['r', 'w']:
                print("bash: chmod: " + '/'.join(caminho) +
                      ": Permissão inválida")
                return False
        if len(permissao) < 2:
            permissao = permissao + '-'        
        match usuario_a_alterar:
            case 'u':
                inode_a_alterar.permissao_dono = permissao
            case 'o':
                inode_a_alterar.permissao_outros = permissao
            case 'a':
                inode_a_alterar.permissao_dono = permissao
                inode_a_alterar.permissao_outros = permissao
            case _:
                print("bash: chmod: " + '/'.join(caminho) +
                        ": Usuário inválido")
                return False
        return True
        
    def adicionar_permissao(self, caminho: list, permissao: str, usuario_a_alterar: str, usuario_atual: str):
        inode_a_alterar = self.encontrar_inode(caminho)
        if inode_a_alterar is False:
            print("bash: chmod: " + '/'.join(caminho) +
                  ": Arquivo ou diretório inexistente")
            return False
        if inode_a_alterar.apontador_inode_pai is None:
            print("bash: chmod: " + '/'.join(caminho) +
                  ": Arquivo ou diretório inexistente")
            return False
        if len(permissao) > 2:
            print("bash: chmod: " + '/'.join(caminho) +
                  ": Permissão inválida")
            return False
        if usuario_atual != inode_a_alterar.dono:
            print("bash: chmod: " + '/'.join(caminho) +
                    ": Permissão negada")
            return False
        for i in permissao:
            if i not in ['r', 'w']:
                print("bash: chmod: " + '/'.join(caminho) +
                      ": Permissão inválida")
                return False
        match usuario_a_alterar:
            case 'u':
                for i in permissao:
                    if i in inode_a_alterar.permissao_dono:
                        print("bash: chmod: " + '/'.join(caminho) +
                            ": Permissão já concedida")
                        return False
                inode_a_alterar.permissao_dono = inode_a_alterar.permissao_dono.replace('-', '')
                inode_a_alterar.permissao_dono = inode_a_alterar.permissao_dono + permissao
                if len(inode_a_alterar.permissao_dono) < 2:
                    inode_a_alterar.permissao_dono = inode_a_alterar.permissao_dono + '-'
                return True
            case 'o':
                for i in permissao:
                    if i in inode_a_alterar.permissao_outros:
                        print("bash: chmod: " + '/'.join(caminho) +
                            ": Permissão já concedida")
                        return False
                inode_a_alterar.permissao_outros = inode_a_alterar.permissao_outros.replace('-', '')
                inode_a_alterar.permissao_outros = inode_a_alterar.permissao_outros + permissao
                if len(inode_a_alterar.permissao_outros) < 2:
                    inode_a_alterar.permissao_outros = inode_a_alterar.permissao_outros + '-'
                return True
            case 'a':
                for i in permissao:
                    if i in inode_a_alterar.permissao_dono and i in inode_a_alterar.permissao_outros:
                        print("bash: chmod: " + '/'.join(caminho) +
                            ": Permissão já concedida")
                        return False
                    if i in inode_a_alterar.permissao_dono:
                        inode_a_alterar.permissao_outros = inode_a_alterar.permissao_outros + i
                        return True
                    if i in inode_a_alterar.permissao_outros:
                        inode_a_alterar.permissao_dono = inode_a_alterar.permissao_dono + i
                        return True
                inode_a_alterar.permissao_dono = inode_a_alterar.permissao_dono.replace('-', '')
                inode_a_alterar.permissao_outros = inode_a_alterar.permissao_outros.replace('-', '')
                inode_a_alterar.permissao_dono = inode_a_alterar.permissao_dono + permissao
                inode_a_alterar.permissao_outros = inode_a_alterar.permissao_outros + permissao
                if len(inode_a_alterar.permissao_dono) < 2:
                    inode_a_alterar.permissao_dono = inode_a_alterar.permissao_dono + '-'
                if len(inode_a_alterar.permissao_outros) < 2:
                    inode_a_alterar.permissao_outros = inode_a_alterar.permissao_outros + '-'
                return True
            case _:
                print("bash: chmod: " + '/'.join(caminho) +
                        ": Usuário inválido")
                return False

    def remover_permissao(self, caminho: list, permissao: str, usuario_a_alterar: str, usuario_atual: str):
        inode_a_alterar = self.encontrar_inode(caminho)
        if inode_a_alterar is False:
            print("bash: chmod: " + '/'.join(caminho) +
                  ": Arquivo ou diretório inexistente")
            return False
        if inode_a_alterar.apontador_inode_pai is None:
            print("bash: chmod: " + '/'.join(caminho) +
                  ": Arquivo ou diretório inexistente")
            return False
        if len(permissao) > 2:
            print("bash: chmod: " + '/'.join(caminho) +
                  ": Permissão inválida")
            return False
        if usuario_atual != inode_a_alterar.dono:
            print("bash: chmod: " + '/'.join(caminho) +
                    ": Permissão negada")
            return False
        for i in permissao:
            if i not in ['r', 'w']:
                print("bash: chmod: " + '/'.join(caminho) +
                      ": Permissão inválida")
                return False
        match usuario_a_alterar:
            case 'u':
                for i in permissao:
                    if i not in inode_a_alterar.permissao_dono:
                        print("bash: chmod: " + '/'.join(caminho) +
                            ": Permissão já negada")
                        return False
                if len(permissao) == 1:
                    inode_a_alterar.permissao_dono = inode_a_alterar.permissao_dono.replace(permissao, '-')
                elif len(permissao) == 2:
                    inode_a_alterar.permissao_dono = inode_a_alterar.permissao_dono.replace(permissao, '--')
                return True
            case 'o':
                for i in permissao:
                    if i not in inode_a_alterar.permissao_outros:
                        print("bash: chmod: " + '/'.join(caminho) +
                            ": Permissão já negada")
                        return False
                if len(permissao) == 1:
                    inode_a_alterar.permissao_outros = inode_a_alterar.permissao_outros.replace(permissao, '-')
                elif len(permissao) == 2:
                    inode_a_alterar.permissao_outros = inode_a_alterar.permissao_outros.replace(permissao, '--')
                return True
            case 'a':
                for i in permissao:
                    if i not in inode_a_alterar.permissao_dono and i not in inode_a_alterar.permissao_outros:
                        print("bash: chmod: " + '/'.join(caminho) +
                            ": Permissão já negada")
                        return False
                    if i not in inode_a_alterar.permissao_dono:
                        inode_a_alterar.permissao_outros = inode_a_alterar.permissao_outros.replace(i, '-')
                        return True
                    if i not in inode_a_alterar.permissao_outros:
                        inode_a_alterar.permissao_dono = inode_a_alterar.permissao_dono.replace(i, '-')
                        return True
                if len(permissao) == 1:
                    inode_a_alterar.permissao_dono = inode_a_alterar.permissao_dono.replace(permissao, '-')
                    inode_a_alterar.permissao_outros = inode_a_alterar.permissao_outros.replace(permissao, '-')
                elif len(permissao) == 2:
                    inode_a_alterar.permissao_dono = inode_a_alterar.permissao_dono.replace(permissao, '--')
                    inode_a_alterar.permissao_outros = inode_a_alterar.permissao_outros.replace(permissao, '--')
                return True
            case _:
                print("bash: chmod: " + '/'.join(caminho) +
                        ": Usuário inválido")
                return False

    def listar_permissoes_arquivo(self, caminho: list, usuario_atual: str):
        inode_a_listar = self.encontrar_inode(caminho)
        if inode_a_listar is False:
            print("bash: ls: " + '/'.join(caminho) +
                  ": Arquivo ou diretório inexistente")
            return False
        if inode_a_listar.tipo == 'a':
            print('-'+inode_a_listar.permissao_dono, inode_a_listar.permissao_outros, inode_a_listar.dono, '/'.join(caminho)) 
            return True
        elif inode_a_listar.tipo == 'd':
            if inode_a_listar.dono != usuario_atual:
                if 'r' not in inode_a_listar.permissao_outros:
                    print("bash: ls: " + '/'.join(caminho) +
                        ": Permissão negada")
                    return False
            if inode_a_listar.dono == usuario_atual:
                if 'r' not in inode_a_listar.permissao_dono:
                    print("bash: ls: " + '/'.join(caminho) +
                        ": Permissão negada")
                    return False
            ## mostrar permissões dos arquivos dentro do diretório
            filhos = inode_a_listar.listar()
            print('d'+inode_a_listar.permissao_dono, inode_a_listar.permissao_outros, inode_a_listar.dono, '/'.join(caminho))
            for i in filhos:
                if i.apontador_inode_pai is not inode_a_listar:
                    continue
                if i.tipo == 'a':
                    print('-'+i.permissao_dono, i.permissao_outros, i.dono, '/'.join(caminho)+'/'+i.nome)
                elif i.tipo == 'd':
                    print('d'+i.permissao_dono, i.permissao_outros, i.dono, '/'.join(caminho)+'/'+i.nome)
            return True

    def copiar_arquivo(self, caminho: list, novo_caminho: list, usuario_atual : str): ## está duplicando o conteúdo do arquivo... pq?
        inode_a_copiar = self.encontrar_inode(caminho)
        if inode_a_copiar is False:
            print("bash: cp: " + '/'.join(caminho) +
                  ": Arquivo ou diretório inexistente")
            return False
        if inode_a_copiar.tipo != 'a':
            print("bash: cp: " + '/'.join(caminho) +
                  ": Não é um arquivo")
            return False
        if inode_a_copiar.dono != usuario_atual:
            if 'w' not in inode_a_copiar.permissao_outros:
                print("bash: cp: " + '/'.join(caminho) +
                    ": Permissão negada")
                return False
        if inode_a_copiar.dono == usuario_atual:
            if 'w' not in inode_a_copiar.permissao_dono:
                print("bash: cp: " + '/'.join(caminho) +
                    ": Permissão negada")
                return False
        inode_copia = self.criar_inode(novo_caminho, self.so.usuario_atual, 'a')
        inode_copia.escrever(inode_a_copiar.ler())
        return True