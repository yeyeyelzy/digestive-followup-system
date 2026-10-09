from typing import Dict


class PatientIdMappingService:
    """Maps business patient IDs (10/11/12) to agent IDs (P_001/P_002/P_003)."""

    _biz_to_agent: Dict[str, str] = {
        "10": "P_001",
        "11": "P_002",
        "12": "P_003",
    }
    _agent_to_biz: Dict[str, str] = {v: k for k, v in _biz_to_agent.items()}

    @classmethod
    def to_agent_id(cls, patient_id: str) -> str:
        if patient_id in cls._biz_to_agent:
            return cls._biz_to_agent[patient_id]
        if patient_id in cls._agent_to_biz:
            return patient_id
        raise ValueError(f"Unsupported patientId: {patient_id}")

    @classmethod
    def to_biz_id(cls, patient_id: str) -> str:
        if patient_id in cls._agent_to_biz:
            return cls._agent_to_biz[patient_id]
        if patient_id in cls._biz_to_agent:
            return patient_id
        raise ValueError(f"Unsupported patientId: {patient_id}")
