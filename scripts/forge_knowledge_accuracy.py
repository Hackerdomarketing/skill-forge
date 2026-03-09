#!/usr/bin/env python3
"""
Forge Knowledge Accuracy — Compara output de skill contra afirmacoes validadas

Uso:
    forge_knowledge_accuracy.py --claims path/to/01-matriz-afirmacoes.csv --output path/to/output.txt --score-file knowledge_accuracy.json

Exemplos:
    forge_knowledge_accuracy.py --claims ./01-matriz-afirmacoes.csv --output ./skill-output.txt --score-file ./knowledge_accuracy.json

Le o CSV de afirmacoes (claim_id, afirmacao, nivel_certeza, fonte),
le o texto de output da skill, e verifica quais afirmacoes estao
refletidas no output.

Saida: knowledge_accuracy.json com:
    {
        "score": 0.0-1.0,
        "claims_total": N,
        "claims_found": N,
        "claims_missing": ["claim_id1", "claim_id2"]
    }
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--claims", required=True, help="Caminho para o CSV de afirmacoes validadas")
    parser.add_argument("--output", required=True, help="Caminho para o arquivo de output da skill a verificar")
    parser.add_argument("--score-file", required=True, help="Caminho para salvar o JSON de score")
    return parser.parse_args()


def load_claims(claims_path: Path) -> list[dict]:
    """Le claims do CSV. Espera colunas: claim_id, afirmacao, [nivel_certeza], [fonte]."""
    claims = []
    try:
        with open(claims_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                claim_id = row.get("claim_id", "").strip()
                afirmacao = row.get("afirmacao", "").strip()
                if claim_id and afirmacao:
                    claims.append({
                        "claim_id": claim_id,
                        "afirmacao": afirmacao,
                    })
    except Exception as e:
        print(f"Erro ao ler CSV de claims: {e}")
    return claims


def check_claim_in_output(claim_text: str, output_text: str) -> bool:
    """Verifica se uma afirmacao esta refletida no output.

    Usa busca por palavras-chave relevantes da afirmacao.
    Palavras com menos de 4 caracteres sao ignoradas para evitar falsos positivos.
    Uma claim e considerada presente se pelo menos 60% das palavras-chave forem encontradas.
    """
    # Extrair palavras significativas da afirmacao (4+ caracteres)
    words = [w.lower() for w in claim_text.split() if len(w) >= 4]
    if not words:
        return False

    output_lower = output_text.lower()
    found = sum(1 for w in words if w in output_lower)
    ratio = found / len(words)
    return ratio >= 0.6


def main() -> int:
    args = parse_args()
    claims_path = Path(args.claims).resolve()
    output_path = Path(args.output).resolve()
    score_path = Path(args.score_file).resolve()

    print(f"Forge Knowledge Accuracy: verificando precisao do conhecimento")
    print(f"  Claims: {claims_path}")
    print(f"  Output: {output_path}")

    # Validar entradas
    if not claims_path.exists():
        print(f"Erro: arquivo de claims nao encontrado: {claims_path}")
        return 1

    if not output_path.exists():
        print(f"Erro: arquivo de output nao encontrado: {output_path}")
        return 1

    # Carregar dados
    claims = load_claims(claims_path)
    if not claims:
        print(f"Erro: nenhuma claim valida encontrada no CSV")
        return 1

    output_text = output_path.read_text(encoding="utf-8")
    if not output_text.strip():
        print(f"Erro: arquivo de output esta vazio")
        return 1

    print(f"  Claims carregadas: {len(claims)}")

    # Verificar cada claim
    claims_found = 0
    claims_missing = []

    for claim in claims:
        if check_claim_in_output(claim["afirmacao"], output_text):
            claims_found += 1
        else:
            claims_missing.append(claim["claim_id"])

    # Calcular score
    score = claims_found / len(claims) if claims else 0.0

    print(f"  Claims encontradas: {claims_found}/{len(claims)}")
    print(f"  Score: {score:.2f}")

    if claims_missing:
        print(f"  Claims ausentes: {', '.join(claims_missing[:10])}")
        if len(claims_missing) > 10:
            print(f"    ... e mais {len(claims_missing) - 10}")

    # Salvar resultado
    result = {
        "score": round(score, 4),
        "claims_total": len(claims),
        "claims_found": claims_found,
        "claims_missing": claims_missing,
    }

    score_path.parent.mkdir(parents=True, exist_ok=True)
    score_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"  Salvo em: {score_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
