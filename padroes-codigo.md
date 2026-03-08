# Padrões de Código para SKILL.md

Este documento contém templates e padrões para incluir código de forma efetiva no corpo do SKILL.md.

## Princípio Fundamental

Código no SKILL.md deve ser:
1. **Executável** — copiar e colar deve funcionar
2. **Autocontido** — não depender de contexto externo não documentado
3. **Comentado estrategicamente** — explicar o "porquê", não o "o quê"

---

## Padrão 1: Bloco de Configuração Inicial

Usar quando a habilidade requer setup antes do uso.

```markdown
### Configuração

```javascript
// Importações necessárias — instalar com: npm install -g pacote
const { Classe1, Classe2, Classe3 } = require('pacote');
const fs = require('fs');

// Configuração base
const config = {
  opcao1: 'valor',
  opcao2: 123
};
```

**Dependências:**
- `pacote`: Descrição do que faz
- `outra-dependencia`: Descrição
```

**Características:**
- Comentário com comando de instalação
- Configuração com valores padrão sensatos
- Lista de dependências após o bloco

---

## Padrão 2: Exemplo Mínimo Funcional

Usar para mostrar o uso mais básico.

```markdown
### Uso Básico

```python
# Exemplo mínimo: converter arquivo
from modulo import funcao_principal

resultado = funcao_principal("entrada.ext")
print(resultado)  # Saída esperada: ...
```

Para casos mais complexos, ver seção [Uso Avançado](#uso-avançado).
```

**Características:**
- Comentário indicando o propósito
- Código em 3-5 linhas
- Saída esperada como comentário
- Link para seção avançada

---

## Padrão 3: Tabela de Referência com Código

Usar para documentar múltiplas operações relacionadas.

```markdown
### Operações Disponíveis

| Operação | Código |
|----------|--------|
| Criar | `objeto = Classe()` |
| Ler | `dados = objeto.ler(arquivo)` |
| Salvar | `objeto.salvar(destino)` |

### Exemplos Detalhados

**Criar:**
```python
objeto = Classe(parametro="valor")
```

**Ler:**
```python
dados = objeto.ler("arquivo.ext")
# dados contém: {'campo': valor, ...}
```
```

**Características:**
- Tabela de referência rápida
- Exemplos expandidos abaixo
- Estrutura de dados documentada em comentário

---

## Padrão 4: Código com Avisos Críticos

Usar quando existem armadilhas comuns.

```markdown
### Criando Elementos

**CRITICAL: Sempre especificar o tipo explicitamente**

```javascript
// ✅ CORRETO — tipo especificado
new Elemento({
  type: "png",  // OBRIGATÓRIO: png, jpg, gif
  data: dados
});

// ❌ ERRADO — tipo omitido causa erro silencioso
new Elemento({
  data: dados  // VAI FALHAR
});
```

| Tipo | Extensões Válidas |
|------|-------------------|
| `"png"` | .png |
| `"jpg"` | .jpg, .jpeg |
| `"gif"` | .gif |
```

**Características:**
- Aviso CRITICAL em negrito antes do código
- Exemplo correto com ✅
- Exemplo incorreto com ❌
- Tabela de valores válidos

---

## Padrão 5: Fluxo de Trabalho em Código

Usar para processos com múltiplos passos.

```markdown
### Fluxo Completo

```bash
# Passo 1: Preparar entrada
python scripts/preparar.py entrada.ext temp/

# Passo 2: Processar
python scripts/processar.py temp/ --opcao valor

# Passo 3: Finalizar
python scripts/finalizar.py temp/ saida.ext

# Limpar temporários
rm -rf temp/
```

**Pontos de Verificação:**
- Após Passo 1: `temp/` deve conter arquivos .json
- Após Passo 2: Verificar logs em `temp/log.txt`
- Após Passo 3: `saida.ext` deve existir
```

**Características:**
- Comentários numerados para cada passo
- Passos executáveis em sequência
- Pontos de verificação após o bloco

---

## Padrão 6: Código Condicional

Usar quando o código varia baseado em condições.

```markdown
### Escolhendo a Abordagem

**Para arquivos pequenos (menos de 10MB):**
```python
# Carrega tudo em memória
dados = arquivo.read()
processar(dados)
```

**Para arquivos grandes (mais de 10MB):**
```python
# Processa em chunks para economizar memória
for chunk in arquivo.iter_chunks(tamanho=1024*1024):
    processar_chunk(chunk)
```

**Regra de decisão:**
- Menos de 10MB → Método em memória (mais rápido)
- Mais de 10MB → Método em chunks (mais seguro)
```

**Características:**
- Condição em negrito antes de cada bloco
- Comentário explicando a diferença
- Regra de decisão explícita

---

## Padrão 7: Estrutura de Dados Documentada

Usar quando o código manipula estruturas complexas.

```markdown
### Estrutura do Documento

```javascript
const documento = {
  // Metadados (obrigatórios)
  titulo: "string",
  autor: "string",
  dataCriacao: "ISO 8601",
  
  // Conteúdo (pelo menos um obrigatório)
  secoes: [
    {
      tipo: "paragrafo" | "titulo" | "lista",
      conteudo: "string",
      nivel: 1-6  // apenas para tipo "titulo"
    }
  ],
  
  // Configuração (opcional)
  opcoes: {
    margens: { topo: 1440, direita: 1440, ... },  // em DXA (1440 = 1 polegada)
    orientacao: "retrato" | "paisagem"
  }
};
```

**Notas:**
- Datas em formato ISO 8601: `"2025-01-15T10:30:00Z"`
- Unidade DXA: 1440 DXA = 1 polegada = 2.54 cm
```

**Características:**
- Comentários inline para cada seção
- Tipos explícitos com `|` para alternativas
- Notas explicando unidades e formatos

---

## Padrão 8: Script de Referência

Usar quando referenciar scripts na pasta `scripts/`.

```markdown
### Usando o Script de Conversão

**Localização:** `scripts/converter.py`

**Uso:**
```bash
python scripts/converter.py <entrada> <saida> [opcoes]
```

**Argumentos:**
| Argumento | Tipo | Descrição |
|-----------|------|-----------|
| `entrada` | caminho | Arquivo de entrada |
| `saida` | caminho | Arquivo de destino |
| `--formato` | string | Formato de saída (padrão: "auto") |
| `--qualidade` | int | Qualidade 1-100 (padrão: 85) |

**Exemplo:**
```bash
python scripts/converter.py documento.pdf saida.docx --formato docx --qualidade 90
```

**Saída esperada:**
```
Convertendo documento.pdf...
Formato detectado: PDF
Processando 15 páginas...
Salvo em: saida.docx
```
```

**Características:**
- Localização explícita do script
- Sintaxe de uso com placeholders
- Tabela de argumentos com tipos e padrões
- Exemplo realista com saída esperada

---

## Regras Gerais para Código em SKILL.md

1. **Usar linguagem de código correta** — especificar `python`, `javascript`, `bash`, não genérico
2. **Não truncar** — código deve ser completo e executável
3. **Comentários em português** — manter consistência com o documento
4. **Evitar dependências desnecessárias** — preferir bibliotecas padrão quando possível
5. **Testar antes de incluir** — código não testado causa frustração
6. **Documentar saídas** — usuário deve saber o que esperar
