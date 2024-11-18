import random
import pickle
import tkinter as tk
from tkinter import messagebox

#Projeto Final

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
        
        if campo[linha][coluna] != 'M' and (primeira_jogada is None or (linha, coluna) != primeira_jogada):
            campo[linha][coluna] = 'M'  # Coloca a mina
            minas_colocadas += 1

    return campo

def minas_vizinhas(linha, coluna, campo, linhas, colunas):
    c_minas = 0
    for i in range(max(0, linha - 1), min(linhas, linha + 2)):
        for j in range(max(0, coluna - 1), min(colunas, coluna + 2)):
            if campo[i][j] == 'M':
                c_minas += 1
    return c_minas

def revelar_celula(campo, visivel, linha, coluna):
    if campo[linha][coluna] == 'M':
        visivel[linha][coluna] = 'M'
        return True
    visivel[linha][coluna] = minas_vizinhas(linha, coluna, campo, len(campo), len(campo[0]))
    return False

def verificar_vitoria(campo, visivel, linhas, colunas):
    for i in range(linhas):
        for j in range(colunas):
            if campo[i][j] != 'M' and visivel[i][j] == ' ':
                return False
    return True

def salvar_jogo(campo, visivel):
    with open('campo_minado_save.pkl', 'wb') as arquivo:
        pickle.dump((campo, visivel), arquivo)
    print("Jogo salvo com sucesso!")

def carregar_jogo():
    try:
        with open('campo_minado_save.pkl', 'rb') as arquivo:
            return pickle.load(arquivo)
    except FileNotFoundError:
        print("Nenhum jogo salvo encontrado.")
        return None, None

class CampoMinadoApp:
    def __init__(self, master, linhas, colunas, bombas, tela_inicial):
        self.master = master
        self.LINHAS = linhas
        self.COLUNAS = colunas
        self.BOMBAS = bombas
        self.tela_inicial = tela_inicial
        self.master.title("Campo Minado")

        # Aumentando o tamanho da janela
        self.master.geometry(f"{colunas * 50}x{linhas * 50}")  # Ajuste a largura e altura aqui

        self.campo = None
        self.visivel = [[' ' for _ in range(self.COLUNAS)] for _ in range(self.LINHAS)]
        self.primeira_jogada = None

        self.botoes = [[None for _ in range(self.COLUNAS)] for _ in range(self.LINHAS)]
        
        # Variável para armazenar as bandeiras (marcação de bombas)
        self.bandeiras = [[' ' for _ in range(self.COLUNAS)] for _ in range(self.LINHAS)]
        
        # Criando os botões e ajustando o tamanho
        for i in range(self.LINHAS):
            for j in range(self.COLUNAS):
                btn = tk.Button(self.master, text=" ", width=6, height=3,  # Aumentando os botões
                                command=lambda i=i, j=j: self.revelar(i, j))
                btn.grid(row=i, column=j, padx=2, pady=2)  # Ajustando o espaçamento entre os botões
                self.botoes[i][j] = btn
                btn.bind("<Button-3>", lambda event, i=i, j=j: self.marcar_bandeira(i, j))  # Botão direito

        self.salvar_button = tk.Button(self.master, text="Salvar Jogo", command=self.salvar_jogo)
        self.salvar_button.grid(row=self.LINHAS, column=0, columnspan=2, padx=5, pady=5)
        
        self.carregar_button = tk.Button(self.master, text="Carregar Jogo", command=self.carregar_jogo)
        self.carregar_button.grid(row=self.LINHAS, column=2, columnspan=2, padx=5, pady=5)

    def revelar(self, linha, coluna):
        if self.primeira_jogada is None:
            self.primeira_jogada = (linha, coluna)
            self.campo = iniciar_tabuleiro(self.LINHAS, self.COLUNAS, self.BOMBAS, primeira_jogada=self.primeira_jogada)

        if self.bandeiras[linha][coluna] == 'F':  # Verifica se está marcado com bandeira
            return  # Impede revelar a célula se estiver marcada

        if revelar_celula(self.campo, self.visivel, linha, coluna):
            self.botoes[linha][coluna].config(text="M", state="disabled")
            messagebox.showinfo("Fim de jogo", "BOOM! Você pisou em uma bomba. Game Over!")
            self.master.after(500, self.revelar_bombas)  # Aguarda um pouco antes de revelar as bombas
            self.master.after(1000, self.fechar_jogo)  # Aguarda para fechar a janela após revelação
        else:
            minas = self.visivel[linha][coluna]
            self.botoes[linha][coluna].config(text=str(minas), state="disabled")
            
            if verificar_vitoria(self.campo, self.visivel, self.LINHAS, self.COLUNAS):
                messagebox.showinfo("Vitória", "Parabéns! Você venceu!")
                self.master.destroy()  # Fecha o jogo
                self.tela_inicial.abrir_tela_inicial()  # Abre a tela inicial novamente

    def revelar_bombas(self):
        for i in range(self.LINHAS):
            for j in range(self.COLUNAS):
                # Revela todas as bombas
                if self.campo[i][j] == 'M' and self.visivel[i][j] != 'M':
                    self.botoes[i][j].config(text="M", state="disabled")  # Revele as bombas que ainda estão escondidas

    def fechar_jogo(self):
        self.master.destroy()  # Fecha a janela do jogo
        self.tela_inicial.abrir_tela_inicial()  # Abre a tela inicial novamente

    def marcar_bandeira(self, linha, coluna):
        if self.visivel[linha][coluna] == ' ' and self.bandeiras[linha][coluna] == ' ':
            self.bandeiras[linha][coluna] = 'F'
            self.botoes[linha][coluna].config(text="F")  # Marca com uma bandeira
        elif self.bandeiras[linha][coluna] == 'F':
            self.bandeiras[linha][coluna] = ' '  # Desmarca a bandeira
            self.botoes[linha][coluna].config(text=" ")  # Remove a bandeira

    def salvar_jogo(self):
        salvar_jogo(self.campo, self.visivel)

    def carregar_jogo(self):
        campo, visivel = carregar_jogo()
        if campo is not None:
            self.campo = campo
            self.visivel = visivel
            for i in range(self.LINHAS):
                for j in range(self.COLUNAS):
                    texto = str(self.visivel[i][j]) if self.visivel[i][j] != ' ' else " "
                    self.botoes[i][j].config(text=texto, state="normal")
            print("Jogo carregado com sucesso") #Mensagem no terminal indicando que o jogo carregou
        else:
            print("nenhum jogo salvo encontrado") #Caso não tenha nenhum jogo salvo

# Adicionando um tutorial simples
class TelaInicial:
    def __init__(self, master):
        self.master = master
        self.master.title("Escolha o Nível de Dificuldade")

        self.botao_facil = tk.Button(self.master, text="Fácil (5x5, 5 minas)", command=self.jogo_facil)
        self.botao_facil.grid(row=0, column=0, padx=10, pady=10)

        self.botao_medio = tk.Button(self.master, text="Médio (10x10, 15 minas)", command=self.jogo_medio)
        self.botao_medio.grid(row=1, column=0, padx=10, pady=10)

        self.botao_dificil = tk.Button(self.master, text="Difícil (15x15, 30 minas)", command=self.jogo_dificil)
        self.botao_dificil.grid(row=2, column=0, padx=10, pady=10)

        self.botao_tutorial = tk.Button(self.master, text="Tutorial", command=self.exibir_tutorial)
        self.botao_tutorial.grid(row=3, column=0, padx=10, pady=10)

        self.app = None

    def jogo_facil(self):
        self.abrir_tela_jogo(5, 5, 5)  # Nível Fácil

    def jogo_medio(self):
        self.abrir_tela_jogo(10, 10, 15)  # Nível Médio

    def jogo_dificil(self):
        self.abrir_tela_jogo(15, 15, 30)  # Nível Difícil

    def exibir_tutorial(self):
        tutorial = "Campo Minado - Instruções:\n\n"
        tutorial += "1. Clique com o botão esquerdo para revelar uma célula.\n"
        tutorial += "2. O objetivo é evitar as minas, revelando as células sem minas.\n"
        tutorial += "3. Use o botão direito para marcar uma célula com uma bandeira, indicando que você acha que há uma mina lá.\n"
        tutorial += "4. O jogo termina quando você revela uma mina ou vence ao revelar todas as células sem mina.\n"
        tutorial += "Boa sorte!\n\n"
        messagebox.showinfo("Tutorial", tutorial)

    def abrir_tela_jogo(self, linhas, colunas, bombas):
        self.master.destroy()  # Fecha a tela inicial
        root = tk.Tk()  # Cria uma nova instância de Tkinter para o jogo
        CampoMinadoApp(root, linhas, colunas, bombas, self)  # Cria o jogo
        root.mainloop()  # Inicia o loop do jogo

    def abrir_tela_inicial(self):
        self.master = tk.Tk()  # Recria a tela inicial
        self.__init__(self.master)
        self.master.mainloop()

# Inicia o programa
if __name__ == "__main__":
    root = tk.Tk()
    tela_inicial = TelaInicial(root)
    root.mainloop()











