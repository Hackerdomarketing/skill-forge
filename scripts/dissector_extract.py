#!/usr/bin/env python3
"""
Dissector Extract — Cria scaffold para pacote de dissecacao

Uso:
    dissector_extract.py --study-bundle path/to/study-bundle/ --output workspace/stage-b-dissection/

Exemplos:
    dissector_extract.py --study-bundle ./workspace/stage-a-study/2026-01-15/api-openai/ --output ./workspace/stage-b-dissection/

Cria a estrutura:
    stage-b-dissection/
    ├── dissection-manifest.json
    ├── 01-conceitos-nucleares.md
    ├── 02-padroes-arquiteturais.md
    ├── 03-regras-e-restricoes.md
    ├── 04-exemplos-referencia.md
    └── 05-decisoes-design.md

Valida que o study bundle tem os arquivos necessarios antes de criar o scaffold.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


DISSECTION_FILES = [
    "01-conceitos-nucleares.md",
    "02-padroes-arquiteturais.md",
    "03-regras-e-restricoes.md",
    "04-exemplos-referencia.md",
    "05-decisoes-design.md",
]

STUDY_BUNDLE_REQUIRED = [
    "00-contexto.md",
    "01-matriz-afirmacoes.csv",
    "02-fontes.json",
    "index.json",
]

MANIFEST_TEMPLATE = {
    "source_study_bundle": "",
    "created_at": "",
    "architecture_pattern": "",
    "estimated_complexity": "",
    "files": DISSECTION_FILES,
    "status": "scaffold",
    "notes": "",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--study-bundle", required=True, help="Caminho para o study bundle de entrada")
    parser.add_argument("--output", required=True, help="Caminho para o diretorio de saida da dissecacao")
    return parser.parse_args()


def validate_study_bundle(bundle_path: Path) -> list[str]:
    """Valida que o study bundle tem os arquivos necessarios."""
    issues = []
    if not bundle_path.exists():
        issues.append(f"Study bundle nao encontrado: {bundle_path}")
        return issues
    if not bundle_path.is_dir():
        issues.append(f"Study bundle nao e um diretorio: {bundle_path}")
        return issues
    for fname in STUDY_BUNDLE_REQUIRED:
        fpath = bundle_path / fname
        if not fpath.exists():
            issues.append(f"Arquivo obrigatorio ausente: {fname}")
        elif fpath.stat().st_size == 0:
            issues.append(f"Arquivo obrigatorio vazio: {fname}")
    return issues


def main() -> int:
    args = parse_args()
    bundle_path = Path(args.study_bundle).resolve()
    output_path = Path(args.output).resolve()

    print(f"Dissector Extract: criando scaffold de dissecacao")
    print(f"  Study bundle: {bundle_path}")
    print(f"  Saida: {output_path}")

    # Validar study bundle
    issues = validate_study_bundle(bundle_path)
    if issues:
        print(f"\nErro: study bundle invalido:")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    print(f"  Study bundle validado")

    # Criar diretorio de saida
    if output_path.exists():
        print(f"Aviso: diretorio de saida ja existe, arquivos existentes serao preservados")

    output_path.mkdir(parents=True, exist_ok=True)

    # Criar arquivos de dissecacao (templates vazios)
    for fname in DISSECTION_FILES:
        fpath = output_path / fname
        if not fpath.exists():
            fpath.write_text(f"# {fname.replace('.md', '').replace('-', ' ').title()}\n\n<!-- Preencher durante a dissecacao -->\n", encoding="utf-8")
            print(f"  Criado: {fname}")
        else:
            print(f"  Ja existe: {fname}")

    # Criar manifest
    manifest = MANIFEST_TEMPLATE.copy()
    manifest["source_study_bundle"] = str(bundle_path)
    manifest["created_at"] = datetime.now(timezone.utc).isoformat()

    manifest_path = output_path / "dissection-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Criado: dissection-manifest.json")

    print(f"\nScaffold de dissecacao criado em: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
