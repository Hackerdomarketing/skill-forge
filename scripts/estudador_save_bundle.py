#!/usr/bin/env python3
"""
Estudador Save Bundle — Cria estrutura de study bundle para o pipeline

Uso:
    estudador_save_bundle.py --tema "topico" --output workspace/stage-a-study/ --pipeline-mode full

Exemplos:
    estudador_save_bundle.py --tema "api-openai-function-calling" --output ./workspace/stage-a-study/ --pipeline-mode full
    estudador_save_bundle.py --tema "markdown-formatting" --output ./workspace/stage-a-study/ --pipeline-mode abbreviated

Cria a estrutura:
    stage-a-study/YYYY-MM-DD/slug/
    ├── 00-contexto.md
    ├── 01-matriz-afirmacoes.csv
    ├── 02-fontes.json
    ├── 03-controversias.md
    ├── 04-ausencias-alertas.md
    ├── 05-mapa-conhecimento.md
    ├── 06-manual-operacional.md
    ├── 07-pacote-especialista.md
    ├── 08-monitoramento.md
    └── index.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


FILES = [
    "00-contexto.md",
    "01-matriz-afirmacoes.csv",
    "02-fontes.json",
    "03-controversias.md",
    "04-ausencias-alertas.md",
    "05-mapa-conhecimento.md",
    "06-manual-operacional.md",
    "07-pacote-especialista.md",
    "08-monitoramento.md",
]


def slugify(text: str) -> str:
    """Converte texto em slug kebab-case."""
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    text = text.strip('-')
    return text[:64] if text else "sem-tema"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tema", required=True, help="Topico do estudo")
    parser.add_argument("--output", required=True, help="Diretorio base de saida (stage-a-study/)")
    parser.add_argument("--pipeline-mode", required=True, choices=["full", "abbreviated"],
                        help="Modo do pipeline: full (estudo completo) ou abbreviated (estudo resumido)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    slug = slugify(args.tema)
    date_str = datetime.now().strftime("%Y-%m-%d")
    out_dir = Path(args.output).resolve() / date_str / slug

    print(f"Estudador Save Bundle: criando study bundle")
    print(f"  Tema: {args.tema}")
    print(f"  Slug: {slug}")
    print(f"  Modo: {args.pipeline_mode}")
    print(f"  Saida: {out_dir}")

    # Criar diretorio
    out_dir.mkdir(parents=True, exist_ok=True)

    # Criar arquivos template
    created = 0
    for fname in FILES:
        fpath = out_dir / fname
        if not fpath.exists():
            if fname.endswith(".csv"):
                fpath.write_text("claim_id,afirmacao,nivel_certeza,fonte\n", encoding="utf-8")
            elif fname.endswith(".json"):
                fpath.write_text("[]", encoding="utf-8")
            else:
                title = fname.replace(".md", "").replace("-", " ").title()
                fpath.write_text(f"# {title}\n\n<!-- Preencher durante o estudo -->\n", encoding="utf-8")
            created += 1
        else:
            print(f"  Ja existe: {fname}")

    # Criar index.json
    index = {
        "topic": args.tema,
        "slug": slug,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pipeline_mode": args.pipeline_mode,
        "method_version": "7.0",
        "certainty_summary": {
            "verdade_absoluta": 0,
            "verdade_provavel_forte": 0,
            "verdade_provavel_fraca": 0,
            "verdade_popular_sem_validacao": 0,
            "indeterminado": 0,
        },
        "files": FILES,
    }
    index_path = out_dir / "index.json"
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"  Criados {created} arquivos template + index.json")
    print(f"\nStudy bundle criado em: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
