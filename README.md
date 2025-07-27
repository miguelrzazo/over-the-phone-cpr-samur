# Over The Phone CPR

This repository contains all code, data, and documentation for our comprehensive study on the effectiveness of Cardiopulmonary Resuscitation (CPR) delivered over the phone (RCP Transtelefónica) by emergency medical services.

## Project Overview

This research project conducts a rigorous analysis of telephone-assisted CPR interventions in real-world emergency scenarios, utilizing data from Madrid's emergency medical service (SAMUR-PC). Our study spans two years of emergency response data, examining the clinical outcomes, survival rates, and effectiveness of remote CPR guidance protocols.

**Key research objectives:**
- Evaluate the clinical effectiveness of telephone-guided CPR compared to traditional approaches
- Analyze survival outcomes and return of spontaneous circulation (ROSC) rates
- Identify optimal intervention protocols and timing factors
- Provide evidence-based recommendations for emergency medical services

**Study characteristics:**
- **Data source:** SAMUR-PC Madrid emergency medical service
- **Time period:** July 2023 to June 2025 (24 months)
- **Study design:** Retrospective observational cohort study
- **Primary endpoints:** ROSC, survival to hospital discharge, neurological outcomes
- **Language:** The main documentation and code comments are in Spanish, as the study was conducted in Spain
- **Audience:** This repository is designed for medical professionals, emergency technicians, researchers, and public health officials. No programming experience is required to follow the workflow or documentation

**Transparency and reproducibility:** All analytical methods, statistical procedures, and visualization techniques are documented and available for peer review and replication. The study was conducted by EMT volunteers at SAMUR-PC Madrid. Note that raw data is not publicly available due to data privacy.

## How to Use This Repository

**For medical professionals and researchers:**

1. **Begin with the methodology**: Start with `documentation/1. Workflow.md` for a comprehensive guide to our research methodology and analytical approach
2. **Understand the data structure**: Navigate to the `data/` folder to explore our data organization:
   - `1.raw_imported/`: Original datasets (not publicly available due to privacy protection)
   - `2.Data_cleaning/`: Data preprocessing scripts and exclusion reports
   - `3.cleaned_data/`: Final analytical datasets in multiple formats
3. **Examine the analysis**: Review our statistical analyses and clinical findings in `final_noteboooks/`:
   - Main analysis notebook with all statistical tests and visualizations
   - Exploratory data analysis with descriptive statistics
4. **Access the publication**: Find the complete scientific manuscript in `latex/paper/rcp_transtelefonica_paper.pdf`
5. **View presentations**: Conference materials and visual summaries available in the `latex/poster/` directory

**For technical users:**
- All code is written in Python with clear documentation
- Statistical analyses use standard medical research methodologies
- Visualizations follow scientific publication standards
- LaTeX source files are provided for complete transparency

## Repository Structure

```
RCP Transtelefonica/
├── data/                    # Data processing pipeline
├── documentation/           # Detailed methodology (Spanish)
├── final_noteboooks/       # Statistical analysis and results
└── latex/                  # Publication materials
    ├── paper/             # Scientific manuscript
    ├── poster/            # Conference poster
    └── figures/           # High-resolution graphics

```

## License

This project is licensed under the MIT License, promoting open science and reproducible research. See the LICENSE file for complete terms.

**Citation requirements:** When using this code, data analysis methods, or research findings, please cite appropriately and acknowledge the original work.

---

**Research ethics:** This study was conducted in accordance with applicable research ethics guidelines and data protection regulations.

---

## Detailed Documentation (Spanish)

The following technical documentation provides comprehensive details for researchers and medical professionals:
- `1. Workflow.md`: Flujo de trabajo del estudio
- `2. data_cleaning.md`: Proceso de limpieza de datos
- `3. data_analysis.md`: Análisis estadístico y visualizaciones
- `4. Presentation.md`: Compilacion de figuras y tabls, escritura del paper en latex y creacion del poster.

