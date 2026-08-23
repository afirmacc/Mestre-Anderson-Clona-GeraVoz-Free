from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .common import REPORTS_DIR, write_json
from .operations import synthesize, verify


BUILTIN_CASES = [
    {"id": "curta", "text": "Esta é uma verificação local de voz autorizada."},
    {"id": "numeros", "text": "Hoje é vinte e três de agosto de dois mil e vinte e seis; o valor é cento e vinte e três reais e quarenta e cinco centavos."},
    {"id": "siglas", "text": "A inteligência artificial e a experiência do usuário devem trabalhar juntas."},
    {"id": "expressividade", "text": "Você percebeu a diferença? Excelente! Vamos continuar com clareza e responsabilidade."},
]


def run_voice_suite(profile: Path, cases_file: Path | None = None) -> dict:
    cases = json.loads(cases_file.read_text(encoding="utf-8"))["cases"] if cases_file else BUILTIN_CASES
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir = REPORTS_DIR / f"voice-test-{run_id}"
    results = []
    for case in cases:
        audio = output_dir / f"{case['id']}.wav"
        manifest = output_dir / f"{case['id']}.manifest.json"
        generation = synthesize(profile, case["text"], audio, manifest)
        validation = verify(audio, case["text"], manifest)
        results.append({"id": case["id"], "generation": generation, "validation": validation})
    blocked = any(item["validation"]["status"] == "BLOQUEADO_VOZ" for item in results)
    report = {
        "schema_version": 1,
        "run_id": run_id,
        "profile": str(profile),
        "results": results,
        "human_qa_required": True,
        "status": "BLOQUEADO_VOZ" if blocked else "AGUARDA_QA_HUMANO",
    }
    write_json(output_dir / "voice-test-report.json", report)
    return report
