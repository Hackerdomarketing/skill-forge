#!/usr/bin/env python3
"""
Forge Init — Inicializa estrutura de nova habilidade

Uso:
    forge_init.py <nome-da-habilidade> --path <diretorio-destino>

Exemplos:
    forge_init.py minha-habilidade --path ./skills
    forge_init.py processador-pdf --path /caminho/absoluto

O script cria:
    nome-da-habilidade/
    ├── SKILL.md (template com TODOs)
    ├── scripts/ (com exemplo)
    ├── references/ (com exemplo)
    └── assets/ (com exemplo)
"""

import sys
import re
from pathlib import Path
from datetime import datetime


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


def criar_habilidade(nome: str, caminho: str) -> Path | None:
    """
    Cria estrutura de diretórios e arquivos para nova habilidade.
    
    Args:
        nome: Nome da habilidade em kebab-case
        caminho: Diretório onde criar a habilidade
    
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
        conteudo = SKILL_TEMPLATE.format(
            skill_name=nome,
            skill_title=titulo
        )
        skill_md.write_text(conteudo, encoding='utf-8')
        print("✅ Criado SKILL.md")
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
    
    return diretorio_habilidade


def main():
    if len(sys.argv) < 4 or sys.argv[2] != '--path':
        print("Forge Init — Inicializa estrutura de nova habilidade")
        print()
        print("Uso: forge_init.py <nome-da-habilidade> --path <diretorio-destino>")
        print()
        print("Requisitos do nome:")
        print("  • Kebab-case: letras minúsculas, dígitos, hífens")
        print("  • Máximo 64 caracteres")
        print("  • Não pode começar/terminar com hífen")
        print("  • Não pode ter hífens consecutivos")
        print()
        print("Exemplos:")
        print("  forge_init.py minha-habilidade --path ./skills")
        print("  forge_init.py processador-pdf --path /home/usuario/skills")
        sys.exit(1)
    
    nome = sys.argv[1]
    caminho = sys.argv[3]
    
    print(f"🔨 Forge Init: Criando habilidade '{nome}'")
    print(f"   Destino: {caminho}")
    print()
    
    resultado = criar_habilidade(nome, caminho)
    
    if resultado:
        print()
        print(f"✅ Habilidade '{nome}' criada em: {resultado}")
        print()
        print("Próximos passos:")
        print("  1. Editar SKILL.md — completar TODOs e descrição")
        print("  2. Criar/remover scripts conforme necessidade")
        print("  3. Criar/remover references conforme necessidade")
        print("  4. Criar/remover assets conforme necessidade")
        print("  5. Validar: python forge_validate.py " + str(resultado))
        print("  6. Empacotar: python forge_package.py " + str(resultado))
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
