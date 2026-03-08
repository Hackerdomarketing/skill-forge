# Checklist de Qualidade para Habilidades

Usar este checklist antes de empacotar e distribuir uma habilidade. Cada item deve ser verificado.

---

## 1. Estrutura de Arquivos

### Obrigatório
- [ ] SKILL.md existe na raiz da habilidade
- [ ] Nome do diretório corresponde ao campo `name` no frontmatter
- [ ] Nome usa kebab-case (letras minúsculas, dígitos, hífens)
- [ ] Nome tem no máximo 64 caracteres

### Verificar Ausência
- [ ] NÃO existe README.md (desnecessário)
- [ ] NÃO existe CHANGELOG.md (desnecessário)
- [ ] NÃO existe INSTALLATION.md (desnecessário)
- [ ] NÃO existem arquivos de teste na raiz
- [ ] NÃO existem arquivos temporários (.tmp, .bak, .swp)
- [ ] NÃO existem diretórios __pycache__ ou node_modules

---

## 2. Frontmatter do SKILL.md

### Formato
- [ ] Começa com `---` na primeira linha
- [ ] Termina com `---` após os campos
- [ ] YAML é válido (sem erros de sintaxe)

### Campos Obrigatórios
- [ ] `name` está presente
- [ ] `name` é string em kebab-case
- [ ] `description` está presente
- [ ] `description` é string
- [ ] `description` tem menos de 1024 caracteres
- [ ] `description` não contém < ou >

### Qualidade da Descrição
- [ ] Descreve O QUE a habilidade faz
- [ ] Descreve QUANDO usar (cenários de ativação)
- [ ] Inclui formatos de arquivo relevantes (se aplicável)
- [ ] Contém palavras-chave que usuários usariam
- [ ] Diferencia de outras habilidades similares

### Campos Opcionais (se presentes)
- [ ] `license` aponta para arquivo existente ou é texto válido
- [ ] `compatibility` tem menos de 500 caracteres (se presente)
- [ ] Não há campos não reconhecidos

---

## 3. Corpo do SKILL.md

### Estrutura
- [ ] Tem título principal (# Título)
- [ ] Tem seção de Visão Geral ou equivalente
- [ ] Seções estão organizadas logicamente
- [ ] Tem menos de 500 linhas (ideal: menos de 300)

### Conteúdo
- [ ] Usa forma imperativa ("Executar", não "Você deve executar")
- [ ] Não duplica informação de references/
- [ ] Armadilhas marcadas com **CRITICAL:**
- [ ] Código é executável (testado)
- [ ] Links para resources estão corretos

### Não Deve Conter
- [ ] Seção "Quando Usar Esta Habilidade" (deve estar na descrição)
- [ ] Explicações de conceitos básicos que Claude já sabe
- [ ] Informação duplicada entre seções
- [ ] TODOs não resolvidos

---

## 4. Diretório scripts/

### Se existe:
- [ ] Todos os scripts são executáveis
- [ ] Scripts têm shebang apropriado (#!/usr/bin/env python3)
- [ ] Scripts têm docstring com uso
- [ ] Scripts foram testados com entradas reais
- [ ] Scripts tratam erros graciosamente
- [ ] Não há scripts de exemplo/placeholder não utilizados

### Scripts Python:
- [ ] Usam argparse ou sys.argv consistentemente
- [ ] Têm função main() se executáveis
- [ ] Imports estão no topo

### Scripts Bash:
- [ ] Usam `set -e` para parar em erros
- [ ] Verificam argumentos obrigatórios
- [ ] Têm mensagens de uso (--help)

---

## 5. Diretório references/

### Se existe:
- [ ] Cada arquivo é referenciado no SKILL.md
- [ ] SKILL.md indica QUANDO ler cada arquivo
- [ ] Não há sobreposição com conteúdo do SKILL.md
- [ ] Arquivos grandes (mais de 10mil palavras) têm padrões de grep documentados
- [ ] Não há arquivos de exemplo/placeholder não utilizados

### Conteúdo:
- [ ] Informação é necessária (Claude não saberia sem ela)
- [ ] Estrutura facilita busca e navegação
- [ ] Código em references é executável

---

## 6. Diretório assets/

### Se existe:
- [ ] Cada asset é usado pela habilidade
- [ ] Assets não são carregados no contexto desnecessariamente
- [ ] Templates estão completos e funcionais
- [ ] Imagens estão otimizadas (não excessivamente grandes)
- [ ] Não há assets de exemplo/placeholder não utilizados

### Organização:
- [ ] Assets relacionados estão agrupados em subdiretórios se necessário
- [ ] Nomes de arquivo são descritivos

---

## 7. Teste Funcional

### Ativação
- [ ] Descrição ativa a habilidade para casos de uso principais
- [ ] Descrição NÃO ativa para casos não relacionados
- [ ] Testar com 3+ prompts diferentes que deveriam ativar
- [ ] Testar com 2+ prompts que NÃO deveriam ativar

### Execução
- [ ] Cada fluxo de trabalho documentado funciona
- [ ] Scripts executam sem erros com entradas válidas
- [ ] Scripts falham graciosamente com entradas inválidas
- [ ] Saídas correspondem ao documentado

### Qualidade de Saída
- [ ] Resultados são úteis e corretos
- [ ] Formatação é profissional
- [ ] Não há efeitos colaterais indesejados

---

## 8. Eficiência de Contexto

### Tokens
- [ ] SKILL.md não excede 5000 palavras (ideal: menos de 2000)
- [ ] Informação detalhada está em references/, não no SKILL.md
- [ ] Não há repetição de informação
- [ ] Comentários em código são concisos

### Revelação Progressiva
- [ ] Informação básica no SKILL.md
- [ ] Detalhes avançados em references/
- [ ] Assets não são lidos para contexto
- [ ] Scripts podem ser executados sem leitura quando possível

---

## 9. Manutenibilidade

### Clareza
- [ ] Outro desenvolvedor entenderia a habilidade
- [ ] Decisões de design são óbvias ou documentadas
- [ ] Não há "código mágico" sem explicação

### Extensibilidade
- [ ] Novos casos de uso podem ser adicionados
- [ ] Estrutura permite iteração
- [ ] Dependências são mínimas e documentadas

---

## Resumo de Validação

Antes de empacotar, confirmar:

```
□ Estrutura de arquivos correta
□ Frontmatter válido e descrição efetiva
□ Corpo do SKILL.md bem organizado
□ Scripts testados e funcionais
□ References não duplicam SKILL.md
□ Assets necessários e otimizados
□ Testes funcionais passam
□ Contexto é eficiente
□ Código é manutenível
```

Executar validação automática:

```bash
python scripts/forge_validate.py <caminho-da-habilidade>
```

Se todas as verificações passarem, empacotar:

```bash
python scripts/forge_package.py <caminho-da-habilidade>
```
