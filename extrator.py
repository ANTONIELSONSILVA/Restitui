import csv
from datetime import date
import xml.etree.ElementTree as ET
import os
import pandas as pd

GASOLINA = [ '320101001',	
			 '320102001',
             '320103001',
             '320101002',
             '320102002',
             '320102003', 
             '320102005']

ETANOL = ['810101001',
		  '810102001',
		  '810102003']

DIESEL = ['820101002',
          '820101003',
          '820101004',
          '820101006',
          '820101007',
          '820101008',
          '820101009',
          '820101011',
          '820101012',
          '820101013',
          '820101014',
          '820101015',
          '820101016',
          '820101022',
          '820101025',
          '820101030',
          '820101031',
		  '820101033',
          '820101034']

#GENERICO = ['740101005']


class Read_xml():

	# Inicia o diretório
	def __init__(self, directory) -> None:
		self.directory = directory

	# Cria dataframe de vendas
	def DataFrameVendas(lista: list):
		vendas = pd.DataFrame(columns=['nomeProd',
										'Chave_nota',
										'N_Item',
										'CNPJ_Vendedor',
										'Data_operacao',
										'UF',
										'Cod_Prod_Interno',
										'Valor_Uni_Venda',
										'Cod_ANP',
										'Q_Produtos'], data= lista)
		return vendas

	# Cria dataframe de compras
	def DataFrameCompra(lista: list):
		compras = pd.DataFrame(columns=['nomeProd',
										'Chave_nota',
										'N_Item',
										'CNPJ_Vendedor',
										'Data_operacao',
										'UF',
										'Cod_Prod_Interno',
										'Valor_Uni_Venda',
										'Cod_ANP',
										'Q_Produtos', 
										'Vol_total',
										'Total_ICMS',
										'ICMS_BC',
										'ICMS_Gasolina',
										'ICMS_Etanol',
										'Retido_Etanol',
										'ICMS_Retido',
										'Aliquota',
										'Informacao',
										'Erro'], data= lista)
		return compras

	# Retorna todos os arquivos do diretório
	def all_files(self):
		print("LENDO ARQUIVOS NA PASTA...")
		return [os.path.join(self.directory, arq) for arq in os.listdir(self.directory)
		if arq.lower().endswith(".xml")]
	
	# Formata as strings númericas para a conversão, troca vírgula por ponto
	def formata_string(string):

		string = string.replace(',', '.')

		return(string)

	# Formata o valor do icms quando está no formato mil.centenda,decimais
	def formataValorICMSCompra(texto):

		if texto[0] == '': texto.pop(0)
		elif texto[len(texto)-1] == '': texto.pop((len(texto)-1))
		#Inicia a variáve com a primeira parte do número
		final = texto[0]

		i = 1
		if len(texto) > 2: #para saber se o número possuí casa de milhar
			while i < len(texto):

				if i == (len(texto) - 1): #Quando estiver na última posição, automaticamente significa que chegou na parte decimal, 
										  #onde deve ser inserido o ponto. Como são valores monetários, essa parte sempre irá existir.
					final = final + '.' + texto[i]
				else: #Enquanto não for a ultíma posição, então apenas concatena as strings
					final = final + texto[i]
				
				i += 1
		else: 
			#caso não possua casa de milhar, basta inserir o ponto entre a centena e os decimais.
			final = final + '.' + texto[i]
			
		
		return final

	# Traz o valor total do ICMS na nota de compra
	def retornaValorICMSCompra(texto):
		if ('Produto contaminado' in texto or 'Cliente em desacordo como pedido registrado' in texto
			or 'ERRO DE PEDIDO POR PARTE DO CLIENTE' in texto or 'Falta de espaco no tanque do cliente' in texto
			or 'ERRO DE FATURAMENTO, PEDIDO NAO CARREGADO' in texto or 'ERRO NO PRODUTO FATURADO' in texto 
			or 'ERRO DE INCLUSAO DE PEDIDO' in texto or 'DEVOLUCAO DE REMESSA PARA ANALISE' in texto):
			return -1
		#Quando a string vem especificando o ICMS Total como Impostos Estaduais
		elif 'Estaduais' in texto:
			#Encontra a posição da palavra no texto.
			numero = texto.find('Estaduais')
			numero += 14 #Incrementa a quatidade de caracteres da palavra + o símbolo R$ + o espaço
			j=0
				
			#busca pelo próximo espaço na string
			for i in texto[numero:]:
				if i == ' ': break      
				j+=1
				
			valor = texto[numero:numero+j] #Corta a string entre o índice incrementado e o índice do próximo espaço
			valor = valor.split(',', -1) #Divide a string pelas vírgulas para poder formatar para número
			final = Read_xml.formataValorICMSCompra(valor)
				
			return final
			#Quando a string vem especificando a base de cálcuo + o valor do icms retido para cada produto na nota	
		elif 'Subst, Tribut, ICMS' in texto:
				
				#Divide a string na quantidade de ocorrências da palavra, mas somente a primeira parte importa
			if 'Conforme DESPACHO' in texto: texto = texto.split("Conforme")
			elif 'Mistura' in texto: texto = texto.split("Mistura") 
			elif 'Produto' in texto: texto = texto.split("Produto")

			novoTexto = texto[0].split("ICMS") #Divide a string na quantidade de ocorrências dessa palavra

			valores = []

			i = 0
			while i < len(novoTexto):
				aux = novoTexto[i].split(' ') #Divide pelos espaços
				valores.append(aux) 
				i += 1
				
			palavras = []

			i = 1
			while i < len(valores):
				j = 0
				palavra = ''
				while j < len(valores[i]):

					if valores[i][j] != '': 
						num = valores[i][j][0].isdigit()
						if not num: palavra += ' ' + valores[i][j]
						
					j += 1
					
				if palavra != '': palavras.append(palavra)
				i += 1

			final = []
			for i in palavras: 
				if 'DIESEL' in i:
					final.append([i])
				if 'GASOLINA' in i:
					final.append([i])

			novos = []
				
			i = 1
			while i < len(valores):
				j = 0
				while j < len(valores[i]):
					if valores[i][j] != '':
						if valores[i][j][0].isdigit():
							novos.append(valores[i][j])
					j += 1
				i += 1
				
			icms_bc = []
			icms_ret = []
				
			i = 0
			while i < len(novos):
				if i % 2 == 0: icms_bc.append(novos[i])
				else: icms_ret.append(novos[i])
				i+=1

			novos1 = []	
			for i in icms_bc:
				if '%' not in i:
					aux = i.split(',')
					aux = Read_xml.formataValorICMSCompra(aux)
					novos1.append(aux)
				else: break

			novos2 = []
			for i in icms_ret:
				if '%' not in i:
					aux = i.split(',')
					aux = Read_xml.formataValorICMSCompra(aux)
					novos2.append(aux)
				else: break

				
			i = 0 
			while i < len(final):
				final[i].append(novos1[i])
				final[i].append(novos2[i])
				i += 1
				
			return final

		elif 'N�mero da Ordem' in texto:
			if 'ICMS RETIDO POR SUBSTITUICAO TRIBUTARIA' in texto:
				texto = texto.split('ICMS RETIDO POR SUBSTITUICAO TRIBUTARIA')
			elif 'N�mero do Boletim' in texto:
				texto = texto.split('N�mero do Boletim')
					
			novoTexto = texto[0].split('*')
			valores = []
				
			i = 0
			while i < len(novoTexto):
				aux = novoTexto[i].split(' ') #Divide pelos espaços
				valores.append(aux) 
				i += 1
	
			palavras = []
			i = 1
			while i < len(valores):
				j = 0
				palavra = ''
				while j < len(valores[i]):
					
					if valores[i][j] != '': 
						num = valores[i][j][0].isdigit()
						if not num: palavra += ' ' + valores[i][j]
					
					j += 1

				if palavra != '': palavras.append(palavra)
				i += 1

			final = []
			for i in palavras:
				if 'S10' in i or 'S-10' in i:
					final.append(['DIESEL S-10'])
				if 'S500' in i or 'S-500' in i:
					final.append(['DIESEL S-500'])
				if 'GAS' in i:
					final.append(['GASOLINA'])

			novos = []  
			i = 0
			while i < len(valores):
				if i % 2 != 0:
					j = 0
					while j < len(valores[i]):
						if valores[i][j] != '':
							if valores[i][j][0].isdigit(): 
								novos.append(valores[i][j])
						j += 1
				i += 1
				
			icms_bc = []
			icms_ret = []

			i = 0
			while i < len(novos):
				if i % 2 == 0: icms_bc.append(novos[i])
				else: icms_ret.append(novos[i])
				i +=1 
				
			novos1 = []	
			for i in icms_bc:
				if '%' not in i:
					aux = i.split(',')
					aux = Read_xml.formataValorICMSCompra(aux)
					novos1.append(aux)
				else: break

			novos2 = []
			for i in icms_ret:
				if '%' not in i:
					aux = i.split(',')
					aux = Read_xml.formataValorICMSCompra(aux)
					novos2.append(aux)
				else: break
				
				
			i = 0 
			while i < len(final):
				final[i].append(novos1[i])
				final[i].append(novos2[i])
				i += 1
				
			return final
			
		elif '* Condição de pagamento:' in texto:
			texto = texto.split(':')
			novoTexto = texto[2].split('ICMS')

			valores = []
				
			i = 0
			while i < len(novoTexto):
				aux = novoTexto[i].split(' ') #Divide pelos espaços
				valores.append(aux) 
				i += 1
	
			palavras = []
			i = 0
			while i < len(valores):
				j = 0
				palavra = ''
				while j < len(valores[i]):
					
					if valores[i][j] != '': 
						num = valores[i][j][0].isdigit()
						if not num: palavra += ' ' + valores[i][j]
					
					j += 1

				if palavra != '': palavras.append(palavra)
				i += 1

			final = []
			for i in palavras:
				if 'S10' in i or 'S-10' in i:
					final.append(['DIESEL S-10'])
				if 'S500' in i or 'S-500' in i:
					final.append(['DIESEL S-500'])
				if 'GAS' in i:
					final.append(['GASOLINA'])
				
			novos = []  
			i = 0
			while i < len(valores):
				j = 0
				while j < len(valores[i]):
					if valores[i][j] != '':
						if valores[i][j][0].isdigit():
							if valores[i][j] not in novos and ',' in valores[i][j]: 
								novos.append(valores[i][j])
					j += 1
				i += 1
				
			icms_bc = []
			icms_ret = []

			i = 0
			while i < len(novos):
				if i % 2 == 0: icms_bc.append(novos[i])
				else: icms_ret.append(novos[i])
				i +=1 
				
			novos1 = []	
			for i in icms_bc:
				if '%' not in i:
					aux = i.split(',')
					aux = Read_xml.formataValorICMSCompra(aux)
					novos1.append(aux)
				else: break

			novos2 = []
			for i in icms_ret:
				if '%' not in i:
					aux = i.split(',')
					aux = Read_xml.formataValorICMSCompra(aux)
					novos2.append(aux)
				else: break
				
			i = 0 
			while i < len(final):
				final[i].append(novos1[i])
				final[i].append(novos2[i])
				i += 1
				
			return final
		
		elif 'BC ST DEST' in texto and 'ICMS ST DEST' in texto:
			
			texto = texto.split(':')
			
			for i in texto:
				if 'BC ST DEST' in i:
					valores = i

			indice = valores.find('BC ST DEST')
			indice -= 4
			valores = valores[indice:(len(valores)- 1)]
			valores = valores.split(' ')
			
			final = []
			for i in valores:
				if 'DIE' in i:
					final.append(['DIESEL S-10'])
				if 'GAS' in i:
					final.append(['GASOLINA'])	

			icms = []
			
			i = 0
			while i < len(valores):
				if valores[i] != '':
					if valores[i][0].isdigit():
						if valores[i][(len(valores[i]) - 1)] == ',': valores[i] = valores[i][0: (len(valores[i]) - 1)]

						if '%' not in valores[i]:
							aux = valores[i].replace(',', '.')
							icms.append(aux)	
				i += 1
			
			bc = []
			ret = []

			i = 0
			while i < len(icms):
				if i % 2 == 0: bc.append(icms[i])
				else: ret.append(icms[i])
				i += 1
			
			i = 0
			while i < len(final):
				final[i].append(bc[i])
				final[i].append(ret[i])
				i += 1

			return final

		elif 'Base ICMS Origem' in texto:

			indice = texto.find('Base ICMS Origem')

			if texto[indice - 2] == ';': texto = texto.split(';')
			elif 'RCTE,' in texto[indice - 6 : indice]: texto = texto.split('RCTE,')
			else: return ''
			
			for i in texto:
				if 'Base ICMS Origem' in i: valores = i	
			
			valores = valores.split(' ')
			icms = []

			i = 0
			while i < len(valores):
				if valores[i] != '':
					if valores[i][0].isdigit():
						aux = valores[i].replace(',', '.')
						
						if len(icms) < 2: icms.append(aux)
				i += 1
			
			return icms
		
		elif texto[0:2] == '//':

			if 'ICMS Normal:' in texto and 'ICMS ST:' in texto:
				texto = texto.split('//')
				
				for i in texto: 
					if 'ICMS ST:' in i: valores = i.split(' ')

			elif 'ICMS Normal:' in texto and 'ICMS ST:' not in texto:
				texto = texto.split('//')
				
				for i in texto: 
					if 'ICMS Normal:' in i: valores = i.split(' ')
					
			else:
				texto = texto.split('//')
				valores = texto[1].split(' ')

			icms = []

			i = 0
			while i < len(valores):
				if valores[i] != '':
					if valores[i][0].isdigit():
						if '%' not in valores[i]:
							aux = valores[i].split(',')
							aux = Read_xml.formataValorICMSCompra(aux)
							icms.append(aux)
				
				i += 1
			
			return icms
		else:
			return ''

	# Filtro dos combustívei
	def verificarANPCombustivel(numero):

		if numero in GASOLINA or numero in ETANOL or numero in DIESEL: return True
		else: return False

	# Retorna verdadeiro se a chave estiver na lista
	def busca(lista: list, inicio: int, final: int, chave: str) -> bool:

		if final < inicio:
			return False
		
		meio = (inicio + final)//2

		if lista[meio] == chave: return True
		elif lista[meio] > chave: return Read_xml.busca(lista, inicio, meio-1, chave)
		else: #lista[meio] < item
			return Read_xml.busca(lista, meio+1, final, chave)
		
	# Exclui notas duplicadas caso haja alguma
	def exclui_duplicatas(self, xml, lista: list):
	
		try:
			root = ET.parse(xml).getroot()
		except:
			return -1

		nsNFE = {'ns': "http://www.portalfiscal.inf.br/nfe"}
		Chave_nota = self.check_none(root.find("./ns:protNFe/ns:infProt/ns:chNFe", nsNFE))
			
			
		if Read_xml.busca(lista, 0, len(lista) - 1, Chave_nota):
			print("\n\n\n A nota: ", Chave_nota, " está duplicada")
			print("Duplicatas não serão consideradas")
			return -1
		else:
			lista.append(Chave_nota)
			return 1

	# Faz extração dos dados
	def nfe_data(self, xml, compras, vendas, chaveVendas, chaveCompras, CNPJ_Informado):

		mensagem = ''

		# Raiz do arquivos XML
		try:
			root = ET.parse(xml).getroot()
		except:
			return -1

		nsNFE = {'ns': "http://www.portalfiscal.inf.br/nfe"}

		# Informações necessárias
		Chave_nota = self.check_none(root.find("./ns:protNFe/ns:infProt/ns:chNFe", nsNFE))
		Chave_nota = "NFe" + Chave_nota
		CNPJ_Vendedor = self.check_none(root.find("./ns:NFe/ns:infNFe/ns:emit/ns:CNPJ", nsNFE))
		CNPJ_Comprador = self.check_none(root.find("./ns:NFe/ns:infNFe/ns:dest/ns:CNPJ", nsNFE))
		Date  = self.check_none(root.find("./ns:NFe/ns:infNFe/ns:ide/ns:dhEmi", nsNFE))

		# Formata a data para o formato 'YYYY-MM-DD' e transforma no tipo date
		Data_operacao = Date[:10]
		Data_operacao = date.fromisoformat(Data_operacao)

		verificador = 's'

		if(CNPJ_Informado != CNPJ_Vendedor and CNPJ_Informado != CNPJ_Comprador):		
			print("\n\n\n A nota " + Chave_nota + " não pertence ao estabelecimento")
			verificador = 'n'

		if(verificador == 's'):
			
			UF = self.check_none(root.find("./ns:NFe/ns:infNFe/ns:emit/ns:enderEmit/ns:UF", nsNFE))

			for item in root.findall("./ns:NFe/ns:infNFe/ns:det", nsNFE):

				# Dados internos na tag <det>
				Cod_ANP = self.check_none(item.find(".ns:prod/ns:comb/ns:cProdANP", nsNFE))
				nomeProd = self.check_none(item.find("./ns:prod/ns:xProd", nsNFE))

				if 'NOTA FISCAL EMITIDA EM AMBIENTE DE HOMOLOGACAO' in nomeProd: mensagem = '\nNota com erro ' + str(Chave_nota) + '\n'
				else:
					# Criar uma função para retorna esta verificação
					if(Read_xml.verificarANPCombustivel(Cod_ANP)):


						Cod_Prod_Interno = self.check_none(item.find(".ns:prod/ns:cProd", nsNFE))

						Valor_Uni_Venda = self.check_none(item.find(".ns:prod/ns:vUnCom", nsNFE))
						Valor_Uni_Venda = Read_xml.formata_string(Valor_Uni_Venda)

						Q_Produtos_Vendidos = self.check_none(item.find(".ns:prod/ns:qCom", nsNFE))
						Q_Produtos_Vendidos = Read_xml.formata_string(Q_Produtos_Vendidos)

						nItem = item.attrib['nItem']
							
						#Vendas
						if(CNPJ_Informado == CNPJ_Vendedor):

							if Chave_nota not in chaveVendas: chaveVendas.append(Chave_nota)

							vendas.append([nomeProd, Chave_nota, nItem, CNPJ_Vendedor,Data_operacao, UF, Cod_Prod_Interno, Valor_Uni_Venda,
							Cod_ANP,Q_Produtos_Vendidos])

						# Compras
						elif(CNPJ_Informado == CNPJ_Comprador):
							
							if Chave_nota not in chaveCompras: chaveCompras.append(Chave_nota)

							ICMS_Retido = ''
							baseICMS = ''
							valorDoICMS = ''
							ICMS_Gasolina = ''

							VolumeTotal = self.check_none(root.find(".ns:NFe/ns:infNFe/ns:transp/ns:vol/ns:qVol", nsNFE))
							VolumeTotal = Read_xml.formata_string(VolumeTotal)
		
							string_Valor_ICMS = self.check_none(item.find(".ns:imposto/ns:ICMS/ns:ICMSST/ns:vBCSTRet", nsNFE))
							ICMS_Retido = self.check_none(item.find(".ns:imposto/ns:ICMS/ns:ICMSST/ns:vICMSSTRet", nsNFE))
								
							if (string_Valor_ICMS != "" and string_Valor_ICMS != '0,00' and string_Valor_ICMS != '0' and len(string_Valor_ICMS) <= 9) and (ICMS_Retido != "" and ICMS_Retido != '0,00' and ICMS_Retido != '0' and len(ICMS_Retido) <= 9): 
								baseICMS = Read_xml.formata_string(string_Valor_ICMS)
								ICMS_Retido = Read_xml.formata_string(ICMS_Retido)
								
							else:
								string_Valor_ICMS = self.check_none(item.find(".ns:imposto/ns:ICMS/ns:ICMS60/ns:vBCSTRet", nsNFE))
								ICMS_Retido = self.check_none(item.find(".ns:imposto/ns:ICMS/ns:ICMS60/ns:vICMSSTRet", nsNFE))

								if (string_Valor_ICMS != "" and string_Valor_ICMS != '0,00' and string_Valor_ICMS != '0' and len(string_Valor_ICMS) <= 9) and (ICMS_Retido != "" and ICMS_Retido != '0,00' and ICMS_Retido != '0' and len(ICMS_Retido) <= 9): 
									baseICMS = Read_xml.formata_string(string_Valor_ICMS)
									ICMS_Retido = Read_xml.formata_string(ICMS_Retido)
								
								else:
									string_Valor_ICMS = self.check_none(item.find(".ns:imposto/ns:ICMS/ns:ICMSST/ns:vBCSTDest", nsNFE))
									ICMS_Retido = self.check_none(item.find(".ns:imposto/ns:ICMS/ns:ICMSST/ns:vICMSSTDest", nsNFE))

									if (string_Valor_ICMS != "" and string_Valor_ICMS != '0,00' and string_Valor_ICMS != '0' and len(string_Valor_ICMS) <= 9) and (ICMS_Retido != "" and ICMS_Retido != '0,00' and ICMS_Retido != '0' and len(ICMS_Retido) <= 9): 
										baseICMS = Read_xml.formata_string(string_Valor_ICMS)
										ICMS_Retido = Read_xml.formata_string(ICMS_Retido)

									else:	
										string_Valor_ICMS = self.check_none(root.find(".ns:NFe/ns:infNFe/ns:infAdic/ns:infCpl", nsNFE))
										string_Valor_ICMS = Read_xml.retornaValorICMSCompra(string_Valor_ICMS)

										if string_Valor_ICMS != '' and string_Valor_ICMS != -1:
											valorDoICMS, baseICMS, ICMS_Gasolina, ICMS_Retido = Read_xml.excecoes(valorDoICMS, baseICMS, ICMS_Gasolina, ICMS_Retido, Cod_ANP, VolumeTotal, Q_Produtos_Vendidos, string_Valor_ICMS)
										else:
											string_Valor_ICMS = self.check_none(item.find(".ns:infAdProd", nsNFE))
											string_Valor_ICMS = Read_xml.retornaValorICMSCompra(string_Valor_ICMS)
											if type(string_Valor_ICMS) == list:
												baseICMS = string_Valor_ICMS[0]
												ICMS_Retido = string_Valor_ICMS[1]

							
							info = self.check_none(root.find(".ns:NFe/ns:infNFe/ns:infAdic/ns:infCpl", nsNFE))
							erro = Read_xml.retornaValorICMSCompra(info)

							if erro != -1:		
										ICMS_Etanol = self.check_none(root.find(".ns:NFe/ns:infNFe/ns:total/ns:ICMSTot/ns:vBCST", nsNFE))

										if (ICMS_Etanol == '0' or ICMS_Etanol == '0,00' or ICMS_Etanol == '') and Cod_ANP in ETANOL:
											
											if 'ETANOL H MAR-' in info: 
												indice = info.find('ETANOL H MAR-')
												indice += 13
												numero = info[indice:indice+6]
												numero = numero.replace(',', '.')

												ICMS_Etanol = str(float(numero) * float(Q_Produtos_Vendidos))

											elif 'ETA HIDR ADT-' in info: 
												indice = info.find('ETA HIDR ADT-')
												indice += 13
												numero = info[indice:indice+6]
												numero = numero.replace(',', '.')

												ICMS_Etanol = str(float(numero) * float(Q_Produtos_Vendidos))
												
										ICMS_Etanol = Read_xml.formata_string(ICMS_Etanol)
										retido_Etanol = self.check_none(root.find(".ns:NFe/ns:infNFe/ns:total/ns:ICMSTot/ns:vICMS", nsNFE))
										retido_Etanol = Read_xml.formata_string(retido_Etanol)

										if float(Q_Produtos_Vendidos) == 0: erro = 1
										else: erro = ''
										
										aliquota = ''
												
										compras.append([nomeProd, Chave_nota, nItem, CNPJ_Vendedor, Data_operacao, UF, Cod_Prod_Interno, Valor_Uni_Venda,
										Cod_ANP, Q_Produtos_Vendidos, VolumeTotal, valorDoICMS, baseICMS, ICMS_Gasolina, ICMS_Etanol, retido_Etanol, ICMS_Retido, aliquota, info, erro])
							else:
								mensagem = '\nNota com erro ' + str(Chave_nota) + '\n'
										
						else:
							continue
		
		return mensagem
			
		
	def excecoes(total, base, gasolina, retido, anp, vol, qtd, string_Valor_ICMS):

		if string_Valor_ICMS != "" and string_Valor_ICMS != '0,00' and string_Valor_ICMS != '0' and string_Valor_ICMS != -1:

			if type(string_Valor_ICMS) == list:
					if type(string_Valor_ICMS[0]) == list:
						i = 0
						while i < len(string_Valor_ICMS):

							if 'DIESEL' in string_Valor_ICMS[i][0] and anp in DIESEL:
								if (anp == '820101034' and ('S-10' in string_Valor_ICMS[i][0] or 'S 10' in string_Valor_ICMS[i][0])):
									base = string_Valor_ICMS[i][1]
									retido = string_Valor_ICMS[i][2]
									break
								elif anp != '820101034':
									base = string_Valor_ICMS[i][1]
									retido = string_Valor_ICMS[i][2]
									break
													
							elif 'GASOLINA' in string_Valor_ICMS[i][0] and anp in GASOLINA:
								gasolina = string_Valor_ICMS[i][1]
								base = string_Valor_ICMS[i][1]
								retido = string_Valor_ICMS[i][2]
								break
													
							i += 1
					else:
						if float(vol) == float(qtd):
							base = string_Valor_ICMS[0]
							retido = string_Valor_ICMS[1]
											
			else: total = string_Valor_ICMS
		
		return total, base, gasolina, retido

	# Verifica se o campo é vazio
	def check_none(self, var):
		if var == None: 
			return ""
		elif var.text == None:
			return ""
		else:
			try:
				return var.text.replace('.',',')
			except:
				return var.text

	# Retorna os itens na pasta
	def getBase(caminho):
		xml = Read_xml(caminho)
		return xml
	


