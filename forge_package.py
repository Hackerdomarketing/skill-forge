#!/usr/bin/env python3
"""
Forge Package — Empacota habilidade em arquivo .skill distribuível

Uso:
    forge_package.py <caminho-da-habilidade> [--output <diretorio>]

Exemplos:
    forge_package.py ./minha-habilidade
    forge_package.py ./minha-habilidade --output ./dist

O script:
    1. Valida a habilidade automaticamente
    2. Cria arquivo .skill (formato ZIP) com toda a estrutura
    3. Salva no diretório atual ou especificado
"""

import sys
import zipfile
from pathlib import Path
from datetime import datetime

# Importar validador do mesmo diretório
from forge_validate import validar_habilidade


def empacotar_habilidade(caminho_habilidade: str, diretorio_saida: str | None = None) -> Path | None:
    """
    Empacota uma habilidade em arquivo .skill.
    
    Args:
        caminho_habilidade: Caminho para o diretório da habilidade
        diretorio_saida: Diretório onde salvar o .skill (opcional)
    
    Returns:
        Path do arquivo .skill criado, ou None se erro
    """
    caminho = Path(caminho_habilidade).resolve()
    
    # Verificar existência
    if not caminho.exists():
        print(f"❌ Erro: Caminho não existe: {caminho}")
        return None
    
    if not caminho.is_dir():
        print(f"❌ Erro: Caminho não é um diretório: {caminho}")
        return None
    
    # Verificar SKILL.md
    skill_md = caminho / 'SKILL.md'
    if not skill_md.exists():
        print(f"❌ Erro: SKILL.md não encontrado em {caminho}")
        return None
    
    # Validar antes de empacotar
    print("🔍 Validando habilidade...")
    valido, mensagem = validar_habilidade(caminho, verbose=False)
    
    if not valido:
        print(f"❌ Validação falhou: {mensagem}")
        print("   Corrigir erros antes de empacotar.")
        return None
    
    print(f"✅ {mensagem}")
    print()
    
    # Determinar nome e destino
    nome_habilidade = caminho.name
    
    if diretorio_saida:
        destino = Path(diretorio_saida).resolve()
        destino.mkdir(parents=True, exist_ok=True)
    else:
        destino = Path.cwd()
    
    arquivo_skill = destino / f"{nome_habilidade}.skill"
    
    # Arquivos a ignorar
    IGNORAR = {
        '__pycache__', '.git', 'node_modules', '.DS_Store', 
        'Thumbs.db', '.gitignore', '.env'
    }
    
    EXTENSOES_IGNORAR = {'.pyc', '.pyo', '.tmp', '.bak', '.swp'}
    
    def deve_incluir(arquivo: Path) -> bool:
        """Verifica se arquivo deve ser incluído no pacote."""
        # Ignorar diretórios/arquivos específicos
        for parte in arquivo.parts:
            if parte in IGNORAR:
                return False
        
        # Ignorar extensões específicas
        if arquivo.suffix in EXTENSOES_IGNORAR:
            return False
        
        # Ignorar arquivos ocultos (exceto na raiz)
        if arquivo.name.startswith('.') and arquivo.parent != caminho:
            return False
        
        return True
    
    # Criar arquivo .skill
    print(f"📦 Empacotando: {nome_habilidade}")
    
    try:
        arquivos_incluidos = 0
        
        with zipfile.ZipFile(arquivo_skill, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for arquivo in caminho.rglob('*'):
                if arquivo.is_file() and deve_incluir(arquivo):
                    # Caminho relativo mantendo estrutura de diretórios
                    caminho_no_zip = arquivo.relative_to(caminho.parent)
                    zipf.write(arquivo, caminho_no_zip)
                    print(f"  + {caminho_no_zip}")
                    arquivos_incluidos += 1
        
        # Verificar tamanho
        tamanho_bytes = arquivo_skill.stat().st_size
        if tamanho_bytes < 1024:
            tamanho_str = f"{tamanho_bytes} bytes"
        elif tamanho_bytes < 1024 * 1024:
            tamanho_str = f"{tamanho_bytes / 1024:.1f} KB"
        else:
            tamanho_str = f"{tamanho_bytes / (1024 * 1024):.1f} MB"
        
        print()
        print(f"✅ Empacotado com sucesso!")
        print(f"   Arquivo: {arquivo_skill}")
        print(f"   Tamanho: {tamanho_str}")
        print(f"   Arquivos: {arquivos_incluidos}")
        
        return arquivo_skill
        
    except Exception as e:
        print(f"❌ Erro ao criar arquivo .skill: {e}")
        # Limpar arquivo parcial se existir
        if arquivo_skill.exists():
            arquivo_skill.unlink()
        return None


def main():
    # Parse argumentos
    args = sys.argv[1:]
    
    if not args or '--help' in args or '-h' in args:
        print("Forge Package — Empacota habilidade em arquivo .skill")
        print()
        print("Uso: forge_package.py <caminho-da-habilidade> [--output <diretorio>]")
        print()
        print("Opções:")
        print("  --output <dir>    Diretório de saída (padrão: diretório atual)")
        print()
        print("Exemplos:")
        print("  forge_package.py ./minha-habilidade")
        print("  forge_package.py ./minha-habilidade --output ./dist")
        print()
        print("O arquivo .skill é um ZIP que pode ser importado no Claude Code.")
        sys.exit(0)
    
    # Extrair argumentos
    caminho_habilidade = None
    diretorio_saida = None
    
    i = 0
    while i < len(args):
        if args[i] == '--output' and i + 1 < len(args):
            diretorio_saida = args[i + 1]
            i += 2
        elif not args[i].startswith('--'):
            caminho_habilidade = args[i]
            i += 1
        else:
            print(f"❌ Argumento desconhecido: {args[i]}")
            sys.exit(1)
    
    if not caminho_habilidade:
        print("❌ Erro: Caminho da habilidade é obrigatório")
        sys.exit(1)
    
    resultado = empacotar_habilidade(caminho_habilidade, diretorio_saida)
    
    if resultado:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
