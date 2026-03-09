# Formatos Intermediarios — Handoff entre Stages

Schemas para dados trocados entre os stages do pipeline Skill Forge v3.

## Study Bundle index.json (Stage A → Stage B)

Manifesto do Study Bundle gerado pelo Estudador.

```json
{
  "tema": "nome-do-dominio",
  "data": "YYYY-MM-DD",
  "pipeline_mode": "full|abbreviated|skipped",
  "estilo_comunicacao": "arquitetural|estrategico|investigativo|didatico",
  "certeza_resumo": {
    "verdade_absoluta": 0,
    "provavel_forte": 0,
    "provavel_fraca": 0,
    "popular_sem_validacao": 0,
    "indeterminado": 0
  },
  "perfil_execucao": {
    "acesso_web": "total|parcial|indisponivel",
    "citacao": "links|textuais|sem_citacao",
    "ferramentas": true,
    "memoria_persistente": true
  },
  "arquivos": [
    "00-contexto.md",
    "01-matriz-afirmacoes.csv",
    "02-fontes.json",
    "03-controversias.md",
    "04-ausencias-alertas.md",
    "05-mapa-conhecimento.md",
    "06-manual-operacional.md",
    "07-pacote-especialista.md",
    "08-monitoramento.md"
  ],
  "gate_qualidade": {
    "diagnostico_especifico": true,
    "busca_3_niveis": true,
    "triangulacao_minima": true,
    "controversias_documentadas": true,
    "busca_ausencia": true,
    "grafo_construido": true,
    "produtos_nivel6": true,
    "certeza_comunicada": true,
    "limitacoes_declaradas": true
  }
}
```

**Campos criticos:**
- `pipeline_mode`: "full" (7 niveis), "abbreviated" (niveis 1-3), "skipped" (fast path)
- `certeza_resumo`: contagem de claims por nivel — informa Stage B sobre profundidade disponivel
- `gate_qualidade`: checklist preenchido — Stage B valida antes de iniciar

## dissection-manifest.json (Stage B → Stage C)

Manifesto do Dissection Package gerado pelo Dissector.

```json
{
  "topic": "domain-name",
  "study_bundle_path": "workspace/stage-a-study/YYYY-MM-DD/slug/",
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
    "architecture_justification": "Por que este padrao foi escolhido",
    "estimated_complexity": "simple|moderate|complex",
    "suggested_references": [
      {
        "filename": "nome-do-arquivo.md",
        "content_summary": "O que deve conter",
        "source_claims": ["claim_ids relevantes"]
      }
    ],
    "suggested_scripts": [
      {
        "filename": "nome-do-script.py",
        "purpose": "O que automatiza",
        "complexity": "simple|moderate"
      }
    ],
    "antipatterns": [
      {
        "description": "O que NAO fazer",
        "source": "controversia|ausencia|popular_sem_validacao",
        "severity": "critico|alto|medio"
      }
    ],
    "domain_knowledge_blocks": [
      {
        "topic": "Sub-topico",
        "certainty": "absoluta|provavel_forte|provavel_fraca",
        "claude_knows": false,
        "include_in_skill": true
      }
    ]
  }
}
```

**Campos criticos para o Forge:**
- `architecture_pattern`: pre-seleciona a arquitetura (Stage C Fase 3)
- `domain_knowledge_blocks` com `claude_knows: false`: conteudo que DEVE ir no SKILL.md
- `antipatterns`: viram a secao "Nao Faca" da skill
- `suggested_references`: geram os arquivos em references/

## triage.json (Triage Gate)

Resultado da triagem inicial.

```json
{
  "topic": "domain-name",
  "timestamp": "ISO8601",
  "signals": [
    {
      "signal": "APIs recentes/mutaveis",
      "score": 1,
      "evidence": "API mudou 3x nos ultimos 6 meses"
    }
  ],
  "total_score": 3,
  "path": "fast|medium|deep",
  "reasoning": "Justificativa da classificacao"
}
```

## pipeline-summary.json (Final)

Metricas consolidadas do pipeline completo.

```json
{
  "skill_name": "nome-da-skill",
  "pipeline_path": "fast|medium|deep",
  "timestamp_start": "ISO8601",
  "timestamp_end": "ISO8601",
  "stages": {
    "triage": {
      "score": 3,
      "path": "deep"
    },
    "study": {
      "pipeline_mode": "full",
      "claims_total": 24,
      "certainty_profile": {},
      "duration_ms": 0
    },
    "dissection": {
      "architecture_recommended": "workflow",
      "antipatterns_found": 5,
      "knowledge_blocks_new": 8,
      "duration_ms": 0
    },
    "forge": {
      "iteration_count": 2,
      "final_pass_rate": 0.92,
      "knowledge_accuracy": 0.88,
      "duration_ms": 0
    }
  },
  "total_duration_ms": 0,
  "total_tokens": 0
}
```
