# KAI-Ethno — Extensión de Investigación Antropológica Aumentada para KognitoAI

Extensión oficial para **KognitoAI** que integra una suite multi-agente especializada en investigación etnográfica, antropología digital, análisis cualitativo del discurso, triangulación de fuentes y generación de informes académicos.

## 🚀 Características Principal

- **Búsqueda Bibliográfica Multi-API**: Consulta libre de API keys a Semantic Scholar, CrossRef, SciELO, RedALyC, PubMed y arXiv.
- **Análisis Etnográfico & Detección PII**: Anonimización de datos sensibles y codificación temática cualitativa (Braun & Clarke / Grounded Theory).
- **Minería de Patrones & Redes Semánticas**: Extracción automática de palabras clave, clusters temáticos y grafos de co-ocurrencia.
- **Síntesis & Triangulación**: Integración de hallazgos etnográficos con la memoria de grafo de KognitoAI.
- **Redacción Académica Automatizada**: Generación de documentos en formatos IMRAD, informe etnográfico o revisión sistemática con citas APA, MLA, Chicago o AAA.

## 📦 Instalación

Ejecuta el script de instalación dentro del directorio de la extensión:

```bash
cd extensions/kai_ethno
./install.sh
```

O instala directamente vía Python:

```bash
python3 install.py
```

## 🛠️ Herramientas Expuestas al Agente KognitoAI

Tras la instalación, el agente de KognitoAI dispondrá de las siguientes herramientas de forma nativa:

1. `run_ethnographic_research`: Ejecuta el pipeline completo de investigación antropológica.
2. `analyze_ethnographic_data`: Procesa transcripciones, notas de campo y realiza análisis cualitativo y anonimización de PII.
3. `search_ethnographic_literature`: Búsqueda especializada de literatura en ciencias sociales y antropología.

## 📐 Arquitectura Multi-Agente

```
KAI Core (Orquestador)
├── Ethics Council (Veto ético)
├── Bibliomancer (Búsqueda académica)
├── Ethnograph (Procesamiento cualitativo)
├── PatternFinder (Redes semánticas)
├── Synthesizer (Triangulación)
├── Visualizer (Dashboards & Gráficos)
├── Scribe (Redacción académica)
└── Archivist (Memoria e indexación)
```
