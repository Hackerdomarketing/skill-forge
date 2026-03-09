#!/usr/bin/env python3
"""
Forge Report — Gera visualizador HTML interativo para resultados de eval

Uso:
    forge_report.py --workspace <caminho> --iteration <N>

Exemplos:
    forge_report.py --workspace ./workspace --iteration 1
    forge_report.py --workspace ./workspace --iteration 2 --output relatorio.html
    forge_report.py --workspace ./workspace --iteration 2 --previous-workspace ./workspace-v1

Gera:
    - Arquivo HTML autocontido com:
      - Aba Outputs: prompt, saídas with/without skill, notas, feedback
      - Aba Benchmark: tabela comparativa de pass rates, timing, tokens
      - Detalhes expansíveis por eval
      - Botão para baixar feedback em JSON
"""

import argparse
import json
import html
import sys
from pathlib import Path
from typing import Optional


class GeradorDeRelatorio:
    """Gera relatório HTML interativo a partir de resultados de avaliação."""

    def __init__(self, workspace: Path, iteration: int,
                 output: Optional[Path] = None, previous_workspace: Optional[Path] = None):
        """
        Inicializa o gerador de relatório.

        Args:
            workspace: Caminho para o diretório workspace
            iteration: Número da iteração a reportar
            output: Caminho para o arquivo HTML de saída (opcional)
            previous_workspace: Workspace anterior para comparação (opcional)
        """
        self.workspace = workspace.resolve()
        self.iteration = iteration
        self.dir_iteracao = self.workspace / f"iteration-{iteration}"
        self.output = output or (self.dir_iteracao / "report.html")
        self.previous_workspace = previous_workspace.resolve() if previous_workspace else None
        self.evals_data: list[dict] = []
        self.benchmark_data: dict = {}
        self.previous_benchmark: dict = {}
        self.pipeline_data: dict = {}  # triage, study, dissection, knowledge_accuracy

    def _carregar_dados_eval(self, eval_dir: Path) -> dict:
        """Carrega todos os dados de um diretório de eval."""
        eval_id = eval_dir.name.replace("eval-", "")
        dados = {"eval_id": eval_id, "configs": {}}

        for config in ["with_skill", "without_skill"]:
            config_dir = eval_dir / config
            if not config_dir.exists():
                continue

            config_dados = {}

            # Carregar output
            output_path = config_dir / "output.txt"
            if output_path.exists():
                config_dados["output"] = output_path.read_text(encoding="utf-8")

            # Carregar timing
            timing_path = config_dir / "timing.json"
            if timing_path.exists():
                try:
                    config_dados["timing"] = json.loads(timing_path.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    config_dados["timing"] = {}

            # Carregar grading
            grading_path = config_dir / "grading.json"
            if grading_path.exists():
                try:
                    config_dados["grading"] = json.loads(grading_path.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    config_dados["grading"] = {}

            # Carregar stderr
            stderr_path = config_dir / "stderr.txt"
            if stderr_path.exists():
                config_dados["stderr"] = stderr_path.read_text(encoding="utf-8")

            dados["configs"][config] = config_dados

        # Extrair prompt do timing (qualquer config serve)
        for config in ["with_skill", "without_skill"]:
            timing = dados["configs"].get(config, {}).get("timing", {})
            if timing.get("prompt"):
                dados["prompt"] = timing["prompt"]
                dados["expected_output"] = timing.get("expected_output", "")
                break

        return dados

    def carregar_dados(self) -> bool:
        """Carrega todos os dados da iteração para o relatório."""
        if not self.dir_iteracao.exists():
            print(f"❌ Diretório de iteração não encontrado: {self.dir_iteracao}")
            return False

        # Carregar dados de cada eval
        eval_dirs = sorted(
            [d for d in self.dir_iteracao.iterdir()
             if d.is_dir() and d.name.startswith("eval-")]
        )

        if not eval_dirs:
            print(f"❌ Nenhum diretório eval-N encontrado em: {self.dir_iteracao}")
            return False

        for eval_dir in eval_dirs:
            self.evals_data.append(self._carregar_dados_eval(eval_dir))

        # Carregar benchmark se existir
        benchmark_path = self.dir_iteracao / "benchmark.json"
        if benchmark_path.exists():
            try:
                self.benchmark_data = json.loads(benchmark_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass

        # Carregar dados de pipeline
        self._carregar_dados_pipeline()

        # Carregar benchmark anterior para comparação
        if self.previous_workspace:
            prev_bench = self.previous_workspace / f"iteration-{self.iteration}" / "benchmark.json"
            if prev_bench.exists():
                try:
                    self.previous_benchmark = json.loads(prev_bench.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    pass

        print(f"   ✅ {len(self.evals_data)} eval(s) carregado(s)")
        return True

    def _carregar_dados_pipeline(self):
        """Carrega dados de pipeline: triage, study, dissection, knowledge_accuracy."""
        pipeline = {}

        # triage.json — pode estar na raiz do workspace
        triage_path = self.workspace / "triage.json"
        if triage_path.exists():
            try:
                pipeline["triage"] = json.loads(triage_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass

        # Study bundle — workspace/stage-a-study/*/index.json
        study_dir = self.workspace / "stage-a-study"
        if study_dir.exists() and study_dir.is_dir():
            study_indices = sorted(study_dir.glob("*/index.json"))
            if study_indices:
                studies = []
                for idx_path in study_indices:
                    try:
                        studies.append(json.loads(idx_path.read_text(encoding="utf-8")))
                    except json.JSONDecodeError:
                        pass
                if studies:
                    pipeline["studies"] = studies

        # Dissection manifest
        dissection_path = self.workspace / "stage-b-dissection" / "dissection-manifest.json"
        if dissection_path.exists():
            try:
                pipeline["dissection"] = json.loads(dissection_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass

        # Knowledge accuracy
        ka_path = self.workspace / "knowledge_accuracy.json"
        if ka_path.exists():
            try:
                pipeline["knowledge_accuracy"] = json.loads(ka_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass

        self.pipeline_data = pipeline

    def _has_pipeline_data(self) -> bool:
        """Verifica se existem dados de pipeline para exibir."""
        return bool(self.pipeline_data)

    def _gerar_aba_pipeline(self) -> str:
        """Gera conteudo HTML da aba Pipeline."""
        if not self.pipeline_data:
            return "<p>Nenhum dado de pipeline disponivel.</p>"

        partes = []

        # --- Triage ---
        triage = self.pipeline_data.get("triage")
        if triage:
            path_used = triage.get("path", triage.get("pipeline", "desconhecido"))
            partes.append(f"""
            <h2>&#x1F6A6; Triage — Pipeline Path</h2>
            <table>
                <tr><th>Campo</th><th>Valor</th></tr>
                <tr><td><strong>Pipeline</strong></td><td>{self._escape(str(path_used))}</td></tr>
            </table>
            """)

            # Sinais e scores do triage
            signals = triage.get("signals", triage.get("scores", {}))
            if signals:
                signal_rows = ""
                for key, val in signals.items():
                    if isinstance(val, float):
                        display_val = f"{val:.2f}"
                    else:
                        display_val = self._escape(str(val))
                    signal_rows += f"<tr><td>{self._escape(str(key))}</td><td>{display_val}</td></tr>\n"
                partes.append(f"""
                <h2>&#x1F4E1; Triage Signals &amp; Scores</h2>
                <table>
                    <tr><th>Signal</th><th>Value</th></tr>
                    {signal_rows}
                </table>
                """)

            # Campos extras do triage (excluindo os ja mostrados)
            extras_keys = [k for k in triage.keys() if k not in ("path", "pipeline", "signals", "scores")]
            if extras_keys:
                extra_rows = ""
                for key in extras_keys:
                    val = triage[key]
                    if isinstance(val, (dict, list)):
                        display_val = f"<pre style='margin:0;white-space:pre-wrap;'>{self._escape(json.dumps(val, indent=2, ensure_ascii=False))}</pre>"
                    else:
                        display_val = self._escape(str(val))
                    extra_rows += f"<tr><td>{self._escape(str(key))}</td><td>{display_val}</td></tr>\n"
                partes.append(f"""
                <h2>&#x1F50D; Triage Details</h2>
                <table>
                    <tr><th>Field</th><th>Value</th></tr>
                    {extra_rows}
                </table>
                """)

        # --- Study Bundle ---
        studies = self.pipeline_data.get("studies")
        if studies:
            partes.append("<h2>&#x1F4DA; Study Bundle Summary</h2>")
            for i, study in enumerate(studies):
                study_name = study.get("name", study.get("domain", f"Study {i+1}"))
                study_rows = ""
                for key, val in study.items():
                    if isinstance(val, (dict, list)):
                        display_val = f"<pre style='margin:0;white-space:pre-wrap;'>{self._escape(json.dumps(val, indent=2, ensure_ascii=False))}</pre>"
                    elif isinstance(val, float):
                        display_val = f"{val:.2f}"
                    else:
                        display_val = self._escape(str(val))
                    study_rows += f"<tr><td>{self._escape(str(key))}</td><td>{display_val}</td></tr>\n"
                partes.append(f"""
                <h3 style="color:#e94560; margin:12px 0 8px;">{self._escape(str(study_name))}</h3>
                <table>
                    <tr><th>Field</th><th>Value</th></tr>
                    {study_rows}
                </table>
                """)

        # --- Dissection ---
        dissection = self.pipeline_data.get("dissection")
        if dissection:
            partes.append("<h2>&#x1F52C; Dissection Summary</h2>")
            dissection_rows = ""
            for key, val in dissection.items():
                if isinstance(val, (dict, list)):
                    display_val = f"<pre style='margin:0;white-space:pre-wrap;'>{self._escape(json.dumps(val, indent=2, ensure_ascii=False))}</pre>"
                elif isinstance(val, float):
                    display_val = f"{val:.2f}"
                else:
                    display_val = self._escape(str(val))
                dissection_rows += f"<tr><td>{self._escape(str(key))}</td><td>{display_val}</td></tr>\n"
            partes.append(f"""
            <table>
                <tr><th>Field</th><th>Value</th></tr>
                {dissection_rows}
            </table>
            """)

        # --- Knowledge Accuracy ---
        ka = self.pipeline_data.get("knowledge_accuracy")
        if ka:
            partes.append("<h2>&#x1F3AF; Knowledge Accuracy Metrics</h2>")

            # Highlight top-level accuracy if present
            accuracy = ka.get("accuracy", ka.get("overall_accuracy"))
            if accuracy is not None:
                if isinstance(accuracy, float) and accuracy <= 1.0:
                    accuracy_display = f"{accuracy:.1%}"
                else:
                    accuracy_display = str(accuracy)
                cor = "positive" if (isinstance(accuracy, (int, float)) and accuracy >= 0.8) else "negative"
                partes.append(f"""
                <p style="font-size:1.4em; margin:12px 0;">
                    Overall Accuracy: <strong class="{cor}">{accuracy_display}</strong>
                </p>
                """)

            ka_rows = ""
            for key, val in ka.items():
                if isinstance(val, (dict, list)):
                    display_val = f"<pre style='margin:0;white-space:pre-wrap;'>{self._escape(json.dumps(val, indent=2, ensure_ascii=False))}</pre>"
                elif isinstance(val, float):
                    if val <= 1.0:
                        display_val = f"{val:.1%}"
                    else:
                        display_val = f"{val:.2f}"
                else:
                    display_val = self._escape(str(val))
                ka_rows += f"<tr><td>{self._escape(str(key))}</td><td>{display_val}</td></tr>\n"
            partes.append(f"""
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                {ka_rows}
            </table>
            """)

        return "\n".join(partes)

    def _escape(self, texto: str) -> str:
        """Escapa texto para inserção segura no HTML."""
        return html.escape(texto) if texto else ""

    def _gerar_css(self) -> str:
        """Gera estilos CSS inline para o relatório."""
        return """
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
               background: #1a1a2e; color: #e0e0e0; line-height: 1.6; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        h1 { color: #e94560; margin-bottom: 8px; font-size: 1.8em; }
        h2 { color: #0f3460; background: #16213e; padding: 12px 16px;
             border-radius: 8px; margin: 20px 0 12px; font-size: 1.2em; color: #e0e0e0; }
        .subtitle { color: #888; margin-bottom: 24px; }
        .tabs { display: flex; gap: 4px; margin-bottom: 0; }
        .tab { padding: 10px 24px; cursor: pointer; background: #16213e;
               border: 1px solid #0f3460; border-bottom: none; border-radius: 8px 8px 0 0;
               color: #888; font-weight: 500; transition: all 0.2s; }
        .tab.active { background: #0f3460; color: #e94560; }
        .tab:hover { color: #e94560; }
        .tab-content { display: none; background: #16213e; border: 1px solid #0f3460;
                       border-radius: 0 8px 8px 8px; padding: 20px; }
        .tab-content.active { display: block; }
        .eval-card { background: #1a1a2e; border: 1px solid #333; border-radius: 8px;
                     margin-bottom: 16px; overflow: hidden; }
        .eval-header { padding: 12px 16px; cursor: pointer; display: flex;
                       justify-content: space-between; align-items: center;
                       background: #16213e; border-bottom: 1px solid #333; }
        .eval-header:hover { background: #1e2a4a; }
        .eval-header .badge { padding: 2px 8px; border-radius: 4px; font-size: 0.8em; }
        .badge.pass { background: #28a745; color: white; }
        .badge.fail { background: #dc3545; color: white; }
        .badge.na { background: #666; color: white; }
        .eval-body { display: none; padding: 16px; }
        .eval-body.open { display: block; }
        .prompt-box { background: #0d1117; border: 1px solid #444; border-radius: 6px;
                      padding: 12px; margin-bottom: 12px; white-space: pre-wrap;
                      font-family: monospace; font-size: 0.9em; }
        .output-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
        .output-col h4 { margin-bottom: 8px; color: #e94560; font-size: 0.95em; }
        .output-box { background: #0d1117; border: 1px solid #444; border-radius: 6px;
                      padding: 12px; max-height: 400px; overflow-y: auto;
                      white-space: pre-wrap; font-family: monospace; font-size: 0.85em; }
        .metrics { display: flex; gap: 16px; margin-top: 8px; font-size: 0.85em; color: #888; }
        .feedback-area { margin-top: 12px; }
        .feedback-area textarea { width: 100%; background: #0d1117; color: #e0e0e0;
                                   border: 1px solid #444; border-radius: 6px; padding: 8px;
                                   font-family: inherit; resize: vertical; min-height: 60px; }
        table { width: 100%; border-collapse: collapse; margin: 12px 0; }
        th, td { padding: 10px 14px; text-align: left; border-bottom: 1px solid #333; }
        th { background: #0f3460; color: #e0e0e0; font-weight: 600; }
        td { background: #1a1a2e; }
        tr:hover td { background: #1e2a4a; }
        .positive { color: #28a745; }
        .negative { color: #dc3545; }
        .btn { padding: 8px 20px; background: #e94560; color: white; border: none;
               border-radius: 6px; cursor: pointer; font-weight: 500; margin-top: 12px; }
        .btn:hover { background: #c73550; }
        .arrow { transition: transform 0.2s; display: inline-block; }
        .arrow.open { transform: rotate(90deg); }
        @media (max-width: 768px) { .output-grid { grid-template-columns: 1fr; } }
        """

    def _gerar_js(self) -> str:
        """Gera JavaScript inline para interatividade."""
        return """
        function switchTab(tabName) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelector('[data-tab="' + tabName + '"]').classList.add('active');
            document.getElementById('tab-' + tabName).classList.add('active');
        }

        function toggleEval(evalId) {
            var body = document.getElementById('eval-body-' + evalId);
            var arrow = document.getElementById('arrow-' + evalId);
            body.classList.toggle('open');
            arrow.classList.toggle('open');
        }

        function downloadFeedback() {
            var feedback = {};
            document.querySelectorAll('.feedback-input').forEach(function(el) {
                var evalId = el.getAttribute('data-eval-id');
                if (el.value.trim()) {
                    feedback[evalId] = el.value.trim();
                }
            });
            var blob = new Blob([JSON.stringify(feedback, null, 2)],
                                {type: 'application/json'});
            var url = URL.createObjectURL(blob);
            var a = document.createElement('a');
            a.href = url;
            a.download = 'feedback.json';
            a.click();
            URL.revokeObjectURL(url);
        }
        """

    def _gerar_aba_outputs(self) -> str:
        """Gera conteúdo HTML da aba de outputs."""
        partes = []

        for ev in self.evals_data:
            eval_id = ev["eval_id"]
            prompt = self._escape(ev.get("prompt", "(prompt não disponível)"))
            expected = self._escape(ev.get("expected_output", ""))

            # Determinar status do grading
            ws_grading = ev["configs"].get("with_skill", {}).get("grading", {})
            wo_grading = ev["configs"].get("without_skill", {}).get("grading", {})
            ws_passed = ws_grading.get("passed")
            wo_passed = wo_grading.get("passed")

            # Badge de status
            if ws_passed is True:
                badge = '<span class="badge pass">PASS</span>'
            elif ws_passed is False:
                badge = '<span class="badge fail">FAIL</span>'
            else:
                badge = '<span class="badge na">N/A</span>'

            # Outputs
            ws_output = self._escape(ev["configs"].get("with_skill", {}).get("output", "(sem saída)"))
            wo_output = self._escape(ev["configs"].get("without_skill", {}).get("output", "(sem saída)"))

            # Métricas
            ws_timing = ev["configs"].get("with_skill", {}).get("timing", {})
            wo_timing = ev["configs"].get("without_skill", {}).get("timing", {})
            ws_ms = ws_timing.get("duration_ms", "-")
            wo_ms = wo_timing.get("duration_ms", "-")
            ws_tokens = ws_timing.get("total_tokens", "-")
            wo_tokens = wo_timing.get("total_tokens", "-")

            # Score de grading
            ws_score = ws_grading.get("score", "-")
            wo_score = wo_grading.get("score", "-")

            partes.append(f"""
            <div class="eval-card">
                <div class="eval-header" onclick="toggleEval('{eval_id}')">
                    <span><span class="arrow" id="arrow-{eval_id}">&#9654;</span>
                    &nbsp; Eval #{eval_id}</span>
                    {badge}
                </div>
                <div class="eval-body" id="eval-body-{eval_id}">
                    <strong>Prompt:</strong>
                    <div class="prompt-box">{prompt}</div>
                    {"<strong>Esperado:</strong><div class='prompt-box'>" + expected + "</div>" if expected else ""}
                    <div class="output-grid">
                        <div class="output-col">
                            <h4>&#x2705; with_skill</h4>
                            <div class="output-box">{ws_output}</div>
                            <div class="metrics">
                                <span>&#x23F1; {ws_ms}ms</span>
                                <span>&#x1F4AC; {ws_tokens} tokens</span>
                                <span>Score: {ws_score}</span>
                            </div>
                        </div>
                        <div class="output-col">
                            <h4>&#x274C; without_skill</h4>
                            <div class="output-box">{wo_output}</div>
                            <div class="metrics">
                                <span>&#x23F1; {wo_ms}ms</span>
                                <span>&#x1F4AC; {wo_tokens} tokens</span>
                                <span>Score: {wo_score}</span>
                            </div>
                        </div>
                    </div>
                    <div class="feedback-area">
                        <strong>Feedback:</strong>
                        <textarea class="feedback-input" data-eval-id="{eval_id}"
                                  placeholder="Adicione feedback para este eval..."></textarea>
                    </div>
                </div>
            </div>
            """)

        partes.append("""
        <button class="btn" onclick="downloadFeedback()">&#x1F4BE; Baixar Feedback (JSON)</button>
        """)

        return "\n".join(partes)

    def _gerar_aba_benchmark(self) -> str:
        """Gera conteúdo HTML da aba de benchmark."""
        if not self.benchmark_data:
            return "<p>Dados de benchmark não disponíveis. Execute forge_benchmark.py primeiro.</p>"

        ws = self.benchmark_data.get("with_skill", {})
        wo = self.benchmark_data.get("without_skill", {})
        delta = self.benchmark_data.get("delta", {})

        # Tabela comparativa principal
        linhas_tabela = ""

        metricas = [
            ("Pass Rate", "pass_rate", True, True),
            ("Timing (ms)", "timing_ms", False, False),
            ("Tokens", "tokens", False, False),
        ]

        for label, key, is_pct, higher_better in metricas:
            ws_data = ws.get(key, {})
            wo_data = wo.get(key, {})
            d_data = delta.get(key, {})

            if is_pct:
                ws_val = f"{ws_data.get('mean', 0):.1%} &plusmn; {ws_data.get('stddev', 0):.1%}"
                wo_val = f"{wo_data.get('mean', 0):.1%} &plusmn; {wo_data.get('stddev', 0):.1%}"
                d_abs = d_data.get("absolute", 0)
                d_val = f"{d_abs:+.1%}"
            else:
                ws_val = f"{ws_data.get('mean', 0):.0f} &plusmn; {ws_data.get('stddev', 0):.0f}"
                wo_val = f"{wo_data.get('mean', 0):.0f} &plusmn; {wo_data.get('stddev', 0):.0f}"
                d_abs = d_data.get("absolute", 0)
                d_val = f"{d_abs:+.0f}"

            # Cor do delta
            if higher_better:
                cor = "positive" if d_abs > 0 else ("negative" if d_abs < 0 else "")
            else:
                cor = "positive" if d_abs < 0 else ("negative" if d_abs > 0 else "")

            linhas_tabela += f"""
            <tr>
                <td><strong>{label}</strong></td>
                <td>{ws_val}</td>
                <td>{wo_val}</td>
                <td class="{cor}">{d_val} ({d_data.get('percentage', 0):+.1f}%)</td>
            </tr>
            """

        # Tabela de detalhes por eval
        ws_per = ws.get("per_eval", {})
        wo_per = wo.get("per_eval", {})
        all_ids = sorted(set(list(ws_per.keys()) + list(wo_per.keys())))

        linhas_detalhes = ""
        for eval_id in all_ids:
            for config, dados in [("with_skill", ws_per), ("without_skill", wo_per)]:
                d = dados.get(eval_id, {})
                passed = d.get("passed")
                badge = "pass" if passed is True else ("fail" if passed is False else "na")
                badge_text = "PASS" if passed is True else ("FAIL" if passed is False else "N/A")
                dur = d.get("duration_ms", "-")
                tkns = d.get("total_tokens", "-")
                linhas_detalhes += f"""
                <tr>
                    <td>{eval_id}</td>
                    <td>{config}</td>
                    <td><span class="badge {badge}">{badge_text}</span></td>
                    <td>{dur}</td>
                    <td>{tkns}</td>
                </tr>
                """

        # Comparação com workspace anterior
        comparacao_html = ""
        if self.previous_benchmark:
            prev_ws = self.previous_benchmark.get("with_skill", {})
            prev_pr = prev_ws.get("pass_rate", {}).get("mean", 0)
            curr_pr = ws.get("pass_rate", {}).get("mean", 0)
            diff = curr_pr - prev_pr
            cor = "positive" if diff > 0 else ("negative" if diff < 0 else "")
            comparacao_html = f"""
            <h2>&#x1F504; Comparação com Iteração Anterior</h2>
            <table>
                <tr><th>Métrica</th><th>Anterior</th><th>Atual</th><th>Delta</th></tr>
                <tr>
                    <td>Pass Rate (with_skill)</td>
                    <td>{prev_pr:.1%}</td>
                    <td>{curr_pr:.1%}</td>
                    <td class="{cor}">{diff:+.1%}</td>
                </tr>
            </table>
            """

        return f"""
        <h2>&#x1F4CA; Resumo Comparativo</h2>
        <table>
            <tr><th>Métrica</th><th>with_skill</th><th>without_skill</th><th>Delta</th></tr>
            {linhas_tabela}
        </table>

        {comparacao_html}

        <h2>&#x1F4CB; Detalhes por Eval</h2>
        <table>
            <tr><th>Eval</th><th>Config</th><th>Status</th><th>Duração (ms)</th><th>Tokens</th></tr>
            {linhas_detalhes}
        </table>
        """

    def gerar_html(self) -> str:
        """Gera o documento HTML completo autocontido."""
        aba_outputs = self._gerar_aba_outputs()
        aba_benchmark = self._gerar_aba_benchmark()

        # Pipeline tab — condicional
        has_pipeline = self._has_pipeline_data()
        aba_pipeline = self._gerar_aba_pipeline() if has_pipeline else ""

        pipeline_tab_btn = ""
        pipeline_tab_content = ""
        if has_pipeline:
            pipeline_tab_btn = """
            <div class="tab" data-tab="pipeline" onclick="switchTab('pipeline')">
                &#x1F6A6; Pipeline
            </div>"""
            pipeline_tab_content = f"""
        <div class="tab-content" id="tab-pipeline">
            {aba_pipeline}
        </div>"""

        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Forge Report — Iteração {self.iteration}</title>
    <style>{self._gerar_css()}</style>
</head>
<body>
    <div class="container">
        <h1>&#x1F525; Forge Report</h1>
        <p class="subtitle">Iteração {self.iteration} &mdash; {len(self.evals_data)} eval(s)
           &mdash; Workspace: {self._escape(str(self.workspace))}</p>

        <div class="tabs">
            <div class="tab active" data-tab="outputs" onclick="switchTab('outputs')">
                &#x1F4DD; Outputs
            </div>
            <div class="tab" data-tab="benchmark" onclick="switchTab('benchmark')">
                &#x1F4CA; Benchmark
            </div>{pipeline_tab_btn}
        </div>

        <div class="tab-content active" id="tab-outputs">
            {aba_outputs}
        </div>

        <div class="tab-content" id="tab-benchmark">
            {aba_benchmark}
        </div>{pipeline_tab_content}
    </div>

    <script>{self._gerar_js()}</script>
</body>
</html>"""

    def executar(self) -> dict:
        """
        Executa a geração do relatório HTML completo.

        Carrega dados, gera HTML e salva no arquivo de saída.
        """
        print(f"📝 Forge Report — Gerando relatório HTML")
        print(f"   📂 Workspace: {self.workspace}")
        print(f"   🔄 Iteração: {self.iteration}")

        if not self.carregar_dados():
            return {"erro": "Falha ao carregar dados"}

        # Gerar HTML
        print(f"   ▶ Gerando HTML...")
        html_content = self.gerar_html()

        # Salvar arquivo
        self.output = Path(self.output)
        self.output.parent.mkdir(parents=True, exist_ok=True)
        self.output.write_text(html_content, encoding="utf-8")

        tamanho_kb = self.output.stat().st_size / 1024

        print(f"\n🏁 Relatório gerado!")
        print(f"   💾 Arquivo: {self.output}")
        print(f"   📏 Tamanho: {tamanho_kb:.1f} KB")
        print(f"   📊 Evals: {len(self.evals_data)}")
        print(f"   🌐 Abrir: file://{self.output}")

        return {
            "output": str(self.output),
            "evals": len(self.evals_data),
            "size_kb": round(tamanho_kb, 1),
        }


def main():
    """Ponto de entrada principal do script."""
    parser = argparse.ArgumentParser(
        description="Forge Report — Gera visualizador HTML para resultados de eval"
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
        help="Número da iteração a reportar (padrão: 1)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Caminho para o arquivo HTML de saída (padrão: workspace/iteration-N/report.html)",
    )
    parser.add_argument(
        "--previous-workspace",
        default=None,
        help="Workspace anterior para comparação entre iterações (opcional)",
    )

    args = parser.parse_args()

    gerador = GeradorDeRelatorio(
        workspace=Path(args.workspace),
        iteration=args.iteration,
        output=Path(args.output) if args.output else None,
        previous_workspace=Path(args.previous_workspace) if args.previous_workspace else None,
    )

    resultado = gerador.executar()

    if "erro" in resultado:
        print(f"\n❌ {resultado['erro']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
