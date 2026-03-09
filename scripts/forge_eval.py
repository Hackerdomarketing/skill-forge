#!/usr/bin/env python3
"""
Forge Eval — Executa casos de teste de avaliação para uma habilidade

Uso:
    forge_eval.py --skill-path <caminho> --evals <evals.json>

Exemplos:
    forge_eval.py --skill-path ./minha-skill --evals ./evals.json
    forge_eval.py --skill-path ./skill --evals ./evals.json --iteration 2 --workspace ./workspace

Formato do evals.json:
    {
        "skill_name": "nome-da-skill",
        "evals": [
            {
                "id": 1,
                "prompt": "Faça X...",
                "expected_output": "Resultado esperado...",
                "files": [],
                "assertions": []
            }
        ]
    }

Executa cada avaliação em duas configurações:
    - with_skill: com a habilidade ativa
    - without_skill: baseline sem a habilidade
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional


class ExecutorDeEval:
    """Executa avaliações comparando desempenho com e sem habilidade."""

    def __init__(self, skill_path: Path, evals_path: Path, workspace: Path, iteration: int):
        """
        Inicializa o executor de avaliações.

        Args:
            skill_path: Caminho para o diretório da habilidade
            evals_path: Caminho para o arquivo evals.json
            workspace: Diretório base de saída
            iteration: Número da iteração atual
        """
        self.skill_path = skill_path.resolve()
        self.evals_path = evals_path.resolve()
        self.workspace = workspace.resolve()
        self.iteration = iteration
        self.dados_evals: dict = {}

    def carregar_evals(self) -> bool:
        """Carrega arquivo de avaliações e valida estrutura básica."""
        if not self.evals_path.exists():
            print(f"❌ Arquivo de evals não encontrado: {self.evals_path}")
            return False

        try:
            self.dados_evals = json.loads(self.evals_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao ler JSON: {e}")
            return False

        # Validar campos obrigatórios
        if "evals" not in self.dados_evals or not isinstance(self.dados_evals["evals"], list):
            print("❌ Formato inválido: campo 'evals' deve ser uma lista")
            return False

        if not self.dados_evals["evals"]:
            print("❌ Lista de evals está vazia")
            return False

        # Validar cada eval tem os campos mínimos
        for i, ev in enumerate(self.dados_evals["evals"]):
            if "id" not in ev or "prompt" not in ev:
                print(f"❌ Eval #{i} falta campo 'id' ou 'prompt'")
                return False

        return True

    def validar_skill(self) -> bool:
        """Verifica se o diretório da habilidade contém SKILL.md."""
        if not self.skill_path.exists():
            print(f"❌ Diretório da habilidade não encontrado: {self.skill_path}")
            return False

        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            print(f"❌ SKILL.md não encontrado em: {self.skill_path}")
            return False

        return True

    def _criar_diretorio_saida(self, eval_id: int, config: str) -> Path:
        """Cria diretório de saída para um eval e configuração específicos."""
        diretorio = self.workspace / f"iteration-{self.iteration}" / f"eval-{eval_id}" / config
        diretorio.mkdir(parents=True, exist_ok=True)
        return diretorio

    def _executar_claude(self, prompt: str, usar_skill: bool, arquivos: list[str]) -> dict:
        """
        Executa claude -p com ou sem a habilidade e captura resultado.

        Args:
            prompt: Texto do prompt a enviar
            usar_skill: Se True, inclui a skill no comando
            arquivos: Lista de caminhos de arquivos de contexto

        Returns:
            Dicionário com output, stderr, duration_ms, total_tokens, exit_code
        """
        # Montar comando base
        cmd = ["claude", "-p"]

        # Adicionar skill se necessário
        if usar_skill:
            cmd.extend(["--skill", str(self.skill_path)])

        # Adicionar arquivos de contexto se existirem
        for arquivo in arquivos:
            caminho_arquivo = Path(arquivo)
            if caminho_arquivo.exists():
                cmd.extend(["--file", str(caminho_arquivo)])

        # Adicionar prompt como último argumento
        cmd.append(prompt)

        # Executar e medir tempo
        inicio = time.time()
        resultado = None
        try:
            resultado = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutos por eval
            )
            duracao_ms = int((time.time() - inicio) * 1000)
            saida = resultado.stdout.strip()
            erro = resultado.stderr.strip()
            codigo_saida = resultado.returncode
        except subprocess.TimeoutExpired:
            duracao_ms = 300000
            saida = ""
            erro = "TIMEOUT: Execução excedeu 5 minutos"
            codigo_saida = -1
        except FileNotFoundError:
            duracao_ms = 0
            saida = ""
            erro = "ERRO: Comando 'claude' não encontrado no PATH"
            codigo_saida = -1

        # Estimar tokens pela contagem de palavras (aproximação)
        tokens_prompt = len(prompt.split())
        tokens_saida = len(saida.split()) if saida else 0
        tokens_estimados = tokens_prompt + tokens_saida

        return {
            "output": saida,
            "stderr": erro,
            "duration_ms": duracao_ms,
            "total_tokens": tokens_estimados,
            "exit_code": codigo_saida,
        }

    def _salvar_resultado(self, diretorio: Path, resultado: dict, eval_caso: dict):
        """Salva resultado de execução em arquivos no diretório de saída."""
        # Salvar saída completa
        (diretorio / "output.txt").write_text(resultado["output"], encoding="utf-8")

        # Salvar stderr se houver
        if resultado["stderr"]:
            (diretorio / "stderr.txt").write_text(resultado["stderr"], encoding="utf-8")

        # Salvar timing e métricas
        timing = {
            "duration_ms": resultado["duration_ms"],
            "total_tokens": resultado["total_tokens"],
            "exit_code": resultado["exit_code"],
            "eval_id": eval_caso["id"],
            "prompt": eval_caso["prompt"],
            "expected_output": eval_caso.get("expected_output", ""),
            "assertions": eval_caso.get("assertions", []),
        }
        (diretorio / "timing.json").write_text(
            json.dumps(timing, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def executar_eval(self, eval_caso: dict) -> dict:
        """
        Executa um caso de avaliação nas duas configurações (com e sem skill).

        Args:
            eval_caso: Dicionário com id, prompt, expected_output, files, assertions

        Returns:
            Dicionário com resultados de with_skill e without_skill
        """
        eval_id = eval_caso["id"]
        prompt = eval_caso["prompt"]
        arquivos = eval_caso.get("files", [])

        print(f"\n  📋 Eval #{eval_id}: {prompt[:60]}...")

        resultados = {}

        # Executar COM a habilidade
        print(f"    ▶ Executando with_skill...")
        dir_with = self._criar_diretorio_saida(eval_id, "with_skill")
        resultado_with = self._executar_claude(prompt, usar_skill=True, arquivos=arquivos)
        self._salvar_resultado(dir_with, resultado_with, eval_caso)
        resultados["with_skill"] = {
            "duration_ms": resultado_with["duration_ms"],
            "total_tokens": resultado_with["total_tokens"],
            "exit_code": resultado_with["exit_code"],
            "output_length": len(resultado_with["output"]),
        }
        print(f"    ✅ with_skill: {resultado_with['duration_ms']}ms, "
              f"{resultado_with['total_tokens']} tokens")

        # Executar SEM a habilidade (baseline)
        print(f"    ▶ Executando without_skill...")
        dir_without = self._criar_diretorio_saida(eval_id, "without_skill")
        resultado_without = self._executar_claude(prompt, usar_skill=False, arquivos=arquivos)
        self._salvar_resultado(dir_without, resultado_without, eval_caso)
        resultados["without_skill"] = {
            "duration_ms": resultado_without["duration_ms"],
            "total_tokens": resultado_without["total_tokens"],
            "exit_code": resultado_without["exit_code"],
            "output_length": len(resultado_without["output"]),
        }
        print(f"    ✅ without_skill: {resultado_without['duration_ms']}ms, "
              f"{resultado_without['total_tokens']} tokens")

        return resultados

    def executar_todos(self) -> dict:
        """Executa todas as avaliações e retorna resumo consolidado."""
        if not self.carregar_evals():
            return {"erro": "Falha ao carregar evals"}

        if not self.validar_skill():
            return {"erro": "Habilidade inválida"}

        skill_name = self.dados_evals.get("skill_name", "desconhecida")
        evals = self.dados_evals["evals"]

        print(f"🔥 Forge Eval — Avaliando habilidade: {skill_name}")
        print(f"   📂 Skill: {self.skill_path}")
        print(f"   📄 Evals: {len(evals)} caso(s)")
        print(f"   🔄 Iteração: {self.iteration}")
        print(f"   💾 Workspace: {self.workspace}")

        todos_resultados = {}
        total_with_ms = 0
        total_without_ms = 0

        for eval_caso in evals:
            eval_id = eval_caso["id"]
            resultado = self.executar_eval(eval_caso)
            todos_resultados[str(eval_id)] = resultado
            total_with_ms += resultado["with_skill"]["duration_ms"]
            total_without_ms += resultado["without_skill"]["duration_ms"]

        # Salvar resumo consolidado da iteração
        resumo = {
            "skill_name": skill_name,
            "skill_path": str(self.skill_path),
            "iteration": self.iteration,
            "total_evals": len(evals),
            "total_duration_with_ms": total_with_ms,
            "total_duration_without_ms": total_without_ms,
            "results": todos_resultados,
        }

        dir_iteracao = self.workspace / f"iteration-{self.iteration}"
        dir_iteracao.mkdir(parents=True, exist_ok=True)
        (dir_iteracao / "eval_summary.json").write_text(
            json.dumps(resumo, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        print(f"\n🏁 Avaliação concluída!")
        print(f"   📊 {len(evals)} eval(s) executado(s)")
        print(f"   ⏱️  Tempo total: with_skill={total_with_ms}ms | "
              f"without_skill={total_without_ms}ms")
        print(f"   💾 Resultados em: {dir_iteracao}")

        return resumo


def main():
    """Ponto de entrada principal do script."""
    parser = argparse.ArgumentParser(
        description="Forge Eval — Executa avaliações comparativas de habilidades"
    )
    parser.add_argument(
        "--skill-path",
        required=True,
        help="Caminho para o diretório da habilidade",
    )
    parser.add_argument(
        "--evals",
        required=True,
        help="Caminho para o arquivo evals.json",
    )
    parser.add_argument(
        "--workspace",
        default="./workspace",
        help="Diretório de saída para resultados (padrão: ./workspace)",
    )
    parser.add_argument(
        "--iteration",
        type=int,
        default=1,
        help="Número da iteração (padrão: 1)",
    )

    args = parser.parse_args()

    executor = ExecutorDeEval(
        skill_path=Path(args.skill_path),
        evals_path=Path(args.evals),
        workspace=Path(args.workspace),
        iteration=args.iteration,
    )

    resultado = executor.executar_todos()

    if "erro" in resultado:
        print(f"\n❌ {resultado['erro']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
