import os
import sys
import logging
import asyncio
from typing import Type, Any, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

# Garantizar resolución de módulos dentro de la skill
current_dir = os.path.dirname(os.path.abspath(__file__))
skill_dir = os.path.dirname(current_dir)
if skill_dir not in sys.path:
    sys.path.insert(0, skill_dir)

logger = logging.getLogger(__name__)


class RunEthnographicResearchInput(BaseModel):
    research_question: str = Field(
        ...,
        description="La pregunta o tema principal de investigación etnográfica. Ejemplo: '¿Cómo construyen los jóvenes su identidad digital en TikTok?'"
    )
    max_sources: int = Field(
        default=20,
        description="Número máximo de fuentes académicas a recuperar y analizar (default: 20)."
    )
    document_type: str = Field(
        default="ethnographic_report",
        description="Tipo de documento a generar: 'ethnographic_report' (informe etnográfico), 'systematic_review' (revisión sistemática) o 'field_notes_analysis' (análisis de campo)."
    )
    year_range_start: Optional[int] = Field(
        default=2018,
        description="Año de inicio para el filtro de literatura (ej. 2018)."
    )
    year_range_end: Optional[int] = Field(
        default=2026,
        description="Año de fin para el filtro de literatura (ej. 2026)."
    )
    citation_style: str = Field(
        default="apa",
        description="Estilo de citación académica: 'apa', 'mla', 'chicago' o 'aaa' (default: 'apa')."
    )


class RunEthnographicResearchTool(BaseTool):
    name: str = "run_ethnographic_research"
    description: str = (
        "Ejecuta un pipeline completo de investigación etnográfica o antropológica. "
        "Realiza búsqueda bibliográfica multi-API (Semantic Scholar, CrossRef, SciELO, RedALyC, PubMed), "
        "análisis temático, triangulación de fuentes y generación del documento académico final."
    )
    args_schema: Type[BaseModel] = RunEthnographicResearchInput
    account_id: Optional[str] = None
    workspace_id: Optional[str] = None

    async def _arun(
        self,
        research_question: str,
        max_sources: int = 20,
        document_type: str = "ethnographic_report",
        year_range_start: Optional[int] = 2018,
        year_range_end: Optional[int] = 2026,
        citation_style: str = "apa",
        **kwargs: Any
    ) -> str:
        try:
            from scripts.orchestrator import KAIEthnoOrchestrator
            
            orchestrator = KAIEthnoOrchestrator(
                enable_ethics=True,
                enable_memory=False,
                enable_message_bus=False
            )

            year_range = None
            if year_range_start and year_range_end:
                year_range = (year_range_start, year_range_end)

            result = await orchestrator.run_research(
                research_question=research_question,
                max_sources=max_sources,
                year_range=year_range,
                include_visualizations=True,
                generate_document=True,
                document_type=document_type,
                citation_style=citation_style
            )

            if isinstance(result, dict):
                status = result.get("status", "completed")
                document = result.get("document", {}).get("content", "")
                summary = result.get("summary", "")
                
                output = f"### Resultado de Investigación Etnográfica: {research_question}\n"
                output += f"**Estado**: {status}\n\n"
                if summary:
                    output += f"**Resumen**: {summary}\n\n"
                if document:
                    output += f"### Documento Generado:\n\n{document}\n"
                else:
                    output += f"Resultados procesados: {result.get('metrics', {})}"
                return output
            return str(result)
        except Exception as e:
            logger.error(f"Error executing RunEthnographicResearchTool: {e}", exc_info=True)
            return f"Error al ejecutar la investigación etnográfica: {str(e)}"

    def _run(self, *args, **kwargs):
        return asyncio.run(self._arun(*args, **kwargs))
