import subprocess
import os
import shutil
from tqdm import tqdm
from interface import recebeBase



def main():
    cwd = recebeBase()

    #cwd = os. getcwd()

    #cwd += '/Notas/'

    #arquivo = input("Nome do arquivo: ")

    #subprocess.run(['unrar', 'x', arquivo, cwd])

    diretorios = subprocess.run(["ls", cwd], stdout=subprocess.PIPE)
    stdout = diretorios.stdout
    u = stdout.decode('UTF-8')
    u = u[0:(len(u)-1)]

    diretorioParaMover = cwd +u
    diretorioPadrao = cwd +u+'/'

    p=os.listdir(diretorioPadrao)

    #Guarda a lista dos meses para depois deletar
    auxMes = p
    #print(diretorioPadrao)


    for i in tqdm(p, colour='#9400D3'):
        # i são os meses
        if '.xml' not in i: 
            mesAtual = diretorioPadrao+i
            # d são as pastas de compra e venda
            d=os.listdir(mesAtual)
        else:
            continue


        for a in tqdm(d, colour='#A020F0'):
            aux = mesAtual
            if '.xml' not in a:
                essemes = aux + '/' + a + '/'
            else:
               new_path = diretorioParaMover + '/'
               try:
                shutil.move(aux + '/' + a, new_path)
               except:
                   continue

            xml =[]
            for f in os.listdir(essemes):
                if '.xml' in f.lower():
                    xml.append(f)

            for xml in tqdm(xml, colour='#D8BFD8'):
                new_path = diretorioParaMover + '/'

                try:
                    shutil.move(essemes+xml, new_path)
                except:
                    continue
                #print('Movendo ' + xml + '\n')

            #for b in x:
                #novo = 'sudo mv ' + aux + '/' + a + '/' + 'nome_aqui' + ' ' + diretorioParaMover
                #print(x+'\n')
                #subprocess.run([novo])



if __name__ == "__main__":
    main()
