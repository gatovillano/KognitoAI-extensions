import os
import sys
import logging
import asyncio
from typing import Type, Any, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

current_dir = os.path.dirname(os.path.abspath(__file__))
skill_dir = os.path.dirname(current_dir)
if skill_dir not in sys.path:
    sys.path.insert(0, skill_dir)

logger = logging.getLogger(__name__)


class AnalyzeEthnographicDataInput(BaseModel):
    text_content: str = Field(
        ...,
        description="El texto de transcripción, grupo focal o notas de trabajo de campo a analizar."
    )
    anonymize_pii: bool = Field(
        default=True,
        description="Si es True, anonimiza automáticamente datos personales identificables (email, teléfonos, nombres)."
    )
    coding_framework: str = Field(
        default="braun_clarke",
        description="Marco metodológico de codificación temática ('braun_clarke' o 'grounded_theory')."
    )


class AnalyzeEthnographicDataTool(BaseTool):
    name: str = "analyze_ethnographic_data"
    description: str = (
        "Analiza cualitativamente textos etnográficos, transcripciones de entrevistas o notas de campo. "
        "Realiza detección y anonimización de PII, codificación temática (Braun & Clarke / Grounded Theory) "
        "y extracción de redes semánticas."
    )
    args_schema: Type[BaseModel] = AnalyzeEthnographicDataInput
    account_id: Optional[str] = None
    workspace_id: Optional[str] = None

    async def _arun(
        self,
        text_content: str,
        anonymize_pii: bool = True,
        coding_framework: str = "braun_clarke",
        **kwargs: Any
    ) -> str:
        try:
            from agents.ethnograph import EthnographAgent
            from agents.pattern_finder import PatternFinderAgent

            ethnograph = EthnographAgent()
            pattern_finder = PatternFinderAgent()

            source_item = {
                "id": "user_input_transcript",
                "title": "Transcripción/Notas de Campo",
                "abstract": text_content,
                "content": text_content
            }

            processed = await ethnograph.process_corpus([source_item])
            patterns = await pattern_finder.analyze(processed)

            output = "### Análisis Etnográfico Cualitativo\n\n"
            
            if processed:
                item = processed[0]
                output += "#### 🔒 Procesamiento Etnográfico:\n"
                output += f"- **PII Detectados**: {len(item.get('pii_detected', []))}\n"
                output += f"- **Temas Codificados**: {', '.join([t.get('name', str(t)) for t in item.get('themes', [])]) or 'Ninguno'}\n\n"

            if patterns:
                output += "#### 🔍 Patrones y Redes Semánticas:\n"
                keywords = patterns.get("keywords", {})
                if keywords:
                    top_kw = list(keywords.keys())[:10] if isinstance(keywords, dict) else keywords[:10]
                    output += f"- **Palabras clave principales**: {', '.join(top_kw)}\n"
                clusters = patterns.get("clusters", [])
                if clusters:
                    output += f"- **Clusters temáticos identificados**: {len(clusters)}\n"

            return output
        except Exception as e:
            logger.error(f"Error executing AnalyzeEthnographicDataTool: {e}", exc_info=True)
            return f"Error al analizar datos etnográficos: {str(e)}"

    def _run(self, *args, **kwargs):
        return asyncio.run(self._arun(*args, **kwargs))
