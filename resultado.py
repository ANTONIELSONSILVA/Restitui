#============================RESULTADO======================================
# Calcular a diferença entre o valor de venda e o valor de compra (feito)
# Calcular o valor da restituição  (feito)
# Organizar as notas processadas para o arquivo final (feito)
# Criar um DataFrame para a formatação do arquivo final (feito)
#---------------------------------------------------------------------------
import pandas as pd
import processo as processo
from datetime import date
from pathlib import Path
from interface import SO
from tqdm import tqdm

#------------------------------------MONTA LINHAS---------------------------------
def string_num(string: str) -> str:
    string = string.replace('.', ',')

    return string
    
def monta_linha_A(cnpj: str, mesAno: str) -> list:
    
    linha = ['A',
            cnpj,
            mesAno,
            'AAAAMMDD',
            '1',
            '1',
            'NOME',
            'TELEFONE']
    return linha

def monta_linha_D(nLinha, venda, compra, diferenca, credito, debito) -> list:

    rst = 0.0

    if compra.Aliquota != '':
        rst = diferenca * float(compra.Aliquota) * float(venda.Q_Produtos)
    else:
        rst = diferenca * processo.aliquotas(compra) * float(venda.Q_Produtos)

    if rst <= 0: debito += rst
    else: credito += rst

    linha = ['D',
            nLinha, 
            venda.Chave_nota,
            venda.N_Item,
            '1', 
            venda.Cod_Prod_Interno, 
            string_num(str(venda.Valor_Uni_Venda)), 
            string_num(str(venda.Q_Produtos)), 
            compra.Chave_nota, 
            compra.N_Item, 
            compra.Cod_Prod_Interno, 
            string_num(str(compra.Valor_Uni_Venda)),
            string_num(str(diferenca)),
            rst]

    return linha, credito, debito

def monta_linha_E(df: list):
    
    topo = df.pop(0)

    soma = 0

    print('\n')
    print("SOMANDO VALORES...")
    for i in tqdm(range(len(df)), colour='#a020f0'):
        #time.sleep(0.01)
        soma += df[i][13]
        df[i][13] = string_num(str(df[i][13]))

    df.insert(0, topo)

    linha = ['E',
            len(df)-1,
            soma]

    return linha

def soma(df: list):
    soma = 0

    print('\n')
    print("SOMANDO VALORES...")
    for i in tqdm(range(len(df)), colour='#4169e1'):
        soma += df[i][13]
    
    return str(soma)

def calculo_diferenca(venda, compra):

    dif = float(venda.Valor_Uni_Venda) - float(compra.Valor_Uni_Venda)

    return dif      
        
#------------------------------------ORGANIZA AS LINHAS----------------------------

def formata_linha(data: list, lista: list, cnpj: str, qlinha: int, periodo: date, credito: float, debito: float) -> int:
    i = 0
    compra = encontra_compra(lista, i, cnpj)

    
    print('\n')
    print("MONTANDO ARQUIVO FINAL: ", periodo.month, "...")
    for i in tqdm(range(len(lista)), colour='#00bfff'):
       
        if lista[i].CNPJ_Vendedor == cnpj:
            diferenca = calculo_diferenca(lista[i], lista[compra])

            if lista[i].UF == 'DF':
                if periodo.year >= 2020:
                    qlinha += 1
                    linhaD, credito, debito = monta_linha_D(qlinha, lista[i], lista[compra], diferenca, credito, debito)
                    data.append(linhaD)

                elif diferenca < 0:
                    qlinha += 1
                    linhaD, credito, debito = monta_linha_D(qlinha, lista[i], lista[compra], diferenca, credito, debito)
                    data.append(linhaD)


            elif lista[i].UF == 'MG' or lista[i].UF == 'TO' or lista[i].UF == 'GO':
                qlinha += 1
                linhaD, credito, debito = monta_linha_D(qlinha, lista[i], lista[compra], diferenca, credito, debito)
                data.append(linhaD)
            
            else:
                qlinha += 1
                linhaD, credito, debito = monta_linha_D(qlinha, lista[i], lista[compra], diferenca, credito, debito)
                data.append(linhaD)

        else:

            compra = i


    return qlinha, credito, debito
                    
def encontra_compra(lista: list, indice: int, cnpj: str):

    while indice < len(lista):
        if(lista[indice].CNPJ_Vendedor != cnpj):
            return indice
        indice += 1  

#------------------------------------MONTA O DATAFRAME FINAL-----------------------------

def arquivo_final(cnpj: str, periodo: date, gasAD: list, gasC: list, gasP: list, et: list, dis10: list, dis500: list, credito: float, debito: float):
    
    dataFinal = []
   

    combs = []

    if periodo.month < 10: mes1 = "0" + str(periodo.month)
    else: mes1 = str(periodo.month)

    ano1 = str(periodo.year)
    novoPeriodo = ano1 + mes1
    
    dataFinal.append(monta_linha_A(cnpj, novoPeriodo))

    qlinha = 0

    dataAux = []
    if len(gasC) > 0: 
        qlinha, credito, debito = formata_linha(dataAux, gasC, cnpj, qlinha, periodo, credito, debito)
        valor = soma(dataAux)
        combs.append(string_num(valor))
        dataFinal = dataFinal + dataAux
    else:
        combs.append(-1)

    dataAux = []
    if len(gasAD) > 0: 
        qlinha, credito, debito = formata_linha(dataAux, gasAD, cnpj, qlinha, periodo, credito, debito)
        valor = soma(dataAux)
        combs.append(string_num(valor))
        dataFinal = dataFinal + dataAux
    else:
        combs.append(-1)
    
    dataAux = []
    if len(gasP) > 0: 
        qlinha, credito, debito = formata_linha(dataAux, gasP, cnpj, qlinha, periodo, credito, debito)
        valor = soma(dataAux)
        combs.append(string_num(valor))
        dataFinal = dataFinal + dataAux
    else:
        combs.append(-1)

    dataAux = []    
    if len(et) > 0: 
        qlinha, credito, debito = formata_linha(dataAux, et, cnpj, qlinha, periodo, credito, debito)
        valor = soma(dataAux)
        valor = string_num(valor)
        combs.append(valor)
        dataFinal = dataFinal + dataAux
    else:
        combs.append(-1)

    dataAux = []        
    if len(dis10) > 0: 
        qlinha, credito, debito = formata_linha(dataAux, dis10, cnpj, qlinha, periodo, credito, debito)
        valor = soma(dataAux)
        combs.append(string_num(valor))
        dataFinal = dataFinal + dataAux
    else:
        combs.append(-1)
    
    dataAux = []        
    if len(dis500) > 0: 
        qlinha, credito, debito = formata_linha(dataAux, dis500, cnpj, qlinha, periodo, credito, debito)
        valor = soma(dataAux)
        combs.append(string_num(valor))
        dataFinal = dataFinal + dataAux
    else:
        combs.append(-1)

    dataFinal.append(monta_linha_E(dataFinal))

    valorFinal = dataFinal[len(dataFinal) - 1][2]
    dataFinal[len(dataFinal) - 1][2] = string_num(str(dataFinal[len(dataFinal) - 1][2]))

    arquivo_csv(pd.DataFrame(dataFinal), ano1 + mes1, cnpj)

    return valorFinal, credito, debito, combs

def arquivo_csv(data: pd.DataFrame, periodo: str, cnpj: str):

    if SO == 'Windows': nomeArq = Path('.\\Arquivos\\Final\\' + periodo + '_' + cnpj + '_' + '0101.csv')
    elif SO == 'Linux': nomeArq = Path('/home/restitui/Restitui/Arquivos/Final/' + periodo + '_' + cnpj + '_' + '0101.csv')
    
    data.to_csv(nomeArq, index=False, header=False, sep= ';')

    
    

    