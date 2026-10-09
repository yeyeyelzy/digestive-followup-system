# Multi-Agent V2 Internal API

## Start

Use Uvicorn from workspace root:

```bash
uvicorn MyAgentSystem.multi_agent_system_v2.api.app_api:app --host 0.0.0.0 --port 8010
```

## Health

- `GET /health`

## Internal AI Endpoints

- `POST /ai/heart-twin/realtime`
- `POST /ai/heart-twin/forecast`
- `POST /ai/recovery/healthy-life-decision`
- `POST /ai/risk/predict`
- `POST /ai/rehab/plan/generate`
- `POST /ai/rehab/plan/revise`
- `POST /ai/rehab/plan/view`
- `POST /ai/rehab/plan/dispatch`
- `POST /ai/health-report/daily`
- `POST /ai/health-report/weekly`
- `POST /ai/health-report/monthly`

All endpoints return:

```json
{
  "code": 200,
  "msg": "success",
  "data": {}
}
```

## patientId mapping

Business IDs are accepted directly:
- `10 -> P_001`
- `11 -> P_002`
- `12 -> P_003`

Agent IDs are also accepted for compatibility:
- `P_001/P_002/P_003`

## Notes

- Current implementation reuses existing data processing and threshold style.
- Rehab plan version records are persisted to:
  - `MyAgentSystem/multi_agent_system_v2/data/output/process/rehab_plan_versions.json`
- Health report endpoints now persist report bundles under:
  - `MyAgentSystem/multi_agent_system_v2/results/<patient>/<scene>/<report_type>/<timestamp>/`
  - Each bundle contains `report.json`, `report_summary.png`, `report_summary.pdf`, and `module_outputs/*.json`.
- `module_outputs` includes payloads for:
  - `heart_3d` (realtime + forecast)
  - `rehab_achievement` (`healthy_today`, score, reasons)
