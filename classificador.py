from sklearn.feature_extraction.text import TfidfVectorizer
from datetime import datetime, timedelta
from collections import Counter 
from math import exp
import pandas as pd
import xml.dom.minidom
import colored
import csv

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

def buildCorpus():
    # lendo arquivos xml
    uolTree = xml.dom.minidom.parse('uol.xml').documentElement
    g1Tree = xml.dom.minidom.parse('g1.xml').documentElement
    metropolesTree = xml.dom.minidom.parse('metropoles.xml').documentElement
    gNewsTree = xml.dom.minidom.parse('gnews.xml').documentElement

    corpus = []
    noticia = ''

    # adicionando notícias do Uol
    items = uolTree.getElementsByTagName("item")

    for item in items:
        noticia = getText(item.getElementsByTagName('titulo')[0].childNodes) + ' - ' + getText(item.getElementsByTagName('corpo')[0].childNodes)
        corpus.append(noticia)

    # adicionando notícias do G1
    items = g1Tree.getElementsByTagName("item")

    for item in items:
        noticia = getText(item.getElementsByTagName('titulo')[0].childNodes) + ' - ' + getText(item.getElementsByTagName('corpo')[0].childNodes)
        corpus.append(noticia)

    # adicionando notícias do Metropoles
    items = metropolesTree.getElementsByTagName("item")

    for item in items:
        noticia = getText(item.getElementsByTagName('titulo')[0].childNodes) + ' - ' + getText(item.getElementsByTagName('corpo')[0].childNodes)
        corpus.append(noticia)

    # adicionando notícias do google news
    items = gNewsTree.getElementsByTagName("item")

    for item in items:
        noticia = getText(item.getElementsByTagName('titulo')[0].childNodes) + ' - ' + getText(item.getElementsByTagName('corpo')[0].childNodes)
        corpus.append(noticia)
    
    return corpus

# criando corpus com todas as notícias
corpus = buildCorpus()

# lista de stop words
with open("stopwords.txt", encoding='utf-8') as file:
    stopwords = file.read().splitlines()

class Sessao:
    def __init__(self):
        self.historico = []
        self.timestamps = []

    def adicionar(self, indice):
        # adicionando notícia e registrando instante de leitura
        self.historico.append(corpus[indice])
        self.timestamps.append(datetime.now())

        print(colored.fg('blue') + 'Você leu: ', [indice], corpus[indice][:140], '...', colored.attr(0))

    
    def comparar(self, indice):
        print('\nVocê pretende ler: ', [indice], corpus[indice][:131], '...')
        temp = self.historico[0:len(self.historico)]
        temp.append(corpus[indice]) # juntando histórico com a notícia a ser comparada para fazer o TF-IDF

        # deletando notícias lidas há mais de uma semana
        for i in reversed(range(len(temp) - 1)): 
            if (datetime.now() - self.timestamps[i]) > timedelta(days=7):
                del self.historico[i:0]
                del self.timestamps[i:0]
                break

        # iniciando variáveis de comparação
        sumarios = []
        mesmoAssunto = []
        vetContagem = [0] * 11
        num = 0

        # gerando TF-IDF do histórico + notícia a ser comparada
        vectorizer = TfidfVectorizer(stop_words=stopwords)
        tfidf = vectorizer.fit_transform(temp).toarray()

        # gerando sumarização do histórico + notícia a ser comparada
        for i in tfidf:
            df = pd.DataFrame(i, index=vectorizer.get_feature_names(), columns=["TF-IDF"])
            df = df[(df.T != 0).any()]
            df = df.sort_values('TF-IDF', ascending=False)
            sumarios.append(df.index[:11].values)
        
        for i in reversed(range(len(sumarios) - 1)):           
            cont = 0
            for j in range(len(sumarios[i])): # criando subconjunto de notícias do mesmo assunto da notícia a ser lida
                if sumarios[-1][j] in sumarios[i]:
                    cont = cont + 1
                if cont >= 2:
                    mesmoAssunto.extend(sumarios[i])
                    break

        # calculando coincidências entre o sumário da notícia a ser comparada e o subconjunto
        for i in range(len(sumarios[-1])): 
            vetContagem[i] = vetContagem[i] + Counter(mesmoAssunto)[sumarios[-1][i]]

        print(sumarios[-1][:11])
        print(vetContagem)

        # calculando similaridade
        for i in range(len(vetContagem)):
            num = num + vetContagem[-i]/(i+1)
        if num > 2:
            print(colored.fg('light_gray') + 'Você já leu uma notícia similar a esta' + colored.attr(0))
        elif num > 1.5 and num < 2:
            print(colored.fg('yellow') + 'Esta notícia pode ter informações novas para você' + colored.attr(0))
        elif num < 1.5:
            print(colored.fg('green') + 'Não há nada parecido com essa notícia em seu histórico' + colored.attr(0))
                
      
def print_menu():       # menu de navegação
    choice =True      
    nav = Navegacao()
  
    while choice:          ## While loop which will keep going until loop = False
        print("\n" + 31 * "-" , "MENU" , 31 * "-")
        print("1. Ler")
        print("2. Comparar")
        print("3. Histórico pronto")
        print("0. Sair")
        print(69 * "-", "\n")
    
        choice = input("Escolha uma opção: ")
        
        if choice == '1':     
            indice = int(input("\nEscolha uma notícia para adicionar [0~148]: "))
            nav.adicionar(indice)
        elif choice == '2':
            indice = int(input("\nEscolha uma notícia para comparar [0~148]: "))
            nav.comparar(indice)
        elif choice == '3':
            historico = [76, 146, 61, 148, 116, 133, 1, 19, 136, 29, 38, 23, 90, 137, 83, 36, 101, 84, 2, 30, 49, 57, 5, 147, 11, 135, 108, 18, 37, 62]
            for i in historico:
                nav.comparar(i)
                nav.adicionar(i)
        elif choice == '0':
            print("\nOK. Encerrando...")
            choice = False # This will make the while loop to end as not value of loop is set to False
        else:
            # Any integer inputs other than values 1-5 we print an error message
            print("Opção incorreta...")

print_menu()