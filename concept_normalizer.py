import re
import pandas as pd

# ============================================================================
# DICCIONARIO DE ALIAS - Mapeo de variantes a nombres canónicos
# ============================================================================

CONCEPT_ALIASES = {
    # Revenues
    "contract revenues": ["contract revenue", "revenues from contracts"],
    "net revenues": ["revenues", "net sales"],
    "service revenues": ["service revenue"],

    # Property, Plant and Equipment
    "property plant and equipment": [
        "properties plant and equipment",
        "properties and plant and equipment",
        "pp&e",
        "ppe",
        "property, plant & equipment",
        "property and equipment and intangible asset"
    ],

    # Current Assets
    "current assets": ["total current assets"],
    "cash and cash equivalents": ["cash and equivalents", "cash"],
    "short term investments": ["short-term investments", "marketable securities"],
    "accounts receivable": ["accounts receivable, net", "trade receivables"],
    "inventory": ["inventories"],

    # Long-term Debt
    "long-term debt": ["long term debt", "long-term borrowings"],
    "short-term debt": ["short term debt", "current portion of debt"],

    # Equity
    "stockholders equity": ["shareholders equity", "total equity", "shareholders' equity"],
    "common stock": ["common shares"],
    "retained earnings": ["accumulated earnings"],

    # Income Statement
    "cost of revenues": ["cost of goods sold", "cost of sales", "cost of revenue"],
    "gross profit": ["gross margin"],
    "operating expenses": ["total operating expenses"],
    "research and development": ["r&d", "research & development"],
    "selling general and administrative": ["sg&a", "selling, general and administrative"],
    "operating income": ["operating profit", "operating earnings"],
    "interest expense": ["interest paid"],
    "income tax expense": ["provision for income taxes", "tax provision"],

    # Balance Sheet
    "total assets": [],
    "total liabilities": [],
    "total current liabilities": ["current liabilities"],
    "account receivable": ["receivable net"],

    # Cash Flow
    "operating cash flow": ["cash flow from operations", "cash flows from operating activities"],
    "investing cash flow": ["cash flow from investing", "cash flows from investing activities"],
    "financing cash flow": ["cash flow from financing", "cash flows from financing activities"],
    "asset impairment": ["impairment of asset"]
}


def singularize_word(word: str) -> str:
    """
    Convierte una palabra a su forma singular (aproximación simple).

    Args:
        word (str): Palabra a singularizar

    Returns:
        str: Palabra en singular
    """
    # No singularizar palabras cortas (ej: "as", "is")
    if len(word) <= 2:
        return word

    # Excepciones conocidas
    exceptions = {
        "sales": "sales",  # Ya es singular/plural
        "securities": "security",
        "properties": "property",
        "inventories": "inventory",
        "activities": "activity",
        "liabilities": "liability",
        "earnings": "earnings",  # Siempre plural
        "proceeds": "proceeds",  # Siempre plural
    }

    if word in exceptions:
        return exceptions[word]

    # Reglas generales de singularización
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"  # activities -> activity
    elif word.endswith("sses"):
        return word[:-2]  # losses -> loss
    elif word.endswith("es") and len(word) > 3:
        # Casos como "expenses" -> "expense"
        return word[:-1]
    elif word.endswith("s") and not word.endswith("ss"):
        return word[:-1]  # repayments -> repayment

    return word


def normalize_concept_name(concept: str) -> str:
    """
    Normaliza un nombre de concepto contable.

    Pasos:
    1. Convertir a minúsculas
    2. Remover espacios múltiples
    3. Remover puntuación (excepto espacios)
    4. Remover artículos como "the", "a", "an"
    5. Remover caracteres especiales como & y comillas
    6. Singularizar palabras para consolidar plurales

    Args:
        concept (str): Nombre del concepto original

    Returns:
        str: Concepto normalizado
    """
    # Convertir a minúsculas
    concept = concept.lower().strip()

    # Remover caracteres especiales: & -> and
    concept = concept.replace("&", "and")

    # Remover comillas y caracteres especiales
    concept = re.sub(r"['\"]", "", concept)

    # Remover puntuación pero mantener espacios y guiones
    concept = re.sub(r"[,;:]", "", concept)

    # Reemplazar múltiples espacios por uno solo
    concept = re.sub(r"\s+", " ", concept)

    # Remover artículos al inicio
    concept = re.sub(r"^(the|a|an)\s+", "", concept)

    # ✅ NUEVA FUNCIONALIDAD: Singularizar cada palabra
    words = concept.split()
    singularized_words = [singularize_word(word) for word in words]
    concept = " ".join(singularized_words)

    return concept.strip()


def find_canonical_form(normalized_concept: str) -> str:
    """
    Encuentra la forma canónica (preferida) de un concepto.

    Args:
        normalized_concept (str): Concepto ya normalizado

    Returns:
        str: Forma canónica del concepto
    """
    # Buscar en el diccionario de aliases
    for canonical, aliases in CONCEPT_ALIASES.items():
        if normalized_concept == canonical:
            return canonical

        for alias in aliases:
            if normalized_concept == normalize_concept_name(alias):
                return canonical

    # Si no encuentra match exacto, retornar como está
    return normalized_concept


def consolidate_duplicate_concepts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Consolida filas con conceptos duplicados o similares.
    Suma los valores de filas que representan el mismo concepto.

    Args:
        df (pd.DataFrame): DataFrame con índice como nombres de conceptos

    Returns:
        pd.DataFrame: DataFrame consolidado sin duplicados
    """
    # ✅ CONVERTIR TODAS LAS COLUMNAS A NUMÉRICAS PRIMERO
    df_numeric = df.copy()
    for col in df_numeric.columns:
        df_numeric[col] = pd.to_numeric(df_numeric[col], errors='coerce')

    # Crear mapeo de nombres originales a formas canónicas
    index_mapping = {}
    for original_name in df_numeric.index:
        normalized = normalize_concept_name(original_name)
        canonical = find_canonical_form(normalized)
        index_mapping[original_name] = canonical

    # Reemplazar índice con formas canónicas
    df_numeric.index = df_numeric.index.map(index_mapping)

    # Agrupar por concepto consolidado y sumar
    df_consolidated = df_numeric.groupby(df_numeric.index, sort=False).sum(numeric_only=True)

    return df_consolidated


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica normalización de conceptos a un DataFrame de estados financieros.

    Args:
        df (pd.DataFrame): DataFrame de estados financieros

    Returns:
        pd.DataFrame: DataFrame normalizado y consolidado
    """
    # Consolidar conceptos duplicados/similares
    df_normalized = consolidate_duplicate_concepts(df)

    return df_normalized


# ============================================================================
# INFORMACIÓN ÚTIL
# ============================================================================

def get_normalization_report(df_original: pd.DataFrame, df_normalized: pd.DataFrame) -> str:
    """
    Genera un reporte de cambios aplicados por normalización.

    Args:
        df_original: DataFrame original
        df_normalized: DataFrame después de normalización

    Returns:
        str: Reporte formateado
    """
    num_original = len(df_original)
    num_normalized = len(df_normalized)
    consolidated = num_original - num_normalized

    report = f"""
REPORTE DE NORMALIZACIÓN DE CONCEPTOS
======================================
Conceptos originales: {num_original}
Conceptos después de consolidar: {num_normalized}
Conceptos consolidados: {consolidated}

Cambios aplicados:
- Normalización de mayúsculas (Contract Revenues → contract revenues)
- Consolidación de puntuación (PP&E → ppe)
- Singularización de palabras (repayments → repayment)
- Fusión de conceptos equivalentes
- Suma de valores de filas duplicadas
"""

    return report

