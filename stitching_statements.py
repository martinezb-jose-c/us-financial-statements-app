from edgar import Company
from edgar.xbrl import XBRLS
from concept_normalizer import normalize_dataframe, get_normalization_report


def company_xbrls_filings(ticker, format, periods=10):
    """
    Obtiene los estados financieros usando XBRL stitching.
    Stitching: Combina múltiples filings 10-K o 10-Q en estados consolidados
    que abarquen múltiples períodos para análisis histórico.

    Args:
        ticker (str): Símbolo bursátil (ej: AAPL, MSFT)
        format (str): Annual or quarter reports (10-K or 10-Q)
        periods (int): Número de períodos a descargar (default: 10)

    Returns:
        tuple: (income_statement, balance_sheet, cash_flow_statement)
               Todos son objetos XBRL listos para convertir a DataFrame
    """
    try:
        company = Company(ticker)
        filings = company.get_filings(form=format).head(periods)
        xbrls = XBRLS.from_filings(filings)

        income_statement = xbrls.statements.income_statement(max_periods=periods).to_dataframe()
        balance_sheet = xbrls.statements.balance_sheet(max_periods=periods).to_dataframe()
        cash_flow_statement = xbrls.statements.cashflow_statement(max_periods=periods).to_dataframe()

        is_statement = income_statement.drop(columns=['concept'])
        bs_statement = balance_sheet.drop(columns=['concept'])
        cs_statement = cash_flow_statement.drop(columns=['concept'])

        return is_statement, bs_statement, cs_statement

    except Exception as e:
        raise Exception(f"Error al obtener filings de {ticker}: {str(e)}")


def normalize_df_statements(ticker, format="10-K", periods=10, normalize=True):
    """


    Opcionalmente, normaliza los nombres de conceptos contables para consolidar
    variantes (ej: "Contract Revenues" + "Contract revenues" → una sola fila)

    Args:
        ticker (str): Símbolo bursátil
        format (str): Tipo de reporte ("10-K" o "10-Q")
        periods (int): Número de períodos
        normalize (bool): Si True, normaliza y consolida conceptos duplicados

    Returns:
        tuple: (bs_df, is_df, cf_df) - DataFrames de Balance Sheet,
               Income Statement y Cash Flow
    """
    try:
        # Obtener statements con stitching
        is_stmt, bs_stmt, cf_stmt = company_xbrls_filings(ticker, format, periods)

        # Limpiar y formatear (SIN sort_index para mantener orden original)
        for df in [is_stmt, bs_stmt, cf_stmt]:
            if 'concept' in df.columns:
                df.drop(columns=['concept'], inplace=True)
            if 'label' in df.columns:
                df.set_index('label', inplace=True)
            # Las filas mantienen su orden de aparición original
            df.fillna(0, inplace=True)

        # NORMALIZACIÓN de conceptos contables
        if normalize:
            is_df = normalize_dataframe(is_stmt)
            bs_df = normalize_dataframe(bs_stmt)
            cf_df = normalize_dataframe(cf_stmt)

        return is_df, bs_df, cf_df

    except Exception as e:
        raise Exception(f"Error al convertir statements: {str(e)}")