# Exemplos de Frontmatter Efetivos

O frontmatter é o **gatilho** da habilidade. A descrição é a única informação que o Claude vê antes de decidir se carrega a habilidade completa. Uma descrição efetiva determina se a habilidade será acionada nos momentos certos.

## Anatomia de uma Descrição Efetiva

```
[CAPACIDADE PRINCIPAL] + [CENÁRIOS DE ATIVAÇÃO ESPECÍFICOS]
```

A descrição deve responder duas perguntas:
1. **O que esta habilidade faz?** (capacidade)
2. **Quando devo usá-la?** (gatilhos)

---

## Exemplos de Descrições Efetivas

### Exemplo 1: Habilidade de Documentos

```yaml
---
name: docx
description: "Criação, edição e análise abrangente de documentos com suporte para controle de alterações, comentários, preservação de formatação e extração de texto. Usar quando Claude precisar trabalhar com documentos profissionais (arquivos .docx) para: (1) Criar novos documentos, (2) Modificar ou editar conteúdo, (3) Trabalhar com controle de alterações, (4) Adicionar comentários, ou qualquer outra tarefa de documentos"
---
```

**Por que funciona:**
- Começa com capacidade abrangente
- Lista cenários numerados
- Inclui formato de arquivo (.docx)
- Termina com "qualquer outra tarefa" para capturar casos não listados

### Exemplo 2: Habilidade de Design

```yaml
---
name: frontend-design
description: "Criar interfaces frontend distintivas e de qualidade profissional com alto padrão de design. Usar quando o usuário pedir para construir componentes web, páginas, artefatos, pôsteres ou aplicações (exemplos incluem websites, landing pages, dashboards, componentes React, layouts HTML/CSS, ou quando estilizar/embelezar qualquer interface web). Gera código criativo e polido que evita estéticas genéricas de IA."
---
```

**Por que funciona:**
- Descreve o resultado (interfaces distintivas)
- Lista múltiplos tipos de saída (componentes, páginas, etc.)
- Inclui exemplos concretos entre parênteses
- Menciona diferencial (evita estéticas genéricas)

### Exemplo 3: Habilidade de Planilhas

```yaml
---
name: xlsx
description: "Criação, edição e análise abrangente de planilhas com suporte para fórmulas, formatação, análise de dados e visualização. Usar quando Claude precisar trabalhar com planilhas (.xlsx, .xlsm, .csv, .tsv, etc) para: (1) Criar novas planilhas com fórmulas e formatação, (2) Ler ou analisar dados, (3) Modificar planilhas existentes preservando fórmulas, (4) Análise e visualização de dados em planilhas, ou (5) Recalcular fórmulas"
---
```

**Por que funciona:**
- Lista extensões de arquivo específicas
- Cenários numerados cobrem casos principais
- Menciona preservação de fórmulas (diferencial importante)

### Exemplo 4: Habilidade de Criação de Habilidades

```yaml
---
name: skill-forge
description: "Sistema avançado para criar habilidades altamente efetivas para o Claude Code. Usar quando o usuário quiser: (1) Criar uma nova habilidade do zero, (2) Melhorar ou refatorar uma habilidade existente, (3) Analisar a qualidade de uma habilidade, (4) Entender como estruturar conhecimento procedural para agentes de inteligência artificial. Esta habilidade guia todo o processo desde a descoberta de requisitos até o empacotamento final."
---
```

**Por que funciona:**
- Identifica o produto (Claude Code)
- Cenários cobrem criação, melhoria e análise
- Menciona o processo completo (descoberta até empacotamento)

---

## Padrões de Estrutura

### Padrão A: Capacidade + Lista Numerada

```yaml
description: "[Capacidade principal]. Usar quando [contexto] para: (1) [cenário], (2) [cenário], (3) [cenário], ou [categoria genérica]"
```

### Padrão B: Capacidade + Exemplos entre Parênteses

```yaml
description: "[Capacidade principal]. Usar quando [contexto] (exemplos incluem [exemplo1], [exemplo2], [exemplo3], ou quando [ação genérica])"
```

### Padrão C: Capacidade + Gatilhos Específicos

```yaml
description: "[Capacidade principal] para [formato/domínio específico]. Ativar quando o usuário mencionar [palavra-chave1], [palavra-chave2], ou [palavra-chave3]. Também usar para [caso de uso secundário]."
```

---

## Palavras-Chave de Alta Ativação

Incluir palavras que o usuário provavelmente usará:

| Domínio | Palavras-Chave Efetivas |
|---------|-------------------------|
| Documentos | criar documento, editar doc, Word, .docx, relatório, contrato |
| Planilhas | planilha, Excel, .xlsx, CSV, fórmulas, dados, tabela |
| Apresentações | slides, apresentação, PowerPoint, .pptx, deck |
| PDFs | PDF, formulário, preencher, mesclar, dividir, extrair |
| Frontend | website, página, componente, React, HTML, CSS, interface, UI |
| Dados | analisar, visualizar, gráfico, dashboard, métricas |

---

## Erros Comuns a Evitar

### Erro 1: Descrição Muito Genérica

❌ **Ruim:**
```yaml
description: "Ajuda com tarefas de documentos"
```

✅ **Bom:**
```yaml
description: "Criação e edição de documentos .docx com suporte para controle de alterações e comentários. Usar quando precisar criar, modificar ou analisar documentos do Word."
```

### Erro 2: Sem Cenários de Ativação

❌ **Ruim:**
```yaml
description: "Processa arquivos PDF de várias formas"
```

✅ **Bom:**
```yaml
description: "Processamento de PDF: mesclar, dividir, extrair texto, preencher formulários. Usar quando o usuário enviar um PDF e pedir para modificá-lo, extrair conteúdo, ou combinar múltiplos PDFs."
```

### Erro 3: Técnico Demais sem Contexto de Uso

❌ **Ruim:**
```yaml
description: "Implementa manipulação de XML para formato OOXML usando lxml e operações de arquivo ZIP"
```

✅ **Bom:**
```yaml
description: "Edição avançada de documentos Word preservando toda formatação original. Usar quando precisar fazer alterações cirúrgicas em .docx mantendo estilos, controle de alterações e comentários intactos."
```

### Erro 4: Descrição Muito Longa (mais de 1024 caracteres)

A descrição tem limite de 1024 caracteres. Priorizar informação de ativação sobre detalhes de implementação.

---

## Checklist de Validação de Descrição

Antes de finalizar a descrição, verificar:

- [ ] Responde "o que faz" claramente?
- [ ] Responde "quando usar" com cenários específicos?
- [ ] Inclui formatos de arquivo relevantes?
- [ ] Contém palavras-chave que o usuário usaria?
- [ ] Tem menos de 1024 caracteres?
- [ ] Não contém caracteres < ou >?
- [ ] Diferencia esta habilidade de outras similares?
