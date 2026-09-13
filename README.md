## 🚀 Status do Projeto

> 🚧 **Em desenvolvimento**

O desenvolvimento está sendo realizado de forma incremental, mantendo o histórico de commits e Pull Requests como registro da evolução técnica e das decisões realizadas durante o projeto.

### ✅ Estrutura e arquitetura inicial

* [x] Criar estrutura inicial do projeto
* [x] Configurar projeto Python com `uv`
* [x] Organizar o código utilizando separação de responsabilidades
* [x] Criar camadas iniciais de `application`, `domain` e `infrastructure`
* [x] Documentar arquitetura inicial

### ✅ Dataset e carregamento

* [x] Definir BANKING77 como dataset do projeto
* [x] Utilizar a fonte oficial `PolyAI/banking77`
* [x] Implementar carregamento através do Hugging Face
* [x] Validar os splits de treino e teste
* [x] Confirmar 13.083 registros
* [x] Confirmar as 77 classes em ambos os splits

### ✅ Validação estrutural dos dados

A validação inicial do BANKING77 foi concluída com os seguintes resultados:

| Validação            | Treino | Teste |
| -------------------- | -----: | ----: |
| Registros            | 10.003 | 3.080 |
| Classes              |     77 |    77 |
| Textos ausentes      |      0 |     0 |
| Labels ausentes      |      0 |     0 |
| Textos vazios        |      0 |     0 |
| Registros duplicados |      0 |     0 |

Também foi verificada a existência de textos compartilhados entre os conjuntos de treino e teste:

```text
Textos presentes em treino e teste: 0
```

Com isso, não foram identificados problemas estruturais que exijam, neste momento, remoção, imputação ou correção de registros.

A ausência de textos compartilhados entre os splits também reduz o risco de data leakage decorrente da presença da mesma mensagem nos conjuntos de treino e teste.

### 🔄 Próxima etapa — Análise Exploratória dos Dados

Com a validação estrutural concluída, a próxima etapa será a **Análise Exploratória dos Dados (EDA)**.

Inicialmente serão investigados:

* distribuição das 77 classes;
* quantidade de exemplos por classe;
* balanceamento do dataset;
* comprimento dos textos;
* distribuição do número de palavras;
* características gerais do corpus;
* possíveis padrões relevantes para a etapa de modelagem.

Os resultados da EDA serão utilizados para orientar as decisões de pré-processamento e a construção do primeiro modelo baseline.

### 📋 Roadmap

* [x] Estrutura inicial do projeto
* [x] Arquitetura inicial
* [x] Carregamento do BANKING77
* [x] Validação estrutural do dataset
* [ ] Análise exploratória dos dados (EDA)
* [ ] Implementação do modelo baseline
* [ ] Avaliação das métricas do modelo
* [ ] API de inferência
* [ ] Containerização
* [ ] Pipeline CI/CD
* [ ] Pipeline de treinamento com Airflow
* [ ] Monitoramento com Prometheus
* [ ] Dashboards no Grafana
* [ ] Conversão e validação ONNX
* [ ] Benchmark de latência
* [ ] Documentação e resultados finais
