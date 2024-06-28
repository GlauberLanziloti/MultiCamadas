# coding: utf-8
from __future__ import division
from cmath import e
import os
from matplotlib.widgets import Slider, Button, RadioButtons
import scipy.integrate as si
import numpy as np
import matplotlib.pyplot as plt
import shutil
import csv
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog


class Amostra:

    def __init__(self, nome, er, ei, ur, ui, d, zin):
        self.nome = nome  # nome arquivo
        self.er = er
        self.ei = ei
        self.ur = ur
        self.ui = ui
        self.d = d  # Espessura
        self.zin = zin  # impedância


# ﻿from __future__ import division
# from matplotlib.ticker import MultipleLocator


# -----------------Mudar Diretorio-------------------
# Armazenar local pasta
local = os.getcwd()
# Pasta: dados_exp
os.chdir('./dados_e_u')

# -----------------Grafico Tamanho------------------
# tamanho do plot
x = 7
y = 7
# fonte dos eixos x e y
fonte = 15

# pular pontos
skip_point = 30


# # <font color = red>Cuidado com a Sequência das amostras!!! Lembre-se que a amostra encostada na placa deverá ser sempre a PRIMEIRA (índice = 0)</font>

# In[4]:

print(f'********************************************************************')
print('Plotagem em Multicamadas')
print(f'********************************************************************\n')

# Listar arquivos CSV na pasta


arq_csv = []

for arquivo in os.listdir('.'):
    if arquivo.endswith('.csv'):
        arq_csv.append(arquivo)

# Dicionário para armazenar as espessuras associadas aos nomes de arquivo
espamostra = {}

# Processar cada arquivo CSV
for csv_file_name in arq_csv:
    print('Arquivo Entrada:', csv_file_name)

    # Ler valores do cabeçalho do arquivo CSV
    with open(csv_file_name, 'r') as csv_file:
        arq = open(csv_file_name, 'r')
        ler = arq.readlines()
        freqini = ler[15]
        freqini = float(freqini[0:15])
        freqfinal = ler[1615]
        freqfinal = float(freqfinal[0:15])
        espessura = float(ler[10][19:27])
        print('Espessura da amostra: %.2f' % espessura)

        # Armazenar a espessura no dicionário usando o nome do arquivo como chave
        espamostra[csv_file_name] = espessura

    # Escrever arquivo TXT a partir do arquivo CSV
    txt_file_name = os.path.splitext(csv_file_name)[0] + ".txt"
    with open(csv_file_name, 'r') as csv_file:
        with open(txt_file_name, 'w') as txt_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                txt_file.write(',\t'.join(row) + '\n')

    print(f'Arquivo TXT gerado: {txt_file_name}')
    print(f'Frequencia inicial: {freqini}\n')
    print(f'--------------------------------------------------------------------\n')

# --------------Nome.txt-------------
input("Pressione Enter para continuar...\n ")

TXT = [None, None, None]

# Com este programa você ordena a sequência das Layers

print('OBS: SENTIDO DE ANÁLISE, INICIA-SE NA PLACA!!!')
print('Exemplo: temos 3 multilayer:\n amostra da Placa = 0\n amostra do meio = 1\n Primeira amostra = 2')

for arquivo in os.listdir('.'):
    extensao = arquivo[len(arquivo) - 4:]
    if extensao == '.txt':
        numero = int(
            input("Qual sequência você deseja para a amostra %s?: " % (arquivo)))
        TXT[numero] = arquivo

# Criando os Objetos e Colocando-os dentro de um Array
samples = []

for arquivo in TXT:
    if arquivo is None:
        break

    # Obtendo a espessura correspondente ao nome do arquivo do dicionário espamostra
    D = espamostra.get(arquivo.replace('.txt', '.csv'), 0) * 1e-3

    samples.append(Amostra(arquivo[:-4], [], [], [], [], D, []))


# plt.text(15, -10, 'texte')


# ------------------Parâmetros do Guia-------------

if freqini >= 8 and freqfinal <= 12.4:
    print("Banda X")
    banda = 1
if freqini >= 12.4 and freqfinal <= 18:
    print("Banda Ku")
    banda = 2
if freqini >= 18 and freqfinal <= 26:
    print("Banda K")
    banda = 3
if freqini >= 26 and freqfinal <= 40:
    print("Banda Ka")
    banda = 4


# BANDA-X
if banda == 1:
    a = 22.86e-3  # [m] Base maior do guia de onda (X-Band)
    offset = 9.76e-3  # Espessura do 1/4 de lambda (X- Band)
    Comp_offset = 9.76
    freq_corte = 6.56e9  # [Hz] Frequência de Corte (X-Band)
    espessura = 0.0


# BANDA-Ku
if banda == 2:

    a = 15.80e-3  # [m] Bas onda (Ke maior do guia deu-Band)
    offset = 6.50e-3  # Espessura do 1/4 de lambda (Ku- Band)
    Comp_offset = 6.5
    freq_corte = 9.49e9  # [Hz] Frequência de Corte (Ku-Band)
    espessura = 0.0


# L1 = offset -d1 -d2 -d3 -d4... #depende de quantas amostras
dL = 0  # [m] Plano de referência porta 2


# Propriedades:
c = 2.998e8  # [m/s] Velocidade da luz
u0 = 4*np.pi*1e-7  # Permeabilidade do vácuo
onda_cut = c/freq_corte  # [m] lambda de corte


# # Organizar Dados $\epsilon$ e $\mu$

F = []  # frequencia [Hz] DE CALCULO
F_grafic = []  # FREQUENCIA PARA PLOTAR EM [GHz]

ler1_col = 1  # er
ler2_col = 2  # ei
ler3_col = 3  # ur
ler4_col = 4  # ui


# # Abrindo o Arquivo e colocando os dados dentro dos OBJETOS
#
# # <CUIDADO COM A FREQUÊNCIA!!!! ALGUNS ARQUIVOS JÁ VEM EM GHz


try:
    for n in range(0, len(TXT)):

        arq = open("./"+TXT[n], 'r')
        ler = arq.readlines()
        arq.close()

        er = []
        ei = []
        ur = []
        ui = []

        # for i in range(0,len(ler)): # ***** começa no 1 por causa do título *****
        for i in range(15, len(ler)-1):

            dados = ler[i].split(',')

            if n == 0:

                # Frequência
                f = float(dados[0])*1e9
                # f = float(dados[0])
                F.append(f)
                F_grafic.append(f/1e9)

            # e and u
            er.append(float(dados[ler1_col]))  # real

            ei.append(float(dados[ler2_col]))  # imag

            ur.append(float(dados[ler3_col]))  # real

            ui.append(float(dados[ler4_col]))  # imag

        samples[n].er = er
        samples[n].ei = ei
        samples[n].ur = ur
        samples[n].ui = ui
except FileNotFoundError:
    pass


def quantidade(n):  # n = len(samples)
    if n == 1:
        L1 = offset - samples[0].d - dL
    elif n == 2:
        L1 = offset - samples[0].d - samples[1].d - dL
    elif n == 3:
        L1 = offset - samples[0].d - samples[1].d - samples[2].d - dL
    elif n == 4:
        L1 = offset - samples[0].d - samples[1].d - \
            samples[2].d - samples[3].d - dL
    return L1


# Executar já
L1 = quantidade(len(samples))

S11 = []


i = 0

for n in range(0, len(samples)):

    while i < 1601:

        f = F[i]

        e1 = samples[n].er[i] - 1j*samples[n].ei[i]
        u1 = samples[n].ur[i] - 1j*samples[n].ui[i]
        d1 = samples[n].d
        # Impedância caracteristica (n)
        # 50 Ohm do cabo/guia
        zo = 50
        zn1 = zo*(u1/e1)**0.5

        e2 = samples[n+1].er[i] - 1j*samples[n+1].ei[i]
        u2 = samples[n+1].ur[i] - 1j*samples[n+1].ui[i]
        d2 = samples[n+1].d
        zn2 = zo*(u2/e2)**0.5

        e3 = samples[n+2].er[i] - 1j*samples[n+2].ei[i]
        u3 = samples[n+2].ur[i] - 1j*samples[n+2].ui[i]
        d3 = samples[n+2].d
        zn3 = zo*(u3/e3)**0.5

        # Cálculo
        zin1 = zn1*np.tanh((2j*np.pi*d1*f/c)*((u1*e1)**(1.0/2.0)))
        zin2 = zn2*(zin1 + zn2*np.tanh(2j*np.pi*f*d2/c*np.sqrt(u2*e2))) / \
            (zn2 + zin1*np.tanh(2j*np.pi*f*d2/c*np.sqrt(u2*e2)))
        zin3 = zn3*(zin2 + zn3*np.tanh(2j*np.pi*f*d3/c*np.sqrt(u3*e3))) / \
            (zn3 + zin2*np.tanh(2j*np.pi*f*d3/c*np.sqrt(u3*e3)))

        # DE LINEAR MAG PARA DB...
        # Coeficiente de Reflexão
        r = (zin3-zo)/(zin3+zo)
        # Linear Mag
        s11 = abs(r)
        # Log Mag
        db = 20*np.log10(s11)

        S11.append(db)

        i += 1

    break


# Testar Gráfico: Refletividade Multicamadas


# ------------------------GRAFICO 1 - Reflection Loss (RL)-----------------------
# ax1=plt.subplot(111)
plt.subplots_adjust(left=0.1, bottom=0.3)
k, = plt.plot(F_grafic, S11, 'r-', label="%s+%s+%s+Placa" %
              (samples[2].nome, samples[1].nome, samples[0].nome), alpha=0.4)

T = plt.title("Espessura total da amostra = %.2fmm" %
              ((samples[0].d+samples[1].d+samples[2].d)*1000))
plt.xlabel('Frequency(GHz)')
plt.ylabel("Reflection Loss (dB)")

# plt.ylim(0,1.1) #LINEAR
plt.ylim(-50, 0)  # dB

# plt.xlim(8.2,12.4)


plt.legend()
plt.grid(True)


# ---------------------------------------barra interativa----------------------------------------------
axcolor = (0.5, 0.7, 0.7)

di = 0e-3
df = 9.8e-3

# Amostra Colada na Placa
# (pos(x da barra),pos(y da barra),comprimento,largura)
d1_ = plt.axes([0.15, 0.15, 0.25, 0.03], facecolor=axcolor)
d1bar = Slider(d1_, 'Camada Placa (m)', di, df,
               valinit=samples[0].d, valfmt='%.2e')

# Amostra no Meio
# (pos(x da barra),pos(y da barra),comprimento,largura)
d2_ = plt.axes([0.15, 0.10, 0.25, 0.03], facecolor=axcolor)
d2bar = Slider(d2_, "Camada Meio (m)", di, df,
               valinit=samples[1].d, valfmt='%.2e')

# Amostra da frente
# (pos(x da barra),pos(y da barra),comprimento,largura)
d3_ = plt.axes([0.15, 0.05, 0.25, 0.03], facecolor=axcolor)
d3bar = Slider(d3_, "Camada Frente (m)", di, df,
               valinit=samples[2].d, valfmt='%.2e')


# -------------------------------------------------------------------------------------------------------


def update(val):  # este val nao tem nada a ver com ...

    # atualizar o valor

    samples[0].d = d1bar.val

    samples[1].d = d2bar.val

    samples[2].d = d3bar.val

    L1 = quantidade(len(samples))
    global S11
    S11 = []

    i = 0

    for n in range(0, len(samples)):

        while i < 1601:

            f = F[i]

            e1 = samples[n].er[i] - 1j*samples[n].ei[i]
            u1 = samples[n].ur[i] - 1j*samples[n].ui[i]
            d1 = samples[n].d
            # Impedância caracteristica (n)
            # 50 Ohm do cabo/guia
            zo = 50
            zn1 = zo*(u1/e1)**0.5

            e2 = samples[n+1].er[i] - 1j*samples[n+1].ei[i]
            u2 = samples[n+1].ur[i] - 1j*samples[n+1].ui[i]
            d2 = samples[n+1].d
            zn2 = zo*(u2/e2)**0.5

            e3 = samples[n+2].er[i] - 1j*samples[n+2].ei[i]
            u3 = samples[n+2].ur[i] - 1j*samples[n+2].ui[i]
            d3 = samples[n+2].d
            zn3 = zo*(u3/e3)**0.5

            # Cálculo
            zin1 = zn1*np.tanh((2j*np.pi*d1*f/c)*((u1*e1)**(1.0/2.0)))
            zin2 = zn2*(zin1 + zn2*np.tanh(2j*np.pi*f*d2/c*np.sqrt(u2*e2))) / \
                (zn2 + zin1*np.tanh(2j*np.pi*f*d2/c*np.sqrt(u2*e2)))
            zin3 = zn3*(zin2 + zn3*np.tanh(2j*np.pi*f*d3/c*np.sqrt(u3*e3))) / \
                (zn3 + zin2*np.tanh(2j*np.pi*f*d3/c*np.sqrt(u3*e3)))

            # DE LINEAR MAG PARA DB...
            # Coeficiente de Reflexão
            r = (zin3-zo)/(zin3+zo)
            # Linear Mag
            s11 = abs(r)
            # Log Mag
            db = 20*np.log10(s11)

            S11.append(db)

            i += 1

        break

    espessura = float((samples[0].d+samples[1].d+samples[2].d)*1000)

    if espessura > Comp_offset:
        # print("Vc execedeu o offset")
        T.set_text(
            "Espessura total da amostra = %.2fmm (Excedeu o limite)" % (espessura))
    else:
        T.set_text("Espessura total da amostra = %.2fmm" % (espessura))

    # Atualizar Gráfico
    k.set_ydata(S11)
    # T.set_text("Espessura total = %.2fmm (Excedeu o limite)" % (espessura))

    # Alterar Gráfico
    plt.draw()


d1bar.on_changed(update)
d2bar.on_changed(update)
d3bar.on_changed(update)


# Botão Save----------------------------------------------------------
savex = plt.axes([0.5, 0.15, 0.1, 0.04])
buttonsave = Button(savex, 'Savar dados', color=axcolor, hovercolor='0.975')


def save(event):
    analisar_local = os.getcwd()

    if analisar_local == local:
        pass
    else:
        os.chdir(local)
    os.chdir("./Calculados_gravados")

    espessura = float((samples[0].d+samples[1].d+samples[2].d)*1000)
    convert_espessura = round(espessura, 2)
    placa = float(d1bar.val)
    convert_placa = round(placa, 6)
    meio = float(d2bar.val)
    convert_meio = round(meio, 6)
    frente = float(d3bar.val)
    convert_frente = round(frente, 6)

    new = open("./%s_%s_%s.txt" %
               (samples[2].nome, samples[1].nome, samples[0].nome), 'w')
    new.write("Sequência\t" + str(convert_placa) + "\t" +
              str(convert_meio) + "\t" + str(convert_frente))
    new.write("\nEspessura(MM)\t" + str(convert_espessura))
    new.write("\nFreq(GHz)\tRL\n")

    for i in range(0, len(F)):
        escrever = "%f \t %f\n" % (float(F_grafic[i]), float(S11[i]))
        new.write(escrever)
    new.close()
    print("Gravado...")


buttonsave.on_clicked(save)


# Barra Resete--------------------------------------------------------

resetax = plt.axes([0.8, 0.15, 0.1, 0.04])
button = Button(resetax, 'Reiniciar', color=axcolor, hovercolor='0.975')


def reset(event):
    d1bar.reset()
    d2bar.reset()
    d3bar.reset()


button.on_clicked(reset)

print(os.getcwd())

# Plotar grafico com menos pontos ---------------------------------------------------

resetax = plt.axes([0.6, 0.10, 0.3, 0.04])
button_menos_potos = Button(
    resetax, 'Grafico com menos pontos', color=axcolor, hovercolor='0.975')


def menos_pontos(event):
    def set_g():
        global g
        g = float(entry.get())
        root.destroy()

# Criar janela principal Tkinter
    root = tk.Tk()
    root.title("Insira o número de pontos desejado")
    root.geometry("400x400")
    label1 = tk.Label(root, text="O número posto abaixo resultará na quantidade de pontos no gráfico")
    
    label1.pack(pady=20)
    

# Criar caixa de entrada
    entry = tk.Entry(root)
    entry.pack(pady=50)

# Botão para confirmar e fechar a janela
    confirm_button = tk.Button(root, text="Confirmar", command=set_g)
    confirm_button.pack()

# Loop principal da aplicação
    root.mainloop()

    analisar_local = os.getcwd()

    if analisar_local == local:
        pass
    else:
        os.chdir(local)
    os.chdir("./Calculados_gravados")

    espessura = float((samples[0].d+samples[1].d+samples[2].d)*1000)
    convert_espessura = round(espessura, 2)
    placa = float(d1bar.val)
    convert_placa = round(placa, 6)
    meio = float(d2bar.val)
    convert_meio = round(meio, 6)
    frente = float(d3bar.val)
    convert_frente = round(frente, 6)

    new = open("./%s_%s_%s.txt" %
               (samples[2].nome, samples[1].nome, samples[0].nome), 'w')
    new.write("Sequência\t" + str(convert_placa) + "\t" +
              str(convert_meio) + "\t" + str(convert_frente))
    new.write("\nEspessura(mm)\t" + str(convert_espessura))
    new.write("\nFreq(GHz)\tRL\n")

    for i in range(0, len(F)):
        escrever = "%f \t %f\n" % (float(F_grafic[i]), float(S11[i]))
        new.write(escrever)
    new.close()
    print("Gravado...")

    diretorio = os.getcwd()  # Pega o diretório atual
    num = diretorio.rfind("\\") + 1  # Acha onde tem a ultima "\"
    os.chdir(diretorio[:num])  # Volta o diretório

    pasta = "Calculados_gravados"  # Nome da pasta onde os arquivos .txt estão

# Listar os arquivos na pasta
    arquivos = [arquivo_botao for arquivo_botao in os.listdir(
        pasta) if arquivo_botao.endswith(".txt")]
    e = 1600/g

    for arquivo_botao in arquivos:
        with open(os.path.join(pasta, arquivo_botao), "r") as f, open("saida.txt", "w") as arqs:
            i = 0
            c = 0

            for _ in range(8):
                f.readline()  # Skip the next line

            while True:
                x = f.readline().strip()
                y = f.readline().strip()
                if not x or not y:
                    break
                c += 1
                if c % e == 0:
                    arqs.write(f"{x}\n{y}\n")

# Move o arquivo "saida.txt" para a pasta "Calculados_gravados"
    shutil.move("saida.txt", os.path.join(pasta, "saida.txt"))


# Verifique se a pasta "Calculados_gravados" existe------------------------------------------------------------
    if not os.path.exists("Calculados_gravados"):
        print("A pasta 'Calculados_gravados' não existe.")
    else:
        # Caminho completo para o arquivo--------------------------------------------------------------------------
        arquivo_botao = os.path.join("Calculados_gravados", "saida.txt")

# Verifique se o arquivo existe---------------------------------------------------------------------------
    if not os.path.exists(arquivo_botao):
        print("O arquivo 'saida.txt' não existe na pasta 'Calculados_gravados'.")
    else:

        # Inicialize listas para armazenar os dados----------------------------------------------------------------
        x = []
        y = []

# Leitura do arquivo-----------------------------------
        with open(arquivo_botao, 'r') as file:
            for line in file:

                # Suponha que cada linha do arquivo tenha dois números separados por espaço----------------------------------
                dados = line.strip().split()
                if len(dados) == 2:
                    x.append(float(dados[0]))
                    y.append(float(dados[1]))

# Verifique se há dados para plotar-------------------------------------------------------------------------------------
            if x and y:
                # Crie o gráfico-----------------------------------------------------------------------------------------
                plt.figure()
                plt.plot(x, y, 'o-')
                plt.xlabel('Frequência (GHz)')
                plt.ylabel('Refletion Loss (dB)')
                plt.title("Espessura total = %.2fmm" %
                          ((samples[0].d+samples[1].d+samples[2].d)*1000))
                plt.show()
            else:
                print("Não foram encontrados dados válidos no arquivo 'saida.txt'.")


button_menos_potos.on_clicked(menos_pontos)
# ---------------------------------------------------------------------

plt.show()

# %%
