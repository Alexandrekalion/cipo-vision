"""Future AD authorization mapping.

This module is deliberately local-only: it does not connect to a directory.
When AD integration is approved, the adapter must resolve stable subject IDs
and groups through LDAPS and pass the groups through this mapping.
"""

AD_GROUP_ROLE_MAP = {
    "GG_CIPOVISION_GESTOR": "Gestor solicitante",
    "GG_CIPOVISION_GERENTE": "Gerente aprovador",
    "GG_CIPOVISION_SEGTRAB": "Segurança do Trabalho",
    "GG_CIPOVISION_RH": "RH",
    "GG_CIPOVISION_TI": "TI",
}

def profiles_from_groups(groups: list[str]) -> list[str]:
    return sorted({AD_GROUP_ROLE_MAP[group] for group in groups if group in AD_GROUP_ROLE_MAP})
