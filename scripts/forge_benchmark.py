#!/usr/bin/env python3
"""
Forge Benchmark — Agrega resultados de avaliação em estatísticas de benchmark

Uso:
    forge_benchmark.py --workspace <caminho> --iteration <N>

Exemplos:
    forge_benchmark.py --workspace ./workspace --iteration 1
    forge_benchmark.py --workspace ./workspace --iteration 3

Gera:
    - benchmark.json: Estatísticas estruturadas por configuração
    - benchmark.md: Tabela resumo em Markdown

Métricas calculadas:
    - pass_rate: taxa de aprovação (média e desvio padrão)
    - timing: duração em ms (média e desvio padrão)
    - tokens: total de tokens (média e desvio padrão)
    - delta: diferença entre with_skill e without_skill
"""

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Optional


class AgregadorDeBenchmark:
    """Agrega resultados de grading em estatísticas de benchmark."""

    def __init__(self, workspace: Path, iteration: int):
        """
        Inicializa o agregador de benchmark.

        Args:
            workspace: Caminho para o diretório workspace
            iteration: Número da iteração a processar
        """
        self.workspace = workspace.resolve()
        self.iteration = iteration
        self.dir_iteracao = self.workspace / f"iteration-{iteration}"

    def _calcular_estatisticas(self, valores: list[float]) -> dict:
        """
        Calcula média e desvio padrão de uma lista de valores numéricos.

        Usa desvio padrão amostral (n-1) quando há mais de um valor.
        """
        if not valores:
            return {"mean": 0.0, "stddev": 0.0, "count": 0}

        n = len(valores)
        media = sum(valores) / n

        if n > 1:
            variancia = sum((x - media) ** 2 for x in valores) / (n - 1)
            desvio = math.sqrt(variancia)
        else:
            desvio = 0.0

        return {
            "mean": round(media, 4),
            "stddev": round(desvio, 4),
            "count": n,
            "min": round(min(valores), 4),
            "max": round(max(valores), 4),
        }

    def _carregar_grading(self, eval_dir: Path, config: str) -> Optional[dict]:
        """Carrega grading.json de um diretório de configuração."""
        grading_path = eval_dir / config / "grading.json"
        if not grading_path.exists():
            return None

        try:
            return json.loads(grading_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"  ⚠️  Erro ao ler: {grading_path}")
            return None

    def _carregar_timing(self, eval_dir: Path, config: str) -> Optional[dict]:
        """Carrega timing.json de um diretório de configuração."""
        timing_path = eval_dir / config / "timing.json"
        if not timing_path.exists():
            return None

        try:
            return json.loads(timing_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"  ⚠️  Erro ao ler: {timing_path}")
            return None

    def _coletar_dados_por_config(self, config: str) -> dict:
        """
        Coleta todos os dados de grading e timing para uma configuração.

        Itera sobre todos os diretórios eval-N na iteração e agrega
        os dados encontrados para a configuração especificada.
        """
        passes = []
        duracoes = []
        tokens = []
        scores = []
        detalhes_por_eval = {}

        # Iterar sobre diretórios de eval ordenados
        eval_dirs = sorted(
            [d for d in self.dir_iteracao.iterdir()
             if d.is_dir() and d.name.startswith("eval-")]
        )

        for eval_dir in eval_dirs:
            eval_id = eval_dir.name.replace("eval-", "")

            # Carregar grading e timing
            grading = self._carregar_grading(eval_dir, config)
            timing = self._carregar_timing(eval_dir, config)

            detalhe = {"eval_id": eval_id}

            # Processar dados de grading
            if grading is not None:
                passou = grading.get("passed", False)
                passes.append(1.0 if passou else 0.0)
                detalhe["passed"] = passou
                score = grading.get("score", 0.0)
                scores.append(float(score))
                detalhe["score"] = score
                detalhe["assertions_passed"] = grading.get("assertions_passed", 0)
                detalhe["assertions_total"] = grading.get("assertions_total", 0)
                detalhe["feedback"] = grading.get("feedback", "")

            # Processar dados de timing
            if timing is not None:
                duracao = timing.get("duration_ms", 0)
                total_tokens = timing.get("total_tokens", 0)
                duracoes.append(float(duracao))
                tokens.append(float(total_tokens))
                detalhe["duration_ms"] = duracao
                detalhe["total_tokens"] = total_tokens

            detalhes_por_eval[eval_id] = detalhe

        return {
            "pass_rate": self._calcular_estatisticas(passes),
            "timing_ms": self._calcular_estatisticas(duracoes),
            "tokens": self._calcular_estatisticas(tokens),
            "scores": self._calcular_estatisticas(scores),
            "per_eval": detalhes_por_eval,
        }

    def _coletar_pipeline_metadata(self) -> dict:
        """
        Collects pipeline metadata from workspace artifacts.

        Searches for triage.json, study bundle index.json, and
        dissection-manifest.json in the workspace directory.

        Returns:
            Dictionary with pipeline metadata, or empty dict if no artifacts found
        """
        metadata = {}

        # Check for triage.json
        triage_path = self.workspace / "triage.json"
        if triage_path.exists():
            try:
                triage = json.loads(triage_path.read_text(encoding="utf-8"))
                metadata["path_taken"] = triage.get("path", triage.get("route", "unknown"))
                print(f"   📋 Pipeline: triage.json encontrado (path={metadata['path_taken']})")
            except json.JSONDecodeError:
                print(f"  ⚠️  Erro ao ler triage.json")

        # Check for study bundle index.json
        study_dir = self.workspace / "stage-a-study"
        if study_dir.exists():
            # Search for index.json in subdirectories
            index_files = list(study_dir.rglob("index.json"))
            if index_files:
                try:
                    index_data = json.loads(index_files[0].read_text(encoding="utf-8"))
                    certeza = index_data.get("certeza_resumo", {})
                    metadata["study_certainty_profile"] = certeza
                    print(f"   📋 Pipeline: study bundle index.json encontrado")
                except json.JSONDecodeError:
                    print(f"  ⚠️  Erro ao ler study bundle index.json")

        # Check for dissection-manifest.json
        dissection_dir = self.workspace / "stage-b-dissection"
        if dissection_dir.exists():
            manifest_path = dissection_dir / "dissection-manifest.json"
            if manifest_path.exists():
                try:
                    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                    certainty = manifest.get("certainty_profile", {})
                    total_claims = sum(certainty.values()) if certainty else 0
                    covered = total_claims - certainty.get("undetermined", 0) if total_claims > 0 else 0
                    coverage = covered / total_claims if total_claims > 0 else 0.0
                    metadata["dissection_coverage"] = round(coverage, 4)
                    print(f"   📋 Pipeline: dissection-manifest.json encontrado (coverage={coverage:.2%})")
                except json.JSONDecodeError:
                    print(f"  ⚠️  Erro ao ler dissection-manifest.json")

        # Check for knowledge_accuracy.json
        accuracy_path = self.workspace / "knowledge_accuracy.json"
        if accuracy_path.exists():
            try:
                accuracy_data = json.loads(accuracy_path.read_text(encoding="utf-8"))
                metadata["knowledge_accuracy_score"] = accuracy_data.get("score", 0.0)
                print(f"   📋 Pipeline: knowledge_accuracy.json encontrado")
            except json.JSONDecodeError:
                print(f"  ⚠️  Erro ao ler knowledge_accuracy.json")

        # Fill defaults for missing fields when at least one artifact was found
        if metadata:
            metadata.setdefault("path_taken", "unknown")
            metadata.setdefault("study_certainty_profile", {})
            metadata.setdefault("dissection_coverage", 0.0)
            metadata.setdefault("knowledge_accuracy_score", 0.0)

        return metadata

    def _calcular_delta(self, with_skill: dict, without_skill: dict) -> dict:
        """
        Calcula diferença (melhoria) entre with_skill e without_skill.

        Para pass_rate e scores, positivo indica melhoria.
        Para timing e tokens, negativo indica melhoria (menor é melhor).
        """
        delta = {}

        for metrica in ["pass_rate", "timing_ms", "tokens", "scores"]:
            ws_mean = with_skill.get(metrica, {}).get("mean", 0.0)
            wo_mean = without_skill.get(metrica, {}).get("mean", 0.0)

            diferenca = ws_mean - wo_mean
            melhoria_pct = ((diferenca / wo_mean) * 100) if wo_mean > 0 else 0.0

            delta[metrica] = {
                "absolute": round(diferenca, 4),
                "percentage": round(melhoria_pct, 2),
                "with_skill_mean": round(ws_mean, 4),
                "without_skill_mean": round(wo_mean, 4),
            }

        return delta

    def _gerar_markdown(self, benchmark: dict) -> str:
        """Gera tabela resumo em formato Markdown legível."""
        linhas = [
            f"# 📊 Benchmark — Iteração {self.iteration}",
            "",
            f"**Workspace:** `{self.workspace}`",
            "",
            "## Resumo Comparativo",
            "",
            "| Métrica | with_skill | without_skill | Delta |",
            "|---------|-----------|---------------|-------|",
        ]

        ws = benchmark.get("with_skill", {})
        wo = benchmark.get("without_skill", {})
        delta = benchmark.get("delta", {})

        # Pass Rate
        ws_pr = ws.get("pass_rate", {})
        wo_pr = wo.get("pass_rate", {})
        d_pr = delta.get("pass_rate", {})
        linhas.append(
            f"| Pass Rate | {ws_pr.get('mean', 0):.2%} ± {ws_pr.get('stddev', 0):.2%} "
            f"| {wo_pr.get('mean', 0):.2%} ± {wo_pr.get('stddev', 0):.2%} "
            f"| {d_pr.get('absolute', 0):+.2%} ({d_pr.get('percentage', 0):+.1f}%) |"
        )

        # Scores
        ws_sc = ws.get("scores", {})
        wo_sc = wo.get("scores", {})
        d_sc = delta.get("scores", {})
        linhas.append(
            f"| Score | {ws_sc.get('mean', 0):.2f} ± {ws_sc.get('stddev', 0):.2f} "
            f"| {wo_sc.get('mean', 0):.2f} ± {wo_sc.get('stddev', 0):.2f} "
            f"| {d_sc.get('absolute', 0):+.2f} ({d_sc.get('percentage', 0):+.1f}%) |"
        )

        # Timing
        ws_tm = ws.get("timing_ms", {})
        wo_tm = wo.get("timing_ms", {})
        d_tm = delta.get("timing_ms", {})
        linhas.append(
            f"| Timing (ms) | {ws_tm.get('mean', 0):.0f} ± {ws_tm.get('stddev', 0):.0f} "
            f"| {wo_tm.get('mean', 0):.0f} ± {wo_tm.get('stddev', 0):.0f} "
            f"| {d_tm.get('absolute', 0):+.0f} ({d_tm.get('percentage', 0):+.1f}%) |"
        )

        # Tokens
        ws_tk = ws.get("tokens", {})
        wo_tk = wo.get("tokens", {})
        d_tk = delta.get("tokens", {})
        linhas.append(
            f"| Tokens | {ws_tk.get('mean', 0):.0f} ± {ws_tk.get('stddev', 0):.0f} "
            f"| {wo_tk.get('mean', 0):.0f} ± {wo_tk.get('stddev', 0):.0f} "
            f"| {d_tk.get('absolute', 0):+.0f} ({d_tk.get('percentage', 0):+.1f}%) |"
        )

        # Detalhes por eval
        linhas.extend(["", "## Detalhes por Eval", ""])

        ws_per_eval = ws.get("per_eval", {})
        wo_per_eval = wo.get("per_eval", {})
        all_eval_ids = sorted(set(list(ws_per_eval.keys()) + list(wo_per_eval.keys())))

        if all_eval_ids:
            linhas.append("| Eval | Config | Passou | Score | Duração (ms) | Tokens |")
            linhas.append("|------|--------|--------|-------|-------------|--------|")

            for eval_id in all_eval_ids:
                for config, dados_config in [("with_skill", ws_per_eval), ("without_skill", wo_per_eval)]:
                    d = dados_config.get(eval_id, {})
                    passou = "✅" if d.get("passed", False) else "❌"
                    score = f"{d.get('score', 0):.2f}" if "score" in d else "-"
                    duracao = d.get("duration_ms", "-")
                    tkns = d.get("total_tokens", "-")
                    linhas.append(
                        f"| {eval_id} | {config} | {passou} | {score} | {duracao} | {tkns} |"
                    )

        linhas.append("")
        return "\n".join(linhas)

    def executar(self) -> dict:
        """
        Executa agregação completa de benchmark e gera artefatos de saída.

        Lê todos os grading.json e timing.json da iteração, calcula
        estatísticas agregadas e salva benchmark.json e benchmark.md.
        """
        if not self.dir_iteracao.exists():
            print(f"❌ Diretório de iteração não encontrado: {self.dir_iteracao}")
            return {"erro": "Diretório de iteração não encontrado"}

        # Verificar se há diretórios de eval
        eval_dirs = [d for d in self.dir_iteracao.iterdir()
                     if d.is_dir() and d.name.startswith("eval-")]
        if not eval_dirs:
            print(f"❌ Nenhum diretório eval-N encontrado em: {self.dir_iteracao}")
            return {"erro": "Nenhum eval encontrado"}

        print(f"📊 Forge Benchmark — Agregando resultados")
        print(f"   📂 Workspace: {self.workspace}")
        print(f"   🔄 Iteração: {self.iteration}")
        print(f"   📋 Evals encontrados: {len(eval_dirs)}")

        # Coletar dados para cada configuração
        print(f"\n   ▶ Coletando dados with_skill...")
        dados_with = self._coletar_dados_por_config("with_skill")
        print(f"   ✅ {dados_with['pass_rate']['count']} eval(s) com grading")

        print(f"   ▶ Coletando dados without_skill...")
        dados_without = self._coletar_dados_por_config("without_skill")
        print(f"   ✅ {dados_without['pass_rate']['count']} eval(s) com grading")

        # Calcular delta entre configurações
        delta = self._calcular_delta(dados_with, dados_without)

        # Collect pipeline metadata from workspace artifacts
        pipeline_metadata = self._coletar_pipeline_metadata()

        # Montar benchmark completo
        benchmark = {
            "workspace": str(self.workspace),
            "iteration": self.iteration,
            "total_evals": len(eval_dirs),
            "with_skill": {
                "pass_rate": dados_with["pass_rate"],
                "timing_ms": dados_with["timing_ms"],
                "tokens": dados_with["tokens"],
                "scores": dados_with["scores"],
                "per_eval": dados_with["per_eval"],
            },
            "without_skill": {
                "pass_rate": dados_without["pass_rate"],
                "timing_ms": dados_without["timing_ms"],
                "tokens": dados_without["tokens"],
                "scores": dados_without["scores"],
                "per_eval": dados_without["per_eval"],
            },
            "delta": delta,
        }

        # Add pipeline metadata if any artifacts were found
        if pipeline_metadata:
            benchmark["pipeline_metadata"] = pipeline_metadata

        # Salvar benchmark.json
        benchmark_json_path = self.dir_iteracao / "benchmark.json"
        benchmark_json_path.write_text(
            json.dumps(benchmark, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"\n   💾 benchmark.json salvo em: {benchmark_json_path}")

        # Gerar e salvar benchmark.md
        markdown = self._gerar_markdown(benchmark)
        benchmark_md_path = self.dir_iteracao / "benchmark.md"
        benchmark_md_path.write_text(markdown, encoding="utf-8")
        print(f"   💾 benchmark.md salvo em: {benchmark_md_path}")

        # Exibir resumo no console
        print(f"\n🏁 Benchmark concluído!")
        pr_ws = dados_with["pass_rate"]["mean"]
        pr_wo = dados_without["pass_rate"]["mean"]
        print(f"   📈 Pass Rate: with_skill={pr_ws:.2%} | without_skill={pr_wo:.2%}")
        print(f"   ⏱️  Timing: with_skill={dados_with['timing_ms']['mean']:.0f}ms "
              f"| without_skill={dados_without['timing_ms']['mean']:.0f}ms")
        d_pr = delta["pass_rate"]["absolute"]
        sinal = "+" if d_pr >= 0 else ""
        print(f"   🔄 Delta pass_rate: {sinal}{d_pr:.2%}")

        return benchmark


def main():
    """Ponto de entrada principal do script."""
    parser = argparse.ArgumentParser(
        description="Forge Benchmark — Agrega resultados de avaliação em estatísticas"
    )
    parser.add_argument(
        "--workspace",
        required=True,
        help="Caminho para o diretório workspace",
    )
    parser.add_argument(
        "--iteration",
        type=int,
        default=1,
        help="Número da iteração a processar (padrão: 1)",
    )

    args = parser.parse_args()

    agregador = AgregadorDeBenchmark(
        workspace=Path(args.workspace),
        iteration=args.iteration,
    )

    resultado = agregador.executar()

    if "erro" in resultado:
        print(f"\n❌ {resultado['erro']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
