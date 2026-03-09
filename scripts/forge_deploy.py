#!/usr/bin/env python3
"""
Forge Deploy — Propaga Skill Forge para projetos-alvo

Uso:
    forge_deploy.py --project /caminho/projeto [--git-push] [--dry-run]
    forge_deploy.py --all [--git-push] [--dry-run]
    forge_deploy.py --list
    forge_deploy.py --unregister /caminho/projeto

Exemplos:
    forge_deploy.py --project /Users/alfa/ECOSSISTEMA --dry-run
    forge_deploy.py --project /Users/alfa/ECOSSISTEMA --git-push
    forge_deploy.py --all --git-push
    forge_deploy.py --list

O script:
    1. Injeta secao SKILL FORGE no CLAUDE.md do projeto
    2. Adiciona skills: [skill-forge] nos agentes construtores
    3. Opcionalmente faz git commit + push
    4. Registra o deploy no deploy-registry.json
    forge_deploy.py --setup [--dry-run]
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


# Caminho do registro de deploys
SCRIPT_DIR = Path(__file__).parent.resolve()
SKILL_FORGE_DIR = SCRIPT_DIR.parent
REGISTRY_PATH = SKILL_FORGE_DIR / 'workspace' / 'deploy-registry.json'

# Template da secao SKILL FORGE para CLAUDE.md
CLAUDE_MD_SECTION = """
### SKILL FORGE — Criacao de Skills

Quando qualquer agente deste projeto precisar criar, modificar ou testar
uma skill, DEVE usar o protocolo do Skill Forge v3 em ~/.claude/skills/skill-forge/.

Passos obrigatorios:
1. Rodar Triage Gate para classificar complexidade
2. Seguir o path indicado (Fast/Medium/Deep)
3. Usar forge_validate.py para validar antes de finalizar
"""

# Padrao de agentes que devem receber skills: [skill-forge]
DEFAULT_AGENT_FILTER = r'construtor|central|builder'

# Bloco de triggers para o CLAUDE.md global (~/.claude/CLAUDE.md)
GLOBAL_TRIGGERS_SECTION = """
### SKILL FORGE

Quando o usuario usar qualquer uma destas frases, ative a skill `skill-forge`:

**Triggers de criacao de skills:**
- "crie uma skill", "nova skill", "criar skill", "fazer uma skill"
- "melhore essa skill", "refatore essa skill", "otimize essa skill"
- "teste essa skill", "rode evals", "benchmark dessa skill"
- "estude esse dominio", "extraia a metodologia"
- "transforme em metodo", "extraia metodo", "transforme em processo", "extraia processo"
- "compare versoes", "otimize o trigger"

**Acao:** Usar a skill `skill-forge` que carrega o pipeline completo do Skill Forge v3 em `~/.claude/skills/skill-forge/`.

**Regra para sub-agentes:** Quando delegar tarefa que envolve criacao, melhoria ou teste de skills para sub-agentes (Agent tool), incluir no prompt do sub-agente: "Consulte a skill skill-forge em ~/.claude/skills/skill-forge/ para seguir o protocolo correto de criacao de skills."

**REGRA CRITICA:** SEMPRE usar a skill `skill-forge` quando o assunto for criacao, melhoria, teste ou estudo para skills. NUNCA criar skills manualmente sem o protocolo do Skill Forge.
"""


def carregar_registry() -> dict:
    """Carrega o registro de deploys."""
    if REGISTRY_PATH.exists():
        try:
            return json.loads(REGISTRY_PATH.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, OSError):
            pass
    return {"version": "3.0", "deployed_at": {}}


def salvar_registry(registry: dict) -> None:
    """Salva o registro de deploys."""
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(
        json.dumps(registry, indent=2, ensure_ascii=False) + '\n',
        encoding='utf-8'
    )


def validar_projeto(caminho: Path) -> tuple[bool, str]:
    """Valida que o caminho e um projeto valido para deploy."""
    if not caminho.exists():
        return False, f"Diretorio nao existe: {caminho}"
    if not caminho.is_dir():
        return False, f"Nao e um diretorio: {caminho}"
    claude_md = caminho / 'CLAUDE.md'
    if not claude_md.exists():
        return False, f"CLAUDE.md nao encontrado em {caminho}"
    return True, "Projeto valido"


def injetar_claude_md(caminho_projeto: Path, dry_run: bool = False) -> tuple[bool, str]:
    """
    Injeta secao SKILL FORGE no CLAUDE.md do projeto.

    Returns:
        (modificado, mensagem)
    """
    claude_md = caminho_projeto / 'CLAUDE.md'
    conteudo = claude_md.read_text(encoding='utf-8')

    # Verificar se ja existe
    if 'SKILL FORGE' in conteudo:
        return False, "Secao SKILL FORGE ja existe (nenhuma alteracao)"

    if dry_run:
        return True, "[DRY-RUN] Adicionaria secao SKILL FORGE ao CLAUDE.md"

    # Adicionar no final do arquivo
    conteudo_novo = conteudo.rstrip() + '\n' + CLAUDE_MD_SECTION
    claude_md.write_text(conteudo_novo, encoding='utf-8')
    return True, "Secao SKILL FORGE adicionada ao CLAUDE.md"


def injetar_skill_em_agentes(
    caminho_projeto: Path,
    filtro: str = DEFAULT_AGENT_FILTER,
    dry_run: bool = False
) -> list[tuple[str, bool, str]]:
    """
    Adiciona skills: [skill-forge] nos agentes que matcham o filtro.

    Returns:
        Lista de (nome_agente, modificado, mensagem)
    """
    resultados = []
    agents_dir = caminho_projeto / '.claude' / 'agents'

    if not agents_dir.exists():
        return [("(nenhum)", False, "Diretorio .claude/agents/ nao encontrado")]

    pattern = re.compile(filtro, re.IGNORECASE)

    for agent_file in sorted(agents_dir.glob('*.md')):
        nome = agent_file.name

        # Verificar se o agente matcha o filtro
        if not pattern.search(nome.replace('.md', '')):
            resultados.append((nome, False, "nao e construtor, pulando"))
            continue

        conteudo = agent_file.read_text(encoding='utf-8')

        # Verificar se ja tem skills: [skill-forge]
        if 'skill-forge' in conteudo:
            resultados.append((nome, False, "skills: [skill-forge] ja presente"))
            continue

        if dry_run:
            resultados.append((nome, True, "[DRY-RUN] Adicionaria skills: [skill-forge]"))
            continue

        # Injetar no frontmatter
        if conteudo.startswith('---'):
            # Encontrar o fechamento do frontmatter
            fim_frontmatter = conteudo.index('---', 3)
            frontmatter = conteudo[3:fim_frontmatter]

            # Verificar se ja tem campo skills
            if 'skills:' in frontmatter:
                # Adicionar skill-forge a lista existente
                frontmatter_novo = re.sub(
                    r'(skills:\s*\[)',
                    r'\1skill-forge, ',
                    frontmatter
                )
            else:
                # Adicionar campo skills no final do frontmatter
                frontmatter_novo = frontmatter.rstrip() + '\nskills: [skill-forge]\n'

            conteudo_novo = '---' + frontmatter_novo + '---' + conteudo[fim_frontmatter + 3:]
            agent_file.write_text(conteudo_novo, encoding='utf-8')
            resultados.append((nome, True, "skills: [skill-forge] adicionado"))
        else:
            # Sem frontmatter — adicionar
            conteudo_novo = '---\nskills: [skill-forge]\n---\n\n' + conteudo
            agent_file.write_text(conteudo_novo, encoding='utf-8')
            resultados.append((nome, True, "frontmatter criado com skills: [skill-forge]"))

    return resultados


def git_commit_push(caminho_projeto: Path, push: bool = False, dry_run: bool = False) -> tuple[bool, str]:
    """
    Faz git commit e opcionalmente push das mudancas.

    Returns:
        (sucesso, mensagem)
    """
    try:
        # Verificar se e um repo git
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=caminho_projeto, capture_output=True, text=True
        )
        if result.returncode != 0:
            return False, "Nao e um repositorio git"

        if not result.stdout.strip():
            return False, "Nenhuma mudanca para commitar"

        if dry_run:
            msg = "[DRY-RUN] Commitaria mudancas"
            if push:
                msg += " e faria push"
            return True, msg

        # Git add dos arquivos conhecidos
        subprocess.run(['git', 'add', 'CLAUDE.md'], cwd=caminho_projeto, capture_output=True)
        agents_dir = caminho_projeto / '.claude' / 'agents'
        if agents_dir.exists():
            subprocess.run(
                ['git', 'add', '.claude/agents/'],
                cwd=caminho_projeto, capture_output=True
            )

        # Commit
        msg = "feat: integrar Skill Forge v3 para criacao de skills"
        result = subprocess.run(
            ['git', 'commit', '-m', msg],
            cwd=caminho_projeto, capture_output=True, text=True
        )
        if result.returncode != 0:
            return False, f"Erro no commit: {result.stderr.strip()}"

        commit_msg = f"Commit criado: {msg}"

        # Push
        if push:
            result = subprocess.run(
                ['git', 'push'],
                cwd=caminho_projeto, capture_output=True, text=True
            )
            if result.returncode != 0:
                return True, f"{commit_msg} (push falhou: {result.stderr.strip()})"
            commit_msg += " + pushed"

        return True, commit_msg

    except FileNotFoundError:
        return False, "git nao encontrado no sistema"


def deploy_projeto(
    caminho_projeto: Path,
    git_push: bool = False,
    dry_run: bool = False,
    agent_filter: str = DEFAULT_AGENT_FILTER
) -> int:
    """
    Executa deploy completo do Skill Forge em um projeto.

    Returns:
        Numero de alteracoes feitas
    """
    alteracoes = 0
    modo = " [DRY-RUN]" if dry_run else ""

    print(f"\n🚀 Skill Forge Deploy → {caminho_projeto}{modo}\n")

    # 1. Validar projeto
    valido, msg = validar_projeto(caminho_projeto)
    if not valido:
        print(f"❌ {msg}")
        return 0

    # 2. CLAUDE.md
    print("1. CLAUDE.md")
    modificado, msg = injetar_claude_md(caminho_projeto, dry_run)
    status = "✅" if modificado else "✅"
    print(f"   {status} {msg}")
    if modificado:
        alteracoes += 1

    # 3. Agentes
    print("\n2. Agentes")
    resultados_agentes = injetar_skill_em_agentes(caminho_projeto, agent_filter, dry_run)
    agentes_modificados = []
    for nome, modificado, msg in resultados_agentes:
        icone = "✅" if modificado else "⏭️"
        print(f"   {icone} {nome} — {msg}")
        if modificado:
            alteracoes += 1
            agentes_modificados.append(nome)

    # 4. Git
    print("\n3. Git")
    if alteracoes > 0 or git_push:
        sucesso, msg = git_commit_push(caminho_projeto, push=git_push, dry_run=dry_run)
        icone = "✅" if sucesso else "⏭️"
        print(f"   {icone} {msg}")
    else:
        print("   ⏭️ Nenhuma mudanca para commitar")

    # 5. Atualizar registro
    if not dry_run and alteracoes > 0:
        registry = carregar_registry()
        caminho_str = str(caminho_projeto)
        registry['deployed_at'][caminho_str] = {
            "date": datetime.now(timezone.utc).strftime('%Y-%m-%d'),
            "claude_md": True,
            "agents": agentes_modificados,
            "git_remote": _detectar_remote(caminho_projeto)
        }
        salvar_registry(registry)

    # Mesmo sem alteracoes, garantir que o projeto esta no registro
    if not dry_run:
        registry = carregar_registry()
        caminho_str = str(caminho_projeto)
        if caminho_str not in registry['deployed_at']:
            registry['deployed_at'][caminho_str] = {
                "date": datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                "claude_md": True,
                "agents": [r[0] for r in resultados_agentes if 'skill-forge' in r[2] or 'ja presente' in r[2]],
                "git_remote": _detectar_remote(caminho_projeto)
            }
            salvar_registry(registry)

    print(f"\nDeploy concluido! {alteracoes} alteracao(oes).")
    return alteracoes


def _detectar_remote(caminho: Path) -> str:
    """Detecta o remote git do projeto."""
    try:
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            cwd=caminho, capture_output=True, text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except FileNotFoundError:
        pass
    return ""


def listar_projetos() -> None:
    """Lista projetos registrados."""
    registry = carregar_registry()
    projetos = registry.get('deployed_at', {})

    if not projetos:
        print("Nenhum projeto registrado.")
        return

    print(f"\n📋 Projetos com Skill Forge ({len(projetos)}):\n")
    for caminho, info in projetos.items():
        data = info.get('date', '?')
        remote = info.get('git_remote', '')
        agentes = ', '.join(info.get('agents', []))
        print(f"  📁 {caminho}")
        print(f"     Deploy: {data} | Agentes: {agentes or 'nenhum'}")
        if remote:
            print(f"     Remote: {remote}")
        print()


def setup_global_triggers(dry_run: bool = False) -> tuple[bool, str]:
    """
    Injeta bloco de triggers do Skill Forge no CLAUDE.md global (~/.claude/CLAUDE.md).
    Se ja existe, atualiza para a versao mais recente.

    Returns:
        (modificado, mensagem)
    """
    claude_md_global = Path.home() / '.claude' / 'CLAUDE.md'

    # Criar ~/.claude/ se nao existir
    if not claude_md_global.parent.exists():
        if dry_run:
            return True, "[DRY-RUN] Criaria ~/.claude/ e ~/.claude/CLAUDE.md com triggers"
        claude_md_global.parent.mkdir(parents=True, exist_ok=True)

    # Criar CLAUDE.md se nao existir
    if not claude_md_global.exists():
        if dry_run:
            return True, "[DRY-RUN] Criaria ~/.claude/CLAUDE.md com triggers do Skill Forge"
        claude_md_global.write_text(GLOBAL_TRIGGERS_SECTION.strip() + '\n', encoding='utf-8')
        return True, "~/.claude/CLAUDE.md criado com triggers do Skill Forge"

    conteudo = claude_md_global.read_text(encoding='utf-8')

    # Verificar se ja tem secao SKILL FORGE
    if '### SKILL FORGE' in conteudo:
        # Extrair a secao existente e comparar com template
        # Encontrar inicio e fim da secao
        inicio = conteudo.index('### SKILL FORGE')

        # Encontrar proxima secao de mesmo nivel ou fim do arquivo
        proxima_secao = re.search(r'\n### (?!SKILL FORGE)', conteudo[inicio + 1:])
        if proxima_secao:
            fim = inicio + 1 + proxima_secao.start()
        else:
            # Pode ser o ultimo bloco — encontrar proximo ## ou fim
            proxima_secao_h2 = re.search(r'\n## ', conteudo[inicio + 1:])
            if proxima_secao_h2:
                fim = inicio + 1 + proxima_secao_h2.start()
            else:
                fim = len(conteudo)

        secao_atual = conteudo[inicio:fim].strip()
        secao_nova = GLOBAL_TRIGGERS_SECTION.strip()

        if secao_atual == secao_nova:
            return False, "Triggers do Skill Forge ja estao atualizados"

        if dry_run:
            return True, "[DRY-RUN] Atualizaria triggers do Skill Forge no CLAUDE.md global"

        # Substituir secao existente pela nova
        conteudo_novo = conteudo[:inicio] + GLOBAL_TRIGGERS_SECTION.strip() + '\n' + conteudo[fim:]
        claude_md_global.write_text(conteudo_novo, encoding='utf-8')
        return True, "Triggers do Skill Forge atualizados no ~/.claude/CLAUDE.md"

    # Nao tem — adicionar no final
    if dry_run:
        return True, "[DRY-RUN] Adicionaria triggers do Skill Forge ao CLAUDE.md global"

    conteudo_novo = conteudo.rstrip() + '\n\n' + GLOBAL_TRIGGERS_SECTION.strip() + '\n'
    claude_md_global.write_text(conteudo_novo, encoding='utf-8')
    return True, "Triggers do Skill Forge adicionados ao ~/.claude/CLAUDE.md"


def unregister_projeto(caminho: str) -> None:
    """Remove projeto do registro."""
    registry = carregar_registry()
    caminho_abs = str(Path(caminho).resolve())

    if caminho_abs in registry.get('deployed_at', {}):
        del registry['deployed_at'][caminho_abs]
        salvar_registry(registry)
        print(f"✅ Projeto removido do registro: {caminho_abs}")
    else:
        print(f"⚠️ Projeto nao encontrado no registro: {caminho_abs}")


def parse_args() -> argparse.Namespace:
    """Parse argumentos da linha de comando."""
    parser = argparse.ArgumentParser(
        description="Forge Deploy — Propaga Skill Forge para projetos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  forge_deploy.py --project /caminho/projeto --dry-run
  forge_deploy.py --project /caminho/projeto --git-push
  forge_deploy.py --all --git-push
  forge_deploy.py --list
  forge_deploy.py --unregister /caminho/projeto
"""
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--project',
        help="Caminho do projeto-alvo"
    )
    group.add_argument(
        '--all',
        action='store_true',
        help="Re-deploy em todos os projetos registrados"
    )
    group.add_argument(
        '--list',
        action='store_true',
        help="Listar projetos registrados"
    )
    group.add_argument(
        '--unregister',
        metavar='PATH',
        help="Remover projeto do registro"
    )
    group.add_argument(
        '--setup',
        action='store_true',
        help="Instalar triggers do Skill Forge no CLAUDE.md global (~/.claude/CLAUDE.md)"
    )

    parser.add_argument(
        '--git-push',
        action='store_true',
        help="Commit e push automatico apos deploy"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Simular sem modificar arquivos"
    )
    parser.add_argument(
        '--agent-filter',
        default=DEFAULT_AGENT_FILTER,
        help=f"Regex para filtrar agentes (default: {DEFAULT_AGENT_FILTER})"
    )

    return parser.parse_args()


def main():
    args = parse_args()

    if args.list:
        listar_projetos()
        sys.exit(0)

    if args.unregister:
        unregister_projeto(args.unregister)
        sys.exit(0)

    if args.setup:
        print("\n🔧 Skill Forge — Setup Global\n")
        modificado, msg = setup_global_triggers(dry_run=args.dry_run)
        icone = "✅" if modificado else "✅"
        print(f"   {icone} {msg}")
        if not args.dry_run and modificado:
            print("\n   Triggers instalados! Agora frases como:")
            print('   "crie uma skill", "extraia metodo", "transforme em processo"')
            print("   vao ativar o Skill Forge automaticamente.")
        sys.exit(0)

    if args.all:
        registry = carregar_registry()
        projetos = registry.get('deployed_at', {})
        if not projetos:
            print("Nenhum projeto registrado. Use --project para deployar individualmente.")
            sys.exit(0)

        total_alteracoes = 0
        for caminho in projetos:
            total_alteracoes += deploy_projeto(
                Path(caminho),
                git_push=args.git_push,
                dry_run=args.dry_run,
                agent_filter=args.agent_filter
            )
        print(f"\n{'='*40}")
        print(f"Total: {len(projetos)} projetos, {total_alteracoes} alteracoes")
        sys.exit(0)

    if args.project:
        caminho = Path(args.project).resolve()
        alteracoes = deploy_projeto(
            caminho,
            git_push=args.git_push,
            dry_run=args.dry_run,
            agent_filter=args.agent_filter
        )
        sys.exit(0 if alteracoes >= 0 else 1)


if __name__ == "__main__":
    main()
