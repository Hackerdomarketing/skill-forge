#!/usr/bin/env python3
"""
Forge Optimize — Otimiza descrição de habilidade para melhor ativação

Uso:
    forge_optimize.py --skill-path <caminho>

Exemplos:
    forge_optimize.py --skill-path ./minha-skill
    forge_optimize.py --skill-path ./skill --iterations 10 --queries 30

Fluxo:
    1. Gera queries de avaliação de trigger (positivas e negativas)
    2. Divide em treino (60%) e teste (40%) estratificado
    3. Para cada iteração:
       a. Testa descrição atual contra conjunto de treino
       b. Identifica falhas e chama claude para melhorar descrição
       c. Valida contra conjunto de teste
       d. Mantém melhor descrição pelo score de teste (evita overfitting)
    4. Gera relatório de otimização com resultados por iteração
"""

import argparse
import json
import random
import re
import subprocess
import sys
import time
import yaml
from pathlib import Path
from typing import Optional


# Limite máximo de caracteres para a descrição
MAX_DESCRICAO_CHARS = 1024


class OtimizadorDeDescricao:
    """Otimiza descrição de habilidade via avaliação iterativa de trigger."""

    def __init__(self, skill_path: Path, iterations: int = 5, num_queries: int = 20):
        """
        Inicializa o otimizador.

        Args:
            skill_path: Caminho para o diretório da habilidade
            iterations: Número de iterações de otimização
            num_queries: Número total de queries de avaliação a gerar
        """
        self.skill_path = skill_path.resolve()
        self.iterations = iterations
        self.num_queries = num_queries
        self.skill_name = ""
        self.descricao_atual = ""
        self.skill_md_content = ""
        self.queries: list[dict] = []
        self.train_set: list[dict] = []
        self.test_set: list[dict] = []

    def _extrair_frontmatter(self) -> bool:
        """Extrai nome e descrição do frontmatter do SKILL.md."""
        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            print(f"❌ SKILL.md não encontrado em: {self.skill_path}")
            return False

        self.skill_md_content = skill_md.read_text(encoding="utf-8")

        # Extrair frontmatter YAML
        match = re.match(r'^---\n(.*?)\n---', self.skill_md_content, re.DOTALL)
        if not match:
            print("❌ Frontmatter YAML não encontrado no SKILL.md")
            return False

        try:
            frontmatter = yaml.safe_load(match.group(1))
        except yaml.YAMLError as e:
            print(f"❌ Erro ao ler frontmatter YAML: {e}")
            return False

        self.skill_name = frontmatter.get("name", self.skill_path.name)
        self.descricao_atual = frontmatter.get("description", "")

        if not self.descricao_atual:
            print("❌ Descrição vazia no frontmatter")
            return False

        return True

    def _chamar_claude(self, prompt: str, timeout: int = 120) -> str:
        """
        Chama claude -p com um prompt e retorna a saída.

        Args:
            prompt: Texto do prompt
            timeout: Timeout em segundos

        Returns:
            Saída do claude como string
        """
        try:
            resultado = subprocess.run(
                ["claude", "-p", prompt],
                capture_output=True, text=True, timeout=timeout,
            )
            return resultado.stdout.strip()
        except subprocess.TimeoutExpired:
            return "ERRO: Timeout"
        except FileNotFoundError:
            return "ERRO: Comando 'claude' não encontrado"

    def gerar_queries(self) -> bool:
        """
        Gera queries de avaliação de trigger usando claude.

        Cria queries positivas (should_trigger=True) e negativas
        (should_trigger=False, near-miss) baseadas na descrição atual.
        """
        # Calcular proporção: 60% positivas, 40% negativas
        num_positivas = int(self.num_queries * 0.6)
        num_negativas = self.num_queries - num_positivas

        print(f"   ▶ Gerando {num_positivas} queries positivas e {num_negativas} negativas...")

        prompt = f"""Gere exatamente {self.num_queries} queries de avaliação para testar se uma skill é ativada corretamente.

Skill: {self.skill_name}
Descrição atual: {self.descricao_atual}

Gere {num_positivas} queries que DEVEM ativar a skill (should_trigger: true).
Gere {num_negativas} queries que NÃO devem ativar a skill (should_trigger: false) — use "near-miss" queries que são similares mas fora do escopo.

Responda APENAS com JSON válido no formato:
[
  {{"id": 1, "query": "texto da query", "should_trigger": true, "reason": "motivo curto"}},
  ...
]

IMPORTANTE: Retorne SOMENTE o JSON, sem texto adicional, sem markdown."""

        saida = self._chamar_claude(prompt, timeout=180)

        # Tentar extrair JSON da saída
        try:
            # Procurar array JSON na saída
            json_match = re.search(r'\[.*\]', saida, re.DOTALL)
            if json_match:
                self.queries = json.loads(json_match.group())
            else:
                self.queries = json.loads(saida)
        except json.JSONDecodeError:
            print(f"  ⚠️  Falha ao parsear JSON, gerando queries padrão...")
            self._gerar_queries_fallback(num_positivas, num_negativas)
            return True

        if len(self.queries) < 4:
            print(f"  ⚠️  Poucas queries geradas ({len(self.queries)}), complementando...")
            self._gerar_queries_fallback(num_positivas, num_negativas)

        print(f"   ✅ {len(self.queries)} queries geradas")
        return True

    def _gerar_queries_fallback(self, num_pos: int, num_neg: int):
        """Gera queries de fallback quando claude falha na geração."""
        self.queries = []
        for i in range(num_pos):
            self.queries.append({
                "id": i + 1,
                "query": f"Use a skill {self.skill_name} para realizar tarefa #{i+1}",
                "should_trigger": True,
                "reason": "Query direta mencionando a skill",
            })
        for i in range(num_neg):
            self.queries.append({
                "id": num_pos + i + 1,
                "query": f"Faça algo genérico não relacionado à skill #{i+1}",
                "should_trigger": False,
                "reason": "Query fora do escopo da skill",
            })

    def dividir_treino_teste(self):
        """
        Divide queries em treino (60%) e teste (40%) com estratificação.

        Mantém proporção de should_trigger em ambos os conjuntos.
        """
        positivas = [q for q in self.queries if q.get("should_trigger", False)]
        negativas = [q for q in self.queries if not q.get("should_trigger", False)]

        random.shuffle(positivas)
        random.shuffle(negativas)

        # 60% treino, 40% teste
        split_pos = max(1, int(len(positivas) * 0.6))
        split_neg = max(1, int(len(negativas) * 0.6))

        self.train_set = positivas[:split_pos] + negativas[:split_neg]
        self.test_set = positivas[split_pos:] + negativas[split_neg:]

        random.shuffle(self.train_set)
        random.shuffle(self.test_set)

        print(f"   📊 Treino: {len(self.train_set)} queries "
              f"({sum(1 for q in self.train_set if q['should_trigger'])} pos, "
              f"{sum(1 for q in self.train_set if not q['should_trigger'])} neg)")
        print(f"   📊 Teste: {len(self.test_set)} queries "
              f"({sum(1 for q in self.test_set if q['should_trigger'])} pos, "
              f"{sum(1 for q in self.test_set if not q['should_trigger'])} neg)")

    def _avaliar_descricao(self, descricao: str, conjunto: list[dict]) -> dict:
        """
        Avalia uma descrição contra um conjunto de queries.

        Pergunta ao claude se cada query deveria ativar uma skill
        com a descrição dada, e compara com o resultado esperado.

        Returns:
            Dicionário com score, acertos, falhas e detalhes
        """
        acertos = 0
        falhas = []
        detalhes = []

        for query in conjunto:
            prompt = f"""Dada a seguinte descrição de uma skill:
"{descricao}"

E a seguinte query do usuário:
"{query['query']}"

Esta skill deveria ser ativada para responder esta query? Responda APENAS "SIM" ou "NÃO"."""

            resposta = self._chamar_claude(prompt, timeout=60)
            respondeu_sim = "SIM" in resposta.upper()[:20]
            esperado = query["should_trigger"]
            correto = respondeu_sim == esperado

            if correto:
                acertos += 1
            else:
                falhas.append({
                    "query": query["query"],
                    "expected": esperado,
                    "got": respondeu_sim,
                    "reason": query.get("reason", ""),
                })

            detalhes.append({
                "query_id": query.get("id", 0),
                "query": query["query"],
                "should_trigger": esperado,
                "triggered": respondeu_sim,
                "correct": correto,
            })

        score = acertos / len(conjunto) if conjunto else 0.0
        return {
            "score": round(score, 4),
            "acertos": acertos,
            "total": len(conjunto),
            "falhas": falhas,
            "detalhes": detalhes,
        }

    def _melhorar_descricao(self, descricao_atual: str, falhas: list[dict]) -> str:
        """
        Chama claude para melhorar a descrição baseado nas falhas encontradas.

        Envia as falhas do treino e pede uma descrição melhorada
        que corrija os problemas mantendo o limite de caracteres.
        """
        falhas_texto = "\n".join(
            f"- Query: \"{f['query']}\" | Esperado: {'ativar' if f['expected'] else 'não ativar'} "
            f"| Resultado: {'ativou' if f['got'] else 'não ativou'}"
            for f in falhas[:10]  # Limitar para não exceder contexto
        )

        prompt = f"""Melhore a descrição desta skill para corrigir os erros de ativação.

Skill: {self.skill_name}

Descrição atual ({len(descricao_atual)} caracteres):
"{descricao_atual}"

Falhas encontradas:
{falhas_texto}

Regras:
1. Máximo {MAX_DESCRICAO_CHARS} caracteres
2. Deve explicar O QUE a skill faz e QUANDO usar
3. Inclua cenários específicos de ativação
4. Inclua cenários que NÃO devem ativar (para evitar falsos positivos)
5. Use linguagem clara e direta

Responda APENAS com a nova descrição, sem aspas, sem explicação adicional."""

        nova_descricao = self._chamar_claude(prompt, timeout=120)

        # Limpar e validar
        nova_descricao = nova_descricao.strip().strip('"').strip("'")

        # Truncar se exceder limite
        if len(nova_descricao) > MAX_DESCRICAO_CHARS:
            nova_descricao = nova_descricao[:MAX_DESCRICAO_CHARS - 3] + "..."

        # Fallback se resultado inválido
        if len(nova_descricao) < 20:
            return descricao_atual

        return nova_descricao

    def executar(self) -> dict:
        """
        Executa o fluxo completo de otimização.

        Gera queries, divide em treino/teste, e itera melhorando
        a descrição com base nos erros do treino, validando no teste.
        """
        if not self._extrair_frontmatter():
            return {"erro": "Falha ao ler SKILL.md"}

        print(f"🔧 Forge Optimize — Otimizando habilidade: {self.skill_name}")
        print(f"   📂 Skill: {self.skill_path}")
        print(f"   📝 Descrição atual ({len(self.descricao_atual)} chars)")
        print(f"   🔄 Iterações: {self.iterations}")
        print(f"   📋 Queries: {self.num_queries}")

        # Gerar e dividir queries
        print(f"\n📋 Gerando queries de avaliação...")
        if not self.gerar_queries():
            return {"erro": "Falha ao gerar queries"}

        # Salvar queries geradas
        trigger_evals_path = self.skill_path / "trigger_evals.json"
        trigger_evals_path.write_text(
            json.dumps(self.queries, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"   💾 Queries salvas em: {trigger_evals_path}")

        # Dividir treino/teste
        print(f"\n📊 Dividindo em treino/teste...")
        self.dividir_treino_teste()

        # Iterar otimização
        melhor_descricao = self.descricao_atual
        melhor_score_teste = 0.0
        resultados_iteracoes = []

        for i in range(1, self.iterations + 1):
            print(f"\n🔄 Iteração {i}/{self.iterations}")

            # Avaliar contra treino
            print(f"   ▶ Avaliando no treino...")
            resultado_treino = self._avaliar_descricao(self.descricao_atual, self.train_set)
            print(f"   📈 Score treino: {resultado_treino['score']:.2%} "
                  f"({resultado_treino['acertos']}/{resultado_treino['total']})")

            # Se há falhas, tentar melhorar
            if resultado_treino["falhas"]:
                print(f"   🔧 Melhorando descrição ({len(resultado_treino['falhas'])} falhas)...")
                nova_descricao = self._melhorar_descricao(
                    self.descricao_atual, resultado_treino["falhas"]
                )
            else:
                nova_descricao = self.descricao_atual
                print(f"   ✅ Sem falhas no treino, mantendo descrição")

            # Avaliar nova descrição no teste (para evitar overfitting)
            print(f"   ▶ Validando no teste...")
            resultado_teste = self._avaliar_descricao(nova_descricao, self.test_set)
            print(f"   📈 Score teste: {resultado_teste['score']:.2%} "
                  f"({resultado_teste['acertos']}/{resultado_teste['total']})")

            # Manter melhor pelo score de TESTE
            if resultado_teste["score"] > melhor_score_teste:
                melhor_score_teste = resultado_teste["score"]
                melhor_descricao = nova_descricao
                self.descricao_atual = nova_descricao
                print(f"   🏆 Nova melhor descrição! (teste: {melhor_score_teste:.2%})")
            else:
                print(f"   ⏸️  Descrição não melhorou no teste, mantendo anterior")

            resultados_iteracoes.append({
                "iteration": i,
                "description": nova_descricao,
                "description_length": len(nova_descricao),
                "train_score": resultado_treino["score"],
                "train_details": resultado_treino["acertos"],
                "test_score": resultado_teste["score"],
                "test_details": resultado_teste["acertos"],
                "is_best": nova_descricao == melhor_descricao,
            })

        # Gerar relatório final
        relatorio = {
            "skill_name": self.skill_name,
            "skill_path": str(self.skill_path),
            "original_description": self.skill_md_content.split("description:")[1].split("\n")[0].strip().strip('"') if "description:" in self.skill_md_content else "",
            "best_description": melhor_descricao,
            "best_test_score": melhor_score_teste,
            "total_iterations": self.iterations,
            "total_queries": len(self.queries),
            "train_size": len(self.train_set),
            "test_size": len(self.test_set),
            "iterations": resultados_iteracoes,
        }

        # Salvar relatório
        relatorio_path = self.skill_path / "optimization_report.json"
        relatorio_path.write_text(
            json.dumps(relatorio, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        # Exibir resumo final
        print(f"\n🏁 Otimização concluída!")
        print(f"   📊 Melhor score de teste: {melhor_score_teste:.2%}")
        print(f"   📝 Melhor descrição ({len(melhor_descricao)} chars):")
        print(f"   \"{melhor_descricao[:100]}{'...' if len(melhor_descricao) > 100 else ''}\"")
        print(f"   💾 Relatório salvo em: {relatorio_path}")
        print(f"   💾 Queries salvas em: {trigger_evals_path}")
        print(f"\n   ⚠️  Para aplicar a nova descrição, atualize manualmente o SKILL.md")

        return relatorio


def main():
    """Ponto de entrada principal do script."""
    parser = argparse.ArgumentParser(
        description="Forge Optimize — Otimiza descrição de skill para melhor ativação"
    )
    parser.add_argument(
        "--skill-path",
        required=True,
        help="Caminho para o diretório da habilidade",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=5,
        help="Número de iterações de otimização (padrão: 5)",
    )
    parser.add_argument(
        "--queries",
        type=int,
        default=20,
        help="Número total de queries de avaliação (padrão: 20)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Seed para reprodutibilidade (opcional)",
    )

    args = parser.parse_args()

    # Configurar seed se fornecida
    if args.seed is not None:
        random.seed(args.seed)

    otimizador = OtimizadorDeDescricao(
        skill_path=Path(args.skill_path),
        iterations=args.iterations,
        num_queries=args.queries,
    )

    resultado = otimizador.executar()

    if "erro" in resultado:
        print(f"\n❌ {resultado['erro']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
