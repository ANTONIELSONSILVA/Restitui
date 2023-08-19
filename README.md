# Restitui
> Extrai campos específicos de notas fiscais de compra combustível automotivo e gera um arquivo em .csv pronto para ser enviado para a Receita Federal, de acordo com a Instrução Normativa SUREC/SEF/SEEC Nº 16 do SINJ-DF

[![Python Version][python-image]][python-url]
[![Downloads Stats][python-downloads]][python-url]

O projeto foi dividido em 3 módulos principais:

1. Extrator: uma classe para manipular os arquivos xml. Cria uma lista com todos os arquivos .xml no repositório indicado, extrai os campos requeridos com formatação prévia, e transforma os dados extraidos em Pandas DataFrames.

2. Processo: faz os cálculos necessários e organiza as notas extraídas por intervalos de data entre elas, transformando os dados em listas para cada tipo de combustível.

3. Resultado: monta o arquivo final em .csv dentro do específicado pela Instrução Normativa.

Módulos adicionais:

1. Diretorios: Organiza os arquivos na pasta, de acordo com o CNPJ informado, criando uma pasta com o CNPJ em questão e organizando em subpastas de acordo com o ano em que os arquivos foram emitidos.

2. Organiza: Organiza a pasta de arquivos de nota de um ano do posto quando as notas estão separadas por mês, compra e venda. Movendo todas as notas para a pasta principal


## Instalação

Linux:

```sh
sudo apt install python3-pip
sudo apt install python3.7

python3.7 -m pip install pip
```

## Dependências

É preciso instalar duas bibliotecas adicionais do python para executar esse projeto:

Pandas

>Windows:
```sh
pip install pandas
```
>Linux:
```sh
python3.7 -m pip install pandas
```

TQDM

>Windows:
```sh
pip install tqdm
```
>Linux:
```sh
python3.7 -m pip install tqdm
```

[python-image]: https://img.shields.io/badge/python-v3.7-blue
[python-url]: https://www.python.org/downloads/release/python-370/
[python-downloads]: https://img.shields.io/badge/downloads-14k%2Fday-brightgreen
