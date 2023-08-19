import os
import shutil
from extrator import Read_xml
from tqdm import tqdm
import time

def pastas_por_cnpj_win(cnpj: str, all: list, xml: Read_xml, caminho: str):

    print('\n\n')
    print("MONTANDO PASTAS...")
    for i in tqdm(all):
        #time.sleep(0.01)
        Data, Chave_nota = xml.organiza_cnpj(i,cnpj)
        if(Chave_nota != '0' and Data != '0'):
            novoCaminho = caminho + '\\\\' + cnpj + '\\\\'
     
            if os.path.isdir(novoCaminho):
                if os.path.isdir(novoCaminho + Data):
                    shutil.move(i, novoCaminho + Data +'\\\\'+ Chave_nota + '.xml')
            
                else:
                    os.mkdir(novoCaminho + Data)
                    shutil.move(i, novoCaminho + Data +'\\\\'+ Chave_nota + '.xml')
            else:
                os.mkdir(novoCaminho)
                os.mkdir(novoCaminho + Data)
                shutil.move(i, novoCaminho + Data +'\\\\'+ Chave_nota + '.xml')


def pastas_por_cnpj_lx(cnpj: str, all: list, xml: Read_xml, caminho: str):
    
    print("MONTANDO PASTAS...")
    for i in tqdm(all):
        #time.sleep(0.01)
        Data, Chave_nota = xml.organiza_cnpj(i,cnpj)
        if(Chave_nota != '0' and Data != '0'):
            novoCaminho = caminho + '/' + cnpj + '/'
     
            if os.path.isdir(novoCaminho):
                if os.path.isdir(novoCaminho + Data):
                    shutil.move(i, novoCaminho + Data +'/'+ Chave_nota + '.xml')
            
                else:
                    os.mkdir(novoCaminho + Data)
                    shutil.move(i, novoCaminho + Data +'/'+ Chave_nota + '.xml')
            else:
                os.mkdir(novoCaminho)
                os.mkdir(novoCaminho + Data)
                shutil.move(i, novoCaminho + Data +'/'+ Chave_nota + '.xml')
