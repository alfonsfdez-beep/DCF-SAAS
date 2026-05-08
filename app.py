import streamlit as st


USERS = {"Admin": "12341234Aa$$"}

def check_login():
    if st.session_state.get("authenticated"):
        return True
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("## 🔐 DCFarma")
        with st.form("login_form"):
            user = st.text_input("Usuario")
            pwd = st.text_input("Contraseña", type="password")
            submitted = st.form_submit_button("Entrar", use_container_width=True)
            if submitted:
                if user in USERS and USERS[user] == pwd:
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = user
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")
    return False

if not check_login():
    st.stop()

from data_loader import (load_compras, load_gastos, load_ingresos_servicios,
                         load_ingresos_alliance, load_banco)


@st.cache_data(ttl=300)
def get_all_data():
    df_c  = load_compras()
    df_g  = load_gastos()
    df_si = load_ingresos_servicios()
    df_al = load_ingresos_alliance()
    raw_b = load_banco()
    df_b, saldo = raw_b if isinstance(raw_b, tuple) else (raw_b, 0.0)
    return df_c, df_g, df_si, df_al, df_b, saldo

df_compras, df_gastos, df_servicios, df_alliance, df_banco, saldo_banco = get_all_data()

hoy = datetime.today()
MESES = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",
         7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"}

with st.sidebar:
    st.title("💊 DCFarma")
    st.caption("Contabilidad SaaS · " + hoy.strftime("%d/%m/%Y"))
    st.markdown("---")
    vista = st.radio("Vista", ["📊 Dashboard","🛒 Compras","📋 Gastos",
                                "💰 Ingresos Servicios","🤝 Ingresos Alliance","🏦 Banco",
                                "📅 Forecast"],
                     label_visibility="collapsed")
    st.markdown("---")
    anios_set = set()
    for _df in [df_compras, df_gastos, df_servicios, df_alliance]:
        if not _df.empty and "ANO" in _df.columns:
            anios_set.update([int(a) for a in _df["ANO"].dropna().unique()])
    anios = sorted(anios_set, reverse=True) or [hoy.year]
    anio_sel = st.selectbox("Año", anios, index=0)
    st.markdown("<p style='font-size:0.75rem;color:#aaa;margin-bottom:4px'>Mes(es)</p>", unsafe_allow_html=True)
    meses_def = list(range(1, min(hoy.month+1,13))) if int(anio_sel)==hoy.year else list(range(1,13))
    if "mes_sel" not in st.session_state:
        st.session_state["mes_sel"] = meses_def
    col_a, col_b = st.columns(2)
    if col_a.button("Todos", use_container_width=True, key="mes_todos"):
        st.session_state["mes_sel"] = list(range(1,13))
        st.rerun()
    if col_b.button("Ninguno", use_container_width=True, key="mes_ninguno"):
        st.session_state["mes_sel"] = []
        st.rerun()
    mes_sel = []
    for m in range(1, 13):
        checked = m in st.session_state["mes_sel"]
        val = st.checkbox(MESES[m], value=checked, key=f"mes_cb_{m}")
        if val:
            mes_sel.append(m)
    st.session_state["mes_sel"] = mes_sel
    st.markdown("---")
    if st.button("🔄 Actualizar datos", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

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

if vista == "📊 Dashboard":
    st.header("Panel de Control")
    fc=filtrar(df_compras); fg=filtrar(df_gastos)
    fsi=filtrar(df_servicios); fal=filtrar(df_alliance)
    def s(df): return df["BASE_IMPONIBLE"].sum() if not df.empty and "BASE_IMPONIBLE" in df.columns else 0
    tc=s(fc); tg=s(fg); tsi=s(fsi); tal=s(fal)
    ti=tsi+tal; tga=tc+tg; res=ti-tga

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("💰 Ingresos Totales", fmtk(ti), help="Servicios + Alliance")
    c2.metric("🛒 Compras", fmtk(tc))
    c3.metric("📋 Gastos", fmtk(tg))
    c4.metric("📈 Resultado", fmtk(res), delta=fmtk(res))

    st.markdown("---")
    d1,d2,d3,d4 = st.columns(4)
    d1.metric("Ingresos Servicios", fmtk(tsi))
    d2.metric("Ingresos Alliance", fmtk(tal))
    d3.metric("Total Gastos", fmtk(tga))
    d4.metric("Saldo Banco", fmtk(saldo_banco))

    st.markdown("---")
    st.subheader("Evolución mensual")
    meses_c=list(range(1,13)); lm=[MESES[m][:3] for m in meses_c]
    def ms(df):
        if df is None or df.empty or "MES" not in df.columns or "BASE_IMPONIBLE" not in df.columns: return [0]*12
        return [df[(df["ANO"]==int(anio_sel))&(df["MES"]==m)]["BASE_IMPONIBLE"].sum()
                if "ANO" in df.columns else df[df["MES"]==m]["BASE_IMPONIBLE"].sum() for m in meses_c]
    fig=go.Figure()
    fig.add_trace(go.Bar(name="Servicios",x=lm,y=ms(df_servicios),marker_color="#2ecc71"))
    fig.add_trace(go.Bar(name="Alliance",x=lm,y=ms(df_alliance),marker_color="#27ae60"))
    fig.add_trace(go.Bar(name="Compras",x=lm,y=ms(df_compras),marker_color="#3498db"))
    fig.add_trace(go.Bar(name="Gastos",x=lm,y=ms(df_gastos),marker_color="#e67e22"))
    fig.update_layout(barmode="group",height=380,margin=dict(l=0,r=0,t=30,b=0),
                      plot_bgcolor="white",paper_bgcolor="white",
                      legend=dict(orientation="h",yanchor="bottom",y=1.02,x=0),
                      yaxis=dict(showgrid=True,gridcolor="#f0f0f0"))
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

elif vista == "🛒 Compras":
    st.header("🛒 Compras")
    fc=filtrar(df_compras)
    total=fc["BASE_IMPONIBLE"].sum() if not fc.empty and "BASE_IMPONIBLE" in fc.columns else 0
    st.metric("Total Base Imponible", fmtk(total))
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
        st.dataframe(show.loc[:,~show.columns.duplicated()], use_container_width=True, hide_index=True)
    else: st.info("Sin datos para el periodo seleccionado")

elif vista == "📋 Gastos":
    st.header("📋 Gastos")
    fg=filtrar(df_gastos)
    total=fg["BASE_IMPONIBLE"].sum() if not fg.empty and "BASE_IMPONIBLE" in fg.columns else 0
    st.metric("Total Base Imponible", fmtk(total))
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
        st.dataframe(show.loc[:,~show.columns.duplicated()], use_container_width=True, hide_index=True)
    else: st.info("Sin datos para el periodo seleccionado")

elif vista == "💰 Ingresos Servicios":
    st.header("💰 Ingresos Servicios")
    fsi=filtrar(df_servicios)
    total=fsi["BASE_IMPONIBLE"].sum() if not fsi.empty and "BASE_IMPONIBLE" in fsi.columns else 0
    st.metric("Total Base Imponible", fmtk(total))
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
        st.dataframe(show.loc[:,~show.columns.duplicated()], use_container_width=True, hide_index=True)
    else: st.info("Sin datos para el periodo seleccionado")

elif vista == "🤝 Ingresos Alliance":
    st.header("🤝 Ingresos Alliance")
    fal=filtrar(df_alliance)
    total=fal["BASE_IMPONIBLE"].sum() if not fal.empty and "BASE_IMPONIBLE" in fal.columns else 0
    st.metric("Total Base Imponible", fmtk(total))
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
        st.dataframe(show.loc[:,~show.columns.duplicated()], use_container_width=True, hide_index=True)
    else: st.info("Sin datos para el periodo seleccionado")

elif vista == "🏦 Banco":
    st.header("🏦 Banco · Santander")
    st.metric("Saldo Actual", fmtk(saldo_banco))
    fb=filtrar(df_banco)
    if not fb.empty:
        st.dataframe(fb.loc[:,~fb.columns.duplicated()], use_container_width=True, hide_index=True)
    else: st.info("Sin movimientos para el periodo seleccionado")

elif vista == "📅 Forecast":
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

        k1,k2,k3,k4 = st.columns(4)
        k1.metric("🏦 Saldo Banco Hoy",      fmtk(saldo_banco))
        k2.metric("💰 Cobros pendientes",     fmtk(cobros_pend))
        k3.metric("💸 Pagos pendientes",      fmtk(abs(pagos_pend)))
        k4.metric("📊 Saldo estimado 60d",    fmtk(saldo_fin),
                  delta=fmtk(saldo_fin - float(saldo_banco)),
                  delta_color="normal")

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
        for fecha in fechas_unicas:
            movs = df_ev[df_ev["Fecha"]==fecha]["Importe"].sum()
            saldo_acum += movs
            timeline_fechas.append(fecha)
            timeline_saldos.append(saldo_acum)
        # añadir punto final en día 60
        if fin_fc not in timeline_fechas:
            timeline_fechas.append(fin_fc)
            timeline_saldos.append(saldo_acum)

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
                customdata=cobros_df[["Contraparte","Estado","Origen"]].values,
                hovertemplate="<b>%{customdata[0]}</b><br>%{x}<br>+%{text}<br>%{customdata[1]} · %{customdata[2]}<extra></extra>",
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
                customdata=pagos_df[["Contraparte","Estado","Origen"]].values,
                hovertemplate="<b>%{customdata[0]}</b><br>%{x}<br>-%{text}<br>%{customdata[1]} · %{customdata[2]}<extra></extra>",
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

st.set_page_config(page_title='DCFarma Contabilidad', page_icon='💊', layout='wide')

USERS = {'Admin': '12341234Aa$$'}

def check_login():
    if st.session_state.get('authenticated'):
        return True
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.markdown('## 🔐 DCFarma')
        with st.form('login_form'):
            user = st.text_input('Usuario')
            pwd = st.text_input('Contraseña', type='password')
            ok = st.form_submit_button('Entrar', use_container_width=True)
            if ok:
                if user in USERS and USERS[user] == pwd:
                    st.session_state['authenticated'] = True
                    st.session_state['username'] = user
                    st.rerun()
                else:
                    st.error('Usuario o contraseña incorrectos')
    return False

if not check_login():
    st.stop()

        fig.add_vline(x=hoy_ts, line_dash="dash", line_color="#95a5a6", line_width=1,
                      annotation_text="Hoy", annotation_position="top right")

        fig.update_layout(
            height=450, margin=dict(l=0,r=0,t=30,b=0),
            plot_bgcolor="white", paper_bgcolor="white",
            hovermode="x unified",
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
