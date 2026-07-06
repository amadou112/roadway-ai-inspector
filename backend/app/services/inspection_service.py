import json

from app.models.inspection import DailyInspectionReport
from app.services.llm_provider import chat_completion

SYSTEM_PROMPT = """You are a state DOT resident engineer's assistant writing a professional \
Daily Inspection Report for a roadway/bridge construction project. Given structured field data, \
produce a well-organized narrative report with these sections, using clear professional language \
suitable for a DOT project file: Summary, Weather, Personnel & Equipment, Work Performed, \
Materials Delivered, Quantities Installed, Deficiencies & Non-Conformances, Safety Observations, \
Photo Log. Be factual and concise; do not invent data not present in the input."""


def generate_narrative(report: DailyInspectionReport) -> str:
    field_data = {
        "report_date": str(report.report_date),
        "inspector_name": report.inspector_name,
        "weather_temp_f": report.weather_temp_f,
        "weather_conditions": report.weather_conditions,
        "contractor_activities": report.contractor_activities,
        "equipment_onsite": report.equipment_onsite,
        "materials_delivered": report.materials_delivered,
        "quantities_installed": report.quantities_installed,
        "deficiencies": report.deficiencies,
        "photos": report.photos,
    }
    user_prompt = f"Field data (JSON):\n{json.dumps(field_data, indent=2, default=str)}"
    return chat_completion(SYSTEM_PROMPT, user_prompt, temperature=0.3)
