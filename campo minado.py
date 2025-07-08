# Importando bibliotecas necessárias
import random
import pickle
import tkinter as tk
from tkinter import messagebox
import time
import os

# Função para inicializar o tabuleiro do jogo com minas e células vazias
def iniciar_tabuleiro(linhas, colunas, n_minas, primeira_jogada=None):
    campo = []
    for i in range(linhas):
        linha = []
        for j in range(colunas):
            linha.append('')  # Usando um espaço para representar célula vazia
        campo.append(linha)

    minas_colocadas = 0
    while minas_colocadas < n_minas:
        linha = random.randint(0, linhas - 1)
        coluna = random.randint(0, colunas - 1)

        # Verifica se não há mina já na célula e se a célula não foi a primeira jogada
        if campo[linha][coluna] != 'M' and (primeira_jogada is None or (linha, coluna) != primeira_jogada):
            campo[linha][coluna] = 'M'  # Coloca a mina
            minas_colocadas += 1

    return campo

# Função que conta as minas vizinhas de uma célula
def minas_vizinhas(linha, coluna, campo, linhas, colunas):
    c_minas = 0
    for i in range(max(0, linha - 1), min(linhas, linha + 2)):
        for j in range(max(0, coluna - 1), min(colunas, coluna + 2)):
            if campo[i][j] == 'M':  # Se houver mina ao redor, conta
                c_minas += 1
    return c_minas

# Função que revela o conteúdo de uma célula
def revelar_celula(campo, visivel, linha, coluna):
    if campo[linha][coluna] == 'M':  # Se a célula for uma mina
        visivel[linha][coluna] = 'M'  # Marca a célula como mina
        return True
    # Se não for mina, conta as minas vizinhas
    visivel[linha][coluna] = minas_vizinhas(linha, coluna, campo, len(campo), len(campo[0]))
    return False

# Função que verifica se o jogador venceu o jogo
def verificar_vitoria(campo, visivel, linhas, colunas):
    for i in range(linhas):
        for j in range(colunas):
            # Se houver célula não revelada e não for mina, o jogo ainda não terminou
            if campo[i][j] != 'M' and visivel[i][j] == ' ':
                return False
    return True

# Função que salva o estado atual do jogo (tabuleiro e células visíveis)
def salvar_jogo(campo, visivel):
    with open('campo_minado_save.pkl', 'wb') as arquivo:
        pickle.dump((campo, visivel), arquivo)
    messagebox.showinfo("Salvar Jogo", "Jogo salvo com sucesso!")

# Função que carrega o jogo salvo, se existir
def carregar_jogo():
    try:
        with open('campo_minado_save.pkl', 'rb') as arquivo:
            return pickle.load(arquivo)  # Retorna o tabuleiro e o estado visível
    except FileNotFoundError:
        messagebox.showinfo("Carregar Jogo", "Nenhum jogo salvo encontrado.")
        return None, None

# Classe que gerencia a lógica do jogo Campo Minado e a interface gráfica
class CampoMinadoApp:
    def __init__(self, master, linhas, colunas, bombas, tela_inicial, jogador_atual):
        self.master = master
        self.jogador_atual = jogador_atual
        self.LINHAS = linhas
        self.COLUNAS = colunas
        self.inicio_tempo = None  # Tempo de início do jogo
        self.tempo_total = 0  # Tempo total de jogo
        self.BOMBAS = bombas
        self.tela_inicial = tela_inicial
        self.master.title("Campo Minado")  # Título da janela do jogo

        # Ajustando o tamanho dos botões com base no tamanho do tabuleiro
        self.button_width = max(2, int(50 / max(self.LINHAS, self.COLUNAS)))
        self.button_height = max(2, int(40 / max(self.LINHAS, self.COLUNAS)))
 
        # Aumentando o tamanho da janela conforme o tabuleiro
        self.master.geometry(f"{self.COLUNAS * 40}x{self.LINHAS * 40 + 60}")
        # Ajuste o tamanho da janela para caber o campo sem ultrapassar um limite
        MAX_LARGURA = 800  # Limite de largura
        MAX_ALTURA = 800   # Limite de altura

# Calcular o tamanho necessário para a janela
        largura = self.COLUNAS * 40
        altura = self.LINHAS * 40 + 60

# Garantir que a janela não ultrapasse o limite máximo
        largura = min(largura, MAX_LARGURA)
        altura = min(altura, MAX_ALTURA)

        self.master.geometry(f"{largura}x{altura}")
        # Inicializa as variáveis do jogo
        self.campo = None
        self.visivel = [[' ' for _ in range(self.COLUNAS)] for _ in range(self.LINHAS)]
        self.bandeiras = [[' ' for _ in range(self.COLUNAS)] for _ in range(self.LINHAS)]  # Armazena as bandeiras
        self.primeira_jogada = None
        self.botoes = [[None for _ in range(self.COLUNAS)] for _ in range(self.LINHAS)]

        # Rótulo do temporizador
        self.tempo_label = tk.Label(self.master, text="Tempo: 0s", font=("Helvetica", 14))
        self.tempo_label.grid(row=self.LINHAS, column=0, columnspan=self.COLUNAS, pady=10)

        # Criação dos botões que representam as células do tabuleiro
        for i in range(self.LINHAS):
            for j in range(self.COLUNAS):
                btn = tk.Button(self.master, text=" ", width=10, height=1, command=lambda i=i, j=j: self.revelar(i, j))
                btn.grid(row=i, column=j, padx=1, pady=1)  # Usando grid para o tabuleiro
                self.botoes[i][j] = btn
                btn.bind("<Button-3>", lambda event, i=i, j=j: self.marcar_bandeira(i, j))  # Botão direito marca uma bandeira

        # Botões para salvar e carregar o jogo
        self.salvar_button = tk.Button(self.master, text="Salvar Jogo", command=self.salvar_jogo)
        self.salvar_button.grid(row=self.LINHAS + 1, column=0, columnspan=2, pady=10)

        self.carregar_button = tk.Button(self.master, text="Carregar Jogo", command=self.carregar_jogo)
        self.carregar_button.grid(row=self.LINHAS + 1, column=2, columnspan=2, pady=10)

    # Função que atualiza o tempo na interface
    def atualizar_temporizador(self):
        if self.inicio_tempo:
            self.tempo_total = int(time.time() - self.inicio_tempo)  # Atualiza o tempo total
            self.tempo_label.config(text=f"Tempo: {self.tempo_total}s")  # Atualiza o label do tempo
        self.master.after(1000, self.atualizar_temporizador)  # Atualiza o temporizador a cada 1 segundo

    # Função que revela o conteúdo de uma célula
    def revelar(self, linha, coluna):
        # Se for a primeira jogada, inicializa o tabuleiro
        if self.primeira_jogada is None:
            self.primeira_jogada = (linha, coluna)
            self.campo = iniciar_tabuleiro(self.LINHAS, self.COLUNAS, self.BOMBAS, primeira_jogada=self.primeira_jogada)
            self.inicio_tempo = time.time()  # Inicia o temporizador
            self.atualizar_temporizador()  # Começa a atualização do temporizador

        # Impede a revelação de células marcadas com bandeira
        if self.bandeiras[linha][coluna] == 'F':
            return 

        # Se a célula for uma mina, exibe "M" e acaba o jogo
        if revelar_celula(self.campo, self.visivel, linha, coluna):
            self.botoes[linha][coluna].config(text="M", bg="red", state="disabled")
            messagebox.showinfo("Fim de jogo", "BOOM! Você pisou em uma bomba. Game Over!")
            self.revelar_bombas()  # Revela todas as minas
            self.master.after(2000, self.fechar_jogo)  # Fecha a janela após 2 segundos

        else:
            minas = self.visivel[linha][coluna]
            self.botoes[linha][coluna].config(text=str(minas), state="disabled")

        # Verifica se o jogador venceu
        if verificar_vitoria(self.campo, self.visivel, self.LINHAS, self.COLUNAS):
            self.revelar_bombas()
            messagebox.showinfo("Vitória", "Parabéns! Você venceu!")
            self.master.after(2000, self.fechar_jogo)

    # Função que revela todas as minas ao final do jogo
    def revelar_bombas(self):
        for i in range(self.LINHAS):
            for j in range(self.COLUNAS):
                if self.campo[i][j] == 'M':
                    self.botoes[i][j].config(text="M", bg="yellow", state="disabled")

    # Função que fecha a janela do jogo
    def fechar_jogo(self):
        self.master.destroy()  # Fecha a janela

    # Função que marca ou desmarca uma célula com uma bandeira
    def marcar_bandeira(self, linha, coluna):
        if self.visivel[linha][coluna] == ' ' and self.bandeiras[linha][coluna] == ' ':
            self.bandeiras[linha][coluna] = 'F'
            self.botoes[linha][coluna].config(text="F")
        elif self.bandeiras[linha][coluna] == 'F':
            self.bandeiras[linha][coluna] = ' '
            self.botoes[linha][coluna].config(text=" ")

    # Função para salvar o estado atual do jogo
    def salvar_jogo(self):
        salvar_jogo(self.campo, self.visivel)

    # Função para carregar o jogo salvo
    def carregar_jogo(self):
        campo, visivel = carregar_jogo()
        if campo is not None:
            self.campo = campo
            self.visivel = visivel
            # Atualiza a interface com o estado carregado
            for i in range(self.LINHAS):
                for j in range(self.COLUNAS):
                    texto = str(self.visivel[i][j]) if self.visivel[i][j] != ' ' else " "
                    self.botoes[i][j].config(text=texto, state="normal")
            messagebox.showinfo("Carregar Jogo", "Jogo carregado com sucesso!")
    
    def finalizar_jogo(self, vitoria=False):
        if self.inicio_tempo:
           self.tempo_total = int(time.time() - self.inicio_tempo)  # Tempo em segundos
    
        if vitoria:
           pontuacao = max(0, 1000 - self.tempo_total)  # Exemplo: Pontuação começa em 1000 e diminui com o tempo
           messagebox.showinfo("Vitória", f"Parabéns! Você venceu em {self.tempo_total} segundos!\nSua pontuação é: {pontuacao}")
        else:
           messagebox.showinfo("Fim de Jogo", f"Você perdeu! Tempo: {self.tempo_total} segundos.")
    
        self.salvar_ranking(self.jogador_atual, self.tempo_total)  # Salva o ranking
        self.revelar_bombas()  # Revela as minas
        self.master.after(2000, self.fechar_jogo)  # Fecha a janela após 2 segundos
        self.salvar_ranking(self.jogador_atual, self.tempo_total)
    
    def salvar_ranking(self, nome, tempo):
        try:
            with open(self.arquivo_ranking, 'a') as f:
                f.write(f"{nome}: {tempo} segundos\n")
        except Exception as e:
            print(f"Erro ao salvar o ranking: {e}")


class SistemaRanking:
    def __init__(self):
        self.arquivo_ranking = 'ranking.txt'
        # Cria o arquivo de ranking se ele não existir
        if not os.path.exists(self.arquivo_ranking):
            with open(self.arquivo_ranking, 'w') as f:
                pass #cria o arquivo vazio se não existir


    def exibir_ranking(self):
        try:
            with open(self.arquivo_ranking, 'r') as f:
                ranking = f.readlines()
                ranking.sort(key=lambda x: int(x.split(":")[1].split()[0]))  # Ordena pelo tempo
                ranking_texto = "".join(ranking)
                if ranking_texto == "":
                    messagebox.showinfo("Ranking", "Ainda não há dados no ranking.")
                else:
                    messagebox.showinfo("Ranking", ranking_texto)
        except FileNotFoundError:
            messagebox.showinfo("Ranking", "Ainda não há dados no ranking.")



# Adiciona sistema de cadastro usando arquivo de texto
class SistemaCadastro:
    def __init__(self, master):
        self.master = master
        self.master.title("Cadastro de Jogadores")
        self.arquivo_jogadores = 'jogadores.txt'  # Nome do arquivo para armazenar os dados dos jogadores
        self.jogador_atual = None  # Armazena o jogador logado

        # Interface do sistema de cadastro
        tk.Label(self.master, text="Nome:").grid(row=0, column=0, pady=5)
        self.entrada_nome = tk.Entry(self.master)
        self.entrada_nome.grid(row=0, column=1, pady=5)

        tk.Label(self.master, text="Senha (opcional):").grid(row=1, column=0, pady=5)
        self.entrada_senha = tk.Entry(self.master, show="*")
        self.entrada_senha.grid(row=1, column=1, pady=5)

        # Botões de ação
        tk.Button(self.master, text="Cadastrar", command=self.cadastrar).grid(row=2, column=0, pady=10)
        tk.Button(self.master, text="Entrar", command=self.entrar).grid(row=2, column=1, pady=10)
        tk.Button(self.master, text="Jogar como Convidado", command=self.jogar_convidado).grid(row=3, column=0, columnspan=2, pady=10)

    # Função para carregar os jogadores do arquivo
    def carregar_jogadores(self):
        jogadores = {}
        try:
            with open(self.arquivo_jogadores, 'r') as arquivo:
                for linha in arquivo:
                    linha = linha.strip()
                    if ':' in linha:
                        nome, senha = linha.split(':', 1)
                    else:
                        nome, senha = linha, ''  # Jogadores sem senha têm o campo de senha vazio
                    jogadores[nome] = senha
        except FileNotFoundError:
            pass
        return jogadores

    # Função para salvar os jogadores no arquivo
    def salvar_jogador(self, nome, senha):
        with open(self.arquivo_jogadores, 'a') as arquivo:
            if senha:  # Salva no formato "nome:senha" se houver senha
                arquivo.write(f"{nome}:{senha}\n")
            else:  # Salva apenas o nome se a senha estiver vazia
                arquivo.write(f"{nome}\n")

    # Função para cadastrar um novo jogador
    def cadastrar(self):
        nome = self.entrada_nome.get().strip()
        senha = self.entrada_senha.get().strip()
        jogadores = self.carregar_jogadores()

        if nome in jogadores:
            messagebox.showerror("Erro", "Jogador já cadastrado.")
            return
        if nome == "":
            messagebox.showerror("Erro", "O nome do jogador não pode ser vazio.")
            return

        self.salvar_jogador(nome, senha)
        messagebox.showinfo("Sucesso", "Jogador cadastrado com sucesso!")

    # Função para fazer login com um jogador existente
    def entrar(self):
        nome = self.entrada_nome.get().strip()
        senha = self.entrada_senha.get().strip()
        jogadores = self.carregar_jogadores()

        if nome not in jogadores:
            messagebox.showerror("Erro", "Jogador não encontrado.")
            return
        if jogadores[nome] != senha:
            messagebox.showerror("Erro", "Senha incorreta.")
            return

        self.jogador_atual = nome
        messagebox.showinfo("Bem-vindo", f"Bem-vindo, {nome}!")
        self.abrir_tela_inicial()

    # Função para jogar como convidado
    def jogar_convidado(self):
        self.jogador_atual = "Convidado"
        self.abrir_tela_inicial()

    # Função para abrir a tela inicial do jogo
    def abrir_tela_inicial(self):
        self.master.destroy()
        root = tk.Tk()
        TelaInicial(root, self.jogador_atual)
        root.mainloop()


# Atualização na Tela Inicial para receber o jogador logado
class TelaInicial:
    def __init__(self, master, jogador="Convidado"):
        self.master = master
        self.jogador = jogador
        self.master.title("Campo Minado")
        self.ranking = SistemaRanking()

        # Exibe o nome do jogador logado
        tk.Label(self.master, text=f"Jogador: {self.jogador}").grid(row=0, column=0, pady=5, columnspan=2)
        
        # Botão para exibir o ranking
        self.botao_ranking = tk.Button(self.master, text="Ranking", command=self.exibir_ranking)
        self.botao_ranking.grid(row=1, column=0, pady=5, columnspan=2)

        # Botões para iniciar o jogo em diferentes níveis de dificuldade
        self.botao_facil = tk.Button(self.master, text="Fácil (5x5, 5 minas)", command=self.jogo_facil)
        self.botao_facil.grid(row=2, column=0, pady=5, columnspan=2)

        self.botao_medio = tk.Button(self.master, text="Médio (10x10, 15 minas)", command=self.jogo_medio)
        self.botao_medio.grid(row=3, column=0, pady=5, columnspan=2)

        self.botao_dificil = tk.Button(self.master, text="Difícil (15x15, 30 minas)", command=self.jogo_dificil)
        self.botao_dificil.grid(row=4, column=0, pady=5, columnspan=2)

        # Botão para exibir o tutorial
        self.botao_tutorial = tk.Button(self.master, text="Tutorial", command=self.exibir_tutorial)
        self.botao_tutorial.grid(row=5, column=0, pady=5, columnspan=2)

    def exibir_tutorial(self):
        tutorial = ("Campo Minado - Instruções:\n\n"
                    "1. Clique com o botão esquerdo para revelar uma célula.\n"
                    "2. O objetivo é evitar as minas, revelando as células sem minas.\n"
                    "3. Use o botão direito para marcar uma célula com uma bandeira.\n"
                    "4. O jogo termina quando você revela uma mina ou vence ao revelar todas as células seguras.\n"
                    "Boa sorte!")
        messagebox.showinfo("Tutorial", tutorial)

    def exibir_ranking(self):
        self.ranking.exibir_ranking()  # Exibe o ranking

    def jogo_facil(self):
        self.abrir_tela_jogo(5, 5, 5)

    def jogo_medio(self):
        self.abrir_tela_jogo(10, 10, 15)

    def jogo_dificil(self):
        self.abrir_tela_jogo(15, 15, 30)

    # Função para abrir a tela do jogo com parâmetros corretos
    def abrir_tela_jogo(self, linhas, colunas, bombas):
        self.master.destroy()
        root = tk.Tk()
        CampoMinadoApp(root, linhas, colunas, bombas, self, self.jogador)
        root.mainloop()


# Inicializa o programa com o sistema de cadastro
if __name__ == "__main__":
    root = tk.Tk()
    SistemaCadastro(root)
    root.mainloop()

#by leleo
