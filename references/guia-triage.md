# Guia de Triagem — Triage Gate

Como classificar a complexidade de um dominio para decidir o caminho do pipeline.

## Sinais e Pontuacao

| Sinal | Score | Como detectar |
|-------|-------|---------------|
| Documentacao oficial acessivel | -1 | Existe docs.X.com, man pages, ou spec oficial publica |
| Usuario diz "skill simples" | -1 | Usuario explicita que e algo simples/rapido |
| APIs recentes/mutaveis | +1 | API mudou nos ultimos 12 meses, deprecations frequentes |
| Contradicoes conhecidas no dominio | +2 | Respostas diferentes em fontes diferentes, debates ativos |
| Claude ja errou nesse dominio | +2 | Usuario reporta que IA errou 2+ vezes nesse topico |
| Conhecimento especializado ausente | +2 | Dominio de nicho, praticas nao-documentadas, conhecimento tacito |
| Output de alto risco | +2 | Seguranca, financeiro, medico, juridico — erro tem consequencia real |

## Roteamento

| Score | Caminho | O que acontece |
|-------|---------|----------------|
| <= 0 | **Fast Path** | Direto pro Stage C (Forge). Identico ao v2 |
| 1-2 | **Medium Path** | Stage A abreviado (niveis 1-3) → Stage C |
| >= 3 | **Deep Path** | Stage A completo → Stage B → Stage C |

## Exemplos Praticos

### Fast Path (score <= 0)

**"Crie uma skill para formatar datas em portugues"**
- Documentacao oficial acessivel: -1 (APIs de data sao bem documentadas)
- Usuario diz "skill simples": -1
- Score total: -2 → **Fast Path**

**"Crie uma skill para gerar commits padronizados"**
- Documentacao oficial acessivel: -1 (git e bem documentado)
- Score total: -1 → **Fast Path**

### Medium Path (score 1-2)

**"Crie uma skill para configurar ESLint com TypeScript e Prettier"**
- Documentacao oficial acessivel: -1
- APIs recentes/mutaveis: +1 (ESLint flat config e recente)
- Contradicoes: +2 (muitas configs conflitantes online)
- Score total: 2 → **Medium Path**

**"Crie uma skill para deploy em Vercel com Edge Functions"**
- Documentacao oficial acessivel: -1
- APIs recentes/mutaveis: +1 (Edge runtime muda frequentemente)
- Score total: 0... mas se usuario reporta erros: +2 → **Medium Path**

### Deep Path (score >= 3)

**"Crie uma skill para seguranca de APIs REST"**
- Contradicoes: +2 (muitas praticas debatidas)
- Conhecimento especializado: +2 (OWASP, threat modeling)
- Output de alto risco: +2 (erro = vulnerabilidade)
- Score total: 6 → **Deep Path**

**"Crie uma skill para RLS no Supabase"**
- Claude ja errou: +2 (erros recorrentes com policies)
- Conhecimento especializado: +2 (interacao RLS + SECURITY DEFINER)
- Output de alto risco: +2 (erro = dados expostos)
- Score total: 6 → **Deep Path**

## Regras de Override

1. **Usuario pode forcar caminho:** Se usuario pedir "estudo profundo" → Deep Path independente do score
2. **Usuario pode pular:** Se usuario pedir "rapido, sem estudo" → Fast Path independente do score
3. **Nunca forcar Deep em skill simples:** Se o dominio e trivial, nao complicar. Trust the score
4. **Na duvida, Medium:** Se score esta entre 0 e 2 e ha incerteza, Medium Path e o mais seguro

## Como Executar a Triagem

1. Ler o pedido do usuario
2. Para cada sinal na tabela, avaliar se aplica (com evidencia)
3. Somar scores
4. Verificar se ha override do usuario
5. Apresentar resultado ao usuario: "Classifiquei como [path] porque [razoes]. Quer seguir assim ou prefere outro caminho?"
6. Salvar `triage.json` no workspace
