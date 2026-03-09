#!/usr/bin/env python3
"""
Dissector Validate — Valida que um pacote de dissecacao esta completo

Uso:
    dissector_validate.py --path workspace/stage-b-dissection/

Exemplos:
    dissector_validate.py --path ./workspace/stage-b-dissection/

Verifica:
    - Todos os 5 arquivos existem e nao estao vazios
    - dissection-manifest.json existe e e JSON valido
    - Manifest tem todos os campos obrigatorios
    - architecture_pattern e um dos valores permitidos
    - estimated_complexity e um dos valores permitidos

Exit 0 se valido, exit 1 se problemas encontrados.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


DISSECTION_FILES = [
    "01-conceitos-nucleares.md",
    "02-padroes-arquiteturais.md",
    "03-regras-e-restricoes.md",
    "04-exemplos-referencia.md",
    "05-decisoes-design.md",
]

MANIFEST_REQUIRED_FIELDS = [
    "source_study_bundle",
    "created_at",
    "architecture_pattern",
    "estimated_complexity",
    "files",
    "status",
]

VALID_ARCHITECTURE_PATTERNS = [
    "workflow",
    "task-based",
    "reference",
    "capability-based",
]

VALID_COMPLEXITIES = [
    "simple",
    "moderate",
    "complex",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--path", required=True, help="Caminho para o diretorio de dissecacao a validar")
    return parser.parse_args()


def validate_dissection(dissection_path: Path) -> list[str]:
    """Valida o pacote de dissecacao. Retorna lista de problemas encontrados."""
    issues = []

    if not dissection_path.exists():
        issues.append(f"Diretorio nao encontrado: {dissection_path}")
        return issues

    if not dissection_path.is_dir():
        issues.append(f"Caminho nao e um diretorio: {dissection_path}")
        return issues

    # Verificar os 5 arquivos de dissecacao
    for fname in DISSECTION_FILES:
        fpath = dissection_path / fname
        if not fpath.exists():
            issues.append(f"Arquivo ausente: {fname}")
        elif fpath.stat().st_size == 0:
            issues.append(f"Arquivo vazio: {fname}")

    # Verificar manifest
    manifest_path = dissection_path / "dissection-manifest.json"
    if not manifest_path.exists():
        issues.append("dissection-manifest.json ausente")
        return issues

    if manifest_path.stat().st_size == 0:
        issues.append("dissection-manifest.json esta vazio")
        return issues

    # Validar JSON
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        issues.append(f"dissection-manifest.json nao e JSON valido: {e}")
        return issues

    if not isinstance(manifest, dict):
        issues.append("dissection-manifest.json deve ser um objeto JSON")
        return issues

    # Verificar campos obrigatorios
    for field in MANIFEST_REQUIRED_FIELDS:
        if field not in manifest:
            issues.append(f"Campo obrigatorio ausente no manifest: {field}")

    # Verificar architecture_pattern
    arch = manifest.get("architecture_pattern", "")
    if arch and arch not in VALID_ARCHITECTURE_PATTERNS:
        issues.append(
            f"architecture_pattern invalido: '{arch}'. "
            f"Valores permitidos: {', '.join(VALID_ARCHITECTURE_PATTERNS)}"
        )

    # Verificar estimated_complexity
    complexity = manifest.get("estimated_complexity", "")
    if complexity and complexity not in VALID_COMPLEXITIES:
        issues.append(
            f"estimated_complexity invalido: '{complexity}'. "
            f"Valores permitidos: {', '.join(VALID_COMPLEXITIES)}"
        )

    return issues


def main() -> int:
    args = parse_args()
    dissection_path = Path(args.path).resolve()

    print(f"Dissector Validate: validando {dissection_path}")

    issues = validate_dissection(dissection_path)

    if issues:
        print(f"\n{len(issues)} problema(s) encontrado(s):")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    else:
        print("  Pacote de dissecacao valido!")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
