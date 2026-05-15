import streamlit as st
import os, re

st.set_page_config(page_title="DCFarma · Contabilidad", page_icon="💊", layout="wide")

LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")

# ── Iconos Bootstrap para cada KPI ───────────────────────────────────────────
_KPI_ICONS = {
    "ingresos totales":       "coin",
    "compras":                "cart3",
    "gastos":                 "receipt",
    "resultado":              "graph-up-arrow",
    "ingresos servicios":     "cash-coin",
    "ingresos alliance":      "people-fill",
    "total gastos":           "calculator",
    "saldo banco":            "bank",
    "saldo banco hoy":        "bank",
    "saldo actual":           "bank",
    "personal":               "person-workspace",
    "total base imponible":   "file-earmark-text",
    "cobros pendientes":      "arrow-down-circle-fill",
    "pagos pendientes":       "arrow-up-circle-fill",
    "saldo estimado 60d":     "graph-up",
    "var. existencias":       "box-seam",
    "margen bruto alliance":  "percent",
    "total cobros filtrados": "arrow-down-circle",
    "total pagos filtrados":  "arrow-up-circle",
    "neto filtrado":          "calculator",
}

def _kpi_icon(label):
    key = re.sub(r'[^\w\s]', '', label).lower().strip()
    return _KPI_ICONS.get(key, "bar-chart-fill")

def _kpi_label(label):
    return re.sub(r'^[^\w\s]+\s*', '', label).strip().upper()

CSS = """
<style>
#MainMenu, footer, header {visibility: hidden;}

/* ── Sidebar base ────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #f4fafa;
    border-right: 2px solid #c8e8e6;
    padding-top: 0.5rem;
}
[data-testid="stSidebar"] hr {border-color: #c8e8e6;}

/* ── option_menu: left border en activo ───────────────── */
[data-testid="stSidebar"] .nav-link-selected {
    border-left: 3px solid #4AADA8 !important;
}

/* ── KPI cards HTML ──────────────────────────────────── */
.kpi-card {
    background: #fff;
    border-radius: 10px;
    padding: 1rem 1.2rem 0.9rem;
    box-shadow: 0 1px 8px rgba(74,173,168,0.12);
    border-top: 3px solid #4AADA8;
    min-height: 90px;
}
.kpi-label {
    display: block;
    font-size: 0.70rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #7a9ea0;
    margin-bottom: 0.35rem;
}
.kpi-label i { margin-right: 4px; }
.kpi-value {
    display: block;
    font-size: 1.5rem;
    font-weight: 700;
    color: #1a3a3a;
}
.kpi-delta { display: block; font-size: 0.78rem; margin-top: 0.2rem; }

/* ── Ocultar botón CSV nativo del dataframe ───────────── */
[data-testid="stElementToolbar"] button[title="Download as CSV"],
[data-testid="stElementToolbar"] button[aria-label="Download as CSV"] {
    display: none !important;
}

/* ── General ─────────────────────────────────────────── */
.block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
h1, h2, h3 {color: #1a3a3a;}
</style>
"""

LOGIN_CSS = """
<style>
#MainMenu, footer, header {visibility: hidden;}
.stApp {
    background: linear-gradient(150deg, #d4eeec 0%, #eaf5f5 35%, #f8fffe 70%, #edf6f5 100%);
}
[data-testid="stForm"] {
    background: rgba(255,255,255,0.92);
    border-radius: 16px;
    padding: 1.8rem 1.6rem !important;
    box-shadow: 0 8px 40px rgba(74,173,168,0.18);
    border-top: 4px solid #4AADA8;
}
[data-testid="stForm"] button {
    background: #4AADA8 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 0.6rem !important;
}
[data-testid="stForm"] button:hover {
    background: #3a9d98 !important;
}
</style>
"""

def kpi_row(items):
    cols = st.columns(len(items))
    for col, item in zip(cols, items):
        label, value = item[0], item[1]
        delta = item[2] if len(item) > 2 else None
        icon  = _kpi_icon(label)
        lbl   = _kpi_label(label)
        delta_html = ""
        if delta is not None:
            try:
                dv = float(re.sub(r'[^\d,.\-]', '', str(delta)).replace('.','').replace(',','.'))
                c  = "#27ae60" if dv >= 0 else "#e74c3c"
            except Exception:
                c  = "#888"
            delta_html = f'<span class="kpi-delta" style="color:{c}">{delta}</span>'
        card = (f'<div class="kpi-card">'
                f'<span class="kpi-label"><i class="bi bi-{icon}"></i>{lbl}</span>'
                f'<span class="kpi-value">{value}</span>'
                f'{delta_html}'
                f'</div>')
        with col:
            st.markdown(card, unsafe_allow_html=True)

USERS = {"Admin": "12341234Aa$$"}

if not st.session_state.get("authenticated"):
    st.markdown(LOGIN_CSS, unsafe_allow_html=True)
    _, col_c, _ = st.columns([1, 1.2, 1])
    with col_c:
        st.markdown("<div style='height:5vh'></div>", unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH):
            _, img_c, _ = st.columns([1, 2, 1])
            with img_c:
                st.image(LOGO_PATH, use_column_width=True)
        else:
            st.markdown("## 💊 DCFarma")
        st.markdown(
            "<p style='text-align:center;color:#7a9ea0;font-size:0.88rem;"
            "margin:-0.4rem 0 1.2rem;letter-spacing:0.03em'>"
            "Contabilidad SaaS · Farmacias</p>",
            unsafe_allow_html=True,
        )
        with st.form("login_form"):
            user = st.text_input("Usuario")
            pwd  = st.text_input("Contraseña", type="password")
            ok   = st.form_submit_button("Entrar", use_container_width=True)
            if ok:
                if user in USERS and USERS[user] == pwd:
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = user
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")
    st.stop()

import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from streamlit_option_menu import option_menu
from data_loader import (load_compras, load_gastos, load_ingresos_servicios,
                         load_ingresos_alliance, load_banco, load_gastos_personal,
                         load_variacion_existencias)


@st.cache_data(ttl=300)
def get_all_data():
    df_c  = load_compras()
    df_g  = load_gastos()
    df_si = load_ingresos_servicios()
    df_al = load_ingresos_alliance()
    raw_b = load_banco()
    df_b, saldo = raw_b if isinstance(raw_b, tuple) else (raw_b, 0.0)
    personal = load_gastos_personal()
    var_exist = load_variacion_existencias()
    return df_c, df_g, df_si, df_al, df_b, saldo, personal, var_exist

df_compras, df_gastos, df_servicios, df_alliance, df_banco, saldo_banco, gastos_personal, var_existencias = get_all_data()

st.markdown(CSS, unsafe_allow_html=True)

hoy = datetime.today()
MESES = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",
         7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"}

with st.sidebar:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=160)
    else:
        st.markdown("## 💊 DCFarma")
    st.caption("Contabilidad SaaS · " + hoy.strftime("%d/%m/%Y"))
    st.markdown("---")
    vista = option_menu(
        menu_title=None,
        options=["Dashboard", "P&G", "Compras", "Gastos",
                 "Ingresos Servicios", "Ingresos Alliance", "Banco", "Forecast"],
        icons=["speedometer2", "graph-up", "cart3", "receipt",
               "cash-coin", "people-fill", "bank", "calendar3"],
        default_index=0,
        key="nav_menu",
        styles={
            "container":        {"padding": "0", "background-color": "transparent"},
            "icon":             {"color": "#4AADA8", "font-size": "1rem"},
            "nav-link":         {
                "font-size": "0.875rem", "text-align": "left",
                "padding": "0.48rem 0.65rem", "border-radius": "8px",
                "color": "#4a6a6a", "margin": "1px 0",
                "--hover-color": "rgba(74,173,168,0.10)",
            },
            "nav-link-selected": {
                "background-color": "rgba(74,173,168,0.16)",
                "color": "#1a3a3a", "font-weight": "700",
            },
        }
    )
    st.markdown("---")
    anios_set = set()
    for _df in [df_compras, df_gastos, df_servicios, df_alliance]:
        if not _df.empty and "ANO" in _df.columns:
            anios_set.update([int(a) for a in _df["ANO"].dropna().unique()])
    anios = sorted(anios_set, reverse=True) or [hoy.year]
    anio_sel = st.selectbox("Año", anios, index=0)
    meses_def = list(range(1, min(hoy.month+1,13))) if int(anio_sel)==hoy.year else list(range(1,13))
    if "mes_sel" not in st.session_state:
        st.session_state["mes_sel"] = meses_def
    _prev = st.session_state["mes_sel"]
    _n = len(_prev)
    _label = "Todos" if _n == 12 else (f"{_n} seleccionados" if _n > 0 else "Ninguno")
    with st.expander(f"Mes(es) — {_label}"):
        _todos = st.checkbox("Todos los meses", value=_n == 12, key="mes_todos_cb")
        mes_sel = []
        for m in range(1, 13):
            _checked = True if _todos else (m in _prev)
            if st.checkbox(MESES[m], value=_checked, key=f"mes_cb_{m}"):
                mes_sel.append(m)
    st.session_state["mes_sel"] = mes_sel
    st.markdown("---")
    if st.button("🔄 Actualizar datos", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    if st.button("🚪 Cerrar sesión", use_container_width=True, key="logout"):
        st.session_state.clear()
        st.rerun()

def to_excel(df):
    import io
    buf = io.BytesIO()
    df.to_excel(buf, index=False, engine="openpyxl")
    return buf.getvalue()

def dl_excel(df, filename):
    st.download_button("⬇️ Exportar Excel", data=to_excel(df),
                       file_name=filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       use_container_width=False)

def filtrar(df):
    if df is None or df.empty: return pd.DataFrame()
    out = df.copy()
    if "ANO" in out.columns: out = out[out["ANO"]==int(anio_sel)]
    if "MES" in out.columns and mes_sel: out = out[out["MES"].isin([int(m) for m in mes_sel])]
    return out

def fmt(v):
    try: return f"{float(v):,.2f} €".replace(",","X").replace(".",",").replace("X",".")
    except: return "0,00 €"

def fmtk(v):
    try: return f"{float(v):,.0f} €".replace(",",".")
    except: return "0 €"

def fdate(v):
    try: return v.strftime("%d/%m/%Y") if pd.notna(v) else ""
    except: return ""

if vista == "Dashboard":
    st.header("Panel de Control")
    fc=filtrar(df_compras); fg=filtrar(df_gastos)
    fsi=filtrar(df_servicios); fal=filtrar(df_alliance)
    def s(df): return df["BASE_IMPONIBLE"].sum() if not df.empty and "BASE_IMPONIBLE" in df.columns else 0
    tc=s(fc); tg=s(fg); tsi=s(fsi); tal=s(fal)
    ti=tsi+tal
    # Personal y variación de existencias acumulados ene→mes actual
    _mes_hasta = hoy.month if int(anio_sel)==hoy.year else 12
    _ve_anual = var_existencias.get(int(anio_sel), [0.0]*12)
    _gp_anual  = gastos_personal.get(int(anio_sel), [0.0]*12)
    tve = sum(_ve_anual[:_mes_hasta])
    tp  = sum(_gp_anual[:_mes_hasta])
    tga = tc + tg + tp - tve
    res = ti - tga
    # Margen bruto Alliance = (Alliance - Compras + Var.Exist) / Alliance
    _margen_abs = tal - tc + tve
    _margen_pct = (_margen_abs / tal * 100) if tal > 0 else 0
    _margen_str = f"{_margen_pct:,.1f} %".replace(".", "X").replace(",", ".").replace("X", ",")

    kpi_row([
        ("💰 Ingresos Totales", fmtk(ti)),
        ("🛒 Compras",          fmtk(tc)),
        ("📋 Gastos",           fmtk(tg)),
        ("Var. Existencias",    fmtk(tve)),
        ("📈 Resultado",        fmtk(res), fmtk(res) if res != 0 else None),
    ])
    kpi_row([
        ("Ingresos Servicios",   fmtk(tsi)),
        ("Ingresos Alliance",    fmtk(tal)),
        ("Margen Bruto Alliance",_margen_str),
        ("Total Gastos",         fmtk(tga)),
        ("🏦 Saldo Banco",       fmtk(saldo_banco)),
    ])

    st.markdown("---")
    st.subheader("Evolución mensual")
    meses_c=list(range(1,13)); lm=[MESES[m][:3] for m in meses_c]
    def ms(df):
        if df is None or df.empty or "MES" not in df.columns or "BASE_IMPONIBLE" not in df.columns: return [0]*12
        return [df[(df["ANO"]==int(anio_sel))&(df["MES"]==m)]["BASE_IMPONIBLE"].sum()
                if "ANO" in df.columns else df[df["MES"]==m]["BASE_IMPONIBLE"].sum() for m in meses_c]
    _ms_si=ms(df_servicios); _ms_al=ms(df_alliance)
    _ms_co=ms(df_compras);   _ms_ga=ms(df_gastos)
    _ms_res=[(_ms_si[i]+_ms_al[i])-(_ms_co[i]+_ms_ga[i]) for i in range(12)]
    # Solo meses con algún dato
    _idx_con_datos=[i for i in range(12) if _ms_si[i]+_ms_al[i]+_ms_co[i]+_ms_ga[i]!=0]
    _lm=[lm[i] for i in _idx_con_datos]
    _ms_si=[_ms_si[i] for i in _idx_con_datos]; _ms_al=[_ms_al[i] for i in _idx_con_datos]
    _ms_co=[_ms_co[i] for i in _idx_con_datos]; _ms_ga=[_ms_ga[i] for i in _idx_con_datos]
    _ms_res=[_ms_res[i] for i in _idx_con_datos]
    fig=go.Figure()
    fig.add_trace(go.Bar(name="Servicios",x=_lm,y=_ms_si,marker_color="#2ecc71"))
    fig.add_trace(go.Bar(name="Alliance",x=_lm,y=_ms_al,marker_color="#27ae60"))
    fig.add_trace(go.Bar(name="Compras",x=_lm,y=_ms_co,marker_color="#3498db"))
    fig.add_trace(go.Bar(name="Gastos",x=_lm,y=_ms_ga,marker_color="#e67e22"))
    fig.add_trace(go.Scatter(
        name="Resultado", x=_lm, y=_ms_res,
        mode="lines+markers",
        line=dict(color="#8e44ad", width=3),
        marker=dict(size=8, color=["#27ae60" if v>=0 else "#e74c3c" for v in _ms_res],
                    line=dict(width=2, color="#8e44ad")),
        hovertemplate="<b>%{x}</b><br>Resultado: %{y:,.0f} €<extra></extra>",
    ))
    fig.update_layout(barmode="group",height=380,margin=dict(l=0,r=0,t=30,b=0),
                      plot_bgcolor="white",paper_bgcolor="white",
                      legend=dict(orientation="h",yanchor="bottom",y=1.02,x=0),
                      yaxis=dict(showgrid=True,gridcolor="#f0f0f0"),
                      hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    if not fc.empty and "LABORATORIO" in fc.columns:
        st.markdown("---")
        st.subheader("Top Proveedores (Compras)")
        top=fc.groupby("LABORATORIO")["BASE_IMPONIBLE"].sum().sort_values(ascending=False).head(10)
        fig2=go.Figure(go.Bar(x=top.values,y=top.index,orientation="h",marker_color="#3498db"))
        fig2.update_layout(height=320,margin=dict(l=0,r=0,t=10,b=0),
                           plot_bgcolor="white",paper_bgcolor="white",
                           xaxis=dict(showgrid=True,gridcolor="#f0f0f0"),
                           yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig2, use_container_width=True)

elif vista == "P&G":
    meses_pg = sorted(mes_sel) if mes_sel else list(range(1, 13))
    label_pg = f"meses seleccionados" if len(meses_pg) < 12 else "año completo"
    st.header(f"📈 Pérdidas y Ganancias · {anio_sel}")
    st.caption(f"Mostrando {len(meses_pg)} mes(es) — {label_pg}")

    MESES_C = meses_pg
    MESES_L = [MESES[m][:3] for m in MESES_C]

    def mes_serie(df):
        if df is None or df.empty or "BASE_IMPONIBLE" not in df.columns:
            return [0.0] * len(MESES_C)
        df_a = df[df["ANO"] == int(anio_sel)] if "ANO" in df.columns else df
        return [float(df_a[df_a["MES"] == m]["BASE_IMPONIBLE"].sum()) if "MES" in df_a.columns else 0.0
                for m in MESES_C]

    personal_anual  = gastos_personal.get(int(anio_sel), [0.0] * 12)
    varexist_anual  = var_existencias.get(int(anio_sel), [0.0] * 12)

    servicios_m  = mes_serie(df_servicios)
    alliance_m   = mes_serie(df_alliance)
    compras_m    = mes_serie(df_compras)
    gastos_m     = mes_serie(df_gastos)
    personal_m   = [personal_anual[m - 1] for m in MESES_C]
    varexist_m   = [varexist_anual[m - 1] for m in MESES_C]

    ingresos_m    = [s + a for s, a in zip(servicios_m, alliance_m)]
    total_gasto_m = [c - v + g + p for c, v, g, p in zip(compras_m, varexist_m, gastos_m, personal_m)]
    resultado_m   = [i - g for i, g in zip(ingresos_m, total_gasto_m)]

    # ── KPIs resumen ──────────────────────────────────────────────────────────
    ti = sum(ingresos_m); tc = sum(compras_m); tg = sum(gastos_m)
    tp = sum(personal_m); tve = sum(varexist_m)
    tga = tc + tg + tp - tve   # var existencias positiva reduce coste neto
    res = ti - tga
    kpi_row([
        ("💰 Ingresos Totales", fmtk(ti)),
        ("🛒 Compras",          fmtk(tc)),
        ("📋 Gastos",           fmtk(tg)),
        ("👥 Personal",         fmtk(tp)),
        ("📈 Resultado",        fmtk(res), fmtk(res) if res != 0 else None),
    ])

    st.markdown("---")

    # ── Tabla P&G ─────────────────────────────────────────────────────────────
    def build_row(label, valores):
        total = sum(valores)
        return {"Concepto": label,
                **{MESES_L[i]: fmt(valores[i]) for i in range(len(MESES_C))},
                "TOTAL": fmt(total)}

    filas = [
        build_row("Servicios",        servicios_m),
        build_row("Alliance",         alliance_m),
        build_row("TOTAL INGRESOS",   ingresos_m),
        build_row("Compras",          compras_m),
        build_row("Var. Existencias", varexist_m),
        build_row("Gastos",           gastos_m),
        build_row("Personal",         personal_m),
        build_row("TOTAL GASTOS",     total_gasto_m),
        build_row("RESULTADO",        resultado_m),
    ]

    df_pg = pd.DataFrame(filas).set_index("Concepto")
    totales_rows = ["TOTAL INGRESOS", "TOTAL GASTOS", "RESULTADO"]

    def color_resultado(val):
        try:
            v = float(str(val).replace(".","").replace(",",".").replace("€","").strip())
            if v < 0: return "color: #e74c3c; font-weight:bold"
            if v > 0: return "color: #27ae60; font-weight:bold"
        except: pass
        return ""

    base_style = (df_pg.style
                  .set_properties(**{"text-align": "right", "font-size": "0.85rem"})
                  .set_properties(subset=pd.IndexSlice[totales_rows, :],
                                  **{"font-weight": "bold", "background-color": "#f8f9fa"}))
    _color_rows = ["RESULTADO", "Var. Existencias", "TOTAL INGRESOS", "TOTAL GASTOS"]
    try:
        styled = base_style.map(color_resultado, subset=pd.IndexSlice[_color_rows, :])
    except AttributeError:
        styled = base_style.applymap(color_resultado, subset=pd.IndexSlice[_color_rows, :])

    # Tabla con selección de fila para drill-down
    DRILLABLE = {"Servicios", "Alliance", "Compras", "Gastos"}
    try:
        ev = st.dataframe(styled, use_container_width=True,
                          on_select="rerun", selection_mode="single-row")
        sel_rows = ev.selection.rows if ev and hasattr(ev, "selection") else []
    except Exception:
        st.dataframe(styled, use_container_width=True)
        sel_rows = []

    concepto_clicked = df_pg.index[sel_rows[0]] if sel_rows else None

    # Selector manual como fallback / complemento
    drill_opts = ["— selecciona un concepto —"] + sorted(DRILLABLE)
    drill_sel = st.selectbox("🔍 Desglose de apuntes", drill_opts,
                             index=0, key="pyg_drill", label_visibility="collapsed")
    concepto_drill = concepto_clicked if (concepto_clicked in DRILLABLE) else \
                     (drill_sel if drill_sel != "— selecciona un concepto —" else None)

    if concepto_drill:
        st.markdown(f"#### 📂 Desglose · {concepto_drill}")
        _src_map = {
            "Servicios": (df_servicios, "DESCRIPCION"),
            "Alliance":  (df_alliance,  "DESCRIPCION"),
            "Compras":   (df_compras,   "LABORATORIO"),
            "Gastos":    (df_gastos,    "LABORATORIO"),
        }
        _src, _sort_col = _src_map[concepto_drill]
        # Filtrar solo por año (no por mes) para mostrar todos los meses del año en el pivot
        _df_drill = _src.copy() if not _src.empty else pd.DataFrame()
        if not _df_drill.empty and "ANO" in _df_drill.columns:
            _df_drill = _df_drill[_df_drill["ANO"] == int(anio_sel)]
        if not _df_drill.empty and _sort_col in _df_drill.columns and "MES" in _df_drill.columns:
            # Pivot: filas=proveedor/concepto, columnas=meses seleccionados, valores=suma BASE_IMPONIBLE
            _pivot = (
                _df_drill.groupby([_sort_col, "MES"])["BASE_IMPONIBLE"]
                .sum()
                .unstack(fill_value=0)
            )
            # Solo columnas de los meses seleccionados (que existan en el pivot)
            _meses_pivot = [m for m in MESES_C if m in _pivot.columns]
            _pivot = _pivot.reindex(columns=_meses_pivot, fill_value=0)
            _pivot.columns = [MESES[m][:3] for m in _meses_pivot]
            _pivot["TOTAL"] = _pivot.sum(axis=1)
            _pivot = _pivot.sort_index()
            # Fila de totales
            _total_row = pd.DataFrame([_pivot.sum(axis=0)], index=["TOTAL"])
            _pivot_full = pd.concat([_pivot, _total_row])

            def _color_drill(val):
                try:
                    v = float(str(val).replace(".","").replace(",",".").replace("€","").strip())
                    if v < 0: return "color:#e74c3c;font-weight:bold"
                    if v > 0: return "color:#1a3a3a"
                except: pass
                return ""

            try:
                _pivot_fmt = _pivot_full.map(fmt)
            except AttributeError:
                _pivot_fmt = _pivot_full.applymap(fmt)
            _styled_pivot = (
                _pivot_fmt.style
                .set_properties(**{"text-align": "right", "font-size": "0.83rem"})
                .set_properties(subset=pd.IndexSlice[["TOTAL"], :],
                                **{"font-weight": "bold", "background-color": "#f0f8f7"})
            )
            try:
                _styled_pivot = _styled_pivot.map(_color_drill)
            except AttributeError:
                _styled_pivot = _styled_pivot.applymap(_color_drill)
            st.dataframe(_styled_pivot, use_container_width=True)
        else:
            st.info("Sin apuntes para el periodo seleccionado.")

    st.markdown("---")

    # ── Gráfico mensual ───────────────────────────────────────────────────────
    st.subheader("Evolución mensual")
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Ingresos",  x=MESES_L, y=ingresos_m,
                         marker_color="#2ecc71", opacity=0.85))
    fig.add_trace(go.Bar(name="Compras",   x=MESES_L, y=compras_m,
                         marker_color="#3498db", opacity=0.85))
    fig.add_trace(go.Bar(name="Gastos",    x=MESES_L, y=gastos_m,
                         marker_color="#e67e22", opacity=0.85))
    fig.add_trace(go.Bar(name="Personal",  x=MESES_L, y=personal_m,
                         marker_color="#9b59b6", opacity=0.85))
    fig.add_trace(go.Scatter(name="Resultado", x=MESES_L, y=resultado_m,
                             mode="lines+markers",
                             line=dict(color="#8e44ad", width=3),
                             marker=dict(size=9, color=[
                                 "#27ae60" if v >= 0 else "#e74c3c" for v in resultado_m
                             ])))
    fig.update_layout(
        barmode="group", height=380, margin=dict(l=0, r=0, t=30, b=0),
        plot_bgcolor="white", paper_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

elif vista == "Compras":
    st.header("🛒 Compras")
    fc=filtrar(df_compras)
    total=fc["BASE_IMPONIBLE"].sum() if not fc.empty and "BASE_IMPONIBLE" in fc.columns else 0
    kpi_row([("Total Base Imponible", fmtk(total))])
    if not fc.empty:
        if "LABORATORIO" in fc.columns:
            st.subheader("Por Proveedor")
            prov=fc.groupby("LABORATORIO")["BASE_IMPONIBLE"].sum().sort_values(ascending=False).reset_index()
            prov.columns=["Proveedor","Base Imponible"]
            prov["Base Imponible"]=prov["Base Imponible"].apply(fmt)
            st.dataframe(prov, use_container_width=True, hide_index=True)
        st.subheader("Detalle")
        cols=[c for c in ["LABORATORIO","FARMACIA","NUM_ALBARAN","NUM_FACTURA",
                           "BASE_IMPONIBLE","FECHA_FACTURA","FECHA_VTO","FECHA_PAGO"] if c in fc.columns]
        show=fc[cols].copy()
        for dc in ["FECHA_FACTURA","FECHA_VTO","FECHA_PAGO"]:
            if dc in show.columns: show[dc]=show[dc].apply(fdate)
        if "BASE_IMPONIBLE" in show.columns: show["BASE_IMPONIBLE"]=show["BASE_IMPONIBLE"].apply(fmt)
        show=show.loc[:,~show.columns.duplicated()]
        st.dataframe(show, use_container_width=True, hide_index=True)
        dl_excel(show, f"compras_{anio_sel}.xlsx")
    else: st.info("Sin datos para el periodo seleccionado")

elif vista == "Gastos":
    st.header("📋 Gastos")
    fg=filtrar(df_gastos)
    total=fg["BASE_IMPONIBLE"].sum() if not fg.empty and "BASE_IMPONIBLE" in fg.columns else 0
    kpi_row([("Total Base Imponible", fmtk(total))])
    if not fg.empty:
        if "LABORATORIO" in fg.columns:
            st.subheader("Por Concepto")
            prov=fg.groupby("LABORATORIO")["BASE_IMPONIBLE"].sum().sort_values(ascending=False).reset_index()
            prov.columns=["Concepto","Base Imponible"]
            prov["Base Imponible"]=prov["Base Imponible"].apply(fmt)
            st.dataframe(prov, use_container_width=True, hide_index=True)
        st.subheader("Detalle")
        cols=[c for c in ["FECHA_FACTURA","LABORATORIO","REGISTRO_FACTURA","NUM_FACTURA",
                           "BASE_IMPONIBLE","FECHA_VTO","FECHA_PAGO"] if c in fg.columns]
        show=fg[cols].copy()
        for dc in ["FECHA_FACTURA","FECHA_VTO","FECHA_PAGO"]:
            if dc in show.columns: show[dc]=show[dc].apply(fdate)
        if "BASE_IMPONIBLE" in show.columns: show["BASE_IMPONIBLE"]=show["BASE_IMPONIBLE"].apply(fmt)
        show=show.loc[:,~show.columns.duplicated()]
        st.dataframe(show, use_container_width=True, hide_index=True)
        dl_excel(show, f"gastos_{anio_sel}.xlsx")
    else: st.info("Sin datos para el periodo seleccionado")

elif vista == "Ingresos Servicios":
    st.header("💰 Ingresos Servicios")
    fsi=filtrar(df_servicios)
    total=fsi["BASE_IMPONIBLE"].sum() if not fsi.empty and "BASE_IMPONIBLE" in fsi.columns else 0
    kpi_row([("Total Base Imponible", fmtk(total))])
    if not fsi.empty:
        if "CLIENTE" in fsi.columns:
            st.subheader("Por Cliente")
            prov=fsi.groupby("CLIENTE")["BASE_IMPONIBLE"].sum().sort_values(ascending=False).reset_index()
            prov.columns=["Cliente","Base Imponible"]
            prov["Base Imponible"]=prov["Base Imponible"].apply(fmt)
            st.dataframe(prov, use_container_width=True, hide_index=True)
        st.subheader("Detalle")
        cols=[c for c in ["DESCRIPCION","NUM_FACTURA","BASE_IMPONIBLE","CLIENTE",
                           "FECHA_FACTURA","FECHA_VTO","FECHA_COBRO"] if c in fsi.columns]
        show=fsi[cols].copy()
        for dc in ["FECHA_FACTURA","FECHA_VTO","FECHA_COBRO"]:
            if dc in show.columns: show[dc]=show[dc].apply(fdate)
        if "BASE_IMPONIBLE" in show.columns: show["BASE_IMPONIBLE"]=show["BASE_IMPONIBLE"].apply(fmt)
        show=show.loc[:,~show.columns.duplicated()]
        st.dataframe(show, use_container_width=True, hide_index=True)
        dl_excel(show, f"servicios_{anio_sel}.xlsx")
    else: st.info("Sin datos para el periodo seleccionado")

elif vista == "Ingresos Alliance":
    st.header("🤝 Ingresos Alliance")
    fal=filtrar(df_alliance)
    total=fal["BASE_IMPONIBLE"].sum() if not fal.empty and "BASE_IMPONIBLE" in fal.columns else 0
    kpi_row([("Total Base Imponible", fmtk(total))])
    if not fal.empty:
        if "FARMACIA" in fal.columns:
            st.subheader("Por Farmacia")
            prov=fal.groupby("FARMACIA")["BASE_IMPONIBLE"].sum().sort_values(ascending=False).reset_index()
            prov.columns=["Farmacia","Base Imponible"]
            prov["Base Imponible"]=prov["Base Imponible"].apply(fmt)
            st.dataframe(prov, use_container_width=True, hide_index=True)
        st.subheader("Detalle")
        cols=[c for c in ["DESCRIPCION","FARMACIA","OBSERVACIONES","BASE_IMPONIBLE",
                           "FECHA_FACTURA","FECHA_VTO","FECHA_COBRO"] if c in fal.columns]
        show=fal[cols].copy()
        for dc in ["FECHA_FACTURA","FECHA_VTO","FECHA_COBRO"]:
            if dc in show.columns: show[dc]=show[dc].apply(fdate)
        if "BASE_IMPONIBLE" in show.columns: show["BASE_IMPONIBLE"]=show["BASE_IMPONIBLE"].apply(fmt)
        show=show.loc[:,~show.columns.duplicated()]
        st.dataframe(show, use_container_width=True, hide_index=True)
        dl_excel(show, f"alliance_{anio_sel}.xlsx")
    else: st.info("Sin datos para el periodo seleccionado")

elif vista == "Banco":
    st.header("🏦 Banco · Santander")
    kpi_row([("🏦 Saldo Actual", fmtk(saldo_banco))])
    fb=filtrar(df_banco)
    if not fb.empty:
        fb_show=fb.loc[:,~fb.columns.duplicated()]
        st.dataframe(fb_show, use_container_width=True, hide_index=True)
        dl_excel(fb_show, f"banco_{anio_sel}.xlsx")
    else: st.info("Sin movimientos para el periodo seleccionado")

elif vista == "Forecast":
    import datetime as dt
    st.header("📅 Forecast de Cobros y Pagos")
    hoy_fc = datetime.today().date()
    fin_fc  = hoy_fc + dt.timedelta(days=60)
    st.caption(f"Ventana: {hoy_fc.strftime('%d/%m/%Y')} → {fin_fc.strftime('%d/%m/%Y')} (60 días)")

    # ── Construir eventos ──────────────────────────────────────────────
    eventos = []

    # PAGOS: compras y gastos → usar FECHA_VTO si no hay FECHA_PAGO
    for df_src, origen in [(df_compras,"Compras"),(df_gastos,"Gastos")]:
        if df_src.empty: continue
        for _, row in df_src.iterrows():
            fp = row.get("FECHA_PAGO", pd.NaT)
            fv = row.get("FECHA_VTO",  pd.NaT)
            # si ya está pagado, lo marcamos como tal pero solo si cae en ventana
            if pd.notna(fp):
                fecha_ref = fp.date() if hasattr(fp,"date") else fp
                estado = "Pagado"
            elif pd.notna(fv):
                fecha_ref = fv.date() if hasattr(fv,"date") else fv
                estado = "Vencido" if fecha_ref < hoy_fc else "Pendiente"
            else:
                continue
            if not (hoy_fc <= fecha_ref <= fin_fc) and estado != "Vencido":
                continue
            # incluir vencidos aunque sean anteriores a hoy
            if estado == "Vencido" and fecha_ref > fin_fc:
                continue
            base = float(row.get("BASE_IMPONIBLE", 0) or 0)
            lab  = str(row.get("LABORATORIO",""))
            eventos.append({
                "Fecha": fecha_ref,
                "Tipo": "PAGO",
                "Origen": origen,
                "Contraparte": lab,
                "Importe": -base,
                "Estado": estado,
            })

    # COBROS: servicios y alliance → usar FECHA_COBRO si existe, sino FECHA_VTO
    for df_src, origen in [(df_servicios,"Servicios"),(df_alliance,"Alliance")]:
        if df_src.empty: continue
        for _, row in df_src.iterrows():
            fc2 = row.get("FECHA_COBRO", pd.NaT)
            fv  = row.get("FECHA_VTO",   pd.NaT)
            if pd.notna(fc2):
                fecha_ref = fc2.date() if hasattr(fc2,"date") else fc2
                estado = "Cobrado"
            elif pd.notna(fv):
                fecha_ref = fv.date() if hasattr(fv,"date") else fv
                estado = "Vencido" if fecha_ref < hoy_fc else "Pendiente"
            else:
                continue
            if not (hoy_fc <= fecha_ref <= fin_fc) and estado != "Vencido":
                continue
            if estado == "Vencido" and fecha_ref > fin_fc:
                continue
            base = float(row.get("BASE_IMPONIBLE", 0) or 0)
            cli  = str(row.get("CLIENTE", row.get("FARMACIA","")))
            eventos.append({
                "Fecha": fecha_ref,
                "Tipo": "COBRO",
                "Origen": origen,
                "Contraparte": cli,
                "Importe": base,
                "Estado": estado,
            })

    df_ev = pd.DataFrame(eventos)

    if df_ev.empty:
        st.info("No hay eventos en los próximos 60 días")
    else:
        df_ev = df_ev.sort_values("Fecha")
        df_ev["FechaStr"] = df_ev["Fecha"].apply(lambda x: x.strftime("%d/%m/%Y") if hasattr(x,"strftime") else str(x))

        # ── KPIs ──────────────────────────────────────────────────────
        pagos_pend  = df_ev[(df_ev["Tipo"]=="PAGO")  & (df_ev["Estado"].isin(["Pendiente","Vencido"]))]["Importe"].sum()
        cobros_pend = df_ev[(df_ev["Tipo"]=="COBRO") & (df_ev["Estado"].isin(["Pendiente","Vencido"]))]["Importe"].sum()
        saldo_fin   = float(saldo_banco) + cobros_pend + pagos_pend  # pagos ya son negativos
        n_vencidos  = len(df_ev[df_ev["Estado"]=="Vencido"])

        delta_60 = saldo_fin - float(saldo_banco)
        kpi_row([
            ("🏦 Saldo Banco Hoy",    fmtk(saldo_banco)),
            ("💰 Cobros pendientes",  fmtk(cobros_pend)),
            ("💸 Pagos pendientes",   fmtk(abs(pagos_pend))),
            ("📊 Saldo estimado 60d", fmtk(saldo_fin), fmtk(delta_60) if delta_60 != 0 else None),
        ])

        if n_vencidos > 0:
            st.warning(f"⚠️ Tienes **{n_vencidos} evento(s) vencido(s)** sin registrar pago/cobro")

        st.markdown("---")

        # ── LÍNEA DE TIEMPO: cashflow acumulado día a día ─────────────
        st.subheader("Línea de tiempo · Cashflow acumulado")

        # Acumular saldo día a día
        fechas_unicas = sorted(df_ev["Fecha"].unique())
        saldo_acum = float(saldo_banco)
        timeline_fechas  = [hoy_fc]
        timeline_saldos  = [saldo_acum]

        # Totales diarios para el tooltip
        _daily_cobros = df_ev[df_ev["Tipo"]=="COBRO"].groupby("Fecha")["Importe"].sum()
        _daily_pagos  = df_ev[df_ev["Tipo"]=="PAGO"].groupby("Fecha")["Importe"].sum().abs()

        for fecha in fechas_unicas:
            movs = df_ev[df_ev["Fecha"]==fecha]["Importe"].sum()
            saldo_acum += movs
            timeline_fechas.append(fecha)
            timeline_saldos.append(saldo_acum)
        # añadir punto final en día 60
        if fin_fc not in timeline_fechas:
            timeline_fechas.append(fin_fc)
            timeline_saldos.append(saldo_acum)

        # customdata del cashflow: [saldo_fmt, cobros_dia_fmt, pagos_dia_fmt]
        _cf_customdata = []
        for _f, _s in zip(timeline_fechas, timeline_saldos):
            _c = _daily_cobros.get(_f, 0)
            _p = _daily_pagos.get(_f, 0)
            _cf_customdata.append([fmtk(_s), fmtk(_c), fmtk(_p)])

        fig = go.Figure()

        # Línea cashflow acumulado
        fig.add_trace(go.Scatter(
            x=timeline_fechas, y=timeline_saldos,
            mode="lines+markers",
            name="Cashflow acumulado",
            line=dict(color="#8e44ad", width=3),
            marker=dict(size=7, color="#8e44ad"),
            fill="tozeroy",
            fillcolor="rgba(142,68,173,0.08)",
            customdata=_cf_customdata,
            hovertemplate=(
                "<b>%{x|%d/%m/%Y}</b><br>"
                "Cashflow acumulado: <b>%{customdata[0]}</b><br>"
                "Ingresos del día: <span style='color:#27ae60'>+%{customdata[1]}</span><br>"
                "Gastos del día: <span style='color:#e74c3c'>-%{customdata[2]}</span>"
                "<extra></extra>"
            ),
        ))

        # Puntos de cobros (verde) encima de la línea
        cobros_df = df_ev[df_ev["Tipo"]=="COBRO"]
        if not cobros_df.empty:
            fig.add_trace(go.Scatter(
                x=cobros_df["Fecha"], y=cobros_df["Importe"],
                mode="markers+text",
                name="Cobros",
                marker=dict(color="#27ae60", size=12, symbol="triangle-up",
                            line=dict(width=1, color="white")),
                text=cobros_df["Importe"].apply(lambda v: fmtk(v)),
                textposition="top center",
                textfont=dict(size=9, color="#27ae60"),
                hoverinfo="skip",
                yaxis="y2",
            ))

        # Puntos de pagos (rojo) debajo
        pagos_df = df_ev[df_ev["Tipo"]=="PAGO"]
        if not pagos_df.empty:
            fig.add_trace(go.Scatter(
                x=pagos_df["Fecha"], y=pagos_df["Importe"].abs(),
                mode="markers+text",
                name="Pagos",
                marker=dict(color="#e74c3c", size=12, symbol="triangle-down",
                            line=dict(width=1, color="white")),
                text=pagos_df["Importe"].abs().apply(lambda v: fmtk(v)),
                textposition="bottom center",
                textfont=dict(size=9, color="#e74c3c"),
                hoverinfo="skip",
                yaxis="y2",
            ))

        # Línea horizontal saldo banco hoy
        fig.add_hline(y=float(saldo_banco), line_dash="dot", line_color="#f39c12", line_width=2,
                      annotation_text="Saldo hoy " + fmtk(saldo_banco),
                      annotation_position="top left",
                      annotation_font_color="#f39c12")

        # Línea vertical hoy (usando timestamp en ms para Plotly)
        import datetime as _dt2
        hoy_ts = _dt2.datetime.combine(hoy_fc, _dt2.time()).timestamp() * 1000
        fig.add_vline(x=hoy_ts, line_dash="dash", line_color="#95a5a6", line_width=1,
                      annotation_text="Hoy", annotation_position="top right")

        fig.update_layout(
            height=450, margin=dict(l=0,r=0,t=30,b=0),
            plot_bgcolor="white", paper_bgcolor="white",
            hovermode="x",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
            xaxis=dict(showgrid=True, gridcolor="#f0f0f0",
                       range=[str(hoy_fc - dt.timedelta(days=2)), str(fin_fc + dt.timedelta(days=2))],
                       tickformat="%d/%m"),
            yaxis=dict(title="Cashflow acumulado (€)", showgrid=True, gridcolor="#f0f0f0",
                       tickfont=dict(color="#8e44ad")),
            yaxis2=dict(title="Importe evento (€)", overlaying="y", side="right",
                        showgrid=False, tickfont=dict(color="#555")),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # ── TABLA DE EVENTOS ──────────────────────────────────────────
        st.subheader("Agenda de vencimientos")
        col_fil1, col_fil2 = st.columns(2)
        with col_fil1:
            tipo_fil = st.multiselect("Tipo", ["COBRO","PAGO"], default=["COBRO","PAGO"], key="fc_tipo")
        with col_fil2:
            est_fil = st.multiselect("Estado", ["Pendiente","Vencido","Pagado","Cobrado"],
                                      default=["Pendiente","Vencido"], key="fc_est")
        show_ev = df_ev[(df_ev["Tipo"].isin(tipo_fil)) & (df_ev["Estado"].isin(est_fil))].copy()
        show_ev["Importe (€)"] = show_ev["Importe"].apply(lambda v: ("+" if v>0 else "") + fmtk(abs(v)))
        # Construir tabla limpia sin columnas duplicadas
        tabla = pd.DataFrame({
            "Fecha":              show_ev["FechaStr"].values,
            "Tipo":               show_ev["Tipo"].values,
            "Origen":             show_ev["Origen"].values,
            "Proveedor/Cliente":  show_ev["Contraparte"].values,
            "Importe (€)":        show_ev["Importe (€)"].values,
            "Estado":             show_ev["Estado"].values,
        })
        st.dataframe(tabla, use_container_width=True, hide_index=True)
        total_cobros_fil = show_ev[show_ev["Tipo"]=="COBRO"]["Importe"].sum()
        total_pagos_fil  = show_ev[show_ev["Tipo"]=="PAGO"]["Importe"].sum()
        col_t1, col_t2, col_t3 = st.columns(3)
        col_t1.metric("Total cobros filtrados", fmtk(total_cobros_fil))
        col_t2.metric("Total pagos filtrados",  fmtk(abs(total_pagos_fil)))
        col_t3.metric("Neto filtrado", fmtk(total_cobros_fil + total_pagos_fil))
