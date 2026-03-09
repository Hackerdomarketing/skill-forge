#!/usr/bin/env python3
"""
Forge Triage — Triage Gate scorer para pipeline de habilidades

Uso:
    forge_triage.py --topic "descricao" --signals "sinal1:score,sinal2:score" --output workspace/triage.json

Exemplos:
    forge_triage.py --topic "API OpenAI com function calling" --signals "apis-mutaveis:1,contradicoes:2" --output ./triage.json
    forge_triage.py --topic "formatacao markdown" --signals "doc-oficial:-1,skill-simples:-1" --output ./triage.json --override fast

Sinais disponiveis e seus pesos padrao:
    doc-oficial-acessivel: -1
    skill-simples: -1
    apis-recentes-mutaveis: +1
    contradicoes-conhecidas: +2
    claude-ja-errou: +2
    conhecimento-especializado-ausente: +2
    output-alto-risco: +2

Roteamento:
    score <= 0  -> fast
    score 1-2   -> medium
    score >= 3  -> deep
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


SINAIS_PADRAO = {
    "doc-oficial-acessivel": -1,
    "skill-simples": -1,
    "apis-recentes-mutaveis": 1,
    "contradicoes-conhecidas": 2,
    "claude-ja-errou": 2,
    "conhecimento-especializado-ausente": 2,
    "output-alto-risco": 2,
}


def parse_signals(raw: str) -> dict[str, int]:
    """Converte string 'sinal1:score,sinal2:score' em dicionario."""
    signals = {}
    for pair in raw.split(","):
        pair = pair.strip()
        if not pair:
            continue
        if ":" not in pair:
            print(f"Aviso: sinal sem score ignorado: '{pair}'")
            continue
        name, score_str = pair.rsplit(":", 1)
        name = name.strip()
        try:
            score = int(score_str.strip())
        except ValueError:
            print(f"Aviso: score invalido para '{name}': '{score_str}'")
            continue
        signals[name] = score
    return signals


def determine_route(score: int) -> str:
    """Determina rota baseado no score total."""
    if score <= 0:
        return "fast"
    elif score <= 2:
        return "medium"
    else:
        return "deep"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--topic", required=True, help="Descricao do topico a avaliar")
    parser.add_argument("--signals", required=True, help="Sinais no formato 'sinal1:score,sinal2:score'")
    parser.add_argument("--output", required=True, help="Caminho para o arquivo triage.json de saida")
    parser.add_argument("--override", choices=["fast", "medium", "deep"], default=None,
                        help="Forcar rota especifica ignorando score")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    print(f"Forge Triage: avaliando topico '{args.topic}'")

    # Parsear sinais
    signals = parse_signals(args.signals)
    if not signals:
        print("Erro: nenhum sinal valido fornecido")
        return 1

    print(f"  Sinais detectados: {len(signals)}")

    # Calcular score
    total_score = sum(signals.values())
    print(f"  Score total: {total_score}")

    # Determinar rota
    if args.override:
        route = args.override
        print(f"  Rota: {route} (override manual)")
    else:
        route = determine_route(total_score)
        print(f"  Rota: {route}")

    # Montar resultado
    triage = {
        "topic": args.topic,
        "signals": signals,
        "total_score": total_score,
        "route": route,
        "override": args.override is not None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "sinais_padrao_referencia": SINAIS_PADRAO,
    }

    # Salvar
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(triage, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"  Salvo em: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
