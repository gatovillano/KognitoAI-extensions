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


class SearchEthnographicLiteratureInput(BaseModel):
    query: str = Field(
        ...,
        description="Consulta o palabras clave para buscar literatura en antropología y ciencias sociales. Ejemplo: 'antropología digital identidad juventud'"
    )
    max_results: int = Field(
        default=15,
        description="Número máximo de artículos a devolver (default: 15)."
    )
    year_range_start: Optional[int] = Field(
        default=2018,
        description="Año mínimo de publicación."
    )
    year_range_end: Optional[int] = Field(
        default=2026,
        description="Año máximo de publicación."
    )


class SearchEthnographicLiteratureTool(BaseTool):
    name: str = "search_ethnographic_literature"
    description: str = (
        "Busca artículos académicos, preprints y publicaciones etnográficas/antropológicas en "
        "Semantic Scholar, CrossRef, SciELO, RedALyC, PubMed y arXiv sin requerir API keys."
    )
    args_schema: Type[BaseModel] = SearchEthnographicLiteratureInput
    account_id: Optional[str] = None
    workspace_id: Optional[str] = None

    async def _arun(
        self,
        query: str,
        max_results: int = 15,
        year_range_start: Optional[int] = 2018,
        year_range_end: Optional[int] = 2026,
        **kwargs: Any
    ) -> str:
        try:
            from agents.bibliomancer import BibliomancerAgent

            biblio = BibliomancerAgent()
            year_range = None
            if year_range_start and year_range_end:
                year_range = (year_range_start, year_range_end)

            sources = await biblio.search(
                query=query,
                max_results=max_results,
                year_range=year_range
            )

            if not sources:
                return f"No se encontraron publicaciones académicas para la búsqueda: '{query}'."

            output = f"### Fuentes Académicas Encontradas ({len(sources)}):\n\n"
            for i, src in enumerate(sources[:max_results], 1):
                title = src.get("title", "Sin título")
                authors = ", ".join(src.get("authors", [])) or "Autores no especificados"
                year = src.get("year", "N/A")
                source_api = src.get("source_api", "API")
                abstract = src.get("abstract", "Sin resumen disponible.")
                url = src.get("url", "")
                
                output += f"**{i}. {title}** ({year})\n"
                output += f"- **Autores**: {authors}\n"
                output += f"- **Fuente**: {source_api}\n"
                if url:
                    output += f"- **Enlace**: {url}\n"
                output += f"- **Resumen**: {abstract[:250]}...\n\n"

            return output
        except Exception as e:
            logger.error(f"Error executing SearchEthnographicLiteratureTool: {e}", exc_info=True)
            return f"Error al buscar literatura etnográfica: {str(e)}"

    def _run(self, *args, **kwargs):
        return asyncio.run(self._arun(*args, **kwargs))
