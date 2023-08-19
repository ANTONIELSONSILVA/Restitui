from datetime import timedelta
from diretorios import *
from resultado import arquivo_final
from extrator import *
from interface import *
from processo import cria_lista_produtos, tipo_calculo, cria_lista_vendas, organiza_datas, valor_correto_compras_modo2
import time
from tqdm import tqdm
from pathlib import Path



# Gerencia a extração, o processamento e a geração do arquivo final, 
# retornando os valores totais de venda, compra e restituição atualizados
def menu(xml, all, CNPJ_Informado, Periodo_Informado: date, totalVendas, totalCompras, totalRestituido, mensagem, credito, debito):
    
    # Inicia as listas vazias.
    compras = []
    vendas = []
    chaves = []
    chaveVendas = []
    chaveCompras = []
    
    
    # Filtra os campos de todos os arquivos na base de dados
    print("\nEXTRAINDO ARQUIVOS PERIODO: ", Periodo_Informado.month, "...") 
    for i in tqdm(all, colour=('red')):
        if 'CANCELADO' not in i:
            dp = xml.exclui_duplicatas(i, chaves)
            if dp == 1:
               mensagem += xml.nfe_data(i, compras, vendas, chaveVendas, chaveCompras, CNPJ_Informado)
            
             
    if len(vendas) == 0:
        mensagem += " Não foram encontradas notas de venda no mês " + str(Periodo_Informado.month) + '\n'
        totalVendas += len(chaveVendas)
        totalCompras += len(chaveCompras)
        totalRestituido += 0.0
        credito += 0.0
        debito += 0.0
        combs = [-1, -1, -1, -1, -1, -1]

        return totalVendas, totalCompras, totalRestituido, mensagem, credito, debito, combs
    
    elif len(compras) == 0:
        mensagem += " Não foram encontradas notas de compra no mês " +  str(Periodo_Informado.month) + '\n'
        totalVendas += len(chaveVendas)
        totalCompras += len(chaveCompras)
        totalRestituido += 0.0
        credito += 0.0
        debito += 0.0
        combs = [-1, -1, -1, -1, -1, -1]
    
        return totalVendas, totalCompras, totalRestituido, mensagem, credito, debito, combs
     
        #Transforma as listas em DataFrames
    compras = Read_xml.DataFrameCompra(compras)
    vendas = Read_xml.DataFrameVendas(vendas)

    # Converte as datas no DataFrame para o formato date do python
    compras['Data_operacao'] = pd.to_datetime(compras['Data_operacao']).dt.date
    vendas['Data_operacao'] = pd.to_datetime(vendas['Data_operacao']).dt.date

    # Organiza os dataframes por data em ordem crescente
    vendas = vendas.sort_values(by=['Data_operacao'], ignore_index=True)
    
    if SO == 'Linux':
        #LINUX
        caminho = '/home/'+ USUARIO +'/Restitui/Arquivos/Consultas/compras.csv' 
        compras.to_csv(caminho, sep= ';')

        caminho = '/home/'+ USUARIO +'/Restitui/Arquivos/Consultas/vendas.csv'
        vendas.to_csv(caminho, sep= ';')
    elif SO == 'Windows':
        compras.to_csv(".\\Arquivos\\Consultas\\compras.csv", sep= ';')
        vendas.to_csv(".\\Arquivos\\Consultas\\vendas.csv", sep= ';')


    listaCompras = cria_lista_produtos(compras, chaveCompras)    
    listaCompras, mensagem = tipo_calculo(listaCompras, Periodo_Informado, mensagem)
    
    listaVendas = cria_lista_vendas(vendas, Periodo_Informado)

    compras = pd.DataFrame(listaCompras)
    
    vendas = pd.DataFrame(listaVendas)

    
    if SO == 'Linux':
        #LINUX
        caminho = '/home/'+ USUARIO +'/Restitui/Arquivos/Consultas/ListaCompras.csv' 
        compras.to_csv(caminho,  sep= ';')

        caminho = '/home/'+ USUARIO +'/Restitui/Arquivos/Consultas/ListaVendas.csv' 
        vendas.to_csv(caminho, sep= ';')
    elif SO == 'Windows':
        compras.to_csv(".\\Arquivos\\Consultas\\ListaCompras.csv",  sep= ';')
        vendas.to_csv(".\\Arquivos\\Consultas\\ListaVendas.csv", sep= ';')

    
    listaGasAD, listaGasC, listaGasP, listaEt, listaDis10, listaDis500 = organiza_datas(listaVendas, listaCompras, Periodo_Informado)
    valorFinal, credito, debito, combs = arquivo_final(CNPJ_Informado, Periodo_Informado, listaGasAD, listaGasC, listaGasP, listaEt, listaDis10, listaDis500, credito, debito)

    #print("----------------------------------------------------------------------------------")
    #imprimeResultado(Periodo_Informado, (fim-inicio), len(chaveVendas), len(chaveCompras), valorFinal, totalLinhas)

    
    totalVendas += len(chaveVendas)
    totalCompras += len(chaveCompras)
    totalRestituido += valorFinal
    

    return totalVendas, totalCompras, totalRestituido, mensagem, credito, debito, combs

# Cria 12 listas equivalentes aos meses do ano e organiza as notas de 1 ano dentro de 12 meses, 
# retornando uma lista com 12 listas
def pre_processo(xml, all, ano, cnpj, mensagem):
    jan = [] 
    fev = []
    mar = []
    abr = []
    mai = []
    jun = []
    jul = []
    ago = []
    sep = []
    out = []
    nov = []
    dez = []

    nome = ''
    erro = ''
    
    print('\n')
    print("ORGANIZANDO ARQUIVOS...")
   
    for i in tqdm(range(len(all))):
        try:
            root = ET.parse(all[i]).getroot()
        except:
            erro += "\nO arquivo: " + all[i] + " está com problemas"
            
            continue

        nsNFE = {'ns': "http://www.portalfiscal.inf.br/nfe"}
        cnpjNota = xml.check_none(root.find("./ns:NFe/ns:infNFe/ns:emit/ns:CNPJ", nsNFE))
        data  = xml.check_none(root.find("./ns:NFe/ns:infNFe/ns:ide/ns:dhEmi", nsNFE))

        data = data[:10]
        try:
            data = date.fromisoformat(data)
        except:
            erro += "\nO arquivo: " + all[i] + " está com problemas"
            
            continue

        if cnpjNota == cnpj:
            nome = xml.check_none(root.find("./ns:NFe/ns:infNFe/ns:emit/ns:xNome", nsNFE))
        else:
            cnpjNota = xml.check_none(root.find("./ns:NFe/ns:infNFe/ns:dest/ns:CNPJ", nsNFE))
            if cnpjNota == cnpj:
                nome = xml.check_none(root.find("./ns:NFe/ns:infNFe/ns:dest/ns:xNome", nsNFE))


        if data.year == ano:
            
            if cnpjNota != cnpj:
                if ((data + timedelta(days=1)) == (date(year= ano, month=1, day=1))) or (data.month == 1):
                    jan.append(all[i])
            elif data.month == 1:
                jan.append(all[i])

            if cnpjNota != cnpj:
               if ((data + timedelta(days=1)) == (date(year= ano, month=2, day=1))) or (data.month == 2):
                    fev.append(all[i])
            elif data.month == 2:
                fev.append(all[i])
            
            if cnpjNota != cnpj:
                if ((data + timedelta(days=1)) == (date(year= ano, month=3, day=1))) or (data.month == 3):
                    mar.append(all[i])
            elif data.month == 3:
                mar.append(all[i])
            
            if cnpjNota != cnpj:
                if ((data + timedelta(days=1)) == (date(year= ano, month=4, day=1))) or (data.month == 4):
                    abr.append(all[i])
            elif data.month == 4:
                abr.append(all[i])
            
            if cnpjNota != cnpj:
                if ((data + timedelta(days=1)) == (date(year= ano, month=5, day=1))) or (data.month == 5):
                    mai.append(all[i])
            elif data.month == 5:
                mai.append(all[i])
            
            if cnpjNota != cnpj:
                if ((data + timedelta(days=1)) == (date(year= ano, month=6, day=1))) or (data.month == 6):
                    jun.append(all[i])
            elif data.month == 6:
                jun.append(all[i])

            if cnpjNota != cnpj:
                if ((data + timedelta(days=1)) == (date(year= ano, month=7, day=1))) or (data.month == 7):
                    jul.append(all[i])
            elif data.month == 7:
                jul.append(all[i])
            
            if cnpjNota != cnpj:
                if ((data + timedelta(days=1)) == (date(year= ano, month=8, day=1))) or (data.month == 8):
                    ago.append(all[i])
            elif data.month == 8:
                ago.append(all[i])
            
            if cnpjNota != cnpj:
                if ((data + timedelta(days=1)) == (date(year= ano, month=9, day=1))) or (data.month == 9):
                    sep.append(all[i])
            elif data.month == 9:
                sep.append(all[i])
            
            if cnpjNota != cnpj:            
                if ((data + timedelta(days=1)) == (date(year= ano, month=10, day=1))) or (data.month == 10):
                    out.append(all[i])
            elif data.month == 10:
                out.append(all[i])
            
            if cnpjNota != cnpj:            
                if ((data + timedelta(days=1)) == (date(year= ano, month=11, day=1))) or (data.month == 11):
                    nov.append(all[i])
            elif data.month == 11:
                nov.append(all[i])
            
            if cnpjNota != cnpj:            
                if ((data + timedelta(days=1)) == (date(year= ano, month=12, day=1))) or (data.month == 12):
                    dez.append(all[i])
            elif data.month == 12:
                dez.append(all[i])
            
        
    full = [jan, fev, mar, abr, mai, jun, jul, ago, sep, out, nov, dez]

    
    mensagem += erro
    return full, nome, mensagem


def main():

    inicio = time.time()

    limpa_tela()

    flag = modo_operacao()

    while flag == 1:
        caminho = recebeBase()
        xml = Read_xml.getBase(caminho)
        CNPJ_Informado = verificarCNPJ()
        all = xml.all_files()

        if SO == 'Windows': pastas_por_cnpj_win(CNPJ_Informado, all, xml, caminho)
        elif SO == 'Linux': pastas_por_cnpj_lx(CNPJ_Informado, all, xml, caminho)

        fim = time.time()
        print("\nDuração processamento do CNPJ", CNPJ_Informado, ":", timedelta(seconds=(round((fim - inicio), 0))))
        
        limpa_tela()

        flag = modo_operacao()

    else:

        limpa_tela()

        if flag == 2: 

            totalVendas = 0
            totalCompras = 0
            totalRestituido = 0.0
            mensagem = ''
            credito = 0.0
            debito = 0.0
            rstCombs = []


            logo ()
            xml = recebeBase()
            xml = Read_xml.getBase(xml)
            CNPJ_Informado = verificarCNPJ()
            ano = recebe_ano()

            all = xml.all_files()
            totalArquivos = len(all)
            arqRest = len(all)
            
            limpa_tela()

            lista = []

            lista, nome, mensagem = pre_processo(xml, all, ano, CNPJ_Informado, mensagem)

            i = 0
            while i < len(lista):
                if len(lista[i]) > 0:
                    periodo = date(year=ano, month=i+1, day=1)
                    totalVendas, totalCompras, totalRestituido, mensagem, credito, debito, combs = menu(xml, lista[i], CNPJ_Informado, periodo, totalVendas, totalCompras, totalRestituido, mensagem, credito, debito)
                    arqRest -= len(lista[i])
                    rstCombs.append(combs)

                    limpa_tela()

                else:
                    rstCombs.append([-1, -1, -1, -1, -1, -1])
                    mensagem += 'Não foram encontradas notas no mês'+  str(i+1) + '\n' 

                i+= 1        

            fim = time.time()

            
            
            limpa_tela()

            logo ()
            print("\n\nDuração processamento: ", timedelta(seconds=(round((fim - inicio), 0))))
            print("Total de notas de compras: ", totalCompras)
            print("Total de notas de vendas: ",totalVendas)
            print("Total de notas : ", (totalVendas+totalCompras))
            print("Total de arquivos : ", totalArquivos)
            print("Valor total a ser restituído: ", round((totalRestituido), 2))
            print("Crédito: ", round((credito), 2))
            print("Débito: ", round((debito), 2))

           
            data_atual = date.today()

            txt = ['Processado em: ', str(data_atual), "\n", nome, "  periodo: ", str(ano), "\nTotal de notas de compra: ", str(totalCompras), "\nTotal de notas de vendas: ", str(totalVendas), 
                "\nTotal de notas utilizadas: ", str((totalVendas+totalCompras)), "\nTotal de arquivos: ", str(totalArquivos), 
                "\nTota a ser restituído: ", str(round((totalRestituido), 2)), "  Crédito: ", str(round((credito), 2)), "  Débito: ", str(round((debito), 2)),
                '\n\n\n', mensagem]

            ano = str(ano)
            
            if SO == 'Windows': 
                arqRelatorioNome = Path('.\\Arquivos\\Final\\' "Relatorio_" + CNPJ_Informado + "_" + ano + ".txt")
                arqTabelaCombustivel = Path('.\\Arquivos\\Final\\' 'TabelaComb_' + CNPJ_Informado + '_' + ano + '.csv')
                
            elif SO == 'Linux':
                caminho = '/home/'+ USUARIO +'/Restitui/Arquivos/Final/Relatorio_'  
                arqRelatorioNome = Path(caminho + CNPJ_Informado + "_" + ano + ".txt")

                caminho = '/home/'+ USUARIO +'/Restitui/Arquivos/Final/TabelaComb_'
                arqTabelaCombustivel = Path(caminho + CNPJ_Informado + '_' + ano + '.csv')

            with open(arqRelatorioNome, "w", encoding="utf-8") as arq:
                arq.writelines(txt)
                

             #Looping para imprimir a restituíção de cada tipo de combustível por mês
            i = 0
            txtRst = []
            while i < len(rstCombs):
                j = 0
                aux = []
                periodo = str(i+1) + '/' + ano
                aux.append(periodo)

                while j < len(rstCombs[i]):
                    if rstCombs[i][j] == -1: rstCombs[i][j] = '-'
                    aux.append(rstCombs[i][j])
                    j += 1
                
                txtRst.append(aux)
                i += 1

            tabela = pd.DataFrame(columns=['PERIODO', 
                                           'GASOLINA', 
                                           'GASOLINA ADITIVADA', 
                                           'GASOLINA PREMIUM',
                                           'ETANOL',
                                           'DIESEL S10',
                                           'DIESEL S500'], data= txtRst)
            
            tabela.to_csv(arqTabelaCombustivel, index=False, sep=';')
            
            

main()