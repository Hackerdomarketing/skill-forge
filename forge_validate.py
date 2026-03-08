#!/usr/bin/env python3
"""
Forge Validate — Valida estrutura e conteúdo de uma habilidade

Uso:
    forge_validate.py <caminho-da-habilidade> [--verbose]

Exemplos:
    forge_validate.py ./minha-habilidade
    forge_validate.py ./minha-habilidade --verbose

Verifica:
    - Estrutura de arquivos
    - Frontmatter YAML
    - Qualidade da descrição
    - Referências a recursos
    - Ausência de arquivos desnecessários
"""

import sys
import re
import yaml
from pathlib import Path
from typing import Callable


class Validador:
    """Validador de habilidades com coleta de erros e avisos."""
    
    def __init__(self, caminho: Path, verbose: bool = False):
        self.caminho = caminho
        self.verbose = verbose
        self.erros: list[str] = []
        self.avisos: list[str] = []
        self.frontmatter: dict = {}
        self.skill_md_content: str = ""
    
    def erro(self, mensagem: str):
        self.erros.append(mensagem)
        if self.verbose:
            print(f"  ❌ {mensagem}")
    
    def aviso(self, mensagem: str):
        self.avisos.append(mensagem)
        if self.verbose:
            print(f"  ⚠️  {mensagem}")
    
    def sucesso(self, mensagem: str):
        if self.verbose:
            print(f"  ✅ {mensagem}")
    
    def validar(self) -> tuple[bool, str]:
        """Executa todas as validações e retorna resultado."""
        
        if self.verbose:
            print(f"\n🔍 Validando: {self.caminho}\n")
        
        # Verificar existência
        if not self.caminho.exists():
            return False, f"Caminho não existe: {self.caminho}"
        
        if not self.caminho.is_dir():
            return False, f"Caminho não é um diretório: {self.caminho}"
        
        # Executar validações
        self._validar_estrutura()
        self._validar_skill_md()
        self._validar_frontmatter()
        self._validar_descricao()
        self._validar_corpo()
        self._validar_scripts()
        self._validar_references()
        self._validar_assets()
        self._validar_arquivos_indesejados()
        
        # Resultado
        if self.erros:
            mensagem = f"{len(self.erros)} erro(s) encontrado(s)"
            if self.avisos:
                mensagem += f", {len(self.avisos)} aviso(s)"
            return False, mensagem
        elif self.avisos:
            return True, f"Válido com {len(self.avisos)} aviso(s)"
        else:
            return True, "Habilidade válida!"
    
    def _validar_estrutura(self):
        """Valida estrutura básica de arquivos."""
        if self.verbose:
            print("📁 Validando estrutura...")
        
        skill_md = self.caminho / 'SKILL.md'
        if not skill_md.exists():
            self.erro("SKILL.md não encontrado")
        else:
            self.sucesso("SKILL.md existe")
            self.skill_md_content = skill_md.read_text(encoding='utf-8')
    
    def _validar_skill_md(self):
        """Valida formato básico do SKILL.md."""
        if not self.skill_md_content:
            return
        
        if self.verbose:
            print("📄 Validando SKILL.md...")
        
        # Verificar frontmatter
        if not self.skill_md_content.startswith('---'):
            self.erro("SKILL.md deve começar com frontmatter YAML (---)")
            return
        
        # Extrair frontmatter
        match = re.match(r'^---\n(.*?)\n---', self.skill_md_content, re.DOTALL)
        if not match:
            self.erro("Frontmatter YAML mal formatado")
            return
        
        frontmatter_text = match.group(1)
        
        try:
            self.frontmatter = yaml.safe_load(frontmatter_text)
            if not isinstance(self.frontmatter, dict):
                self.erro("Frontmatter deve ser um dicionário YAML")
                return
            self.sucesso("Frontmatter YAML válido")
        except yaml.YAMLError as e:
            self.erro(f"Erro de sintaxe YAML: {e}")
            return
    
    def _validar_frontmatter(self):
        """Valida campos do frontmatter."""
        if not self.frontmatter:
            return
        
        if self.verbose:
            print("🏷️  Validando frontmatter...")
        
        # Campos permitidos
        CAMPOS_PERMITIDOS = {'name', 'description', 'license', 'allowed-tools', 'metadata', 'compatibility'}
        campos_extras = set(self.frontmatter.keys()) - CAMPOS_PERMITIDOS
        if campos_extras:
            self.erro(f"Campos não reconhecidos no frontmatter: {', '.join(campos_extras)}")
        
        # Campo name
        name = self.frontmatter.get('name', '')
        if not name:
            self.erro("Campo 'name' é obrigatório no frontmatter")
        elif not isinstance(name, str):
            self.erro(f"Campo 'name' deve ser string, não {type(name).__name__}")
        else:
            name = name.strip()
            if not re.match(r'^[a-z0-9-]+$', name):
                self.erro(f"Nome '{name}' deve usar kebab-case")
            elif name.startswith('-') or name.endswith('-') or '--' in name:
                self.erro(f"Nome '{name}' tem hífens inválidos")
            elif len(name) > 64:
                self.erro(f"Nome muito longo ({len(name)} caracteres). Máximo: 64")
            elif name != self.caminho.name:
                self.aviso(f"Nome '{name}' não corresponde ao diretório '{self.caminho.name}'")
            else:
                self.sucesso(f"Nome válido: {name}")
        
        # Campo description
        if 'description' not in self.frontmatter:
            self.erro("Campo 'description' é obrigatório no frontmatter")
    
    def _validar_descricao(self):
        """Valida qualidade da descrição."""
        description = self.frontmatter.get('description', '')
        if not description:
            return
        
        if self.verbose:
            print("📝 Validando descrição...")
        
        if not isinstance(description, str):
            self.erro(f"Descrição deve ser string, não {type(description).__name__}")
            return
        
        description = description.strip()
        
        # Tamanho
        if len(description) > 1024:
            self.erro(f"Descrição muito longa ({len(description)} caracteres). Máximo: 1024")
        elif len(description) < 50:
            self.aviso("Descrição muito curta. Considere adicionar mais detalhes de ativação")
        else:
            self.sucesso(f"Tamanho da descrição OK ({len(description)} caracteres)")
        
        # Caracteres proibidos
        if '<' in description or '>' in description:
            self.erro("Descrição não pode conter < ou >")
        
        # Qualidade
        if '[TODO' in description or 'TODO:' in description:
            self.erro("Descrição contém TODO não resolvido")
        
        # Palavras-chave de ativação
        palavras_ativacao = ['usar quando', 'when', 'para:', 'for:', 'exemplos', 'examples']
        tem_ativacao = any(p in description.lower() for p in palavras_ativacao)
        if not tem_ativacao:
            self.aviso("Descrição pode não ter cenários de ativação claros")
        else:
            self.sucesso("Descrição parece ter cenários de ativação")
    
    def _validar_corpo(self):
        """Valida o corpo do SKILL.md."""
        if not self.skill_md_content:
            return
        
        if self.verbose:
            print("📖 Validando corpo...")
        
        # Extrair corpo (após frontmatter)
        match = re.match(r'^---\n.*?\n---\n?(.*)', self.skill_md_content, re.DOTALL)
        if not match:
            return
        
        corpo = match.group(1).strip()
        
        # Verificar título
        if not corpo.startswith('#'):
            self.aviso("Corpo deveria começar com título (#)")
        else:
            self.sucesso("Corpo tem título principal")
        
        # Verificar TODOs
        todos = re.findall(r'\[TODO.*?\]|TODO:', corpo)
        if todos:
            self.aviso(f"Corpo contém {len(todos)} TODO(s) não resolvidos")
        
        # Verificar tamanho
        linhas = corpo.split('\n')
        if len(linhas) > 500:
            self.aviso(f"Corpo muito longo ({len(linhas)} linhas). Considere mover detalhes para references/")
        else:
            self.sucesso(f"Tamanho do corpo OK ({len(linhas)} linhas)")
        
        # Verificar seção "Quando Usar"
        if re.search(r'##.*quando usar|when to use', corpo, re.IGNORECASE):
            self.aviso("Seção 'Quando Usar' deveria estar na descrição do frontmatter, não no corpo")
    
    def _validar_scripts(self):
        """Valida diretório scripts/."""
        scripts_dir = self.caminho / 'scripts'
        if not scripts_dir.exists():
            return
        
        if self.verbose:
            print("⚙️  Validando scripts/...")
        
        scripts = list(scripts_dir.glob('*.py')) + list(scripts_dir.glob('*.sh'))
        
        for script in scripts:
            conteudo = script.read_text(encoding='utf-8')
            
            # Verificar shebang
            if script.suffix == '.py' and not conteudo.startswith('#!/'):
                self.aviso(f"{script.name}: falta shebang (#!/usr/bin/env python3)")
            
            # Verificar docstring
            if script.suffix == '.py' and '"""' not in conteudo[:500]:
                self.aviso(f"{script.name}: falta docstring")
            
            # Verificar se é placeholder
            if 'placeholder' in conteudo.lower() or 'exemplo' in script.name.lower():
                self.aviso(f"{script.name}: parece ser placeholder/exemplo")
        
        if scripts:
            self.sucesso(f"Encontrados {len(scripts)} script(s)")
    
    def _validar_references(self):
        """Valida diretório references/."""
        refs_dir = self.caminho / 'references'
        if not refs_dir.exists():
            return
        
        if self.verbose:
            print("📚 Validando references/...")
        
        refs = list(refs_dir.glob('*.md'))
        
        for ref in refs:
            # Verificar se é referenciado no SKILL.md
            if ref.name not in self.skill_md_content:
                self.aviso(f"references/{ref.name}: não parece ser referenciado no SKILL.md")
            
            # Verificar se é placeholder
            conteudo = ref.read_text(encoding='utf-8')
            if 'placeholder' in conteudo.lower() or 'exemplo' in ref.name.lower():
                self.aviso(f"references/{ref.name}: parece ser placeholder/exemplo")
        
        if refs:
            self.sucesso(f"Encontrados {len(refs)} arquivo(s) de referência")
    
    def _validar_assets(self):
        """Valida diretório assets/."""
        assets_dir = self.caminho / 'assets'
        if not assets_dir.exists():
            return
        
        if self.verbose:
            print("🎨 Validando assets/...")
        
        # Contar assets (excluindo placeholders)
        assets = [f for f in assets_dir.rglob('*') if f.is_file()]
        placeholders = [f for f in assets if 'placeholder' in f.name.lower()]
        
        if placeholders:
            self.aviso(f"assets/ contém {len(placeholders)} placeholder(s)")
        
        reais = len(assets) - len(placeholders)
        if reais > 0:
            self.sucesso(f"Encontrados {reais} asset(s)")
    
    def _validar_arquivos_indesejados(self):
        """Verifica ausência de arquivos que não deveriam existir."""
        if self.verbose:
            print("🚫 Verificando arquivos indesejados...")
        
        indesejados = [
            'README.md', 'CHANGELOG.md', 'INSTALLATION.md', 
            'QUICK_REFERENCE.md', 'CONTRIBUTING.md',
            '.git', '__pycache__', 'node_modules',
            '.DS_Store', 'Thumbs.db'
        ]
        
        for nome in indesejados:
            caminho = self.caminho / nome
            if caminho.exists():
                if nome in ['README.md', 'CHANGELOG.md', 'INSTALLATION.md']:
                    self.aviso(f"Arquivo desnecessário: {nome}")
                else:
                    self.aviso(f"Arquivo/diretório indesejado: {nome}")
        
        # Verificar arquivos temporários
        for ext in ['*.tmp', '*.bak', '*.swp', '*~']:
            for arquivo in self.caminho.rglob(ext):
                self.aviso(f"Arquivo temporário: {arquivo.relative_to(self.caminho)}")


def validar_habilidade(caminho: str, verbose: bool = False) -> tuple[bool, str]:
    """
    Valida uma habilidade e retorna resultado.
    
    Args:
        caminho: Caminho para o diretório da habilidade
        verbose: Se True, imprime detalhes durante validação
    
    Returns:
        Tupla (válido, mensagem)
    """
    validador = Validador(Path(caminho).resolve(), verbose)
    return validador.validar()


def main():
    verbose = '--verbose' in sys.argv
    args = [a for a in sys.argv[1:] if a != '--verbose']
    
    if len(args) != 1:
        print("Forge Validate — Valida estrutura e conteúdo de uma habilidade")
        print()
        print("Uso: forge_validate.py <caminho-da-habilidade> [--verbose]")
        print()
        print("Opções:")
        print("  --verbose    Mostra detalhes de cada verificação")
        print()
        print("Exemplos:")
        print("  forge_validate.py ./minha-habilidade")
        print("  forge_validate.py ./minha-habilidade --verbose")
        sys.exit(1)
    
    caminho = args[0]
    
    if not verbose:
        print(f"🔍 Validando: {caminho}")
    
    valido, mensagem = validar_habilidade(caminho, verbose)
    
    print()
    if valido:
        print(f"✅ {mensagem}")
        sys.exit(0)
    else:
        print(f"❌ {mensagem}")
        sys.exit(1)


if __name__ == "__main__":
    main()
