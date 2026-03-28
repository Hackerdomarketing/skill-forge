# Protocolo Stage 0 — Normalizador de Input

Protocolo completo para Stage 0 do pipeline Skill Forge v3.
Executado ANTES do Triage Gate quando o input é conversa bruta ou pesquisa não estruturada.

## Quando Stage 0 se aplica

Stage 0 é ativado quando o usuário fornece:
- Conversa exportada de LLM (ChatGPT, Claude, Gemini, etc.)
- Transcrição de sessão iterativa onde ideias evoluíram
- Pesquisa bruta não formatada como Study Bundle
- Combinação de conversa + pesquisa no mesmo documento

Stage 0 NÃO se aplica quando:
- O usuário está construindo uma skill do zero (ir direto ao Triage Gate)
- O input já é um Study Bundle estruturado (ir direto ao Stage A ou B)

---

## Fase 1 — Classificação do Input

Identificar o tipo predominante do input antes de qualquer processamento.

### Sinais de Conversa Iterativa

- Estrutura de turnos detectável (Usuário/Assistente, Human/AI, ou similar)
- Linguagem de mudança: "agora muda", "adiciona", "tira isso", "volta para", "ajusta"
- Múltiplas versões do mesmo objeto ao longo do texto
- Instruções em primeira pessoa com expectativa de resposta
- Refinamentos sequenciais do mesmo conceito

### Sinais de Pesquisa Estruturada

- Voz única ou objetiva sem turnos
- Afirmações declarativas com fontes, dados ou evidências
- Sem versioning — conteúdo é declarativo, não iterativo
- Estrutura em seções, headers, tópicos
- Linguagem de terceira pessoa ou impessoal

### Classificação

```
Turnos detectáveis + linguagem de mudança → CONVERSA
Voz única + declarativo + sem versioning  → PESQUISA
Ambos presentes no mesmo documento        → MISTO
```

### Roteamento por tipo

| Tipo | Ação |
|------|------|
| Pesquisa | Pré-formatar como Study Bundle → Stage A |
| Conversa | Executar Fases 2-6 deste protocolo |
| Misto | Separar blocos por tipo → processar cada um → unificar outputs |

---

## Fase 2 — Segmentação de Objetos

Identificar os "objetos" sendo desenvolvidos na conversa.

Um objeto é qualquer elemento que possui múltiplas versões ao longo da conversa:
- Um texto, copy, headline, argumento
- Um processo, método, framework, estrutura
- Um conceito, definição, modelo mental
- Uma lista de itens, regras, princípios

**Como identificar:**
- Nomear cada objeto pelo que ele representa ("headline da oferta", "estrutura do método", "regra de precificação")
- Um objeto pode ter sub-objetos se partes foram iteradas independentemente
- Objetos que aparecem apenas uma vez e nunca são revisitados são contexto, não objetos iterados

**Output desta fase:** Lista nomeada de objetos identificados na conversa.

---

## Fase 3 — Timeline de Versões

Para cada objeto identificado, construir a sequência de versões em ordem cronológica.

Cada versão recebe:
- `v_id`: identificador sequencial (v1, v2, v3...)
- `conteudo`: o estado do objeto nessa versão
- `posicao`: onde na conversa essa versão aparece
- `tipo_transicao`: como se chegou a essa versão (ver tabela abaixo)

### Os 7 Padrões de Iteração

| # | Padrão | Sinais de Detecção | Tipo de Nó |
|---|--------|--------------------|------------|
| 1 | **Evolução linear** | Melhorias sequenciais sem rollback. "agora", "adiciona", "inclui também", "melhora" | `evolucao` |
| 2 | **Regressão deliberada** | "volta para", "prefiro como estava", "a versão anterior era melhor", "desfaz", insatisfação explícita com resultado testado | `regressao` |
| 3 | **Fusão seletiva** | "quero X da versão 2 com Y da versão 1", "combina", "mistura", "pega A de um e B de outro" | `fusao` |
| 4 | **Ramificação** | "tenta de outra forma", "e se fosse assim", "explora essa ideia", seguido de escolha explícita de um dos caminhos | `ramificacao` — marcar branch ativo e branch arquivado |
| 5 | **Abandono parcial** | Elemento adicionado deixa de ser mencionado; nova adição incompatível com ele; insatisfação sem remoção explícita | `abandono_implicito` — confidence: media/baixa |
| 6 | **Retorno com modificação** | "como estava mas muda só X", "volta para V1 mas adiciona Y de V3", cherry-pick explícito | `retorno_modificado` |
| 7 | **Invalida premissa** | Insight tardio que contradiz fundamento anterior: "percebo agora que", "na verdade", "isso muda tudo", mudança de entendimento fundamental | `invalida_premissa` — marcar premissas afetadas |

---

## Fase 4 — Construção do Grafo de Versões

Para cada objeto, montar o grafo de versões usando as timelines da Fase 3.

```
Nós:  cada versão identificada
Arestas: transições entre versões, tipadas conforme Fase 3
Folha ativa: nó sem saída que está no caminho ativo (não arquivado)
```

### Resolução do Estado Canônico

Seguir o grafo de cada objeto até a **folha ativa**:

- `evolucao`: a versão mais recente na cadeia linear
- `regressao`: a versão reativada (pode ser uma versão anterior com pequeno delta)
- `fusao`: o nó de merge com os elementos especificados
- `ramificacao`: o branch escolhido explicitamente pelo usuário
- `abandono_implicito`: última versão explícita, com o elemento marcado como possivelmente removido
- `retorno_modificado`: versão anterior + delta aplicado
- `invalida_premissa`: última versão, com premissas afetadas marcadas para revisão

### Regra para Abandono Parcial (implícito)

Nunca marcar como remoção confirmada. Sempre:
1. Manter o elemento no estado canônico
2. Adicionar warning: "elemento X pode ter sido abandonado — confirmar com usuário"
3. Confidence da versão: `media` (sinais indiretos) ou `baixa` (apenas ausência de menção)

### Regra para Invalida Premissa

Este é o padrão mais perigoso. Ao detectar:
1. Identificar qual insight tardio invalida qual premissa anterior
2. Marcar as versões afetadas: `premissa_invalidada: true`
3. No estado canônico, aplicar o insight como reinterpretação retroativa
4. Adicionar warning de alto risco: "conclusão tardia [X] contradiz premissa [Y] — estado canônico pode estar incorreto sem revisão manual"

---

## Fase 5 — Validação de Premissas

Comparar premissas estabelecidas no início da conversa com conclusões do final.

**O que buscar:**
- Afirmações no início que contradizem insights do final
- Mudanças de objetivo ou critério de sucesso ao longo da conversa
- Restrições que foram removidas ou adicionadas depois

**Output:** Lista de conflitos premissa/conclusão, cada um com:
- Premissa original
- Insight que a invalida
- Impacto no estado canônico
- Nível de risco: `alto` (muda o output inteiro) | `medio` (afeta parte do output) | `baixo` (detalhe sem impacto central)

---

## Fase 6 — Montagem do Canonical State Bundle

Gerar o output estruturado que alimenta os stages seguintes.

### Arquivo: `canonical-state.json`

```json
{
  "input_type": "conversa|pesquisa|misto",
  "objects": [
    {
      "id": "objeto-1",
      "name": "nome descritivo do objeto",
      "canonical_state": "conteúdo do estado final canônico",
      "evolution_pattern": "linear|regressao|fusao|ramificacao|abandono|retorno|invalida",
      "version_count": 0,
      "confidence": "alta|media|baixa",
      "warnings": []
    }
  ],
  "premissa_conflicts": [],
  "research_blocks": [],
  "recommended_handoff": "stage-a|dissector|stage-c",
  "handoff_justification": "razão da recomendação"
}
```

### Arquivo: `evolution-log.md`

Para cada objeto: tabela com versões, tipo de transição e o que mudou. Usado para auditoria e revisão manual.

```markdown
## [Nome do Objeto]

| Versão | Tipo | O que mudou | Posição na conversa |
|--------|------|-------------|---------------------|
| v1 | inicial | — | início |
| v2 | evolucao | adicionado X, removido Y | meio |
| v3 | regressao | voltou ao formato de v1 | final |

**Estado canônico:** v3 (baseado em v1, reativado por escolha explícita)
**Confidence:** alta
```

---

## Roteamento para Stages Seguintes

Com o Canonical State Bundle gerado:

| Situação | Handoff recomendado |
|----------|---------------------|
| Objetos são metodologias/processos complexos | Dissector (Stage B) |
| Objetos são conhecimento de domínio | Estudador (Stage A) |
| Objetos são componentes diretos de uma skill | Stage C direto |
| Misto com blocos de pesquisa | Stage A para pesquisa + Dissector/Stage C para conversas |

Apresentar ao usuário: "Identifiquei [N] objetos com padrão [padrão]. Estado canônico extraído. Recomendo [handoff] porque [razão]. Quer seguir assim?"

---

## Regras Críticas

1. **Abandono parcial nunca é certeza.** Sempre manter + warning, nunca remover silenciosamente.
2. **Invalida premissa tem prioridade máxima.** Detectar antes de resolver qualquer estado canônico.
3. **Confidence baixa bloqueia handoff automático.** Se qualquer objeto tem confidence baixa, perguntar ao usuário antes de prosseguir.
4. **Ramificações arquivadas são preservadas.** Não descartar — podem ser úteis em fusões futuras.
5. **Pesquisa embutida em conversa é extraída.** Blocos declarativos dentro de conversas vão para `research_blocks`, não para o grafo de versões.
6. **Máximo 7 objetos por bundle.** Se detectar mais, agrupar por afinidade ou perguntar ao usuário o que priorizar.
