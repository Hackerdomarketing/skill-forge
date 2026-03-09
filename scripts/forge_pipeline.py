#!/usr/bin/env python3
"""
Forge Pipeline — Orquestrador end-to-end do pipeline de criacao de skills

Uso:
    forge_pipeline.py --topic "descricao" --workspace path/ [--path fast|medium|deep]

Exemplos:
    forge_pipeline.py --topic "API OpenAI function calling" --workspace ./workspace/
    forge_pipeline.py --topic "formatacao markdown" --workspace ./workspace/ --path fast

Etapas:
    1. Cria diretorio workspace
    2. Roda triage (ou usa --path override)
    3. Salva triage.json
    4. Se medium/deep: cria scaffold do study bundle
    5. Se deep: cria scaffold de dissecacao
    6. Cria workspace do forge (estrutura da skill)
    7. Salva pipeline-summary.json

NOTA: Este script cria apenas os scaffolds. O estudo e a dissecacao
propriamente ditos sao executados pelos agentes LLM, nao por este script.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


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
    parser.add_argument("--topic", required=True, help="Descricao do topico da skill")
    parser.add_argument("--workspace", required=True, help="Diretorio base do workspace")
    parser.add_argument("--path", choices=["fast", "medium", "deep"], default=None,
                        help="Forcar rota especifica (pula triage automatico)")
    return parser.parse_args()


def step_print(step_num: int, message: str):
    """Imprime mensagem de status de etapa."""
    print(f"  [{step_num}/7] {message}")


def create_triage(workspace: Path, topic: str, route_override: str | None) -> str:
    """Cria triage.json e retorna a rota determinada."""
    if route_override:
        route = route_override
        triage = {
            "topic": topic,
            "signals": {},
            "total_score": 0,
            "route": route,
            "override": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    else:
        # Score padrao: sem sinais = score 0 = fast
        # O usuario deve rodar forge_triage.py separadamente para scoring real
        route = "fast"
        triage = {
            "topic": topic,
            "signals": {},
            "total_score": 0,
            "route": route,
            "override": False,
            "note": "Triage automatico sem sinais. Rode forge_triage.py para scoring detalhado.",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    triage_path = workspace / "triage.json"
    triage_path.write_text(json.dumps(triage, ensure_ascii=False, indent=2), encoding="utf-8")
    return route


def create_study_bundle_scaffold(workspace: Path, topic: str) -> Path:
    """Cria scaffold do study bundle."""
    files = [
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

    date_str = datetime.now().strftime("%Y-%m-%d")
    slug = slugify(topic)
    study_dir = workspace / "stage-a-study" / date_str / slug
    study_dir.mkdir(parents=True, exist_ok=True)

    for fname in files:
        fpath = study_dir / fname
        if not fpath.exists():
            if fname.endswith(".csv"):
                fpath.write_text("claim_id,afirmacao,nivel_certeza,fonte\n", encoding="utf-8")
            elif fname.endswith(".json"):
                fpath.write_text("[]", encoding="utf-8")
            else:
                title = fname.replace(".md", "").replace("-", " ").title()
                fpath.write_text(f"# {title}\n\n<!-- Preencher durante o estudo -->\n", encoding="utf-8")

    index = {
        "topic": topic,
        "slug": slug,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pipeline_mode": "full",
        "method_version": "7.0",
        "files": files,
    }
    (study_dir / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return study_dir


def create_dissection_scaffold(workspace: Path) -> Path:
    """Cria scaffold de dissecacao."""
    dissection_files = [
        "01-conceitos-nucleares.md",
        "02-padroes-arquiteturais.md",
        "03-regras-e-restricoes.md",
        "04-exemplos-referencia.md",
        "05-decisoes-design.md",
    ]

    dissection_dir = workspace / "stage-b-dissection"
    dissection_dir.mkdir(parents=True, exist_ok=True)

    for fname in dissection_files:
        fpath = dissection_dir / fname
        if not fpath.exists():
            title = fname.replace(".md", "").replace("-", " ").title()
            fpath.write_text(f"# {title}\n\n<!-- Preencher durante a dissecacao -->\n", encoding="utf-8")

    manifest = {
        "source_study_bundle": "",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "architecture_pattern": "",
        "estimated_complexity": "",
        "files": dissection_files,
        "status": "scaffold",
    }
    (dissection_dir / "dissection-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return dissection_dir


def create_forge_workspace(workspace: Path, topic: str) -> Path:
    """Cria workspace do forge (estrutura da skill)."""
    slug = slugify(topic)
    skill_dir = workspace / "stage-c-forge" / slug
    skill_dir.mkdir(parents=True, exist_ok=True)

    # Criar estrutura basica da skill (similar ao forge_init)
    (skill_dir / "scripts").mkdir(exist_ok=True)
    (skill_dir / "references").mkdir(exist_ok=True)
    (skill_dir / "assets").mkdir(exist_ok=True)

    # Criar SKILL.md placeholder
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        title = " ".join(w.capitalize() for w in slug.split("-"))
        skill_md.write_text(f"""---
name: {slug}
description: "[TODO: Preencher apos estudo e dissecacao]"
---

# {title}

<!-- Skill gerada pelo Forge Pipeline. Preencher apos completar as etapas anteriores. -->
""", encoding="utf-8")

    return skill_dir


def main() -> int:
    args = parse_args()
    workspace = Path(args.workspace).resolve()
    topic = args.topic
    slug = slugify(topic)

    print(f"Forge Pipeline: iniciando pipeline para '{topic}'")
    print(f"  Workspace: {workspace}")
    print()

    # 1. Criar workspace
    step_print(1, "Criando workspace...")
    workspace.mkdir(parents=True, exist_ok=True)
    print(f"       {workspace}")

    # 2-3. Triage
    step_print(2, "Executando triage...")
    route = create_triage(workspace, topic, args.path)
    step_print(3, f"Triage salvo. Rota: {route}")

    # 4. Study bundle (medium/deep)
    study_dir = None
    if route in ("medium", "deep"):
        step_print(4, "Criando scaffold do study bundle...")
        study_dir = create_study_bundle_scaffold(workspace, topic)
        print(f"       {study_dir}")
    else:
        step_print(4, "Study bundle: pulado (rota fast)")

    # 5. Dissection (deep)
    dissection_dir = None
    if route == "deep":
        step_print(5, "Criando scaffold de dissecacao...")
        dissection_dir = create_dissection_scaffold(workspace)
        print(f"       {dissection_dir}")
    else:
        step_print(5, "Dissecacao: pulado (rota nao-deep)")

    # 6. Forge workspace
    step_print(6, "Criando workspace do forge...")
    forge_dir = create_forge_workspace(workspace, topic)
    print(f"       {forge_dir}")

    # 7. Pipeline summary
    step_print(7, "Salvando pipeline-summary.json...")
    summary = {
        "topic": topic,
        "slug": slug,
        "route": route,
        "route_override": args.path is not None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "stages": {
            "triage": str(workspace / "triage.json"),
            "study": str(study_dir) if study_dir else None,
            "dissection": str(dissection_dir) if dissection_dir else None,
            "forge": str(forge_dir),
        },
        "status": "scaffold-created",
        "next_steps": [],
    }

    # Definir proximos passos baseado na rota
    if route == "fast":
        summary["next_steps"] = [
            "Preencher SKILL.md diretamente em stage-c-forge/",
            "Rodar forge_validate.py para validar",
        ]
    elif route == "medium":
        summary["next_steps"] = [
            "Executar estudo em stage-a-study/ (agente LLM)",
            "Preencher SKILL.md baseado no estudo",
            "Rodar forge_validate.py para validar",
        ]
    else:  # deep
        summary["next_steps"] = [
            "Executar estudo em stage-a-study/ (agente LLM)",
            "Executar dissecacao em stage-b-dissection/ (agente LLM)",
            "Preencher SKILL.md baseado no estudo e dissecacao",
            "Rodar forge_knowledge_accuracy.py para verificar precisao",
            "Rodar forge_validate.py para validar",
        ]

    summary_path = workspace / "pipeline-summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"       {summary_path}")

    print(f"\nPipeline scaffold criado com sucesso!")
    print(f"  Rota: {route}")
    print(f"  Proximos passos:")
    for i, step in enumerate(summary["next_steps"], 1):
        print(f"    {i}. {step}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
