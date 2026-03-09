#!/usr/bin/env python3
"""
Estudador Normalize Sources — Normaliza evidencias para formato padrao

Uso:
    estudador_normalize_sources.py --input sources.json --output normalized-sources.json

Exemplos:
    estudador_normalize_sources.py --input ./02-fontes.json --output ./02-fontes-normalized.json

Formato de saida:
    Array de objetos com campos:
    - claim_id: identificador da afirmacao
    - nivel: ouro | prata | bronze | ferro | chumbo
    - url: URL da fonte
    - data: data da fonte
    - autor: autor da fonte
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


NIVEIS_VALIDOS = ["ouro", "prata", "bronze", "ferro", "chumbo"]

CAMPOS_OBRIGATORIOS = ["claim_id", "nivel", "url", "data", "autor"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", required=True, help="Arquivo JSON de entrada com fontes brutas")
    parser.add_argument("--output", required=True, help="Arquivo JSON de saida normalizado")
    return parser.parse_args()


def normalize_entry(entry: dict, index: int) -> dict | None:
    """Normaliza uma entrada de fonte. Retorna None se invalida."""
    normalized = {}

    # claim_id
    claim_id = entry.get("claim_id", entry.get("id", entry.get("claim", "")))
    if not claim_id:
        claim_id = f"claim-{index:03d}"
    normalized["claim_id"] = str(claim_id).strip()

    # nivel
    nivel = entry.get("nivel", entry.get("level", entry.get("tier", ""))).strip().lower()
    if nivel not in NIVEIS_VALIDOS:
        print(f"  Aviso: nivel invalido '{nivel}' na entrada {index}, usando 'chumbo'")
        nivel = "chumbo"
    normalized["nivel"] = nivel

    # url
    url = entry.get("url", entry.get("link", entry.get("source", ""))).strip()
    normalized["url"] = url

    # data
    data = entry.get("data", entry.get("date", entry.get("published", ""))).strip()
    normalized["data"] = data

    # autor
    autor = entry.get("autor", entry.get("author", entry.get("by", ""))).strip()
    normalized["autor"] = autor

    return normalized


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()

    print(f"Estudador Normalize Sources: normalizando fontes")
    print(f"  Entrada: {input_path}")
    print(f"  Saida: {output_path}")

    # Ler entrada
    if not input_path.exists():
        print(f"Erro: arquivo de entrada nao encontrado: {input_path}")
        return 1

    try:
        raw = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"Erro: JSON invalido no arquivo de entrada: {e}")
        return 1

    if not isinstance(raw, list):
        print(f"Erro: arquivo de entrada deve conter um array JSON")
        return 1

    # Normalizar
    normalized = []
    for i, entry in enumerate(raw):
        if not isinstance(entry, dict):
            print(f"  Aviso: entrada {i} nao e um objeto, ignorada")
            continue
        result = normalize_entry(entry, i)
        if result:
            normalized.append(result)

    # Salvar
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"  Normalizadas {len(normalized)} de {len(raw)} entradas")
    print(f"  Salvo em: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
