from colorama import Fore, Style

from classes.sistema_operacional import sistema_operacional

'''# main.py
# sistema de arquivos baseado em inodes
# assumir q o disco rígido tem 256mb de espaço
# disco tem blocos de tamanho fixo, 4kb de tamanho cada
# i-node: metainformações do arquivo
# 1. nome do arquivo
# 2. criador do arquivo
# 3. dono do arquivo
# 4. tamanho do arquivo
# 5. data de criação
# 6. data de modificação
# 7. permissões de acesso (dono e outros usuários - leitura, escrita, execução)
# 8. apontadores para blocos
# 9. apontador para eventual outro i-node
# 10. apontador para i-node pai
# # 11. apontador para i-node de diretório
# # 12. apontador para i-node de arquivo
# parte do armazenamento do disco é reservada para armazenar as informações de gerenciamento, controle sobre quais blocos estão sendo usados e quais estão livres
# 1. bitmap de blocos livres
# 2. bitmap de blocos ocupados
# 3. bitmap de i-nodes livres
# 4. bitmap de i-nodes ocupados
# import datetime'''

so = sistema_operacional()

def criar_usuario():
    print("criar usuário")
    print("usuário: ", end="")
    usuario = input()
    print("senha: ", end="")
    senha = input()
    so.criar_usuario(usuario, senha)
    
def logar():
    print("logar")
    print("usuário: ", end="")
    usuario = input()
    print("senha: ", end="")
    senha = input()
    o =so.logar(usuario, senha)
    if o == True:
        print("logado")
    else:
        print("não logado")
        criar_ou_logar()
def criar_ou_logar():
    print("1. criar usuário")
    print("2. logar")
    print("3. sair")
    opcao = input()
    if opcao == "1":
        criar_usuario()
        criar_ou_logar()
    elif opcao == "2":
        logar()
    elif opcao == "3":
        exit()
    else:
        print("opção inválida")
        criar_ou_logar()

def main():
    criar_ou_logar()
    while (comando := input(f"{Fore.GREEN}{so.usuario_atual}{Style.RESET_ALL}:{Fore.BLUE}~{so.arquivos.diretorio_atual}{Style.RESET_ALL}$ ")) != "sair" and so.usuario_atual is not None:
        comando = comando.split(" ")
        comando = list(filter(None, comando))
        match comando[0]:
            case "sair_usuario":
                so.deslogar()
                criar_ou_logar()
            case "chmod":
                try:
                    if len(comando) == 1:
                        print("chmod: falta operando")
                        print("Tente 'chmod --help' para mais informações.")
                    if len(comando) > 1:
                        if "=" in comando[1]:
                            caminho_lista = so.converter_caminho_para_lista(comando[2])
                            permissao = comando[1].split("=")[1]
                            usuario_a_alterar = comando[1].split("=")[0]
                            if usuario_a_alterar == '':
                                usuario_a_alterar = 'a'
                            so.arquivos.alterar_permissao(caminho_lista, permissao, usuario_a_alterar, so.usuario_atual)
                        if "+" in comando[1]:
                            caminho_lista = so.converter_caminho_para_lista(comando[2])
                            permissao = comando[1].split("+")[1]
                            usuario_a_alterar = comando[1].split("+")[0]
                            if usuario_a_alterar == '':
                                usuario_a_alterar = 'a'
                            so.arquivos.adicionar_permissao(caminho_lista, permissao, usuario_a_alterar, so.usuario_atual)
                        if "-" in comando[1]:
                            caminho_lista = so.converter_caminho_para_lista(comando[2])
                            permissao = comando[1].split("-")[1]
                            usuario_a_alterar = comando[1].split("-")[0]
                            if usuario_a_alterar == '':
                                usuario_a_alterar = 'a'
                            so.arquivos.remover_permissao(caminho_lista, permissao, usuario_a_alterar, so.usuario_atual)
                        
                except Exception as e:
                    print(e)
            case "chown":
                try:
                    if len(comando) == 1:
                        print("chown: falta operando")
                        print("Tente 'chown --help' para mais informações.")
                    else:
                        caminho_lista = so.converter_caminho_para_lista(comando[1])
                        usuario_permitido = comando[2]
                        so.arquivos.alterar_usuario(caminho_lista, usuario_permitido, so.usuario_atual)
                except Exception as e:
                    print(e)
            case "salvar":
                so.disco.para_texto()
            case "touch":
                try:
                    if len(comando) == 1:
                        print("touch: falta operando")
                        print("Tente 'touch --help' para mais informações.")
                    else:
                        for diretorio in comando[1:]:
                            caminho_lista = so.converter_caminho_para_lista(diretorio)
                            so.arquivos.criar_inode(caminho_lista, so.usuario_atual, "a")
                except Exception as e:
                    print(e)
                    print("erro ao criar diretório")
                    print("uso: touch <nome>")
            case "rm":
                try:
                    if len(comando) == 1:
                        print("rm: falta operando")
                        print("Tente 'rm --help' para mais informações.")
                    else:
                        for diretorio in comando[1:]:
                            caminho_lista = so.converter_caminho_para_lista(diretorio)
                            so.arquivos.remover_arquivo(caminho_lista)

                except Exception as e:
                    print(e)
                    print("erro ao remover arquivo")
                    print("uso: rm <nome>")
            case "echo":
                # try:
                if len(comando) == 1:
                    print("echo: falta operando")
                    print("Tente 'echo --help' para mais informações.")
                if len(comando) > 1:
                    if ">>" in comando:
                        i = comando.index(">>")
                        if i > 1:
                            # texto está entre 1 e i
                            if comando[1][0] == comando[i-1][-1] == '"':
                                texto = ''
                                for j in range(1, i):
                                    texto += comando[j] + ' '
                                caminho = comando[i+1]
                                conteudo = texto.rstrip()
                                conteudo = conteudo.strip('"')
                                caminho_lista = so.converter_caminho_para_lista(caminho)
                                so.arquivos.escrever_arquivo(caminho_lista, conteudo, so.usuario_atual)
                    else:
                        print(' '.join(comando[1:]))
                # except Exception as e:
                #     print(e)
                #     print("erro ao escrever no arquivo")
                #     print("uso: echo \"<conteudo>\" >> <nome>")
            case "cat":
                try:
                    if len(comando) == 1:
                        print("cat: falta operando")
                        print("Tente 'cat --help' para mais informações.")
                    else:
                        for diretorio in comando[1:]:
                            caminho_lista = so.converter_caminho_para_lista(diretorio)
                            so.arquivos.ler_arquivo(caminho_lista, so.usuario_atual)
                except Exception as e:
                    print(e)
                    print("erro ao ler arquivo")
                    print("uso: cat <nome>")
            case "cp":
                try:
                    if len(comando) <=2:
                        if len(comando) == 1:
                            print("cp: falta operando arquivo de origem.")
                        if len(comando) == 2:
                            print(f"cp: falta operando arquivo cópia de destino após '{comando[1]}'.")
                    else:
                        caminho_antigo = so.converter_caminho_para_lista(comando[1])
                        caminho_copiado = so.converter_caminho_para_lista(comando[2])
                        so.arquivos.copiar_arquivo(caminho_antigo, caminho_copiado)
                except Exception as e:
                    print(e)
                    print("erro ao copiar arquivo")
                    print("uso: cp <nome> <novo_nome>")
            case "mv":
                # try:
                if len(comando) <= 2:
                    if len(comando) == 1:
                        print("mv: falta o operando arquivo")
                    elif len(comando) == 2:
                        print(f"mv: falta o operando arquivo de destino após '{comando[1]}'")
                else:
                    destino = comando.pop(-1)
                    destino = so.converter_caminho_para_lista(destino)
                    for diretorio in comando[1:]:
                        origem = so.converter_caminho_para_lista(diretorio)
                        so.arquivos.renomear_arquivo_ou_diretorio(origem, destino)
                        
                # so.arquivos.renomear_arquivo_ou_diretorio(comando[1], comando[2])
                # except Exception as e:
                #     print(e)
                #     print("erro ao renomear arquivo")
                #     print("uso: mv <nome> <novo_nome>")
            case "mkdir": # PRONTO
                try:
                    if len(comando) == 1:
                        print("mkdir: falta operando")
                        print("Tente 'mkdir --help' para mais informações.")
                    else:
                        for diretorio in comando[1:]:
                            caminho_lista = so.converter_caminho_para_lista(diretorio)
                            so.arquivos.criar_inode(caminho_lista, so.usuario_atual, "d")
                except Exception as e:
                    print(e)
                    print("erro ao criar diretório")
                    print("uso: mkdir <nome>")
            case "ls": # PRONTO
                try:
                    if len(comando) == 1:
                        so.arquivos.listar_diretorio()
                        for diretorio in comando[1:]:
                            caminho_lista = so.converter_caminho_para_lista(diretorio)
                            so.arquivos.listar_diretorio(caminho_lista)
                    if len(comando) > 1:
                        if comando[1] == "-l":
                                if comando[2].startswith("/"):
                                    caminho_lista = so.converter_caminho_para_lista(comando[2])
                                    so.arquivos.listar_permissoes_arquivo(caminho_lista)
                                if comando[2] == '':
                                    raise Exception
                                if comando[2].startswith("/") == False:
                                    caminho = so.converter_caminho_para_lista(comando[2])
                                    so.arquivos.listar_permissoes_arquivo(caminho)


                except Exception as e:
                    print(e)
                    print("erro ao listar diretório")
                    print("uso: ls")
            case "rmdir": # PRONTO
                try:
                    if len(comando) == 1:
                        print("rmdir: falta operando")
                        print("Tente 'rmdir --help' para mais informações.")
                    else:
                        for diretorio in comando[1:]:
                            caminho_lista = so.converter_caminho_para_lista(diretorio)
                            so.arquivos.remover_diretorio(caminho_lista)
                except Exception as e:
                    print(e)
                    print("erro ao remover diretório")
                    print("uso: rmdir <nome>")
            case "cd": # PRONTO
                try:
                    if len(comando) == 1:
                        so.arquivos.trocar_diretorio(['/'])
                    elif len(comando) == 2:
                        caminho = so.converter_caminho_para_lista(comando[1])
                        so.arquivos.trocar_diretorio(caminho)
                    else:
                        print("cd: número excessivo de argumentos")
                except Exception as e:
                    print("erro ao trocar diretório")
                    print("uso: cd <nome>")
            case _:
                print("comando não encontrado")


if __name__ == "__main__":
    main()
