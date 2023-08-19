import getpass
import hashlib
from itertools import cycle
from datetime import date
import os
import csv
import pandas as pd
import subprocess
import platform

SO = platform.system()
GASOLINA_AD = '320103001'
GASOLINA_P = '320102003'     
DIESEL_S10 = '820101034'
DIESEL_S500 = '820101002'
GASOLINA_C = '320101001'

def user():
   #Abre um subprocesso ping usando a sintaxe Linux
   p = subprocess.run(['whoami'], stdout=subprocess.PIPE)
   stdout = p.stdout #captura stdout

   #Retorna o texto do terminal se hover erro retorna vazia
   u = stdout.decode('UTF-8') 
   u = u[0:(len(u)-1)]
   return u

USUARIO = user()

def limpa_tela():

	if SO == 'Linux': subprocess.run(['clear'])
	elif SO == 'Windows': os.system('cls')

def modo_operacao() -> int:
	sair = 'a'

	print('\n')
	logo()
	while sair != 'q':

			print('\n')
			print('\t1 - Organizar pastas por cnpj e ano')
			print('\t2 - Começar processamento das notas')
			print('\t3 - Sair')
			op = input('Escolha uma opção: ')

			while (op != '1' and op != '2' and op !='3'):
				op = input("\n Opção inválida, digite novamente: ")

			if op == '1': return 1
			elif op == '2': return 2
			elif op == '3': sair = 'q'

			if sair == 'q': quit()

# Diz se o cnpj informado é válido ou não
def cnpj_valido(cnpj: str) -> bool:
	LENGTH_CNPJ = 14

	if len(cnpj) != LENGTH_CNPJ:
		return False

	if cnpj in (c * LENGTH_CNPJ for c in "1234567890"):
		return False

	cnpj_r = cnpj[::-1]
	for i in range(2, 0, -1):
		cnpj_enum = zip(cycle(range(2, 10)), cnpj_r[i:])
		dv = sum(map(lambda x: int(x[1]) * x[0], cnpj_enum)) * 10 % 11
		if cnpj_r[i - 1:i] != str(dv % 10):
			return False

	return True

def logo():
	#os.system("color a")
	print("\t.______       _______      _______..___________. __  .___________. __    __   __ ")
	print("\t|   _  \     |   ____|    /       ||           ||  | |           ||  |  |  | |  |")
	print("\t|  |_)  |    |  |__      |   (----``---|  |----`|  | `---|  |----`|  |  |  | |  |")
	print("\t|      /     |   __|      \   \        |  |     |  |     |  |     |  |  |  | |  |")
	print("\t|  |\  \----.|  |____ .----)   |       |  |     |  |     |  |     |  `--'  | |  |")
	print("\t| _| `._____||_______||_______/        |__|     |__|     |__|      \______/  |__| ⓡ")
	print("\t\nHS Informática\n")

# Faz a autenticação da senha inserida
def verificaSenha():
	senha = getpass.getpass(prompt='Digite sua Senha: ', stream=None)

	result = hashlib.sha256(senha.encode('utf-8')).hexdigest()

	if(result != 'be17aa4e4837ebc816f53c0ab5eb292df1e17f43ca4059155ae400dc6b80ed01'):
		print("Senha inválida!!!")
		quit()

	return True

# Faz a formação da string referente ao caminho da base de dados
def recebeBase():
	xml = ''
	while (len(xml) <= 0):
		xml = input('Informe o caminho da base de dados: ')
		xml = xml.replace("\\", "\\\\")
		
		if SO == 'Linux':
			if xml[0] != '/':
				xml = '/' + xml
			elif xml[len(xml)-1] != '/':
				xml = xml + '/'
		
	return xml

# Retorna o CNPJ informado pelo usuário 
def verificarCNPJ():
	sair = 'a'

	while(sair != 'q'):
		CNPJ_Informado = input("Informe o CNPJ do requisitante: ")

		if(cnpj_valido(CNPJ_Informado)):
			break
		else:
			limpa_tela()
			logo()
			sair = input("\n\t CNPJ inválido.... q para sair ou enter para continuar")
			if(sair == 'q'):
				quit()
			continue

	return CNPJ_Informado

# Retorna o período em que será feita a análise das notas
def recebe_data():

	sair = ''
	while sair != 'q':
		ano = input("Informe o ano no formato YYYY: ")
		mes = input("Informe o mês no formato MM: ")
		if ((len(ano) != 4) or (len(mes) != 2)):
			sair = input("\n\t Formato inválido.... q para sair ou enter para continuar")
			if sair == 'q': quit()
			continue
		elif (int(ano) < 1 or int(ano) > 9999) or (int(mes) < 1 or int(mes) > 12):
			sair = input("\n\t Formato inválido.... q para sair ou enter para continuar")
			if sair == 'q': quit()
			continue	
		else:
			data = ano + '-' + mes + '-' + '01'
			periodo = date.fromisoformat(data)
			return periodo
		
def recebe_ano():
	sair = ''
	while sair != 'q':
		ano = input("Informe o ano no formato YYYY: ")
		if (len(ano) != 4) or (int(ano) < 1 or int(ano) > 9999):
			sair = input("\n\t Formato inválido.... q para sair ou enter para continuar")
			if sair == 'q': quit()
			continue
		else:
			ano = int(ano)
			return ano

# Associa a lista com os nomes dos combustíveis com seus devidos códigos ANP
def cod_combustivel():

	if SO == 'Windows':
		with open('.\\Arquivos\\Listas\\nomeComb.csv', 'r', encoding='utf-8') as file:
			reader = csv.reader(file, delimiter=';')
			listaCodigos = list(reader)
	elif SO == 'Linux':
		caminho = '/home/'+ USUARIO +'/Restitui/Arquivos/Listas/nomeComb.csv'
		with open(caminho, 'r', encoding='utf-8') as file:
			reader = csv.reader(file, delimiter=';')
			listaCodigos = list(reader)
	
	file.close()

	i = 0
	while i < len(listaCodigos):

		if listaCodigos[i][1] == '0':

			limpa_tela()
			logo()
			print("\t O combustível", listaCodigos[i][0], "é: \n")
			print("\t 1 - Gasolina Comum")
			print("\t 2 - Gasolina Aditivada")
			print("\t 3 - Gasolina Podium")
			print("\t 4 - Etanol")
			print("\t 5 - Diesel S-10")
			print("\t 6 - Diesel S-500")
			
			print("\n")
			op = input("Escolha uma opção: ")
			
			while op != '1' and op != '2' and op !='3' and op !='4' and op !='5' and op !='6': 
				op = input("\n Opção inválida, digite novamente: ")

			if op == '1':
				listaCodigos[i][1] = GASOLINA_C
				
			elif op == '2':
				listaCodigos[i][1] = GASOLINA_AD
				
			elif op == '3':
				listaCodigos[i][1] = GASOLINA_P
				
			elif op == '4':
				listaCodigos[i][1] = '810101001'
				
			elif op == '5':
				listaCodigos[i][1] = DIESEL_S10
				
			elif op == '6':
				listaCodigos[i][1] = DIESEL_S500
				
		i += 1
	
	dataNomes = pd.DataFrame(listaCodigos)
	if SO == 'Windows': dataNomes.to_csv('.\\Arquivos\\Listas\\nomeComb.csv', index=False, header=False, sep=';')
	elif SO == 'Linux':
		caminho = '/home/'+ USUARIO +'/Restitui/Arquivos/Listas/nomeComb.csv' 
		dataNomes.to_csv(caminho, index=False, header=False, sep=';')

# modo de edição dos campos de uma nota	
def edicao(item):
	
	sair = ''
	while sair != 'q':
		print('\n\n---------------------MODO DE EDIÇÃO---------------------')
		print(item)
		print(item.Informacao)
		print('--------------------------------------------------------')

		print('\nQual valor deseja editar? Pressione q para sair...\n')
		print('1 - Nome do produto')
		print('2 - Chave da nota')
		print('3 - Número do Item')
		print('4 - CNPJ')
		print('5 - Data')
		print('6 - UF')
		print('7 - Código Interno do Produto')
		print('8 - Valor do produto')
		print('9 - Código ANP')
		print('10 - Quantidade de produto')
		print('11 - Volume total da nota')
		print('12 - ICMS total da nota')
		print('13 - ICMS do produto')
		print('14 - ICMS total da gasolina')
		print('15 - ICMS do Etanol')
		print('16 - ICMS retido do Etanol')
		print('17 - ICMS retido do produto')
		print('18 - Alíquota')
		print('19 - Erro')

		op = input()

		while (op != '1' and  op != '2' and  op != '3' and op != '4' and  op != '5' and  op != '6' and
			   op != '7' and  op != '8' and  op != '9' and op != '10' and  op != '11' and  op != '12' and
			   op != '13' and  op != '14' and  op != '15' and op != '16' and  op != '17' and  op != '18' and op != 'q' and op != '19'):
			
			op = input('\nOpção Inválida! Digite novamente: ')
			
		if op == '1':
			print('NOME ATUAL: ', item.nomeProd, 'Digite o novo nome para o produto: ')
			item.nomeProd = input()
		elif op == '2':
			print('CHAVE ATUAL: ', item.Chave_nota, 'Digite a nova chave para a nota: ')
			item.Chave_nota = input()
		elif op == '3':
			print('NÚMERO DO ITEM ATUAL: ', item.N_Item, 'Digite o novo número do item para o produto: ')
			item.N_Item = input()
		elif op == '4':
			print('CNPJ ATUAL: ', item.CNPJ_Vendedor, 'Digete o novo CNPJ da nota: ')
			item.CNPJ_Vendedor = verificarCNPJ()
		elif op == '5':
			print('DATA ATUAL: ', item.Data_operacao, 'Digite a nova data para a nota: ')
			data = input()
			item.Data_operacao = date.fromisoformat(data)
		elif op == '6':
			print('UF ATUAL: ', item.UF, 'Digite o novo UF para a nota: ')
			item.UF = input()
		elif op == '7':
			print('CODIGO INTERNO ATUAL: ', item.Cod_Prod_Interno, 'Digite o novo código interno do produto: ')
			item.Cod_Prod_Interno = input()
		elif op == '8':
			print('VALOR ATUAL: ', item.Valor_Uni_Venda, 'Digite o novo valor para o produto: ')
			valor = input()
			while ',' in valor: 
				valor = input('Decimal deve ser separado por ponto! Digite novamente:')
			item.Valor_Uni_Venda = float(valor)
		elif op == '9':
			print('CÓDIGO ANP ATUAL: ', item.Cod_ANP, 'Digite o novo código ANP para o produto: ')
			item.Cod_ANP = input()
		elif op == '10':
			print('QUANTIDADE ATUAL: ', item.Q_Produtos, 'Digite a nova quantidade de produto: ')
			valor = input()
			while ',' in valor: 
				valor = input('Decimal deve ser separado por ponto! Digite novamente:')
			item.Q_Produtos = float(valor)
		elif op == '11':
			print('VOLUME ATUAL: ', item.Vol_Total, 'Digite o novo volume de produto para a nota: ')
			valor = input()
			while ',' in valor: 
				valor = input('Decimal deve ser separado por ponto! Digite novamente:')
			item.Vol_Total = float(valor)
		elif op == '12':
			print('ICMS TOTAL ATUAL: ', item.Total_ICMS, 'Digite o novo total de ICMS para a nota: ')
			valor = input()
			while ',' in valor: 
				valor = input('Decimal deve ser separado por ponto! Digite novamente:')
			item.Total_ICMS = float(valor)
		elif op == '13':
			print('ICMS DO PRODUTO ATUAL: ', item.ICMS_BC, 'Digite o novo ICMS do produto: ')
			valor = input()
			while ',' in valor: 
				valor = input('Decimal deve ser separado por ponto! Digite novamente:')
			item.ICMS_BC = float(valor)
		elif op == '14':
			print('ICMS DE GASOLINA ATUAL: ', item.ICMS_Gasolina, 'Digite o novo ICMS de gasolina do produto: ')
			valor = input()
			while ',' in valor: 
				valor = input('Decimal deve ser separado por ponto! Digite novamente:')
			item.ICMS_Gasolina = float(valor)
		elif op == '15':
			print('ICMS DE ETANOL ATUAL: ', item.ICMS_Etanol, 'Digite o novo ICMS de etanol do produto: ')
			valor = input()
			while ',' in valor: 
				valor = input('Decimal deve ser separado por ponto! Digite novamente:')
			item.ICMS_Etanol = float(valor)
		elif op == '16':
			print('ICMS RETIDO DO ETANOL ATUAL: ', item.Retido_Etanol, 'Digite o novo ICMS retido do etanol do produto: ')
			valor = input()
			while ',' in valor: 
				valor = input('Decimal deve ser separado por ponto! Digite novamente:')
			item.Retido_Etanol = float(valor)
		elif op == '17':
			print('ICMS RETIDO DO PRODUTO ATUAL: ', item.ICMS_Retido, 'Digite o novo ICMS retido do produto: ')
			valor = input()
			while ',' in valor: 
				valor = input('Decimal deve ser separado por ponto! Digite novamente:')
			item.ICMS_Retido = float(valor)
		elif op == '18':
			print('ALÍQUOTA DO PRODUTO ATUAL: ', item.Aliquota, 'Digite a nova Alíquota do produto: ')
			valor = input()
			while ',' in valor: 
				valor = input('Decimal deve ser separado por ponto! Digite novamente:')
			item.Aliquota = float(valor)
		elif op == '19':
			print('Nota com erro? Digite 1 para sim e 0 para não')
			valor = input()
			while valor != '1' and valor != '0':
				valor = input('Entrada inválida! Digite novamente: ')
			item.Erro = int(valor)
		elif op == 'q':
			sair = op
	
	return item



