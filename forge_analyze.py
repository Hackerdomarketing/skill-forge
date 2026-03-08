#!/usr/bin/env python3
"""
Forge Analyze — Analisa habilidade existente e sugere melhorias

Uso:
    forge_analyze.py <caminho-da-habilidade>

Exemplos:
    forge_analyze.py ./minha-habilidade
    forge_analyze.py /caminho/para/skill-existente

Analisa:
    - Eficiência de contexto (tamanho de arquivos)
    - Qualidade da descrição
    - Estrutura e organização
    - Uso de recursos (scripts, references, assets)
    - Potenciais melhorias
"""

import sys
import re
import yaml
from pathlib import Path
from collections import defaultdict


class Analisador:
    """Analisa habilidades e gera sugestões de melhoria."""
    
    def __init__(self, caminho: Path):
        self.caminho = caminho
        self.sugestoes: list[str] = []
        self.metricas: dict = {}
        self.frontmatter: dict = {}
        self.skill_md_content: str = ""
    
    def analisar(self) -> dict:
        """Executa análise completa e retorna relatório."""
        
        if not self.caminho.exists():
            return {"erro": f"Caminho não existe: {self.caminho}"}
        
        if not self.caminho.is_dir():
            return {"erro": f"Caminho não é um diretório: {self.caminho}"}
        
        skill_md = self.caminho / 'SKILL.md'
        if not skill_md.exists():
            return {"erro": "SKILL.md não encontrado"}
        
        self.skill_md_content = skill_md.read_text(encoding='utf-8')
        self._extrair_frontmatter()
        
        # Executar análises
        self._analisar_tamanho()
        self._analisar_descricao()
        self._analisar_estrutura()
        self._analisar_recursos()
        self._analisar_codigo()
        self._analisar_duplicacao()
        
        return {
            "caminho": str(self.caminho),
            "nome": self.frontmatter.get('name', 'desconhecido'),
            "metricas": self.metricas,
            "sugestoes": self.sugestoes
        }
    
    def _extrair_frontmatter(self):
        """Extrai frontmatter YAML."""
        match = re.match(r'^---\n(.*?)\n---', self.skill_md_content, re.DOTALL)
        if match:
            try:
                self.frontmatter = yaml.safe_load(match.group(1)) or {}
            except yaml.YAMLError:
                self.frontmatter = {}
    
    def _analisar_tamanho(self):
        """Analisa tamanho dos arquivos para eficiência de contexto."""
        
        # Tamanho do SKILL.md
        skill_md_linhas = len(self.skill_md_content.split('\n'))
        skill_md_palavras = len(self.skill_md_content.split())
        skill_md_chars = len(self.skill_md_content)
        
        self.metricas['skill_md'] = {
            'linhas': skill_md_linhas,
            'palavras': skill_md_palavras,
            'caracteres': skill_md_chars
        }
        
        if skill_md_linhas > 400:
            self.sugestoes.append(
                f"SKILL.md tem {skill_md_linhas} linhas. Considere mover detalhes "
                "para references/ para reduzir uso de contexto."
            )
        
        if skill_md_palavras > 3000:
            self.sugestoes.append(
                f"SKILL.md tem {skill_md_palavras} palavras. Habilidades mais "
                "concisas são mais eficientes. Revise se toda informação é essencial."
            )
        
        # Tamanho total de references
        refs_dir = self.caminho / 'references'
        if refs_dir.exists():
            total_refs = sum(
                f.stat().st_size for f in refs_dir.rglob('*') if f.is_file()
            )
            self.metricas['references_bytes'] = total_refs
            
            if total_refs > 100000:  # 100KB
                self.sugestoes.append(
                    f"references/ tem {total_refs // 1024}KB. Para arquivos grandes, "
                    "considere adicionar padrões de grep no SKILL.md para busca eficiente."
                )
    
    def _analisar_descricao(self):
        """Analisa qualidade da descrição."""
        
        description = self.frontmatter.get('description', '')
        if not description:
            self.sugestoes.append(
                "Descrição está vazia. Adicione descrição detalhada com cenários de ativação."
            )
            return
        
        self.metricas['descricao_caracteres'] = len(description)
        
        # Verificar elementos de qualidade
        tem_quando_usar = any(p in description.lower() for p in 
            ['usar quando', 'when', 'para:', 'for:', 'cenário', 'scenario'])
        tem_exemplos = any(p in description.lower() for p in 
            ['exemplo', 'example', '(1)', '(2)', 'inclui', 'include'])
        tem_formato = any(p in description.lower() for p in 
            ['.docx', '.pdf', '.xlsx', '.pptx', '.md', '.html', '.json'])
        
        self.metricas['descricao_qualidade'] = {
            'tem_quando_usar': tem_quando_usar,
            'tem_exemplos': tem_exemplos,
            'tem_formato_arquivo': tem_formato
        }
        
        if not tem_quando_usar:
            self.sugestoes.append(
                "Descrição não parece ter cenários de ativação claros. "
                "Adicione 'Usar quando...' seguido de cenários específicos."
            )
        
        if not tem_exemplos:
            self.sugestoes.append(
                "Descrição poderia ter exemplos numerados ou entre parênteses "
                "para maior clareza sobre quando ativar a habilidade."
            )
        
        if len(description) < 100:
            self.sugestoes.append(
                "Descrição muito curta. Descrições efetivas geralmente têm "
                "100-500 caracteres com cenários de ativação detalhados."
            )
    
    def _analisar_estrutura(self):
        """Analisa estrutura e organização do SKILL.md."""
        
        # Contar seções
        secoes = re.findall(r'^##\s+(.+)$', self.skill_md_content, re.MULTILINE)
        subsecoes = re.findall(r'^###\s+(.+)$', self.skill_md_content, re.MULTILINE)
        
        self.metricas['estrutura'] = {
            'secoes': len(secoes),
            'subsecoes': len(subsecoes),
            'titulos_secoes': secoes[:10]  # Primeiros 10
        }
        
        if len(secoes) < 2:
            self.sugestoes.append(
                "SKILL.md tem poucas seções. Considere organizar em seções claras "
                "como 'Visão Geral', 'Referência Rápida', e seções específicas por tarefa."
            )
        
        if len(secoes) > 15:
            self.sugestoes.append(
                f"SKILL.md tem {len(secoes)} seções. Muitas seções podem dificultar "
                "navegação. Considere consolidar ou mover para references/."
            )
        
        # Verificar tabela de referência rápida
        tem_tabela = '|' in self.skill_md_content and '---' in self.skill_md_content
        if not tem_tabela and len(secoes) > 5:
            self.sugestoes.append(
                "Considere adicionar uma tabela de Referência Rápida no início "
                "para facilitar navegação entre as muitas seções."
            )
        
        # Verificar se tem "Quando Usar" no corpo (deveria estar na descrição)
        if re.search(r'##.*quando usar|when to use', self.skill_md_content, re.IGNORECASE):
            self.sugestoes.append(
                "Seção 'Quando Usar' encontrada no corpo. Esta informação "
                "deveria estar na descrição do frontmatter para ativação correta."
            )
    
    def _analisar_recursos(self):
        """Analisa uso de scripts, references e assets."""
        
        # Scripts
        scripts_dir = self.caminho / 'scripts'
        if scripts_dir.exists():
            scripts = list(scripts_dir.glob('*.py')) + list(scripts_dir.glob('*.sh'))
            self.metricas['scripts'] = [s.name for s in scripts]
            
            # Verificar se scripts são referenciados
            for script in scripts:
                if script.name not in self.skill_md_content:
                    self.sugestoes.append(
                        f"Script '{script.name}' não parece ser referenciado no SKILL.md. "
                        "Documente seu uso ou remova se não for necessário."
                    )
        else:
            self.metricas['scripts'] = []
        
        # References
        refs_dir = self.caminho / 'references'
        if refs_dir.exists():
            refs = list(refs_dir.glob('*.md'))
            self.metricas['references'] = [r.name for r in refs]
            
            for ref in refs:
                if ref.name not in self.skill_md_content:
                    self.sugestoes.append(
                        f"Referência '{ref.name}' não é mencionada no SKILL.md. "
                        "Adicione indicação de quando consultar este arquivo."
                    )
        else:
            self.metricas['references'] = []
        
        # Assets
        assets_dir = self.caminho / 'assets'
        if assets_dir.exists():
            assets = [f.name for f in assets_dir.rglob('*') if f.is_file()]
            self.metricas['assets'] = assets[:20]  # Primeiros 20
        else:
            self.metricas['assets'] = []
    
    def _analisar_codigo(self):
        """Analisa blocos de código no SKILL.md."""
        
        # Encontrar blocos de código
        blocos = re.findall(r'```(\w*)\n(.*?)```', self.skill_md_content, re.DOTALL)
        
        linguagens = defaultdict(int)
        total_linhas_codigo = 0
        
        for linguagem, codigo in blocos:
            linguagens[linguagem or 'sem_especificar'] += 1
            total_linhas_codigo += len(codigo.strip().split('\n'))
        
        self.metricas['codigo'] = {
            'blocos': len(blocos),
            'linhas_totais': total_linhas_codigo,
            'linguagens': dict(linguagens)
        }
        
        if linguagens.get('sem_especificar', 0) > 2:
            self.sugestoes.append(
                f"Há {linguagens['sem_especificar']} blocos de código sem linguagem especificada. "
                "Especifique a linguagem (python, javascript, bash, etc.) para syntax highlighting."
            )
        
        # Verificar avisos CRITICAL
        critical_count = len(re.findall(r'\*\*CRITICAL', self.skill_md_content, re.IGNORECASE))
        self.metricas['avisos_critical'] = critical_count
        
        if critical_count == 0 and total_linhas_codigo > 50:
            self.sugestoes.append(
                "Nenhum aviso **CRITICAL** encontrado. Se existem armadilhas comuns, "
                "marque-as claramente para evitar erros."
            )
    
    def _analisar_duplicacao(self):
        """Verifica potencial duplicação entre SKILL.md e references."""
        
        refs_dir = self.caminho / 'references'
        if not refs_dir.exists():
            return
        
        # Extrair frases significativas do SKILL.md (mais de 10 palavras)
        frases_skill = set()
        for linha in self.skill_md_content.split('\n'):
            palavras = linha.split()
            if len(palavras) > 10:
                frases_skill.add(' '.join(palavras[:10]))
        
        # Verificar em references
        for ref_file in refs_dir.glob('*.md'):
            conteudo_ref = ref_file.read_text(encoding='utf-8')
            duplicadas = 0
            
            for frase in frases_skill:
                if frase in conteudo_ref:
                    duplicadas += 1
            
            if duplicadas > 3:
                self.sugestoes.append(
                    f"Possível duplicação entre SKILL.md e {ref_file.name}. "
                    f"Encontradas {duplicadas} frases similares. "
                    "Considere manter informação em apenas um lugar."
                )


def analisar_habilidade(caminho: str) -> dict:
    """
    Analisa uma habilidade e retorna relatório.
    
    Args:
        caminho: Caminho para o diretório da habilidade
    
    Returns:
        Dicionário com métricas e sugestões
    """
    analisador = Analisador(Path(caminho).resolve())
    return analisador.analisar()


def formatar_relatorio(relatorio: dict) -> str:
    """Formata relatório para exibição."""
    
    if 'erro' in relatorio:
        return f"❌ Erro: {relatorio['erro']}"
    
    linhas = []
    linhas.append(f"📊 Análise: {relatorio['nome']}")
    linhas.append(f"   Caminho: {relatorio['caminho']}")
    linhas.append("")
    
    # Métricas
    metricas = relatorio.get('metricas', {})
    
    if 'skill_md' in metricas:
        sm = metricas['skill_md']
        linhas.append("📄 SKILL.md:")
        linhas.append(f"   • {sm['linhas']} linhas")
        linhas.append(f"   • {sm['palavras']} palavras")
        linhas.append(f"   • {sm['caracteres']} caracteres")
    
    if 'descricao_caracteres' in metricas:
        linhas.append(f"\n📝 Descrição: {metricas['descricao_caracteres']} caracteres")
        qual = metricas.get('descricao_qualidade', {})
        linhas.append(f"   • Cenários de ativação: {'✅' if qual.get('tem_quando_usar') else '❌'}")
        linhas.append(f"   • Exemplos: {'✅' if qual.get('tem_exemplos') else '❌'}")
        linhas.append(f"   • Formatos de arquivo: {'✅' if qual.get('tem_formato_arquivo') else '❌'}")
    
    if 'estrutura' in metricas:
        est = metricas['estrutura']
        linhas.append(f"\n📁 Estrutura:")
        linhas.append(f"   • {est['secoes']} seções")
        linhas.append(f"   • {est['subsecoes']} subseções")
    
    if 'codigo' in metricas:
        cod = metricas['codigo']
        linhas.append(f"\n💻 Código:")
        linhas.append(f"   • {cod['blocos']} blocos")
        linhas.append(f"   • {cod['linhas_totais']} linhas totais")
        if cod['linguagens']:
            linhas.append(f"   • Linguagens: {', '.join(cod['linguagens'].keys())}")
    
    if metricas.get('scripts'):
        linhas.append(f"\n⚙️  Scripts: {', '.join(metricas['scripts'])}")
    
    if metricas.get('references'):
        linhas.append(f"📚 References: {', '.join(metricas['references'])}")
    
    if metricas.get('assets'):
        linhas.append(f"🎨 Assets: {len(metricas['assets'])} arquivo(s)")
    
    # Sugestões
    sugestoes = relatorio.get('sugestoes', [])
    if sugestoes:
        linhas.append(f"\n💡 Sugestões de Melhoria ({len(sugestoes)}):")
        for i, sugestao in enumerate(sugestoes, 1):
            linhas.append(f"\n   {i}. {sugestao}")
    else:
        linhas.append("\n✅ Nenhuma sugestão de melhoria identificada!")
    
    return '\n'.join(linhas)


def main():
    if len(sys.argv) != 2:
        print("Forge Analyze — Analisa habilidade e sugere melhorias")
        print()
        print("Uso: forge_analyze.py <caminho-da-habilidade>")
        print()
        print("Exemplos:")
        print("  forge_analyze.py ./minha-habilidade")
        print("  forge_analyze.py /caminho/para/skill")
        sys.exit(1)
    
    caminho = sys.argv[1]
    
    print(f"🔍 Analisando: {caminho}")
    print()
    
    relatorio = analisar_habilidade(caminho)
    print(formatar_relatorio(relatorio))


if __name__ == "__main__":
    main()
