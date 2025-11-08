# 📊 Descarga de Estados Financieros SEC - VERSIÓN SIMPLIFICADA

## ✅ Lo Que Tienes

Una aplicación **Streamlit** limpia y simple que:

- Descarga estados financieros consolidados de la SEC
- Usa **XBRL Stitching** para combinar múltiples períodos
- Genera 3 CSVs listos para usar

---

## 📁 Archivos Necesarios

```
proyecto/
├── app.py ⭐ (MAIN - Único archivo importante)
├── stitching_statements.py (Procesa datos)
├── concept_normalizer.py (Normaliza conceptos)
└── requirements.txt (Dependencias)
```

---

## 🚀 Instalación Rápida

### 1. Instala dependencias
```bash
pip install -r requirements.txt
# O manualmente:
pip install streamlit edgartools pandas
```

### 2. Ejecuta la app
```bash
streamlit run app.py
```

### 3. Usa la app
- **Sidebar:** Ingresa email y ticker (ej: AAPL)
- **Slider:** Selecciona cuántos años o trimestres (1-30)
- **Checkbox:** Normalizar conceptos (opcional)
- **Botón:** Clic en "⬇️ Procesar Stitching"
- **Descarga:** Los 3 CSV generados

---

## 📊 Qué Genera

**3 archivos CSV descargables:**

1. **IncomeStatement_AAPL.csv** - Estado de Resultados
2. **BalanceSheet_AAPL.csv** - Balance General
3. **CashFlowStatement_AAPL.csv** - Flujo de Efectivo

Cada uno contiene **múltiples períodos** consolidados históricamente.

---

## ⚙️ Configuración

| Campo      | Tipo     | Default | Rango     |
|------------|----------|---------|-----------|
| Email      | text     | -       | -         |
| Ticker     | text     | AAPL    | -         |
| Formato    | radio    | 10-K    | 10-K/10-Q |
| Períodos   | slider   | 10      | 1-30      |
| Normalizar | checkbox | ✓       | ON/OFF    |

---

## 🎯 Ejemplo de Uso

```
1. Email: tu_email@gmail.com
2. Ticker: MSFT
3. Períodos: 5
4. Anual/Trimestral: 10-K o 10-Q
5. Clic "⬇️ Procesar Stitching"
↓
Espera mientras descarga...
↓
Descarga los 3 CSV
↓
¡Listo!
```

---

## 📋 Vista de Datos

**Income Statement** (Ejemplo):
```
             2023-12-31    2022-12-31    2021-12-31
Revenue       383,284       198,072       168,088
Cost of Goods Sold
              141,680        60,024        52,857
Gross Profit  241,604       138,048       115,231
```

---

## ⚡ Características

✅ Interfaz limpia y simple
✅ Solo Tab 1 (Stitching)
✅ Descarga automática de CSV
✅ Validación de datos
✅ Manejo de errores
✅ Responsive design

---

## 🆘 Troubleshooting

### Error: "EmailNotSetError"
→ Necesitas ingresa un email válido en el sidebar

### Error: "CompanyNotFoundError"
→ El ticker no existe. Intenta con AAPL, MSFT, etc.

### Error: Timeout
→ Hay muchos períodos. Intenta con menos años (5-10)

---

## 📝 Notas

- Requiere **conexión a internet**
- La SEC API es gratuita pero requiere email
- Primer uso toma más tiempo (caching)
- Los datos son **públicos y verificados**

---

## 🔗 Recursos

- SEC XBRL: https://www.sec.gov/cgi-bin/browse-edgar
- edgartools: https://github.com/dgunning/edgartools
- Streamlit: https://streamlit.io/

---

**¡Listo! Solo ejecuta `streamlit run app.py` y disfruta! 🎉**
