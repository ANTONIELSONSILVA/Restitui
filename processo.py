#=============================PROCESSAMENTO================================
# Isolar notas de compra com mais de um combustivel (feito)
# Corrigir valor do ICMS das notas de compra compostas (feito) 
# Atribuir notas de venda para notas de compra (feito)
#   - primeiro separar as notas de compra e venda por produto (feito)
#   - fazer a comparação por datas (feito)
#---------------------------------------------------------------------------

import pandas as pd
from datetime import date, timedelta
from interface import SO, USUARIO, limpa_tela, cod_combustivel, edicao, GASOLINA_AD, GASOLINA_C, GASOLINA_P, DIESEL_S10, DIESEL_S500
from extrator import GASOLINA, DIESEL, ETANOL
import csv
from tqdm import tqdm


# Retorna a alíquota do ICMS para cada tipo de combustível 
def aliquotas(prod) -> float:
    
    if SO == 'Windows':
        with open('.\\Arquivos\\Listas\\aliquotas.csv', "r", encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            aliquotas = list(reader)
    elif SO == 'Linux':
         caminho = '/home/'+ USUARIO +'/Restitui/Arquivos/Listas/aliquotas.csv' 
         with open(caminho, "r", encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            aliquotas = list(reader)
        
    file.close()

    header = aliquotas.pop(0)

    aliquotas = pd.DataFrame(aliquotas, columns=header)

    i = 0
    while i < len(aliquotas):

        if prod.UF == aliquotas['UF'].values[i]:

            if (prod.Cod_ANP in GASOLINA) and (aliquotas['COMBUSTIVEL'].values[i] in GASOLINA):
                if prod.Data_operacao.year < 2022 and  prod.Data_operacao.year > 2016:
                    ali = aliquotas[str(prod.Data_operacao.year)].values[i]
                    return float(ali)

                elif prod.Data_operacao.year == 2022:

                    if prod.Data_operacao.month >= 6:
                        ali = aliquotas['2022.2'].values[i]
                        return float(ali)
                    else:
                        ali = aliquotas['2022.1'].values[i]
                        return float(ali)

            elif (prod.Cod_ANP in ETANOL) and (aliquotas['COMBUSTIVEL'].values[i] in ETANOL):
                if prod.Data_operacao.year < 2022 and  prod.Data_operacao.year > 2016:
                    ali = aliquotas[str(prod.Data_operacao.year)].values[i]
                    return float(ali)

                elif prod.Data_operacao.year == 2022:

                    if prod.Data_operacao.month >= 6:
                        ali = aliquotas['2022.1'].values[i]
                        return float(ali)
                    else:
                        ali = aliquotas['2022.2'].values[i]
                        return float(ali)

            elif (prod.Cod_ANP in DIESEL) and (aliquotas['COMBUSTIVEL'].values[i] in DIESEL):
                if prod.Data_operacao.year < 2022 and  prod.Data_operacao.year > 2016:
                    ali = aliquotas[str(prod.Data_operacao.year)].values[i]
                    return float(ali)

                elif prod.Data_operacao.year == 2022:

                    if prod.Data_operacao.month >= 6:
                        ali = aliquotas['2022.1'].values[i]
                        return float(ali)
                    else:
                        ali = aliquotas['2022.2'].values[i]
                        return float(ali)
        
        i += 1
       
#----------------------------Agrupa produtos de uma mesma nota-------------------------------------------

# Retorna uma lista com os produtos de uma mesma nota de compra
def  cria_lista_produtos(df: pd.DataFrame, listaChaves: list) -> list:
    listaProd = []
   
    i = 0
    j = 0
    while j < len(listaChaves):
        prod = []
        while i < len(df):
            if df['Chave_nota'].values[i] == listaChaves[j]:
                prod.append(df.loc[i]) 
                i += 1
            else: break
        j += 1
        if len(prod) > 0: listaProd.append(prod)
        

    return listaProd
            

#-------------------------------Calculo do valor correto de compra---------------------------------------
def tipo_calculo(compras: list, periodo: date, mensagem):
    i = 0
    modo1 = 0
    modo2 = 0
    
    while i < len(compras):
        j = 0
        cont1 = 0
        cont2 = 0
        etanol = 0
        while j < len(compras[i]):
            if compras[i][j].Cod_ANP not in ETANOL:
                if compras[i][j].Total_ICMS != '' and compras[i][j].Total_ICMS != '0' and compras[i][j].Total_ICMS != '0.00' :cont1 += 1
                elif compras[i][j].ICMS_BC != '': cont2 += 1
            
            if compras[i][j].Cod_ANP in ETANOL:
                etanol += 1
            
            j += 1
        
        if etanol == len(compras[i]):
            i += 1
        else:
            if cont1 + etanol == len(compras[i]): modo1 += 1
            elif cont2 + etanol == len(compras[i]): modo2 += 1
            i += 1
    
    if (modo1 != 0 and modo2 != 0) or (modo1 == 0 and modo2 == 0): raise NameError("Possibilidade de mudança de padrão, verificar periodo: ", periodo)
    elif modo1 != 0: compras = valor_correto_compras_modo1(compras, periodo)
    elif modo2 != 0: compras, mensagem = valor_correto_compras_modo2(compras, periodo, mensagem)
    
    return compras, mensagem

#-----------------------------Modo de calculo 1-------------------------------------------------------------
def valor_correto_compras_modo1(compras: list, periodo: date) -> list:

    aux = calculo_gasolina(compras, periodo)
    if len(aux) > 0: compras = aux

    compras = calculo_etanol(compras, periodo)
    compras = calculo_diesel(compras, periodo)

    return compras
    
# Calcula o icms para gasolina
def calculo_gasolina(compras: list, periodo: date) -> list:
    
    inicio = [] #notas do dia 30/31 do mês anterior ao dia 15
    final = [] #notas do dia 16 em diante

    i = 0
    while i < len(compras):
        if date.fromisoformat(str(compras[i][0].Data_operacao)) < (periodo + timedelta(days=15)) :
            inicio.append(compras[i])
        else:
            final.append(compras[i])

        i += 1

    if len(inicio) > 0:
        inicio = valor_gasolina(inicio, periodo)
    
    if len(final) > 0:
        final = valor_gasolina(final, periodo)

    aux = inicio + final

    
    return aux

# Calcula o valor da gasolina
def valor_gasolina(lista: list, periodo: date) -> list: 

    i = 0

        # ciclo para pegar o indice da primeira nota que tiver só gasolina
    while i < len(lista):   
        if só_gasolina(lista[i]): break
        i += 1
    
        #retorna vazio se a lista não tiver nota só com gasolina
    if i == len(lista): return []

        # calcula o novo valor para gasolina
    precoUnd = calculo_icms(float(lista[i][0].Total_ICMS), float(lista[i][0].Vol_total), aliquotas(lista[i][0]))
        

    # ciclo de inserção do novo valor em todas as notas que tem gasolina
    print('\n')
    print("  CALCULANDO VALOR DA GASOLINA:", periodo.month, "...")
    for i in tqdm(range(len(lista)), colour=('red')):
       
        j = 0
        while j < len(lista[i]):
            if lista[i][j].Cod_ANP in GASOLINA:
                lista[i][j].Valor_Uni_Venda = precoUnd
            j += 1

    return lista

# Verifica se a nota é só gasolina
def só_gasolina(lista: list) -> bool:
    temGasolina = 0 # contador pra quantas gasolinas tem na nota
    i = 0 
    while i < len(lista):
        if lista[i].Cod_ANP in GASOLINA:
            temGasolina += 1 
        i += 1

    # se o contador for igual ao tamanho da lista, significa q há apenas gasolina na nota    
    if temGasolina == len(lista):
        return True
    
    return False
        
# Calcula o icms e o valor para etanol        
def calculo_etanol(compras: list, periodo: date) -> list:

    print('\n')
    print("  CALCULANDO VALOR DO ETANOL: ", periodo.month, "...")

    for i in tqdm(range(len(compras)), colour=('#ff6600')):
      
        j = 0
        while j < len(compras[i]):
            
            if compras[i][j].Cod_ANP in ETANOL:
                precoUnd = float(compras[i][j].ICMS_Etanol)/ float(compras[i][j].Q_Produtos)
                compras[i][j].Valor_Uni_Venda = precoUnd
            j += 1

    return compras

# Calcula o icms para diesel
def calculo_diesel(compras: list, periodo: date) -> list:
    # ciclo principal
    print('\n')
    print('  CALCULANDO O VALOR DO DIESEL: ', periodo.month, "...")
    for i in tqdm(range(len(compras)), colour='#ff6600'):

         # verifica se tem disel na nota
        if tem_diesel(compras[i]):

            j = 0 # indice sublista
            icmsDiesel = float(compras[i][j].Total_ICMS) # icms do disel, começa recebendo o total de icms na nota
            volDiesel = float(compras[i][j].Vol_total) # quantidade total de diesel, começa recebendo a quantidade total de produto na nota

            while j < len(compras[i]):

                #traz o valor do icms do diesel e da quantidade de diesel na nota
                if compras[i][j].Cod_ANP not in DIESEL:

                    #subtrai o icms de cada produto do total de icms na nota, no final terá apenas o valor correspondente ao diesel.
                    icmsDiesel -= float(compras[i][j].Valor_Uni_Venda) * float(compras[i][j].Q_Produtos) * aliquotas(compras[i][j])

                    # subtrai a quantidade de cada produto do total de produto na nota, no final terá apenas o valor correspondente ao diesel.
                    volDiesel -= float(compras[i][j].Q_Produtos)

                j += 1
            
            compras[i] = valor_diesel(compras[i], volDiesel, icmsDiesel)
        
    return compras

# Verifica se tem diesel na nota
def tem_diesel(lista: list) -> bool:
    i = 0
    while i < len(lista):
        if lista[i].Cod_ANP in DIESEL:
            return True
        i += 1
    return False

# Calcula o valor do diesel
def valor_diesel(lista: list, quantidade: float, icms: float) -> list:
    
    i = 0
    while i < len(lista):
        if lista[i].Cod_ANP in DIESEL:
            valorDiesel = calculo_icms(icms, quantidade, aliquotas(lista[i]))
            lista[i].Valor_Uni_Venda = valorDiesel
        i += 1

    return lista

# Calcula o valor unitário do produto na nota
def calculo_icms(icmsTotal: float, volTotal: float, icmsPercent: float) -> float: 
    precoUnd = icmsTotal/(volTotal * icmsPercent)
    return precoUnd

#--------------------------------Modo de calculo 2------------------------------------
def valor_correto_compras_modo2(compras: list, perido: date, mensagem: str):

    print("\n\nCALCULANDO O VALOR CORRETO ETANOL E DIESEL: ", perido.month, "...")
    for i in tqdm(range(len(compras)), colour='#ff4500'):

        j = 0

        while j < len(compras[i]):

            if compras[i][j].Cod_ANP in ETANOL and compras[i][j].Erro != 1:
                         
                flag = 1
                try:
                    precoUnd = float(compras[i][j].ICMS_Etanol) / float(compras[i][j].Q_Produtos)
                except:
                    flag = -1
                    print('\n Nota: ', compras[i][j].Chave_nota, 'com problema')
                    sair = input("Deseja editar? Pressione ENTER para continuar, 'a' para abrir a edição ou CTRL + C para sair: ")
                    if sair == 'a': 
                        compras[i][j] = edicao(compras[i][j])
                        if compras[i][j].Erro != 1: 
                            flag = 1
                            precoUnd = float(compras[i][j].ICMS_Etanol) / float(compras[i][j].Q_Produtos)
                        else: 
                            mensagem += '\n Nota: ' + str(compras[i][j].Chave_nota) + ' com erro.'
                        
                        continue
                try:
                    ali = float(compras[i][j].Retido_Etanol) / float(compras[i][j].ICMS_Etanol)
                except:
                    flag = -1
                    print('\n Nota: ', compras[i][j].Chave_nota, 'com problema')
                    sair = input("Deseja editar? Pressione ENTER para continuar, 'a' para abrir a edição ou CTRL + C para sair: ")
                    if sair == 'a': 
                        compras[i][j] = edicao(compras[i][j])
                        if compras[i][j].Erro != 1: 
                            flag = 1
                            ali = float(compras[i][j].Retido_Etanol) / float(compras[i][j].ICMS_Etanol)
                        else: 
                            mensagem += '\n Nota: ' + str(compras[i][j].Chave_nota) + ' com erro.'

                        continue
                if flag == 1:
                    aux = confere_valor_calculado(compras[i][j], ali)

                    if aux != 1:
                        compras[i][j].Valor_Uni_Venda = precoUnd
                        compras[i][j].Aliquota = ali
                

            elif compras[i][j].Cod_ANP in DIESEL and compras[i][j].Erro != 1:

                flag = 1
                try:
                    precoUnd = float(compras[i][j].ICMS_BC) / float(compras[i][j].Q_Produtos)
                except:
                    flag = -1
                    print('\n Nota: ', compras[i][j].Chave_nota, 'com problema')
                    sair = input("Deseja editar? Pressione ENTER para continuar, 'a' para abrir a edição ou CTRL + C para sair: ")
                    if sair == 'a': 
                        compras[i][j] = edicao(compras[i][j])
                        if compras[i][j].Erro != 1: 
                            flag = 1
                            precoUnd = float(compras[i][j].ICMS_BC) / float(compras[i][j].Q_Produtos)
                        else: 
                            mensagem += '\n Nota: ' + str(compras[i][j].Chave_nota) + ' com erro.'
                        
                        continue
                try:
                    ali = float(compras[i][j].ICMS_Retido) / float(compras[i][j].ICMS_BC)
                except:
                    flag = -1
                    print('\n Nota: ', compras[i][j].Chave_nota, 'com problema')
                    sair = input("Deseja editar? Pressione ENTER para continuar, 'a' para abrir a edição ou CTRL + C para sair: ")
                    if sair == 'a': 
                        compras[i][j] = edicao(compras[i][j])
                        if compras[i][j].Erro != 1: 
                            flag = 1
                            ali = float(compras[i][j].ICMS_Retido) / float(compras[i][j].ICMS_BC)
                        else: 
                            mensagem += '\n Nota: ' + str(compras[i][j].Chave_nota) + ' com erro.'
                        
                        continue
                
                if flag == 1:
                    aux = confere_valor_calculado(compras[i][j], ali)

                    if aux != 1:
                        compras[i][j].Valor_Uni_Venda = precoUnd
                        compras[i][j].Aliquota = ali

            j += 1

    print("\nCALCULANDO O VALOR CORRETO GASOLINA: ", perido.month, "...")
    for i in tqdm(range(len(compras)), colour='#ff7f50'):

        j = 0
        qtdGas = 0.0
         
        while j < len(compras[i]):

            if compras[i][j].Cod_ANP in GASOLINA and compras[i][j].Erro != 1:
                try:
                    qtdGas += float(compras[i][j].Q_Produtos)
                except:
                    print('\n Nota: ', compras[i][j].Chave_nota, 'com problema')
                    sair = input("Deseja editar? Pressione ENTER para continuar, 'a' para abrir a edição ou CTRL + C para sair: ")
                    if sair == 'a': 
                        compras[i][j] = edicao(compras[i][j])
            j += 1

        j = 0
        while j < len(compras[i]):

            

            if compras[i][j].Cod_ANP in GASOLINA and compras[i][j].Erro != 1:
                flag = 1
                if compras[i][j].ICMS_Gasolina != '':
                    
                    flag = 1
                    try:
                        precoUnd = float(compras[i][j].ICMS_Gasolina) / qtdGas
                    except:
                        flag = -1
                        print('\n Nota: ', compras[i][j].Chave_nota, 'com problema')
                        sair = input("Deseja editar? Pressione ENTER para continuar, 'a' para abrir a edição ou CTRL + C para sair: ")
                        if sair == 'a': 
                            compras[i][j] = edicao(compras[i][j])
                            if compras[i][j].Erro != 1: 
                                flag = 1
                                precoUnd = float(compras[i][j].ICMS_Gasolina) / qtdGas
                            else: 
                                mensagem += '\n Nota: ' + str(compras[i][j].Chave_nota) + ' com erro.'
                            
                            continue
                    try:
                        ali = float(compras[i][j].ICMS_Retido) / float(compras[i][j].ICMS_Gasolina)
                    except:
                        flag = -1
                        print('\n Nota: ', compras[i][j].Chave_nota, 'com problema')
                        sair = input("Deseja editar? Pressione ENTER para continuar, 'a' para abrir a edição ou CTRL + C para sair: ")
                        if sair == 'a': 
                            compras[i][j] = edicao(compras[i][j])
                            if compras[i][j].Erro != 1: 
                                flag = 1
                                ali = float(compras[i][j].ICMS_Retido) / float(compras[i][j].ICMS_Gasolina)
                            else: 
                                mensagem += '\n Nota: ' + str(compras[i][j].Chave_nota) + ' com erro.'

                            continue
                    
                    if flag == 1:
                        aux = confere_valor_calculado(compras[i][j], ali)

                        if aux != 1:
                            compras[i][j].Valor_Uni_Venda = precoUnd
                            compras[i][j].Aliquota = ali

                else:

                    flag = 1
                    try:
                        precoUnd = float(compras[i][j].ICMS_BC) / float(compras[i][j].Q_Produtos)
                    except:
                        flag = -1
                        print('\n Nota: ', compras[i][j].Chave_nota, 'com problema')
                        sair = input("Deseja editar? Pressione ENTER para continuar, 'a' para abrir a edição ou CTRL + C para sair: ")
                        if sair == 'a': 
                            compras[i][j] = edicao(compras[i][j])
                            if compras[i][j].Erro != 1: 
                                flag = 1
                                precoUnd = float(compras[i][j].ICMS_BC) / float(compras[i][j].Q_Produtos)
                            else: 
                                mensagem += '\n Nota: ' + str(compras[i][j].Chave_nota) + ' com erro.'
                        
                            continue
                    try:
                        ali = float(compras[i][j].ICMS_Retido) / float(compras[i][j].ICMS_BC)
                    except:
                        flag = -1
                        print('\n Nota: ', compras[i][j].Chave_nota, 'com problema')
                        sair = input("Deseja editar? Pressione ENTER para continuar, 'a' para abrir a edição ou CTRL + C para sair: ")
                        if sair == 'a': 
                            compras[i][j] = edicao(compras[i][j])
                            if compras[i][j].Erro != 1: 
                                flag = 1
                                ali = float(compras[i][j].ICMS_Retido) / float(compras[i][j].ICMS_BC)
                            else: 
                                mensagem += '\n Nota: ' + str(compras[i][j].Chave_nota) + ' com erro.'
                        
                            continue
                
                    if flag == 1:
                        aux = confere_valor_calculado(compras[i][j], ali)

                        if aux != 1:
                            compras[i][j].Valor_Uni_Venda = precoUnd
                            compras[i][j].Aliquota = ali
                    
            j += 1
        
    
    i = 0
    while i < len(compras):
        j = 0
        erro = 0
        while j < len(compras[i]):
            if compras[i][j].Erro == 1:
                erro = 1 
                break
            j += 1
        
        if erro == 1: compras.pop(i)
        else: i += 1


    i = 0
    inicio = []
    final = []

    while i < len(compras):
        if date.fromisoformat(str(compras[i][0].Data_operacao)) < (perido + timedelta(days=15)) :
            inicio.append(compras[i]) 
        else:
            final.append(compras[i])          
        i += 1

    IG, aliGas = valores_quinzenais(inicio, 'GAS')
    IE, aliEt = valores_quinzenais(inicio, 'ET')
    ID, aliDis = valores_quinzenais(inicio, 'DIS')
    FG, aliGas = valores_quinzenais(final, 'GAS')
    FE, aliEt = valores_quinzenais(final, 'ET')
    FD, aliDis = valores_quinzenais(final, 'DIS')


    print("\nCONFERINDO VALORES DA PRIMEIRA QUINZENA: ", perido.month, "...")
    for i in tqdm(range(len(inicio)), colour='#ff8c00'):
        j = 0
        while j < len(inicio[i]):
            if inicio[i][j].Cod_ANP in ETANOL and float(inicio[i][j].ICMS_Etanol) == 1:
                inicio[i][j].Valor_Uni_Venda = IE
                inicio[i][j].Aliquota = aliEt

            if inicio[i][j].Cod_ANP in GASOLINA and inicio[i][j].ICMS_BC == 1:
                inicio[i][j].Valor_Uni_Venda = IG
                inicio[i][j].Aliquota = aliGas
            
            if inicio[i][j].Cod_ANP in DIESEL and inicio[i][j].ICMS_BC == 1:
                inicio[i][j].Valor_Uni_Venda = ID
                inicio[i][j].Aliquota = aliDis

            confere_valor_final(IG, IE, ID, inicio[i][j])
            j += 1
    
    print("\nCONFERINDO VALORES DA SEGUNDA QUINZENA: ", perido.month, "...")
    for i in tqdm(range(len(final)), colour='#ffa500'):
        j = 0
        while j < len(final[i]):
            if final[i][j].Cod_ANP in ETANOL and float(final[i][j].ICMS_Etanol) == 1:
                final[i][j].Valor_Uni_Venda = FE
                final[i][j].Aliquota = aliEt

            if final[i][j].Cod_ANP in GASOLINA and final[i][j].ICMS_BC == 1:
                final[i][j].Valor_Uni_Venda = FG
                final[i][j].Aliquota = aliGas
            
            if final[i][j].Cod_ANP in DIESEL and final[i][j].ICMS_BC == 1:
                final[i][j].Valor_Uni_Venda = FD
                final[i][j].Aliquota = aliDis

            confere_valor_final(FG, FE, FD, final[i][j])
            j += 1

    compras = inicio + final

    allzeroGas, allzeroaliG = valores_quinzenais(compras, 'GAS')
    allzeroEt, allzeroaliE = valores_quinzenais(compras, 'ET')
    allzeroDis, allzeroaliD = valores_quinzenais(compras, 'DIS')

    i = 0
    while i < len(compras):
        j = 0
        while j < len(compras[i]):
            if compras[i][j].Cod_ANP in ETANOL and float(compras[i][j].ICMS_Etanol) == 1:
                compras[i][j].Valor_Uni_Venda = allzeroEt
                compras[i][j].Aliquota = allzeroaliE

            if compras[i][j].Cod_ANP in GASOLINA and compras[i][j].ICMS_BC == 1:
                compras[i][j].Valor_Uni_Venda = allzeroGas
                compras[i][j].Aliquota = allzeroaliG
            
            if compras[i][j].Cod_ANP in DIESEL and compras[i][j].ICMS_BC == 1:
                compras[i][j].Valor_Uni_Venda = allzeroDis
                compras[i][j].Aliquota = allzeroaliD

            j += 1
        i += 1

             
    return compras, mensagem

def confere_valor_calculado(item, aliquota):
    
    if aliquota >= 0.30  and item.Cod_ANP not in GASOLINA:
        print('Alíquota suspeita: ', item.Chave_nota, ' Produto: ', item.nomeProd, 'Alíquota: ', aliquota)

        if item.Cod_ANP in ETANOL:
            print( 'ICMS BC: ', item.ICMS_Etanol, 'ICMS Ret: ', item.Retido_Etanol)
        
        elif item.Cod_ANP in DIESEL:
            print( 'ICMS BC: ', item.ICMS_BC, 'ICMS Ret: ', item.ICMS_Retido)

        sair = input("Pressione qualquer tecla para continuar,  'a' para editar ou 'q' para parar o processamento: ")
        if sair == 'q': quit()
        if sair == 'a': 
            edicao(item)
            return 1

    elif aliquota >= 0.30  and (item.Cod_ANP in GASOLINA and item.UF != 'GO'):
        print('Alíquota suspeita: ', item.Chave_nota, ' Produto: ', item.nomeProd, 'Alíquota: ', aliquota)

        if item.Cod_ANP in GASOLINA and item.ICMS_Gasolina != '':

            print( 'ICMS BC: ', item.ICMS_Gasolina, 'ICMS Ret: ', item.ICMS_Retido)
        elif item.Cod_ANP in GASOLINA and item.ICMS_Gasolina == '':
            print( 'ICMS BC: ', item.ICMS_BC, 'ICMS Ret: ', item.ICMS_Retido)
        
        sair = input("Pressione qualquer tecla para continuar,  'a' para editar ou 'q' para parar o processamento: ")
        if sair == 'q': quit()
        if sair == 'a': 
            edicao(item)
            return 1
    

    elif aliquota > 0.31  and item.UF == 'GO' and item.Cod_ANP in GASOLINA:
        print('Alíquota suspeita: ', item.Chave_nota, ' Produto: ', item.nomeProd, 'Alíquota: ', aliquota)

        if item.Cod_ANP in GASOLINA and item.ICMS_Gasolina != '':
            print( 'ICMS BC: ', item.ICMS_Gasolina, 'ICMS Ret: ', item.ICMS_Retido)
        else:
           print( 'ICMS BC: ', item.ICMS_BC, 'ICMS Ret: ', item.ICMS_Retido) 

        sair = input("Pressione qualquer tecla para continuar,  'a' para editar ou 'q' para parar o processamento: ")
        if sair == 'q': quit()
        if sair == 'a': 
            edicao(item)
            return 1

def valores_quinzenais(quinzena, tipoComb):
    i = 0
    valor = 0
    ali = 0
    while i < len(quinzena):
        j = 0
        while j < len(quinzena[i]):
            if tipoComb == 'GAS':
                if quinzena[i][j].Cod_ANP in GASOLINA:
                    if quinzena[i][j].ICMS_BC != 1:
                        valor = quinzena[i][j].Valor_Uni_Venda
                        ali = quinzena[i][j].Aliquota
                        
            elif tipoComb == 'ET':        
                if quinzena[i][j].Cod_ANP in ETANOL:
                    if float(quinzena[i][j].ICMS_Etanol) != 1:
                        valor = quinzena[i][j].Valor_Uni_Venda
                        ali = quinzena[i][j].Aliquota

            elif tipoComb == 'DIS':
                if quinzena[i][j].Cod_ANP in DIESEL:
                    if quinzena[i][j].ICMS_BC != 1:
                        valor = quinzena[i][j].Valor_Uni_Venda
                        ali = quinzena[i][j].Aliquota
            
            j += 1
        
        if valor != 0: break
        i += 1
    return valor, ali

def confere_valor_final(gas, et, dis, item):

    if item.Cod_ANP in GASOLINA:
        dif = gas - item.Valor_Uni_Venda
        if dif < 0: dif = dif * -1

        if dif > 0.5:
            print('A nota: ', item.Chave_nota, 'tem o valor diferente da quinzena, ', gas, '. Valor: ', item.Valor_Uni_Venda)
            sair = input("Pressione qualquer tecla para continuar, ou q para parar o processamento: ")
            if sair == 'q': quit()
       
    if item.Cod_ANP in ETANOL:

        dif = et - item.Valor_Uni_Venda
        if dif < 0: dif = dif * -1

        if dif > 0.5:
            print('A nota: ', item.Chave_nota, 'tem o valor diferente da quinzena, ', et, '. Valor: ', item.Valor_Uni_Venda)
            sair = input("Pressione qualquer tecla para continuar, ou q para parar o processamento: ")
            if sair == 'q': quit()
        
    if item.Cod_ANP in DIESEL:
        dif = dis - item.Valor_Uni_Venda
        if dif < 0: dif = dif * -1

        if dif > 0.5:
            print('A nota: ', item.Chave_nota, 'tem o valor diferente da quinzena,', dis, '. Valor: ', item.Valor_Uni_Venda)
            sair = input("Pressione qualquer tecla para continuar, ou q para parar o processamento: ")
            if sair == 'q': quit()
 
#--------------------------Cria lista de vendas----------------------------

# Retorna uma lista com as notas de venda
def cria_lista_vendas(vendas: pd.DataFrame, periodo: date) -> list:
    
    lista = []

    print('\n')
    print("  CRIANDO LISTA DE VENDAS: ", periodo.month, "...")
    for i in tqdm(range(len(vendas)), colour='#ffd700'):
              
        lista.insert(i, vendas.loc[i])
        lista[i].Valor_Uni_Venda = float(lista[i].Valor_Uni_Venda)
        
    
    return lista

#---------------------------------Cria listas para cada produto-----------------------------
# Retorna uma lista com os nomes dos combustíveis
def arq_nome_comb(lista):

    if SO == 'Windows':
        with open('.\\Arquivos\\Listas\\nomeComb.csv', "r", encoding='utf-8') as file:
           reader = csv.reader(file, delimiter=';')
           listaNomes = list(reader)
    elif SO == 'Linux':
        caminho = '/home/'+ USUARIO +'/Restitui/Arquivos/Listas/nomeComb.csv'  
        with open(caminho, "r", encoding='utf-8') as file:
           reader = csv.reader(file, delimiter=';')
           listaNomes = list(reader)

    file.close() 
    
    i = 0
    while i < len(lista):
        j = 0
        sinal =  0

        while j < len(listaNomes):

            if lista[i].nomeProd == listaNomes[j][0]:
                sinal = 1
                break

            j += 1

        if sinal != 1: listaNomes.append([lista[i].nomeProd, 0])
        
        i += 1
   
    dataNomes = pd.DataFrame(listaNomes)
    
    if SO == 'Windows': dataNomes.to_csv('.\\Arquivos\\Listas\\nomeComb.csv', index=False, header=False, sep= ';')
    elif SO == 'Linux':
        caminho = '/home/'+ USUARIO +'/Restitui/Arquivos/Listas/nomeComb.csv'  
        dataNomes.to_csv(caminho, index=False, header=False, sep= ';')

# Retorna 4 listas separadas por produtos
def separa_produtos_vendas(vendas: list, periodo: date) -> list:
    listaGasAD = []
    listaGasC = [] 
    listaGasP = []
    listaEt = [] 
    listaDis10 = []
    listaDis500 = []

    arq_nome_comb(vendas)
    cod_combustivel()

    if SO == 'Windows':
        with open('.\\Arquivos\\Listas\\nomeComb.csv', "r", encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            codigos = list(reader)
    elif SO == 'Linux':
        caminho = '/home/'+ USUARIO +'/Restitui/Arquivos/Listas/nomeComb.csv'  
        with open(caminho, "r", encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            codigos = list(reader)

    file.close() 


    print('\n')
    print("  SEPARANDO VENDAS: ", periodo.month, "...")
    for i in tqdm(range(len(vendas)), colour='#ffff00'):
        
        j = 0
        while j < len(codigos):
            if codigos[j][0] == vendas[i].nomeProd: vendas[i].Cod_ANP = codigos[j][1]
            j += 1

        if vendas[i].Cod_ANP == GASOLINA_AD: listaGasAD.append(vendas[i])

        elif vendas[i].Cod_ANP in GASOLINA_C: listaGasC.append(vendas[i])

        elif vendas[i].Cod_ANP == GASOLINA_P: listaGasP.append(vendas[i])

        elif vendas[i].Cod_ANP in ETANOL: listaEt.append(vendas[i])

        elif vendas[i].Cod_ANP == DIESEL_S10: listaDis10.append(vendas[i])

        elif vendas[i].Cod_ANP == DIESEL_S500: listaDis500.append(vendas[i])
        
        
    return listaGasAD, listaGasC, listaGasP, listaEt, listaDis10, listaDis500
   
# Retorna 4 listas separadas por produtos   
def separa_produtos_compras(compras: list, periodo: date) -> list:
    
    listaGasAD = []
    listaGasC = []
    listaGasP = []
    listaEt = []
    listaDis10 = []
    listaDis500 = []

    for i in compras:
        arq_nome_comb(i)

    cod_combustivel()

    if SO == 'Windows':
        with open('.\\Arquivos\\Listas\\nomeComb.csv', "r", encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            codigos = list(reader)
    elif SO == 'Linux':
        caminho = '/home/'+ USUARIO +'/Restitui/Arquivos/Listas/nomeComb.csv'  
        with open(caminho, "r", encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            codigos = list(reader)

    file.close()

    
    print('\n')
    print("  SEPARANDO COMPRAS: ", periodo.month, "...")
    for i in tqdm(range(len(compras)), colour='adff2f'):

        j = 0
        while j < len(compras[i]):

            k = 0
            while k < len(codigos):
                if codigos[k][0] == compras[i][j].nomeProd: compras[i][j].Cod_ANP = codigos[k][1]
                k += 1

            if compras[i][j].Cod_ANP == GASOLINA_AD: listaGasAD.append(compras[i][j])

            elif compras[i][j].Cod_ANP in GASOLINA_C: listaGasC.append(compras[i][j])

            if compras[i][j].Cod_ANP == GASOLINA_P: listaGasP.append(compras[i][j])

            elif compras[i][j].Cod_ANP in ETANOL: listaEt.append(compras[i][j])

            elif compras[i][j].Cod_ANP == DIESEL_S10: listaDis10.append(compras[i][j])

            elif compras[i][j].Cod_ANP == DIESEL_S500: listaDis500.append(compras[i][j])

            j += 1
    
    if len(listaGasAD) > 0:
        listaGasAD = ordena_compras(listaGasAD, periodo)
    if len(listaGasC) > 0:
        listaGasC = ordena_compras(listaGasC, periodo)
    if len(listaGasP) > 0:
        listaGasP = ordena_compras(listaGasP, periodo)
    if len(listaEt) > 0:
        listaEt = ordena_compras(listaEt, periodo)
    if len(listaDis10) > 0:
        listaDis10 = ordena_compras(listaDis10, periodo)
    if len(listaDis500) > 0:
        listaDis500 = ordena_compras(listaDis500, periodo)
    
    return listaGasAD, listaGasC, listaGasP, listaEt, listaDis10, listaDis500

# Retorna uma lista ordenada por datas
def ordena_compras(compras: list, periodo: date) -> list:
    df = pd.DataFrame(compras)
    df['Data_operacao'] = pd.to_datetime(df['Data_operacao']).dt.date
    df = df.sort_values(by=['Data_operacao'], ignore_index=True)

    
    lista = []

    print("  ORDENANDO COMPRAS POR DATA: ", periodo.month, "...")
    for i in tqdm(range(len(df)), colour='32cd32'):
         
        lista.insert(i, df.loc[i])
    
    return lista

#---------------------------------Agrupa listas por data-------------------------------------

# Retorna 3 listas separadas por produtos já organizadas por data
def organiza_datas(vendas: list, compras: list, periodo: date) -> list:

    listaGasADV, listaGasCV, listaGasPV, listaEtV, listaDis10V, listaDis500V = separa_produtos_vendas(vendas, periodo)
    listaGasADC, listaGasCC, listaGasPC, listaEtC, listaDis10C, listaDis500C = separa_produtos_compras(compras, periodo)

    if SO == 'Windows': d = '.\\Arquivos\\Consultas\\'
    elif SO == 'Linux': d ='/home/restitui/Restitui/Arquivos/Consultas/'

    limpa_tela()
    if len(listaGasADV) > 0 and len(listaGasADC) > 0: 
        finalGasAD = atribui_notas(listaGasADV, listaGasADC)
        Gasolina = pd.DataFrame(finalGasAD)

        Gasolina.to_csv(d + 'GasolinaAD.csv', index=False, header=False, sep=';')
      
    else: finalGasAD = []

    if len(listaGasCV) > 0 and len(listaGasCC) > 0: 
        finalGasC = atribui_notas(listaGasCV, listaGasCC)
        Gasolina = pd.DataFrame(finalGasC)
        
        Gasolina.to_csv(d + 'GasolinaC.csv', index=False, header=False, sep=';')

    else: finalGasC = []

    if len(listaGasPV) > 0 and len(listaGasPC) > 0: 
        finalGasP = atribui_notas(listaGasPV, listaGasPC)
        Gasolina = pd.DataFrame(finalGasP)
        
        Gasolina.to_csv(d + 'GasolinaP.csv', index=False, header=False, sep=';')

    else: finalGasP = []

    if len(listaEtV) > 0 and len(listaEtC) > 0: 
        finalEt = atribui_notas(listaEtV, listaEtC)
        Etanol = pd.DataFrame(finalEt)
        
        Etanol.to_csv(d + 'Etanol.csv', index=False, header=False, sep=';')

    else: finalEt = []
        
    if len(listaDis10V) > 0 and len(listaDis10C) > 0: 
        finalDis10 = atribui_notas(listaDis10V, listaDis10C)
        Diesel = pd.DataFrame(finalDis10)
        
        Diesel.to_csv(d + 'Diesel-10.csv', index=False, header=False, sep=';')

    else: finalDis10 = []

    if len(listaDis500V) > 0 and len(listaDis500C) > 0: 
        finalDis500 = atribui_notas(listaDis500V, listaDis500C)
        Diesel = pd.DataFrame(finalDis500)
        
        Diesel.to_csv(d + 'Diesel-500.csv', index=False, header=False, sep=';')

    else: finalDis500 = []

    limpa_tela()

    return finalGasAD, finalGasC, finalGasP, finalEt, finalDis10, finalDis500

# Retorna uma lista com as notas de venda e compra ordenadas por data
def atribui_notas(vendas: list, compras: list) -> list:
    final = []
    v = 0 #indice vendas
    c = 0 #indice compras

    while vendas[v].Data_operacao < compras[c].Data_operacao:
        v += 1
        if v == len(vendas): break
    
    final.append(compras[c])
    c += 1

    if v < len(vendas):
        while c < len(compras):
            print("ORGANIZANDO...")
            if v < len(vendas):
                while (vendas[v].Data_operacao >= compras[c-1].Data_operacao and 
                    vendas[v].Data_operacao < compras[c].Data_operacao):
                    final.append(vendas[v])
                    v += 1
                    if v == len(vendas): break
        
            final.append(compras[c])   
            c += 1
        
        if ((c == len(compras)) and (v < len(vendas))):
            while vendas[v].Data_operacao >= compras[c-1].Data_operacao:
                final.append(vendas[v])
                v += 1
                if v == len(vendas): break
                
        if len(final) == 1: final = []

    else: final = []
    
    return final

def emergencia(df: pd.DataFrame) -> list:
    lista = []

    for i in tqdm(range(len(df)), colour='yellow'): lista.insert(i, df.loc[i])
        
    return lista

    
     

        


            





    
