# 01 — Dataset e validação estrutural

## Contexto

O projeto utiliza o **BANKING77**, um dataset de classificação de intenções no domínio bancário. A versão utilizada possui:

- 13.083 mensagens;
- 10.003 registros de treinamento;
- 3.080 registros de teste;
- 77 classes;
- colunas `text` e `label`.

O problema é de **classificação multiclasse de textos**.

## O que validamos

Antes de iniciar modelagem ou EDA mais profunda, verificamos se os dados possuíam a estrutura mínima esperada.

Resultados:

| Verificação | Treino | Teste |
| --- | ---: | ---: |
| Registros | 10.003 | 3.080 |
| Classes | 77 | 77 |
| Textos ausentes | 0 | 0 |
| Labels ausentes | 0 | 0 |
| Textos vazios | 0 | 0 |
| Registros duplicados | 0 | 0 |

Também confirmamos que os dois splits possuem o mesmo conjunto de classes.

## Aprendizado

Antes de perguntar **qual modelo utilizar**, é necessário perguntar **se os dados possuem condições mínimas para serem utilizados**.

A validação estrutural procura problemas como:

- colunas ausentes;
- splits ausentes;
- valores nulos;
- textos vazios;
- labels ausentes;
- registros duplicados.

## Ponto de atenção

Validação estrutural não é a mesma coisa que EDA.

A validação responde perguntas como:

> “O dataset possui a estrutura esperada?”

A EDA responde perguntas como:

> “Como esses dados se comportam e quais características podem afetar a modelagem?”

## Decisão do projeto

Como não foram encontrados problemas estruturais que exigissem correção, não realizamos remoção ou imputação de registros nesta etapa.

## Como explicar em vídeo

> “Antes de treinar qualquer modelo, validamos a qualidade mínima do BANKING77. Confirmamos os splits, as colunas esperadas, as 77 classes e verificamos dados ausentes, textos vazios e duplicidades. Como esses problemas não foram encontrados, conseguimos avançar para a análise exploratória sem alterar o dataset.”
