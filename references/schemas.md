# Schemas JSON — Skill Forge

Schemas para padronizar dados de evals, grading, benchmarks e comparações.

## evals.json

Define os casos de teste para avaliação de uma skill.

```json
{
  "skill_name": "nome-da-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "Prompt que o usuário enviaria",
      "expected_output": "Descrição do resultado esperado",
      "files": ["caminho/para/arquivo-de-input.txt"],
      "assertions": [
        {
          "text": "O output contém uma tabela com 3 colunas",
          "type": "content"
        }
      ]
    }
  ]
}
```

**Campos:**
- `id`: Identificador único do eval (inteiro)
- `prompt`: O prompt exato que simula um pedido real do usuário
- `expected_output`: Descrição humana do que se espera (não precisa ser literal)
- `files`: Lista de arquivos de input necessários (pode ser vazia)
- `assertions`: Lista de asserções verificáveis — adicionar após primeira execução

## timing.json

Captura métricas de performance de cada execução.

```json
{
  "eval_id": 1,
  "configuration": "with_skill",
  "duration_ms": 12340,
  "total_tokens": 8567,
  "timestamp": "2026-03-08T14:30:00Z"
}
```

**Importante:** Quando um subagente completa, `total_tokens` e `duration_ms` vêm na notificação da tarefa. Salvar imediatamente — esses dados não são persistidos em nenhum outro lugar.

## grading.json

Resultado da avaliação de asserções por eval.

```json
{
  "eval_id": 1,
  "configuration": "with_skill",
  "expectations": [
    {
      "text": "O output contém uma tabela com 3 colunas",
      "passed": true,
      "evidence": "Tabela gerada com colunas: Nome, Tipo, Descrição"
    },
    {
      "text": "Todos os campos obrigatórios estão presentes",
      "passed": false,
      "evidence": "Campo 'versão' ausente no frontmatter"
    }
  ],
  "eval_feedback": [
    "Asserção 'tabela com 3 colunas' é fraca — passa mesmo se o conteúdo for errado. Sugerir verificar conteúdo das colunas."
  ],
  "pass_rate": 0.5
}
```

**Campos de expectations:**
- `text`: Texto exato da asserção (não usar `name`)
- `passed`: Booleano (não usar `met`)
- `evidence`: Evidência concreta do output (máx 125 caracteres, não usar `details`)

**Atenção:** Usar exatamente estes nomes de campo. O visualizador HTML depende deles.

## benchmark.json

Estatísticas agregadas de múltiplas execuções.

```json
{
  "skill_name": "nome-da-skill",
  "iteration": 1,
  "configurations": {
    "with_skill": {
      "pass_rate": { "mean": 0.85, "stddev": 0.12 },
      "duration_ms": { "mean": 15200, "stddev": 3100 },
      "total_tokens": { "mean": 9800, "stddev": 1500 }
    },
    "without_skill": {
      "pass_rate": { "mean": 0.60, "stddev": 0.20 },
      "duration_ms": { "mean": 18500, "stddev": 4200 },
      "total_tokens": { "mean": 12300, "stddev": 2100 }
    }
  },
  "delta": {
    "pass_rate": "+0.25",
    "duration_ms": "-3300",
    "total_tokens": "-2500"
  },
  "per_eval": [
    {
      "eval_id": 1,
      "with_skill_pass_rate": 1.0,
      "without_skill_pass_rate": 0.5,
      "notes": "Melhoria significativa na estrutura do output"
    }
  ],
  "analyst_notes": [
    "Eval 2 tem alta variância — possível flakiness na asserção de formatação",
    "Skill reduz tokens em ~20% mantendo qualidade superior"
  ]
}
```

## comparison.json

Resultado de comparação cega A/B entre dois outputs.

```json
{
  "eval_id": 1,
  "winner": "A",
  "rubric": {
    "content": {
      "relevancia": { "A": 4, "B": 3 },
      "precisao": { "A": 5, "B": 4 },
      "completude": { "A": 4, "B": 3 },
      "profundidade": { "A": 5, "B": 3 }
    },
    "structure": {
      "organizacao": { "A": 5, "B": 4 },
      "formatacao": { "A": 4, "B": 3 },
      "legibilidade": { "A": 5, "B": 4 },
      "exemplos": { "A": 4, "B": 2 }
    }
  },
  "score_A": 9,
  "score_B": 6,
  "reasoning": "Output A demonstra compreensão mais profunda...",
  "strengths_A": ["Exemplos concretos", "Estrutura clara"],
  "strengths_B": ["Mais conciso"],
  "key_differentiators": ["Profundidade de exemplos", "Organização"]
}
```

## analysis.json

Resultado da análise pós-comparação.

```json
{
  "comparison_summary": "Skill v2 venceu em 4 de 5 evals...",
  "instruction_scores": {
    "winner": 8,
    "loser": 5
  },
  "strengths": [
    {
      "skill": "winner",
      "description": "Segue formato de output especificado",
      "evidence": "Tabela gerada exatamente como descrito no SKILL.md"
    }
  ],
  "weaknesses": [
    {
      "skill": "loser",
      "description": "Ignora instrução de formato",
      "evidence": "Output em texto corrido, sem tabela"
    }
  ],
  "suggestions": [
    {
      "category": "instrucoes",
      "priority": "alta",
      "description": "Adicionar exemplo explícito de output esperado",
      "evidence": "Sem exemplo, o modelo improvisa o formato"
    },
    {
      "category": "exemplos",
      "priority": "media",
      "description": "Incluir caso edge de input vazio",
      "evidence": "Eval 3 falha quando input não tem dados"
    }
  ]
}
```

**Categorias válidas para sugestões:** `instrucoes`, `ferramentas`, `exemplos`, `tratamento_erros`, `estrutura`, `referencias`

**Prioridades:** `alta`, `media`, `baixa`

## history.json

Rastreia progressão entre iterações de melhoria.

```json
{
  "skill_name": "nome-da-skill",
  "versions": [
    {
      "iteration": 1,
      "pass_rate": 0.60,
      "timestamp": "2026-03-08T14:30:00Z",
      "changes": "Versão inicial"
    },
    {
      "iteration": 2,
      "pass_rate": 0.85,
      "parent_iteration": 1,
      "timestamp": "2026-03-08T15:00:00Z",
      "changes": "Adicionado exemplo de output, corrigido formato de tabela",
      "grading_result": "won"
    }
  ]
}
```

**Valores de grading_result:** `baseline` (primeira versão), `won` (melhorou), `lost` (piorou), `tie` (sem mudança significativa)

## feedback.json

Feedback do usuário coletado pelo visualizador HTML.

```json
{
  "skill_name": "nome-da-skill",
  "iteration": 1,
  "timestamp": "2026-03-08T16:00:00Z",
  "reviews": [
    {
      "eval_id": 1,
      "feedback": "O output está bom mas falta o cabeçalho da tabela"
    },
    {
      "eval_id": 2,
      "feedback": ""
    }
  ]
}
```

**Regra:** Feedback vazio significa que o eval está satisfatório. Quando todos os feedbacks estão vazios, a skill está pronta para empacotamento.

## trigger_evals.json

Queries para otimização de description (trigger/no-trigger).

```json
{
  "skill_name": "nome-da-skill",
  "queries": [
    {
      "id": 1,
      "prompt": "Crie um componente React com testes",
      "should_trigger": true,
      "set": "train"
    },
    {
      "id": 2,
      "prompt": "Qual a capital da França?",
      "should_trigger": false,
      "set": "test"
    }
  ],
  "split": {
    "train": 12,
    "test": 8,
    "ratio": "60/40"
  }
}
```

---

## Schemas do Pipeline v3

Os schemas abaixo são usados exclusivamente no pipeline integrado (Estudar → Dissecar → Construir).
Para detalhes completos e exemplos, ver `references/formatos-intermediarios.md`.

## triage.json

Resultado da triagem inicial do pipeline.

```json
{
  "topic": "domain-name",
  "timestamp": "ISO8601",
  "signals": [
    {
      "signal": "Nome do sinal",
      "score": 2,
      "evidence": "Justificativa"
    }
  ],
  "total_score": 3,
  "path": "fast|medium|deep",
  "reasoning": "Justificativa da classificacao"
}
```

## study-bundle/index.json

Manifesto do Study Bundle (Stage A → Stage B).

```json
{
  "tema": "nome-do-dominio",
  "data": "YYYY-MM-DD",
  "pipeline_mode": "full|abbreviated|skipped",
  "certeza_resumo": {
    "verdade_absoluta": 0,
    "provavel_forte": 0,
    "provavel_fraca": 0,
    "popular_sem_validacao": 0,
    "indeterminado": 0
  },
  "arquivos": ["00-contexto.md", "..."],
  "gate_qualidade": {
    "diagnostico_especifico": true,
    "busca_3_niveis": true,
    "triangulacao_minima": true
  }
}
```

## dissection-manifest.json

Manifesto do Dissection Package (Stage B → Stage C).

```json
{
  "topic": "domain-name",
  "study_bundle_path": "workspace/stage-a-study/...",
  "pipeline_mode": "full|abbreviated",
  "certainty_profile": {
    "absolute_truths": 0,
    "strong_probable": 0,
    "weak_probable": 0,
    "popular_unvalidated": 0,
    "undetermined": 0
  },
  "extracted_methodology": {
    "process_map": "01-process-map.md",
    "operational_principles": "02-operational-principles.md",
    "tools_and_resources": "03-tools-and-resources.md",
    "replicable_model": "04-replicable-model.md",
    "validation_tests": "05-validation-tests.md"
  },
  "skill_recommendations": {
    "architecture_pattern": "workflow|task-based|reference|capability-based",
    "estimated_complexity": "simple|moderate|complex",
    "suggested_references": [],
    "suggested_scripts": [],
    "antipatterns": [],
    "domain_knowledge_blocks": []
  }
}
```

## pipeline-summary.json

Métricas consolidadas do pipeline completo.

```json
{
  "skill_name": "nome-da-skill",
  "pipeline_path": "fast|medium|deep",
  "timestamp_start": "ISO8601",
  "timestamp_end": "ISO8601",
  "stages": {
    "triage": { "score": 3, "path": "deep" },
    "study": {
      "pipeline_mode": "full",
      "claims_total": 24,
      "certainty_profile": {}
    },
    "dissection": {
      "architecture_recommended": "workflow",
      "antipatterns_found": 5,
      "knowledge_blocks_new": 8
    },
    "forge": {
      "iteration_count": 2,
      "final_pass_rate": 0.92,
      "knowledge_accuracy": 0.88
    }
  }
}
```
