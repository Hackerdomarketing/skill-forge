# Arquiteturas de Habilidades

Este documento detalha os quatro padrões arquiteturais para estruturar habilidades. Escolher o padrão que melhor corresponde ao tipo de tarefa.

## Padrão 1: Habilidade Baseada em Fluxo de Trabalho

**Usar quando:** A tarefa tem passos sequenciais bem definidos que devem ser seguidos em ordem.

**Exemplos:** Preenchimento de formulários PDF, edição de documentos com controle de alterações, processos de revisão de código.

**Estrutura:**

```markdown
# Nome da Habilidade

## Visão Geral
[Breve descrição do que o fluxo realiza]

## Árvore de Decisão

Determinar o tipo de operação:

**Criando novo conteúdo?** → Seguir "Fluxo de Criação"
**Editando conteúdo existente?** → Seguir "Fluxo de Edição"
**Analisando sem modificar?** → Seguir "Fluxo de Análise"

## Fluxo de Criação

### Passo 1: [Nome do Passo]
[Instruções detalhadas]
```código se aplicável```

### Passo 2: [Nome do Passo]
[Instruções detalhadas]

### Passo 3: [Nome do Passo]
[Instruções detalhadas]

## Fluxo de Edição

### Passo 1: Desempacotar
[...]

### Passo 2: Modificar
[...]

### Passo 3: Reempacotar
[...]
```

**Características:**
- Passos numerados explicitamente
- Cada passo tem pré-condições e resultados esperados
- Pontos de decisão claramente marcados
- Scripts frequentemente usados para passos complexos

---

## Padrão 2: Habilidade Baseada em Tarefas

**Usar quando:** A habilidade oferece várias operações independentes que podem ser executadas isoladamente.

**Exemplos:** Manipulação de PDFs (mesclar, dividir, extrair), processamento de imagens, utilitários de linha de comando.

**Estrutura:**

```markdown
# Nome da Habilidade

## Visão Geral
[Descrição das capacidades gerais]

## Referência Rápida

| Tarefa | Comando/Abordagem |
|--------|-------------------|
| Tarefa A | `script_a.py` ou método |
| Tarefa B | `script_b.py` ou método |
| Tarefa C | Abordagem manual descrita abaixo |

## Tarefa A: [Nome Descritivo]

### Quando Usar
[Cenários específicos]

### Como Executar
```bash
python scripts/script_a.py entrada.ext saida.ext
```

### Opções Disponíveis
- `--opcao1`: Descrição
- `--opcao2`: Descrição

### Exemplo Completo
[Exemplo realista de uso]

## Tarefa B: [Nome Descritivo]
[Mesma estrutura]

## Tarefa C: [Nome Descritivo]
[Mesma estrutura]
```

**Características:**
- Tabela de referência rápida no início
- Cada tarefa é autocontida
- Exemplos concretos para cada tarefa
- Opções e parâmetros documentados

---

## Padrão 3: Habilidade de Referência e Diretrizes

**Usar quando:** A habilidade estabelece padrões, regras ou especificações a serem seguidas.

**Exemplos:** Diretrizes de marca, padrões de código, políticas de comunicação, especificações técnicas.

**Estrutura:**

```markdown
# Nome da Habilidade

## Visão Geral
[Propósito das diretrizes]

## Princípios Fundamentais

1. **[Princípio 1]**: [Explicação concisa]
2. **[Princípio 2]**: [Explicação concisa]
3. **[Princípio 3]**: [Explicação concisa]

## Diretrizes Detalhadas

### [Categoria 1]

**Fazer:**
- Item específico
- Item específico

**Não Fazer:**
- Item específico
- Item específico

**Exemplos:**

Correto:
```
[exemplo]
```

Incorreto:
```
[exemplo]
```

### [Categoria 2]
[Mesma estrutura]

## Especificações Técnicas

| Elemento | Especificação |
|----------|---------------|
| [Item] | [Valor ou regra] |
| [Item] | [Valor ou regra] |

## Checklist de Conformidade

- [ ] [Verificação 1]
- [ ] [Verificação 2]
- [ ] [Verificação 3]
```

**Características:**
- Princípios no topo para orientação geral
- Exemplos de "fazer" e "não fazer"
- Especificações em formato tabular
- Checklist para verificação

---

## Padrão 4: Habilidade Baseada em Capacidades

**Usar quando:** A habilidade representa um sistema integrado com múltiplas funcionalidades relacionadas.

**Exemplos:** Sistemas de gerenciamento de projetos, plataformas de criação de conteúdo, ferramentas de análise de dados.

**Estrutura:**

```markdown
# Nome da Habilidade

## Visão Geral
[Descrição do sistema e suas capacidades integradas]

## Capacidades Principais

Este sistema oferece as seguintes capacidades integradas:

1. **[Capacidade 1]** — [Descrição em uma linha]
2. **[Capacidade 2]** — [Descrição em uma linha]
3. **[Capacidade 3]** — [Descrição em uma linha]

## Capacidade 1: [Nome Completo]

### Propósito
[O que esta capacidade permite]

### Integração com Outras Capacidades
- Usa dados de [Capacidade X]
- Alimenta [Capacidade Y]

### Uso

[Instruções detalhadas]

### Configuração
[Parâmetros e opções]

## Capacidade 2: [Nome Completo]
[Mesma estrutura]

## Fluxos de Trabalho Integrados

### Fluxo: [Nome do Fluxo]
Combina [Capacidade 1] → [Capacidade 2] → [Capacidade 3]

1. [Passo usando Capacidade 1]
2. [Passo usando Capacidade 2]
3. [Passo usando Capacidade 3]
```

**Características:**
- Lista de capacidades no início
- Cada capacidade documenta integrações
- Fluxos de trabalho que combinam capacidades
- Configuração centralizada quando aplicável

---

## Combinando Padrões

A maioria das habilidades combina elementos de múltiplos padrões:

| Combinação Comum | Exemplo |
|------------------|---------|
| Tarefas + Fluxo | PDF: tarefas independentes mas edição segue fluxo |
| Capacidades + Referência | Sistema com diretrizes de uso |
| Fluxo + Referência | Processo com padrões de qualidade |

**Regra:** Começar com o padrão primário e adicionar elementos de outros conforme necessário.

---

## Escolhendo o Padrão Certo

```
                    ┌─────────────────────────────┐
                    │ A tarefa tem passos que     │
                    │ DEVEM ser seguidos em ordem?│
                    └─────────────┬───────────────┘
                                  │
                    ┌─────────────┴───────────────┐
                    │                             │
                   SIM                           NÃO
                    │                             │
                    ▼                             ▼
          ┌─────────────────┐         ┌─────────────────────────┐
          │ FLUXO DE        │         │ As operações são        │
          │ TRABALHO        │         │ independentes entre si? │
          └─────────────────┘         └───────────┬─────────────┘
                                                  │
                                    ┌─────────────┴───────────────┐
                                    │                             │
                                   SIM                           NÃO
                                    │                             │
                                    ▼                             ▼
                          ┌─────────────────┐         ┌─────────────────────────┐
                          │ BASEADA EM      │         │ É sobre padrões/regras  │
                          │ TAREFAS         │         │ ou sistema integrado?   │
                          └─────────────────┘         └───────────┬─────────────┘
                                                                  │
                                                    ┌─────────────┴───────────────┐
                                                    │                             │
                                              PADRÕES/REGRAS              SISTEMA INTEGRADO
                                                    │                             │
                                                    ▼                             ▼
                                          ┌─────────────────┐         ┌─────────────────┐
                                          │ REFERÊNCIA E    │         │ BASEADA EM      │
                                          │ DIRETRIZES      │         │ CAPACIDADES     │
                                          └─────────────────┘         └─────────────────┘
```
