#!/usr/bin/env python3
"""
Forge Init — Inicializa estrutura de nova habilidade

Uso:
    forge_init.py <nome-da-habilidade> [--path <diretorio-destino>] [--local] [--pipeline-mode fast|medium|deep] [--from-dissection <manifest.json>]

Exemplos:
    forge_init.py minha-habilidade                          # instala em ~/.claude/skills/ (global)
    forge_init.py minha-habilidade --local                  # instala em .claude/skills/ (projeto atual)
    forge_init.py processador-pdf --path /caminho/absoluto  # caminho customizado
    forge_init.py api-segura --pipeline-mode deep
    forge_init.py api-segura --from-dissection workspace/stage-b-dissection/dissection-manifest.json

O script cria:
    nome-da-habilidade/
    ├── SKILL.md (template com TODOs)
    ├── scripts/ (com exemplo)
    ├── references/ (com exemplo)
    ├── assets/ (com exemplo)
    └── workspace/ (se --pipeline-mode medium ou deep)
        ├── stage-a-study/ (se medium ou deep)
        ├── stage-b-dissection/ (se deep)
        └── triage.json (template)
"""

import argparse
import json
import platform
import sys
import re
from pathlib import Path
from datetime import datetime, timezone


SKILL_TEMPLATE = '''---
name: {skill_name}
description: "[TODO: Descrever O QUE a habilidade faz E QUANDO usar. Incluir cenários específicos de ativação, formatos de arquivo relevantes, e palavras-chave que o usuário provavelmente usará. Máximo 1024 caracteres.]"
---

# {skill_title}

## Visão Geral

[TODO: 1-2 frases explicando o que esta habilidade permite realizar]

## Referência Rápida

[TODO: Adicionar tabela de decisão se houver múltiplos caminhos, ou remover esta seção]

| Situação | Ação |
|----------|------|
| [Cenário 1] | [O que fazer] |
| [Cenário 2] | [O que fazer] |

## [TODO: Primeira Seção Principal]

[TODO: Adicionar conteúdo. Opções de estrutura:

**Baseada em Fluxo** (processos sequenciais):
- Árvore de decisão → Passo 1 → Passo 2...

**Baseada em Tarefas** (operações independentes):
- Referência rápida → Tarefa A → Tarefa B...

**Referência/Diretrizes** (padrões e regras):
- Princípios → Diretrizes → Especificações...

**Baseada em Capacidades** (sistema integrado):
- Capacidades → Recurso 1 → Recurso 2...

Ver references/arquiteturas.md no skill-forge para detalhes.]

## Recursos Incluídos

### Scripts (`scripts/`)

[TODO: Listar scripts incluídos e quando usar cada um, ou remover se não houver scripts]

| Script | Função |
|--------|--------|
| `exemplo.py` | [Descrição] |

### Referências (`references/`)

[TODO: Listar arquivos de referência e quando consultar cada um, ou remover se não houver]

| Arquivo | Quando Consultar |
|---------|------------------|
| `exemplo.md` | [Situação] |

### Ativos (`assets/`)

[TODO: Listar ativos disponíveis e como são usados, ou remover se não houver]

---

**Remover todas as seções TODO e este bloco antes de finalizar.**
'''


SKILL_TEMPLATE_FROM_DISSECTION = '''---
name: {skill_name}
description: "{description}"
---

# {skill_title}

## Visão Geral

{overview}

## Princípios Fundamentais

{principles}

## Referência Rápida

| Situação | Ação |
|----------|------|
| [TODO: Cenário 1] | [O que fazer] |
| [TODO: Cenário 2] | [O que fazer] |

## Processo

{process_summary}

## Antipadrões

{antipatterns}

## Recursos Incluídos

### Scripts (`scripts/`)

| Script | Função |
|--------|--------|
| `exemplo.py` | [TODO: Descrição] |

### Referências (`references/`)

{references_table}

### Ativos (`assets/`)

[TODO: Listar ativos disponíveis e como são usados, ou remover se não houver]

---

**Revisar e completar todas as seções TODO antes de finalizar.**
'''


EXAMPLE_SCRIPT = '''#!/usr/bin/env python3
"""
Script de exemplo para {skill_name}

Este é um placeholder. Substituir com implementação real ou deletar.

Uso:
    python scripts/exemplo.py <argumento>

Exemplo:
    python scripts/exemplo.py entrada.txt
"""

import sys


def main():
    if len(sys.argv) < 2:
        print("Uso: python scripts/exemplo.py <argumento>")
        print("\\nEste é um script de exemplo. Substituir com implementação real.")
        sys.exit(1)

    argumento = sys.argv[1]
    print(f"Processando: {{argumento}}")
    # TODO: Implementar lógica real
    print("Concluído!")


if __name__ == "__main__":
    main()
'''


EXAMPLE_REFERENCE = '''# Referência de Exemplo para {skill_title}

Este é um arquivo de referência placeholder. Substituir com conteúdo real ou deletar.

## Quando Usar Este Arquivo

Arquivos em `references/` são carregados no contexto apenas quando necessário.
Usar para:
- Documentação detalhada demais para SKILL.md
- Especificações técnicas extensas
- Guias de referência que nem sempre são necessários

## Estrutura Sugerida

### Para Documentação de API
- Visão geral
- Autenticação
- Endpoints com exemplos
- Códigos de erro
- Limites de uso

### Para Guias de Workflow
- Pré-requisitos
- Instruções passo a passo
- Padrões comuns
- Solução de problemas
- Melhores práticas

---

**Deletar este arquivo se não houver necessidade de referências.**
'''


EXAMPLE_ASSET = '''# Placeholder de Asset

Este arquivo representa onde ativos reais seriam armazenados.

Ativos são arquivos NÃO destinados a serem lidos no contexto,
mas sim usados na saída que o Claude produz.

## Tipos Comuns de Assets

- Templates: .pptx, .docx, diretórios de boilerplate
- Imagens: .png, .jpg, .svg
- Fontes: .ttf, .otf, .woff
- Dados: .csv, .json, .yaml

## Organização

Agrupar assets relacionados em subdiretórios quando necessário:

```
assets/
├── templates/
│   ├── relatorio.docx
│   └── apresentacao.pptx
├── imagens/
│   ├── logo.png
│   └── icones/
└── dados/
    └── configuracao.json
```

---

**Deletar este arquivo e adicionar assets reais, ou remover o diretório assets/ se não for necessário.**
'''


TRIAGE_TEMPLATE = {
    "topic": "",
    "timestamp": "",
    "signals": [],
    "total_score": 0,
    "path": "fast",
    "reasoning": "Skill inicializada com pipeline-mode. Preencher sinais e recalcular."
}


def get_default_skills_path() -> Path:
    """Retorna caminho global de skills baseado no OS.

    - macOS/Linux: ~/.claude/skills
    - Windows: %USERPROFILE%\\.claude\\skills
    """
    return Path.home() / '.claude' / 'skills'


def validar_nome(nome: str) -> tuple[bool, str]:
    """Valida o nome da habilidade segundo as regras."""
    if not nome:
        return False, "Nome não pode ser vazio"

    if len(nome) > 64:
        return False, f"Nome muito longo ({len(nome)} caracteres). Máximo: 64"

    if not re.match(r'^[a-z0-9-]+$', nome):
        return False, "Nome deve usar kebab-case (letras minúsculas, dígitos, hífens)"

    if nome.startswith('-') or nome.endswith('-'):
        return False, "Nome não pode começar ou terminar com hífen"

    if '--' in nome:
        return False, "Nome não pode conter hífens consecutivos"

    return True, "Nome válido"


def titulo_do_nome(nome: str) -> str:
    """Converte nome-kebab-case para Título Com Espaços."""
    return ' '.join(palavra.capitalize() for palavra in nome.split('-'))


def carregar_dissection_manifest(caminho_manifest: str) -> dict | None:
    """
    Carrega e valida um dissection-manifest.json.

    Args:
        caminho_manifest: Caminho para o arquivo dissection-manifest.json

    Returns:
        Dicionário com dados do manifest, ou None se erro
    """
    manifest_path = Path(caminho_manifest).resolve()

    if not manifest_path.exists():
        print(f"❌ Erro: Manifest não encontrado: {manifest_path}")
        return None

    try:
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao ler manifest JSON: {e}")
        return None

    # Validate required fields
    required = ['topic', 'extracted_methodology', 'skill_recommendations']
    for field in required:
        if field not in manifest:
            print(f"❌ Erro: Campo obrigatório ausente no manifest: {field}")
            return None

    return manifest


def gerar_skill_md_from_dissection(nome: str, titulo: str, manifest: dict) -> str:
    """
    Gera conteúdo do SKILL.md pré-populado a partir de um dissection manifest.

    Args:
        nome: Nome da habilidade em kebab-case
        titulo: Título da habilidade com espaços
        manifest: Dicionário do dissection-manifest.json

    Returns:
        Conteúdo formatado do SKILL.md
    """
    recs = manifest.get('skill_recommendations', {})
    certainty = manifest.get('certainty_profile', {})

    # Build description from topic and recommendations
    topic = manifest.get('topic', nome)
    arch = recs.get('architecture_pattern', 'capability-based')
    description = f"[TODO: Skill para {topic}. Padrão arquitetural recomendado: {arch}. Completar com cenários de ativação.]"

    # Build overview
    overview = f"Skill construída a partir de dissecação do domínio '{topic}'.\n"
    if recs.get('architecture_justification'):
        overview += f"Arquitetura: {arch} — {recs['architecture_justification']}\n"
    complexity = recs.get('estimated_complexity', 'moderate')
    overview += f"Complexidade estimada: {complexity}"

    # Build principles from domain knowledge blocks
    principles_lines = []
    knowledge_blocks = recs.get('domain_knowledge_blocks', [])
    for i, block in enumerate(knowledge_blocks[:7], 1):
        topic_name = block.get('topic', f'Princípio {i}')
        certainty_level = block.get('certainty', 'provavel_forte')
        principles_lines.append(f"{i}. **{topic_name}** — Certeza: {certainty_level}")
    if not principles_lines:
        principles_lines.append("[TODO: Definir princípios fundamentais]")
    principles = '\n'.join(principles_lines)

    # Build process summary from extracted methodology
    methodology = manifest.get('extracted_methodology', {})
    process_lines = []
    method_files = [
        ('process_map', 'Process Map'),
        ('operational_principles', 'Princípios Operacionais'),
        ('replicable_model', 'Modelo Replicável'),
    ]
    for key, label in method_files:
        filename = methodology.get(key)
        if filename:
            process_lines.append(f"- Consultar `workspace/stage-b-dissection/{filename}` para {label}")
    if not process_lines:
        process_lines.append("[TODO: Definir processo]")
    process_summary = '\n'.join(process_lines)

    # Build antipatterns
    antipatterns = recs.get('antipatterns', [])
    if antipatterns:
        ap_lines = ["| Antipadrão | Severidade | Fonte |", "|---|---|---|"]
        for ap in antipatterns:
            desc = ap.get('description', '')
            sev = ap.get('severity', 'medio')
            src = ap.get('source', '')
            ap_lines.append(f"| {desc} | {sev} | {src} |")
        antipatterns_text = '\n'.join(ap_lines)
    else:
        antipatterns_text = "[TODO: Listar antipadrões]"

    # Build references table
    suggested_refs = recs.get('suggested_references', [])
    if suggested_refs:
        ref_lines = ["| Arquivo | Quando Consultar |", "|---------|------------------|"]
        for ref in suggested_refs:
            fname = ref.get('filename', 'referencia.md')
            summary = ref.get('content_summary', '[TODO]')
            ref_lines.append(f"| `{fname}` | {summary} |")
        references_table = '\n'.join(ref_lines)
    else:
        references_table = "| Arquivo | Quando Consultar |\n|---------|------------------|\n| `exemplo.md` | [TODO] |"

    return SKILL_TEMPLATE_FROM_DISSECTION.format(
        skill_name=nome,
        skill_title=titulo,
        description=description,
        overview=overview,
        principles=principles,
        process_summary=process_summary,
        antipatterns=antipatterns_text,
        references_table=references_table,
    )


def criar_pipeline_dirs(diretorio_habilidade: Path, pipeline_mode: str, nome: str) -> bool:
    """
    Cria diretórios de pipeline e triage.json template.

    Args:
        diretorio_habilidade: Caminho raiz da habilidade
        pipeline_mode: Modo do pipeline (fast, medium, deep)
        nome: Nome da habilidade

    Returns:
        True se sucesso, False se erro
    """
    try:
        workspace = diretorio_habilidade / 'workspace'
        workspace.mkdir(exist_ok=True)
        print("✅ Criado workspace/")

        # Create triage.json template
        triage = TRIAGE_TEMPLATE.copy()
        triage['topic'] = nome
        triage['timestamp'] = datetime.now(timezone.utc).isoformat()
        triage['path'] = pipeline_mode

        triage_path = workspace / 'triage.json'
        triage_path.write_text(
            json.dumps(triage, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        print("✅ Criado workspace/triage.json")

        # Create stage-a-study/ for medium and deep
        if pipeline_mode in ('medium', 'deep'):
            stage_a = workspace / 'stage-a-study'
            stage_a.mkdir(exist_ok=True)
            print("✅ Criado workspace/stage-a-study/")

        # Create stage-b-dissection/ for deep only
        if pipeline_mode == 'deep':
            stage_b = workspace / 'stage-b-dissection'
            stage_b.mkdir(exist_ok=True)
            print("✅ Criado workspace/stage-b-dissection/")

        return True
    except Exception as e:
        print(f"❌ Erro ao criar diretórios de pipeline: {e}")
        return False


def criar_habilidade(nome: str, caminho: str, pipeline_mode: str | None = None,
                     from_dissection: str | None = None) -> Path | None:
    """
    Cria estrutura de diretórios e arquivos para nova habilidade.

    Args:
        nome: Nome da habilidade em kebab-case
        caminho: Diretório onde criar a habilidade
        pipeline_mode: Modo do pipeline (fast, medium, deep) ou None
        from_dissection: Caminho para dissection-manifest.json ou None

    Returns:
        Path do diretório criado, ou None se erro
    """
    # Validar nome
    valido, mensagem = validar_nome(nome)
    if not valido:
        print(f"❌ Erro: {mensagem}")
        return None

    # Determinar caminho completo
    diretorio_habilidade = Path(caminho).resolve() / nome

    # Verificar se já existe
    if diretorio_habilidade.exists():
        print(f"❌ Erro: Diretório já existe: {diretorio_habilidade}")
        return None

    # Load dissection manifest if provided
    manifest = None
    if from_dissection:
        manifest = carregar_dissection_manifest(from_dissection)
        if manifest is None:
            return None
        print(f"✅ Manifest de dissecação carregado: {from_dissection}")

    # Criar diretório principal
    try:
        diretorio_habilidade.mkdir(parents=True, exist_ok=False)
        print(f"✅ Criado diretório: {diretorio_habilidade}")
    except Exception as e:
        print(f"❌ Erro ao criar diretório: {e}")
        return None

    titulo = titulo_do_nome(nome)

    # Criar SKILL.md
    try:
        skill_md = diretorio_habilidade / 'SKILL.md'
        if manifest:
            conteudo = gerar_skill_md_from_dissection(nome, titulo, manifest)
        else:
            conteudo = SKILL_TEMPLATE.format(
                skill_name=nome,
                skill_title=titulo
            )
        skill_md.write_text(conteudo, encoding='utf-8')
        print("✅ Criado SKILL.md" + (" (pré-populado via dissecação)" if manifest else ""))
    except Exception as e:
        print(f"❌ Erro ao criar SKILL.md: {e}")
        return None

    # Criar scripts/
    try:
        scripts_dir = diretorio_habilidade / 'scripts'
        scripts_dir.mkdir()

        script_exemplo = scripts_dir / 'exemplo.py'
        script_exemplo.write_text(
            EXAMPLE_SCRIPT.format(skill_name=nome),
            encoding='utf-8'
        )
        script_exemplo.chmod(0o755)
        print("✅ Criado scripts/exemplo.py")
    except Exception as e:
        print(f"❌ Erro ao criar scripts/: {e}")
        return None

    # Criar references/
    try:
        references_dir = diretorio_habilidade / 'references'
        references_dir.mkdir()

        ref_exemplo = references_dir / 'exemplo.md'
        ref_exemplo.write_text(
            EXAMPLE_REFERENCE.format(skill_title=titulo),
            encoding='utf-8'
        )
        print("✅ Criado references/exemplo.md")
    except Exception as e:
        print(f"❌ Erro ao criar references/: {e}")
        return None

    # Criar assets/
    try:
        assets_dir = diretorio_habilidade / 'assets'
        assets_dir.mkdir()

        asset_exemplo = assets_dir / 'PLACEHOLDER.md'
        asset_exemplo.write_text(EXAMPLE_ASSET, encoding='utf-8')
        print("✅ Criado assets/PLACEHOLDER.md")
    except Exception as e:
        print(f"❌ Erro ao criar assets/: {e}")
        return None

    # Criar pipeline directories if pipeline-mode specified
    if pipeline_mode:
        if not criar_pipeline_dirs(diretorio_habilidade, pipeline_mode, nome):
            return None

    return diretorio_habilidade


def parse_args() -> argparse.Namespace:
    """Parse command line arguments using argparse."""
    parser = argparse.ArgumentParser(
        description="Forge Init — Inicializa estrutura de nova habilidade",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Requisitos do nome:
  - Kebab-case: letras minúsculas, dígitos, hífens
  - Máximo 64 caracteres
  - Não pode começar/terminar com hífen
  - Não pode ter hífens consecutivos

Exemplos:
  forge_init.py minha-habilidade                          # global (~/.claude/skills/)
  forge_init.py minha-habilidade --local                  # projeto atual (.claude/skills/)
  forge_init.py processador-pdf --path /caminho/custom    # caminho customizado
  forge_init.py api-segura --pipeline-mode deep
  forge_init.py api-segura --from-dissection manifest.json
"""
    )
    parser.add_argument(
        'nome',
        help="Nome da habilidade em kebab-case"
    )
    parser.add_argument(
        '--path',
        default=None,
        help="Diretório destino. Padrão: ~/.claude/skills/ (global, visível em todos os projetos)"
    )
    parser.add_argument(
        '--local',
        action='store_true',
        help="Instalar no projeto atual (.claude/skills/ — visível apenas neste projeto)"
    )
    parser.add_argument(
        '--pipeline-mode',
        choices=['fast', 'medium', 'deep'],
        default=None,
        help="Modo do pipeline. Cria diretórios adicionais: "
             "fast (workspace + triage.json), "
             "medium (+ stage-a-study/), "
             "deep (+ stage-a-study/ + stage-b-dissection/)"
    )
    parser.add_argument(
        '--from-dissection',
        default=None,
        metavar='MANIFEST_PATH',
        help="Caminho para dissection-manifest.json. "
             "Pré-popula o SKILL.md com dados extraídos da dissecação"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    nome = args.nome

    # Resolver caminho de instalacao
    if args.local and args.path:
        print("❌ Erro: Use --local OU --path, não ambos.")
        sys.exit(1)

    if args.local:
        caminho = str(Path.cwd() / '.claude' / 'skills')
        escopo = "local (visível apenas neste projeto)"
    elif args.path:
        caminho = args.path
        escopo = "customizado"
    else:
        caminho = str(get_default_skills_path())
        escopo = "global (visível em todos os projetos)"

    print(f"🔨 Forge Init: Criando habilidade '{nome}'")
    print(f"   Destino: {caminho}")
    print(f"   Escopo: {escopo}")
    if args.pipeline_mode:
        print(f"   Pipeline: {args.pipeline_mode}")
    if args.from_dissection:
        print(f"   Dissecação: {args.from_dissection}")
    print()

    resultado = criar_habilidade(
        nome, caminho,
        pipeline_mode=args.pipeline_mode,
        from_dissection=args.from_dissection
    )

    if resultado:
        print()
        print(f"✅ Habilidade '{nome}' criada em: {resultado}")
        if escopo.startswith("global"):
            print("   ℹ️  Skill global — auto-descoberta pelo Claude Code em qualquer projeto")
        elif escopo.startswith("local"):
            print("   ℹ️  Skill local — visível apenas quando trabalhando neste projeto")
        print()
        print("Próximos passos:")
        print("  1. Editar SKILL.md — completar TODOs e descrição")
        print("  2. Criar/remover scripts conforme necessidade")
        print("  3. Criar/remover references conforme necessidade")
        print("  4. Criar/remover assets conforme necessidade")
        print("  5. Validar: python3 forge_validate.py " + str(resultado))
        print("  6. Empacotar: python3 forge_package.py " + str(resultado))
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
