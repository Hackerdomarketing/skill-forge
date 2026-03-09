# Skill Forge v3

Sistema completo para criar, testar e otimizar skills do Claude Code.

Combina design rigoroso com validacao empirica e pipeline de rigor epistemico.

## Instalacao

### Passo 1 — Clonar na pasta de skills do Claude Code

```bash
git clone https://github.com/Hackerdomarketing/skill-forge.git ~/.claude/skills/skill-forge
```

### Passo 2 — Instalar triggers de ativacao automatica

```bash
python3 ~/.claude/skills/skill-forge/scripts/forge_deploy.py --setup
```

Isso adiciona os triggers no seu `~/.claude/CLAUDE.md` para que frases como "crie uma skill", "extraia metodo" ou "transforme em processo" ativem o Skill Forge automaticamente.

Pronto. O Skill Forge ja esta funcionando.

## Como usar

Abra o Claude Code e diga qualquer uma destas frases:

| Frase | O que acontece |
|-------|---------------|
| "crie uma skill para X" | Triage Gate avalia complexidade e escolhe o caminho |
| "estude esse dominio" | Stage A — estudo profundo antes de construir |
| "extraia a metodologia" | Stage B — disseca processos de um conhecimento |
| "transforme em metodo" | Stage B — extrai metodo de um corpo de conhecimento |
| "melhore essa skill" | Refatora uma skill existente |
| "teste essa skill" | Roda evals e benchmarks |
| "compare versoes" | Compara duas versoes de uma skill |

## Pipeline

```
TRIAGE GATE (fast / medium / deep)
  → Stage A: Estudador (study bundle)
  → Stage B: Dissector (dissection package)
  → Stage C: Forge (6 fases de construcao)
```

| Caminho | Quando | Stages |
|---------|--------|--------|
| **Fast** | Skill simples, dominio conhecido | Triage → Stage C |
| **Medium** | Complexidade moderada | Triage → Stage A abreviado → Stage C |
| **Deep** | Skill complexa, dominio novo | Triage → Stage A completo → Stage B → Stage C |

## Estrutura

```
skill-forge/
├── SKILL.md                  # Documentacao completa do protocolo
├── agents/                   # Agentes especializados do pipeline
│   ├── triagista.md          # Classifica complexidade
│   ├── dissector.md          # Extrai metodologias
│   ├── analisador.md         # Analisa skills existentes
│   ├── avaliador.md          # Avalia qualidade
│   └── comparador.md         # Compara versoes
├── scripts/                  # Ferramentas de automacao
│   ├── forge_deploy.py       # Deploy e setup (--setup, --project, --all)
│   ├── forge_init.py         # Scaffold de nova skill
│   ├── forge_validate.py     # Validacao de estrutura
│   ├── forge_package.py      # Empacota skill em .skill
│   ├── forge_eval.py         # Evals automatizados
│   ├── forge_benchmark.py    # Benchmarks A/B
│   ├── forge_analyze.py      # Analise de skill existente
│   ├── forge_optimize.py     # Otimizacao de triggers
│   ├── forge_triage.py       # Triage automatizado
│   └── forge_pipeline.py     # Pipeline orquestrador
├── references/               # Documentacao de referencia
│   ├── arquiteturas.md       # Padroes de arquitetura
│   ├── checklist-qualidade.md
│   ├── frontmatter-exemplos.md
│   ├── padroes-codigo.md
│   ├── protocolo-estudador.md
│   ├── protocolo-dissector.md
│   └── schemas.md
└── assets/                   # Templates
    ├── template-study-bundle/
    └── template-dissection/
```

## Deploy em projetos

Para integrar o Skill Forge em projetos que usam agentes construtores:

```bash
# Deploy em um projeto (injeta CLAUDE.md + agentes)
python3 ~/.claude/skills/skill-forge/scripts/forge_deploy.py --project /caminho/projeto

# Simular antes
python3 ~/.claude/skills/skill-forge/scripts/forge_deploy.py --project /caminho/projeto --dry-run

# Deploy com git push automatico
python3 ~/.claude/skills/skill-forge/scripts/forge_deploy.py --project /caminho/projeto --git-push

# Re-deploy em todos os projetos registrados
python3 ~/.claude/skills/skill-forge/scripts/forge_deploy.py --all --git-push
```

## Licenca

MIT
