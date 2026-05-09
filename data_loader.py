import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly",
          "https://www.googleapis.com/auth/drive.readonly"]
SHEET1_ID = "19M7oCB5q44prrYUivHNH5kc30vA3oleJcAWPLMQb0Cs"
SHEET2_ID = "1uZQkGLkOO1BP1BSFQ8K7KrxQJVV2JZWSbTEVH1GK0hs"

def get_client():
    try:
        import streamlit as st
        if "gcp_service_account" in st.secrets:
            import json
            info = dict(st.secrets["gcp_service_account"])
            creds = Credentials.from_service_account_info(info, scopes=SCOPES)
            return gspread.authorize(creds)
    except Exception:
        pass
    creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    return gspread.authorize(creds)

def safe_float(val):
    if val is None or str(val).strip() == "": return 0.0
    s = str(val).replace(" ","").replace(".","").replace(",",".").replace("€","").strip()
    try: return float(s)
    except: return 0.0

def safe_date(val):
    if val is None or str(val).strip() == "": return pd.NaT
    s = str(val).strip()
    for fmt in ["%d/%m/%Y","%Y-%m-%d","%d-%m-%Y","%d/%m/%y"]:
        try: return pd.to_datetime(s, format=fmt)
        except: pass
    return pd.NaT

def add_mes_anio(df, date_col):
    if date_col in df.columns:
        df["MES"] = df[date_col].apply(lambda x: x.month if pd.notna(x) else None)
        df["ANO"] = df[date_col].apply(lambda x: x.year if pd.notna(x) else None)
    return df

def load_compras():
    gc = get_client()
    ss = gc.open_by_key(SHEET1_ID)
    frames = []
    for sname in ["COMPRAS 2026","COMPRAS 2025"]:
        try:
            raw = ss.worksheet(sname).get_all_values()
            if len(raw) < 2: continue
            rows = []
            for row in raw[1:]:
                while len(row) < 15: row.append("")
                lab=row[0]; farm=row[1]; alb=row[3]; fac=row[5]
                base=safe_float(row[8])
                ff=safe_date(row[10]); fv=safe_date(row[11]); fp=safe_date(row[14])
                if lab.strip()=="" and base==0.0: continue
                rows.append({"LABORATORIO":lab,"FARMACIA":farm,"NUM_ALBARAN":alb,
                             "NUM_FACTURA":fac,"BASE_IMPONIBLE":base,
                             "FECHA_FACTURA":ff,"FECHA_VTO":fv,"FECHA_PAGO":fp})
            df = pd.DataFrame(rows)
            if not df.empty:
                df = add_mes_anio(df,"FECHA_FACTURA")
                frames.append(df)
        except Exception as e: print(f"Error {sname}: {e}")
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

def load_gastos():
    gc = get_client()
    ss = gc.open_by_key(SHEET1_ID)
    frames = []
    for sname in ["GASTOS 2026","GASTOS 2025"]:
        try:
            raw = ss.worksheet(sname).get_all_values()
            if len(raw) < 2: continue
            rows = []
            for row in raw[1:]:
                while len(row) < 9: row.append("")
                ff=safe_date(row[0]); lab=row[1]; reg=row[2]
                nfac=row[3]; base=safe_float(row[4])
                fv=safe_date(row[6]); fp=safe_date(row[8])
                if lab.strip()=="" and base==0.0: continue
                rows.append({"FECHA_FACTURA":ff,"LABORATORIO":lab,"REGISTRO_FACTURA":reg,
                             "NUM_FACTURA":nfac,"BASE_IMPONIBLE":base,
                             "FECHA_VTO":fv,"FECHA_PAGO":fp})
            df = pd.DataFrame(rows)
            if not df.empty:
                df = add_mes_anio(df,"FECHA_FACTURA")
                frames.append(df)
        except Exception as e: print(f"Error {sname}: {e}")
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

def load_ingresos_servicios():
    gc = get_client()
    ss = gc.open_by_key(SHEET2_ID)
    try:
        raw = ss.worksheet("remesas").get_all_values()
        if len(raw) < 2: return pd.DataFrame()
        rows = []
        for row in raw[1:]:
            while len(row) < 10: row.append("")
            ff = safe_date(row[7])
            if pd.isna(ff): continue
            desc=row[0]; nfac=row[1]; base=safe_float(row[2])
            cli=row[4]; fv=safe_date(row[8]); fc=safe_date(row[9])
            rows.append({"DESCRIPCION":desc,"NUM_FACTURA":nfac,"BASE_IMPONIBLE":base,
                         "CLIENTE":cli,"FECHA_FACTURA":ff,"FECHA_VTO":fv,"FECHA_COBRO":fc})
        df = pd.DataFrame(rows)
        if not df.empty: df = add_mes_anio(df,"FECHA_FACTURA")
        return df
    except Exception as e:
        print(f"Error remesas: {e}")
        return pd.DataFrame()

def load_ingresos_alliance():
    gc = get_client()
    ss = gc.open_by_key(SHEET2_ID)
    try:
        raw = ss.worksheet("INGRESOS ALLIANCE").get_all_values()
        if len(raw) < 2: return pd.DataFrame()
        rows = []
        for row in raw[1:]:
            while len(row) < 11: row.append("")
            base=safe_float(row[6])
            desc=row[0]; farm=row[1]; obs=row[5]
            ff=safe_date(row[8]); fv=safe_date(row[9]); fc=safe_date(row[10])
            if desc.strip()=="" and base==0.0: continue
            rows.append({"DESCRIPCION":desc,"FARMACIA":farm,"OBSERVACIONES":obs,
                         "BASE_IMPONIBLE":base,"FECHA_FACTURA":ff,
                         "FECHA_VTO":fv,"FECHA_COBRO":fc})
        df = pd.DataFrame(rows)
        if not df.empty: df = add_mes_anio(df,"FECHA_FACTURA")
        return df
    except Exception as e:
        print(f"Error alliance: {e}")
        return pd.DataFrame()

def load_gastos_personal():
    """Devuelve {año: [m1..m12]} con el gasto laboral mensual (valores positivos).
    La hoja tiene formato pivot: fila 'Gastos de personal' es el total,
    columnas C-N son los meses Ene-Dic."""
    gc = get_client()
    ss = gc.open_by_key(SHEET1_ID)
    try:
        raw = ss.worksheet("GASTOS PERSONAL").get_all_values()
        result = {}
        for row in raw[1:]:
            if len(row) < 3: continue
            concepto = row[0].strip()
            if concepto == "": continue
            try:
                year = int(row[1])
            except:
                continue
            monthly = [abs(safe_float(row[i])) if i < len(row) else 0.0 for i in range(2, 14)]
            if concepto == "Gastos de personal":
                result[year] = monthly
        return result
    except Exception as e:
        print(f"Error GASTOS PERSONAL: {e}")
        return {}

def load_banco():
    gc = get_client()
    ss = gc.open_by_key(SHEET2_ID)
    try:
        raw = ss.worksheet("santander").get_all_values()
        if len(raw) < 6: return pd.DataFrame(), 0.0
        headers = raw[4]
        df = pd.DataFrame(raw[5:], columns=headers)
        df.columns = [str(c).strip() for c in df.columns]
        df = df.loc[:,~df.columns.duplicated()]
        saldo_actual = 0.0
        saldo_cols = [c for c in df.columns if "SALDO" in str(c).upper()]
        if saldo_cols:
            for _, row in df.iterrows():
                v = safe_float(row[saldo_cols[0]])
                if v != 0.0: saldo_actual = v; break
        keep = list(df.columns[:6])
        df = df[keep].copy()
        df["MES"] = None; df["ANO"] = None
        date_col = df.columns[0]
        for idx, row in df.iterrows():
            d = safe_date(row[date_col])
            if pd.notna(d):
                df.at[idx,"MES"] = d.month
                df.at[idx,"ANO"] = d.year
        df = df[df[date_col].str.strip() != ""]
        return df, saldo_actual
    except Exception as e:
        print(f"Error santander: {e}")
        return pd.DataFrame(), 0.0
