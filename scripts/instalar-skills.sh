#!/bin/bash
# =============================================================================
# instalar-skills.sh — Instalador de Skills do Claude Code
# Instala/atualiza: skill-forge, estudador, criador-de-projetos
# Uso: curl ... | bash  OU  bash instalar-skills.sh
# =============================================================================

set -e

SKILLS_DIR="$HOME/.claude/skills"
CLAUDE_MD="$HOME/.claude/CLAUDE.md"
GITHUB_ORG="Hackerdomarketing"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ok()   { echo -e "${GREEN}✅ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
fail() { echo -e "${RED}❌ $1${NC}"; }

# ---------------------------------------------------------------------------
# Pre-requisitos
# ---------------------------------------------------------------------------
check_prereqs() {
    echo ""
    echo "================================================"
    echo "  Instalador de Skills — Claude Code"
    echo "================================================"
    echo ""

    if ! command -v git &>/dev/null; then
        fail "Git nao encontrado. Instale o Git primeiro."
        exit 1
    fi

    if ! command -v gh &>/dev/null; then
        warn "GitHub CLI (gh) nao encontrado. Clonando via HTTPS."
        USE_GH=false
    else
        USE_GH=true
    fi

    mkdir -p "$SKILLS_DIR"
    ok "Diretorio de skills: $SKILLS_DIR"
}

# ---------------------------------------------------------------------------
# Funcao generica: clonar ou atualizar repo
# ---------------------------------------------------------------------------
install_or_update() {
    local repo="$1"
    local dest="$2"
    local label="$3"

    echo ""
    echo "--- $label ---"

    if [ -d "$dest/.git" ]; then
        echo "Ja instalado. Atualizando..."
        cd "$dest"
        git pull --ff-only 2>/dev/null && ok "$label atualizado" || warn "$label: pull falhou (conflito local?)"
        cd - >/dev/null
    else
        if [ -d "$dest" ]; then
            # Pasta existe mas sem .git — backup e re-clone
            warn "Pasta $dest existe sem .git. Fazendo backup..."
            mv "$dest" "${dest}.bak.$(date +%s)"
        fi
        echo "Clonando $repo..."
        if $USE_GH; then
            gh repo clone "$GITHUB_ORG/$repo" "$dest" 2>/dev/null && ok "$label instalado" || {
                fail "Falha ao clonar $repo"
                return 1
            }
        else
            git clone "https://github.com/$GITHUB_ORG/$repo.git" "$dest" 2>/dev/null && ok "$label instalado" || {
                fail "Falha ao clonar $repo"
                return 1
            }
        fi
    fi
}

# ---------------------------------------------------------------------------
# 1. Skill Forge
# ---------------------------------------------------------------------------
install_skill_forge() {
    install_or_update "skill-forge" "$SKILLS_DIR/skill-forge" "Skill Forge v3"

    # Rodar --setup para injetar triggers no CLAUDE.md
    if [ -f "$SKILLS_DIR/skill-forge/scripts/forge_deploy.py" ]; then
        echo "Configurando triggers no CLAUDE.md..."
        python3 "$SKILLS_DIR/skill-forge/scripts/forge_deploy.py" --setup 2>/dev/null && ok "Triggers do Skill Forge configurados" || warn "Nao foi possivel rodar --setup (Python3 necessario)"
    fi
}

# ---------------------------------------------------------------------------
# 2. Estudador
# ---------------------------------------------------------------------------
install_estudador() {
    install_or_update "estudador" "$SKILLS_DIR/estudador" "Estudador"
}

# ---------------------------------------------------------------------------
# 3. Criador de Projetos
# ---------------------------------------------------------------------------
install_criador() {
    local PROJ_DIR="$HOME/Documents/VSCODE/CRIADOR-DE-PROJETOS"
    local SKILL_DIR="$SKILLS_DIR/criador-de-projetos"

    install_or_update "CRIADOR-DE-PROJETOS" "$PROJ_DIR" "Criador de Projetos"

    # Copiar SKILL.md para pasta de skills (auto-discovery)
    if [ -f "$PROJ_DIR/SKILL.md" ]; then
        mkdir -p "$SKILL_DIR"
        cp "$PROJ_DIR/SKILL.md" "$SKILL_DIR/SKILL.md"
        ok "SKILL.md copiado para $SKILL_DIR"
    else
        warn "SKILL.md nao encontrado em $PROJ_DIR"
    fi
}

# ---------------------------------------------------------------------------
# 4. Injetar triggers do Estudador no CLAUDE.md
# ---------------------------------------------------------------------------
inject_estudador_triggers() {
    echo ""
    echo "--- Triggers do Estudador ---"

    if [ ! -f "$CLAUDE_MD" ]; then
        warn "CLAUDE.md nao existe em $CLAUDE_MD. Triggers do Estudador nao injetados."
        echo "   Crie o arquivo e adicione manualmente a secao de triggers."
        return
    fi

    if grep -q "### ESTUDADOR" "$CLAUDE_MD" 2>/dev/null; then
        ok "Triggers do Estudador ja presentes no CLAUDE.md"
    else
        cat >> "$CLAUDE_MD" << 'TRIGGER_EOF'

### ESTUDADOR

Quando o usuario usar qualquer uma destas frases, ative a skill `estudador`:

**Triggers de estudo e pesquisa:**
- "use o estudador", "com o estudador", "pesquise com o estudador", "ative o estudador"
- "estudo profundo", "pesquise isso", "investigue isso", "valide isso"
- "preciso ter certeza", "confirme isso", "verifique isso com rigor"
- "triangule as fontes", "busque evidencia", "escavacao profunda"

**Acao:** Usar a skill `estudador` que carrega o protocolo completo do Arquiteto de Certezas Universal em `~/.claude/skills/estudador/`.

**REGRA CRITICA:** Quando o usuario mencionar "estudador" por nome, SEMPRE ativar a skill. NUNCA substituir por pesquisa manual.
TRIGGER_EOF
        ok "Triggers do Estudador adicionados ao CLAUDE.md"
    fi
}

# ---------------------------------------------------------------------------
# 5. Injetar triggers do Criador de Projetos no CLAUDE.md
# ---------------------------------------------------------------------------
inject_criador_triggers() {
    echo ""
    echo "--- Triggers do Criador de Projetos ---"

    if [ ! -f "$CLAUDE_MD" ]; then
        return
    fi

    if grep -q "### CRIADOR DE PROJETOS" "$CLAUDE_MD" 2>/dev/null; then
        ok "Triggers do Criador de Projetos ja presentes no CLAUDE.md"
    else
        cat >> "$CLAUDE_MD" << 'TRIGGER_EOF'

### CRIADOR DE PROJETOS

Quando o usuario usar qualquer uma destas frases, ative a skill `criador-de-projetos`:

**Triggers de criacao:**
- "cria um projeto", "novo projeto", "criar um sistema", "desenvolve um", "quero criar", "faz um app", "preciso de um", "monta um"

**Triggers de estrutura:**
- "onde coloco", "qual pasta", "como organizo", "estrutura de pastas"

**Acao:** Usar a skill `criador-de-projetos` que carrega o protocolo completo de `~/Documents/VSCODE/CRIADOR-DE-PROJETOS/`.
TRIGGER_EOF
        ok "Triggers do Criador de Projetos adicionados ao CLAUDE.md"
    fi
}

# ---------------------------------------------------------------------------
# Resumo final
# ---------------------------------------------------------------------------
show_summary() {
    echo ""
    echo "================================================"
    echo "  Instalacao concluida!"
    echo "================================================"
    echo ""
    echo "Skills instaladas em: $SKILLS_DIR"
    echo ""
    echo "  skill-forge/        — Cria e testa skills"
    echo "  estudador/          — Pesquisa com rigor epistemico"
    echo "  criador-de-projetos/— Cria projetos estruturados"
    echo ""
    echo "O Claude Code vai detectar as skills automaticamente."
    echo "Abra um novo terminal e teste: 'crie uma skill para...'"
    echo ""
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
check_prereqs
install_skill_forge
install_estudador
install_criador
inject_estudador_triggers
inject_criador_triggers
show_summary
