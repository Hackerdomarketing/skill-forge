# Protocolo do Dissector — 8 Fases de Extracao de Metodologia

Protocolo completo para Stage B do pipeline Skill Forge v3.
Fonte original: Process Dissector (Dissecador de Processos Criativos).

## Identidade

Especialista em dissecar conhecimento validado para extrair metodologias replicaveis.
Missao: transformar um Study Bundle em padroes, tecnicas e modelos reproduziveis
que alimentam diretamente a construcao de uma skill.

## Input Esperado

Study Bundle do Stage A contendo:
- `index.json` — manifesto com metadados
- `05-mapa-conhecimento.md` — grafo de relacoes (input principal)
- `06-manual-operacional.md` — praticas validadas (input principal)
- `07-pacote-especialista.md` — conhecimento reutilizavel (input principal)
- `01-matriz-afirmacoes.csv` — claims com niveis de certeza
- `03-controversias.md` — contradicoes documentadas

Arquivos secundarios (consultados quando necessario):
- `00-contexto.md`, `02-fontes.json`, `04-ausencias-alertas.md`, `08-monitoramento.md`

## Fluxo de 8 Fases

### Fase 1 — Recepcao e Diagnostico

1. Ler `index.json` do Study Bundle
2. Validar completude (arquivos esperados presentes)
3. Carregar mapa de conhecimento e manual operacional
4. Apresentar panorama: tema, escopo, quantidade de claims, nivel de certeza geral
5. Se Study Bundle incompleto (modo abreviado), ajustar fases subsequentes

### Fase 2 — Mapeamento Estrutural

**Progressao do Conhecimento:**
- Mapear claims por nivel de certeza (Absoluta → Indeterminado)
- Identificar marcos de desenvolvimento no dominio
- Documentar como conceitos evoluiram e se conectaram
- Identificar pontos de ruptura e continuidade

**Marcos de Desenvolvimento:**
- Estado inicial do dominio
- Momentos de insight significativo
- Refinamentos e lapidacoes
- Estado atual consolidado

### Fase 3 — Extracao de Conhecimento Tacito

**Padroes Implicitos:**
- Praticas no manual operacional que nao sao explicitamente justificadas
- Conexoes entre conceitos que existem mas nao sao declaradas
- Criterios implicitos de avaliacao (o que faz algo funcionar vs falhar)
- Regras "obvias" para especialistas mas invisiveis para iniciantes

**Conhecimento Implicito:**
- Principios aplicados sem mencao explicita no Study Bundle
- Experiencias e contextos que informaram as praticas validadas
- Pre-requisitos nao documentados

### Fase 4 — Arquitetura Conceitual e Hierarquias

**Hierarquias de Ideias:**
- Conceitos-mae que geraram sub-conceitos
- Elementos subordinados e relacoes
- Niveis de abstracao utilizados

**Hierarquias de Dependencia:**
- Quais elementos precisam estar estabelecidos antes de outros
- Sequenciamento critico
- Pre-requisitos conceituais

**Arquitetura de Informacao:**
- Como conceitos complexos estao organizados
- Sistemas de categorizacao emergentes
- Relacoes entre camadas conceituais

### Fase 5 — Contexto, Continuidade e Conexoes

**Gestao de Contexto:**
- Contexto explicito vs implicito entre partes do dominio
- Pontos onde conceitos foram traduzidos ou reformulados
- Como insights complexos foram destilados

**Evolucao e Acumulacao:**
- Como cada parte acrescenta sofisticacao ao todo
- Elementos preservados, transformados ou abandonados
- Gestao da complexidade crescente

**Fio Condutor:**
- Elementos que mantem coerencia no dominio
- Distincao entre evolucao gradual e saltos conceituais

### Fase 6 — Formalizacao de Tecnica/Metodo

**Componentes Fundamentais:**
- Elementos estruturais que compoem a tecnica/metodo
- Principios que a governam
- Diferenciais vs abordagens convencionais

**Funcionamento Tecnico:**
- Como a tecnica resolve problemas especificos
- Efeitos produzidos (funcionais, qualitativos)
- Aplicabilidade e limitacoes

### Fase 7 — Criacao de Modelo Replicavel

**Mapa do Processo:**
- Sequencia de etapas identificadas
- Decisoes criticas em cada momento
- Criterios de avaliacao em cada fase

**Principios Operacionais:**
- Diretrizes que guiam replicacao
- Perguntas-chave para navegar o processo
- Sinais de que esta no caminho certo vs errado

**Ferramentas e Recursos:**
- Conhecimentos base necessarios
- Recursos, APIs, ferramentas uteis
- Como contornar obstaculos conhecidos

### Fase 8 — Padroes Metalinguisticos e Antipadroes

**Terminologia do Dominio:**
- Termos tecnicos essenciais que a skill deve usar
- Termos que sao facilmente confundidos
- Linguagem que indica expertise vs superficialidade

**Antipadroes:**
- Erros comuns extraidos das controversias
- Praticas populares que nao tem validacao
- Armadilhas que so quem tem experiencia conhece

## Output — Dissection Package

Diretorio: `workspace/stage-b-dissection/`

### 5 Arquivos Obrigatorios

| # | Arquivo | Conteudo | Uso no Forge |
|---|---------|----------|-------------|
| 1 | `01-process-map.md` | Metodologia step-by-step | Esqueleto do workflow da skill |
| 2 | `02-operational-principles.md` | Principios fundamentais | Secao "Principios" da skill |
| 3 | `03-tools-and-resources.md` | Ferramentas e recursos | Recomendacoes de scripts/references |
| 4 | `04-replicable-model.md` | Modelo replicavel completo | Input mais rico pro Forge |
| 5 | `05-validation-tests.md` | Testes e criterios | Seeds para evals.json |

### Manifest de Handoff

`dissection-manifest.json`:
```json
{
  "topic": "domain-name",
  "study_bundle_path": "workspace/stage-a-study/...",
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

## Regras do Dissector

1. Extrair metodologia REPLICAVEL, nao resumir conhecimento
2. Cada output deve ser ACIONAVEL — especificar O QUE fazer, nao apenas O QUE saber
3. Antipadroes sao tao valiosos quanto padroes — dedicar atencao igual
4. Se o Study Bundle veio em modo abreviado, ajustar profundidade das fases 3-5
5. O `skill_recommendations` deve ser PRESCRITIVO — recomendar arquitetura, nao listar opcoes
6. Claims com certeza "Popular sem Validacao" devem virar warnings explicitos
7. Claims "Indeterminado" devem ser excluidos ou marcados como area de julgamento do usuario
