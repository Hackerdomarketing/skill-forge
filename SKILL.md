---
name: skill-forge
description: "Sistema avançado para criar habilidades altamente efetivas para o Claude Code. Usar quando o usuário quiser: (1) Criar uma nova habilidade do zero, (2) Melhorar ou refatorar uma habilidade existente, (3) Analisar a qualidade de uma habilidade, (4) Entender como estruturar conhecimento procedural para agentes de inteligência artificial. Esta habilidade guia todo o processo desde a descoberta de requisitos até o empacotamento final."
---

# Skill Forge — Sistema de Criação de Habilidades

Sistema completo para criar habilidades que transformam o Claude de um agente genérico em um especialista com conhecimento procedural específico.

## Filosofia Fundamental

Uma habilidade efetiva é como um guia de integração para um novo funcionário especialista: fornece exatamente o conhecimento procedural e os recursos que a pessoa precisaria para executar tarefas específicas com excelência, sem explicar conceitos básicos que ela já domina.

**Três perguntas que toda habilidade deve responder:**
1. Quando devo ser acionada? (descrição no frontmatter)
2. O que devo fazer? (instruções no corpo)
3. Com quais recursos? (scripts, referências, ativos)

## Processo de Criação em Cinco Fases

Seguir estas fases em ordem. Não pular etapas.

### Fase 1: Descoberta Profunda

**Objetivo:** Entender casos de uso concretos antes de criar qualquer coisa.

Fazer perguntas direcionadas até ter clareza sobre:

```
┌─────────────────────────────────────────────────────────────┐
│ CHECKLIST DE DESCOBERTA                                     │
├─────────────────────────────────────────────────────────────┤
│ □ Quais são 3-5 exemplos específicos de uso?                │
│ □ O que o usuário diria para acionar esta habilidade?       │
│ □ Qual é o resultado esperado em cada caso?                 │
│ □ Quais ferramentas ou formatos estão envolvidos?           │
│ □ Existem padrões ou templates que devem ser seguidos?      │
│ □ Quais erros comuns devem ser evitados?                    │
│ □ Há conhecimento específico de domínio necessário?         │
└─────────────────────────────────────────────────────────────┘
```

**Não avançar** até ter pelo menos 3 exemplos concretos validados com o usuário.

### Fase 2: Análise de Recursos

**Objetivo:** Identificar o que incluir na habilidade.

Para cada exemplo concreto da Fase 1, analisar:

| Pergunta | Se sim, criar... |
|----------|------------------|
| Código seria reescrito repetidamente? | `scripts/` com implementação reutilizável |
| Precisa de documentação para tomar decisões? | `references/` com guias detalhados |
| Usa templates, imagens ou boilerplate? | `assets/` com arquivos prontos |
| Processo tem múltiplos passos sequenciais? | Fluxo de trabalho no SKILL.md |
| Existem armadilhas técnicas não óbvias? | Avisos CRITICAL no SKILL.md |

**Regra de ouro:** Se o Claude já sabe fazer algo naturalmente, não incluir. Adicionar apenas conhecimento procedural que ele não possui.

### Fase 3: Arquitetura da Habilidade

**Objetivo:** Definir a estrutura baseada no tipo de habilidade.

Consultar `references/arquiteturas.md` para escolher o padrão apropriado:

| Tipo de Habilidade | Quando Usar | Estrutura |
|--------------------|-------------|-----------|
| Baseada em Fluxo | Processos sequenciais com passos definidos | Árvore de decisão → Passo 1 → Passo 2... |
| Baseada em Tarefas | Coleção de operações independentes | Referência rápida → Tarefa A → Tarefa B... |
| Referência/Diretrizes | Padrões, especificações, regras | Visão geral → Diretrizes → Especificações |
| Baseada em Capacidades | Sistema com funcionalidades integradas | Capacidades → Recurso 1 → Recurso 2... |

### Fase 4: Implementação

**Objetivo:** Criar os arquivos da habilidade.

#### 4.1 Inicializar Estrutura

```bash
python scripts/forge_init.py <nome-da-habilidade> --path <diretorio-destino>
```

#### 4.2 Escrever o Frontmatter

O frontmatter é o GATILHO da habilidade. É a única coisa visível antes da ativação.

```yaml
---
name: nome-em-kebab-case
description: "[O QUE FAZ] + [QUANDO USAR com exemplos específicos]"
---
```

**Descrição efetiva inclui:**
- Capacidade principal em uma frase
- Lista numerada de cenários de ativação
- Palavras-chave que o usuário provavelmente usará

Consultar `references/frontmatter-exemplos.md` para modelos.

#### 4.3 Escrever o Corpo do SKILL.md

Seguir a estrutura progressiva:

```markdown
# Título da Habilidade

## Visão Geral
[1-2 frases sobre o que a habilidade permite]

## Referência Rápida
[Tabela de decisão quando há múltiplos caminhos]

## [Seção Principal 1]
[Instruções detalhadas com código quando aplicável]

## [Seção Principal 2]
[...]

## Recursos Incluídos
[Descrição de scripts/, references/, assets/ e quando usar cada um]
```

**Regras de escrita:**
- Usar forma imperativa ("Executar", "Criar", não "Você deve executar")
- Marcar armadilhas com `**CRITICAL:**` em negrito
- Preferir exemplos de código a explicações verbosas
- Nunca duplicar informação entre SKILL.md e references/

#### 4.4 Criar Recursos Complementares

**Scripts (`scripts/`):**
- Testar cada script executando-o
- Incluir docstring com uso e exemplos
- Usar argumentos de linha de comando para flexibilidade

**Referências (`references/`):**
- Criar apenas quando informação é grande demais para SKILL.md
- Incluir padrões de busca com grep se arquivo for extenso
- Referenciar explicitamente no SKILL.md com indicação de quando ler

**Ativos (`assets/`):**
- Templates devem estar prontos para uso
- Incluir README mínimo dentro da pasta se estrutura for complexa

#### 4.5 Validar

```bash
python scripts/forge_validate.py <caminho-da-habilidade>
```

### Fase 5: Teste e Iteração

**Objetivo:** Garantir que a habilidade funciona na prática.

1. Simular cada exemplo de uso da Fase 1
2. Verificar se a descrição ativa a habilidade corretamente
3. Testar scripts com entradas variadas
4. Identificar lacunas ou instruções confusas
5. Refinar baseado nos resultados

Quando satisfeito, empacotar:

```bash
python scripts/forge_package.py <caminho-da-habilidade> --output <diretorio>
```

## Antipadrões — O Que Evitar

| Antipadrão | Por Que é Ruim | O Que Fazer |
|------------|----------------|-------------|
| README.md, CHANGELOG.md | Poluição do contexto | Apenas SKILL.md e recursos essenciais |
| Explicar conceitos básicos | Claude já sabe | Focar em conhecimento procedural específico |
| Descrição vaga no frontmatter | Habilidade não ativa | Incluir cenários e palavras-chave específicas |
| Duplicar info entre arquivos | Tokens desperdiçados | Cada informação em um único lugar |
| Scripts não testados | Falhas em produção | Testar cada script antes de incluir |
| Instruções opcionais como "pode" | Ambiguidade | Usar imperativo: "fazer" ou "não fazer" |

## Recursos Desta Habilidade

### Scripts Disponíveis

| Script | Função |
|--------|--------|
| `scripts/forge_init.py` | Inicializa estrutura de nova habilidade |
| `scripts/forge_validate.py` | Valida estrutura e conteúdo |
| `scripts/forge_package.py` | Empacota em arquivo .skill |
| `scripts/forge_analyze.py` | Analisa habilidade existente e sugere melhorias |

### Referências Disponíveis

| Arquivo | Conteúdo |
|---------|----------|
| `references/arquiteturas.md` | Padrões de estrutura detalhados |
| `references/frontmatter-exemplos.md` | Modelos de descrições efetivas |
| `references/padroes-codigo.md` | Templates para código em SKILL.md |
| `references/checklist-qualidade.md` | Lista de verificação antes de publicar |

### Templates Disponíveis

| Template | Uso |
|----------|-----|
| `assets/templates/skill-fluxo.md` | Habilidades baseadas em fluxo de trabalho |
| `assets/templates/skill-tarefas.md` | Habilidades baseadas em tarefas |
| `assets/templates/skill-referencia.md` | Habilidades de diretrizes |
