import streamlit as st
import pandas as pd
from datetime import datetime
import os
import csv

st.set_page_config(
    page_title="PANINI 2026 · ALBUM DIGITAL",
    layout="wide",
    initial_sidebar_state="expanded"
)

C = {
    "bg_deep":   "#06090f", "bg_panel": "#0c1220", "bg_card":  "#101828",
    "bg_input":  "#080e1a", "gold_hi":  "#ffd700", "gold_lo":  "#c9960c",
    "gold_glow": "#ffe566", "cyan":      "#00d4ff", "green_hi": "#05d68a",
    "green_bg":  "#021a0e", "red_hi":   "#ff4060", "red_bg":   "#1a0008",
    "text_hi":   "#ddeeff", "text_mid": "#7a9ec0", "text_dim": "#354a61",
    "border":    "#1c3352", "sep":      "#111d30", "row_alt":  "#0b1522",
}

HEADERS   = ["ID", "NOMBRE / DESC", "SECCION", "POSICION", "ESTADO", "REPE", "CANTIDAD_REPES", "ID SECCION"]
FILE_NAME = "AlbumVirtual_Mundial_2026.csv"
LOG_FILE  = "registro.csv"

g_hi  = C["gold_hi"];  g_lo  = C["gold_lo"];  g_gl  = C["gold_glow"]
bg_d  = C["bg_deep"];  bg_p  = C["bg_panel"]; bg_c  = C["bg_card"]
bd    = C["border"];   t_hi  = C["text_hi"];  t_mid = C["text_mid"]
t_dim = C["text_dim"]; cyan  = C["cyan"];     r_hi  = C["red_hi"]
gr_hi = C["green_hi"]; sep   = C["sep"]

st.markdown(f"""
<style>
.stApp {{
    background-color: {bg_d};
    color: {t_hi};
    font-family: "Segoe UI", sans-serif;
}}
[data-testid="stSidebar"] {{
    background-color: {bg_p};
    border-right: 1px solid {bd};
}}
[data-testid="stSidebar"] * {{ color: {t_hi} !important; }}

div.stDownloadButton > button {{
    background: linear-gradient(135deg, {g_hi}, {g_lo}) !important;
    color: {bg_d} !important;
    font-family: "Segoe UI Semibold", sans-serif;
    font-size: 13px; font-weight: bold; border: none;
    border-radius: 6px; padding: 7px 18px;
    box-shadow: 0 0 8px {g_hi}33;
    transition: all .2s ease-in-out; width: 100%;
}}
div.stDownloadButton > button:hover {{
    background: {g_gl} !important;
    box-shadow: 0 0 15px {g_gl}aa !important;
    transform: scale(1.02);
}}
.stButton>button {{
    background-color: {bg_c} !important;
    color: {t_hi} !important;
    border: 1px solid {bd} !important;
    border-radius: 6px; padding: 6px 14px;
    transition: all .2s; width: 100%;
}}
.stButton>button:hover {{
    border-color: {cyan} !important;
    color: {cyan} !important;
}}
div[data-testid="stDataEditor"] {{
    background-color: {bg_c};
    border: 1px solid {bd};
    border-radius: 8px;
    font-family: "Consolas", monospace;
    font-size: 14px;
}}
div[data-testid="stDataEditor"] th {{
    background-color: {bg_p} !important;
    color: {g_hi} !important;
    font-family: "Segoe UI Semibold", sans-serif !important;
    font-size: 13px !important;
    border-bottom: 2px solid {bd} !important;
}}
div[data-testid="stDataEditor"] td {{
    background-color: {bg_c} !important;
    color: {t_hi} !important;
    border-bottom: 1px solid {sep} !important;
}}
div[data-testid="stSelectbox"] > div,
div[data-testid="stTextInput"] > div > div {{
    background-color: {C["bg_input"]} !important;
    border: 1px solid {bd} !important;
    border-radius: 6px !important;
    color: {t_hi} !important;
}}
div[data-testid="stProgress"] > div > div {{
    background-color: {gr_hi} !important;
}}
details summary {{
    color: {cyan} !important;
    font-family: "Consolas", monospace;
    font-size: 12px;
}}
.sobre-panel {{
    background: {bg_p};
    border: 1px solid {cyan};
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 16px;
}}
::-webkit-scrollbar {{ width: 10px; height: 10px; }}
::-webkit-scrollbar-track {{ background: {bg_d}; }}
::-webkit-scrollbar-thumb {{
    background: {bg_p};
    border: 2px solid {bg_d};
    border-radius: 4px;
}}
.footer {{
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background-color: {bg_p};
    border-top: 1px solid {bd};
    padding: 8px 24px;
    text-align: center;
    z-index: 9999;
    font-family: "Consolas", monospace;
    font-size: 11px;
    color: {t_dim};
}}
.footer span.brand {{
    color: {g_hi};
    font-weight: bold;
    letter-spacing: 1px;
}}
.footer span.sep {{
    color: {bd};
    margin: 0 10px;
}}
</style>
""", unsafe_allow_html=True)

DEFAULTS = {
    "full_data":        pd.DataFrame(columns=HEADERS),
    "cat_filter":       "TODOS",
    "logs":             [],
    "show_sobre":       False,
    "data_loaded":      False,
    "lista_secciones":  ["TODAS"],
    "lista_posiciones": ["TODAS"],
    "last_uploaded":    None
}
for _k, _v in DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


def add_log_entry(accion: str, detalle: str):
    ahora = datetime.now()
    entry = {
        "FECHA":   ahora.strftime("%Y-%m-%d"),
        "HORA":    ahora.strftime("%H:%M:%S"),
        "ACCION":  accion,
        "DETALLE": detalle,
    }
    st.session_state.logs.insert(0, entry)
    try:
        file_exists = os.path.isfile(LOG_FILE)
        with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if not file_exists:
                w.writerow(["FECHA", "HORA", "ACCION", "DETALLE"])
            w.writerow([entry["FECHA"], entry["HORA"], accion, detalle])
    except Exception:
        pass


def load_data():
    if st.session_state.full_data.empty:
        st.session_state.full_data        = pd.DataFrame(columns=HEADERS)
        st.session_state.lista_secciones  = ["TODAS"]
        st.session_state.lista_posiciones = ["TODAS"]


def get_csv_download_data():
    df     = st.session_state.full_data
    output = csv.StringIO()
    w      = csv.DictWriter(output, fieldnames=HEADERS, delimiter=";")
    w.writeheader()
    for _, row in df.iterrows():
        r           = dict(row)
        r["ESTADO"] = "TENGO" if r["ESTADO"] else "FALTA"
        r["REPE"]   = "SI"    if r["REPE"]   else "NO"
        w.writerow(r)
    return output.getvalue().encode("utf-8-sig")


def get_filtered_df() -> pd.DataFrame:
    df  = st.session_state.full_data.copy()
    if df.empty:
        return df

    q   = st.session_state.get("search_input",    "").strip().lower()
    sf  = st.session_state.get("filter_seccion",  "TODAS")
    pf  = st.session_state.get("filter_posicion", "TODAS")
    cat = st.session_state.cat_filter

    if q:
        mask = (
            df["ID"].str.lower().str.contains(q, na=False)
            | df["NOMBRE / DESC"].str.lower().str.contains(q, na=False)
            | df["SECCION"].str.lower().str.contains(q, na=False)
            | df["POSICION"].str.lower().str.contains(q, na=False)
        )
        df = df[mask]

    if sf and sf not in ("TODAS", ""):
        df = df[df["SECCION"].str.strip() == sf.strip()]

    if pf and pf not in ("TODAS", ""):
        df = df[df["POSICION"].str.strip() == pf.strip()]

    if cat == "FALTAN":
        df = df[~df["ESTADO"]]
    elif cat == "REPES":
        df = df[df["REPE"]]

    return df


def handle_click(original_df: pd.DataFrame, edited_df: pd.DataFrame) -> bool:
    full    = st.session_state.full_data
    changed = False
    orig_r  = original_df.reset_index(drop=True)
    edit_r  = edited_df.reset_index(drop=True)

    for i in range(len(orig_r)):
        o    = orig_r.iloc[i]
        e    = edit_r.iloc[i]
        mask = full["ID"] == o["ID"]
        if not mask.any():
            continue
        fi     = full[mask].index[0]
        nombre = full.at[fi, "NOMBRE / DESC"]

        o_estado, e_estado = bool(o["ESTADO"]), bool(e["ESTADO"])
        if o_estado != e_estado:
            full.at[fi, "ESTADO"] = e_estado
            if e_estado:
                add_log_entry("CONSEGUIDO", f"Anadido {nombre}")
            else:
                full.at[fi, "REPE"]           = False
                full.at[fi, "CANTIDAD_REPES"]  = 0
                add_log_entry("ELIMINADO", f"Quitado {nombre} (Reset repes)")
            changed = True

        o_repe, e_repe = bool(o["REPE"]), bool(e["REPE"])
        if o_repe != e_repe:
            if full.at[fi, "ESTADO"]:
                full.at[fi, "REPE"] = e_repe
                if not e_repe:
                    full.at[fi, "CANTIDAD_REPES"] = 0
                add_log_entry("ESTADO REPE", f"{nombre} -> {'SI' if e_repe else 'NO'}")
                changed = True
            else:
                st.toast("⚠️ No puedes tener repes de un cromo que no tienes.", icon="⚠️")

        try:
            o_qty = int(o["CANTIDAD_REPES"])
            e_qty = int(e["CANTIDAD_REPES"])
        except (ValueError, TypeError):
            continue

        if o_qty != e_qty:
            if full.at[fi, "ESTADO"] and full.at[fi, "REPE"]:
                new_q = max(0, e_qty)
                full.at[fi, "CANTIDAD_REPES"] = new_q
                add_log_entry("CANTIDAD", f"{nombre}: {o_qty} -> {new_q}")
                changed = True
            else:
                st.toast("⚠️ Activa primero REPE en SI para este cromo.", icon="⚠️")

    st.session_state.full_data = full
    return changed


def set_cat_filter(f_type: str):
    st.session_state.cat_filter = f_type


def update_stats():
    df_all = st.session_state.full_data
    total  = len(df_all)
    tengo  = int(df_all["ESTADO"].sum()) if total > 0 else 0
    pct    = tengo / total if total > 0 else 0.0
    return total, tengo, total - tengo, pct


def procesar_sobre(lista_ids: list) -> list:
    full    = st.session_state.full_data
    resumen = []
    ahora   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for p_id in lista_ids:
        p_id_norm = str(p_id).zfill(3)
        if p_id_norm in ("082", "083"):
            continue
        mask = full["ID"] == p_id_norm
        if not mask.any():
            continue
        fi     = full[mask].index[0]
        nombre = full.at[fi, "NOMBRE / DESC"]

        if not full.at[fi, "ESTADO"]:
            full.at[fi, "ESTADO"] = True
            resumen.append(f"✨ {p_id_norm} - {nombre} (NUEVO)")
            add_log_entry("SOBRE", f"NUEVO: {p_id_norm} - {nombre}")
        else:
            actual = int(full.at[fi, "CANTIDAD_REPES"])
            full.at[fi, "REPE"]           = True
            full.at[fi, "CANTIDAD_REPES"]  = actual + 1
            resumen.append(f"🔁 {p_id_norm} - {nombre} (REPE x{actual + 1})")
            add_log_entry("SOBRE", f"REPE: {p_id_norm} - {nombre} (Total: {actual+1})")

    try:
        with open("historico_sobres.txt", "a", encoding="utf-8") as f:
            short = [s.split(" - ")[0].lstrip("✨🔁 ") for s in resumen]
            f.write(f"[{ahora}] {', '.join(short)}\n")
    except Exception:
        pass

    st.session_state.full_data = full
    return resumen


# Carga inicial
if not st.session_state.data_loaded:
    load_data()
    st.session_state.data_loaded = True

# Header
st.markdown("### ⚽")
st.title("MUNDIAL 2026 · ALBUM DIGITAL")
st.markdown(
    f"<p style='color:{t_mid};font-family:Consolas;margin-top:-15px;'>"
    "P A N I N I   C O L L E C T I O N   T R A C K E R</p>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<hr style='border:1px solid {g_lo};margin:5px 0 20px;'>",
    unsafe_allow_html=True,
)

# Sidebar
with st.sidebar:
    st.markdown(
        f"<h3 style='color:{g_hi};font-family:\"Segoe UI Semibold\",sans-serif;'>"
        "FILTROS DE BUSQUEDA</h3>",
        unsafe_allow_html=True,
    )

    st.text_input(
        "📝 JUGADOR / NOMBRE / ID",
        placeholder="Escribe para buscar...",
        key="search_input",
    )

    secciones  = st.session_state.lista_secciones
    posiciones = st.session_state.lista_posiciones

    sec_idx = 0
    if st.session_state.get("filter_seccion") in secciones:
        sec_idx = secciones.index(st.session_state["filter_seccion"])

    pos_idx = 0
    if st.session_state.get("filter_posicion") in posiciones:
        pos_idx = posiciones.index(st.session_state["filter_posicion"])

    st.selectbox("🗂️ SECCION",  secciones,  index=sec_idx, key="filter_seccion")
    st.selectbox("🎯 POSICION", posiciones, index=pos_idx, key="filter_posicion")

    st.markdown("---")
    total, tengo, faltan, pct = update_stats()
    st.markdown(
        f"<p style='color:{t_mid};font-family:Consolas;font-size:13px;margin-bottom:4px;'>"
        f"⚽ {tengo} / {total} CONSEGUIDOS · {faltan} FALTAN</p>",
        unsafe_allow_html=True,
    )
    st.progress(pct, text=f"{pct*100:.1f}%")

    st.markdown("---")
    st.markdown(
        f"<p style='color:{t_dim};font-size:12px;'>📁 CONFIGURACION DE TU ALBUM</p>",
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader("📂 CARGAR CSV", type=["csv"], label_visibility="collapsed")

    if uploaded is not None and st.session_state.last_uploaded != uploaded.name:
        try:
            raw_bytes = uploaded.read()
            try:
                decoded_file = raw_bytes.decode("utf-8-sig").splitlines()
                if len(decoded_file) > 0 and ";" not in decoded_file[0] and "," in decoded_file[0]:
                    raise ValueError()
            except Exception:
                decoded_file = raw_bytes.decode("latin-1").splitlines()

            reader      = csv.reader(decoded_file, delimiter=";")
            raw_headers = [h.strip().upper() for h in next(reader, None)]

            idx_id    = raw_headers.index("ID") if "ID" in raw_headers else 0
            idx_nom   = raw_headers.index("NOMBRE / DESC") if "NOMBRE / DESC" in raw_headers else 1
            idx_sec   = [i for i, h in enumerate(raw_headers) if "SEC" in h][0]
            idx_pos   = [i for i, h in enumerate(raw_headers) if "POS" in h][0]
            idx_est   = [i for i, h in enumerate(raw_headers) if "EST" in h][0]
            idx_rep   = [i for i, h in enumerate(raw_headers) if "REP" in h and "CANT" not in h][0]
            idx_cant  = [i for i, h in enumerate(raw_headers) if "CANT" in h][0]
            idx_idsec = [i for i, h in enumerate(raw_headers) if "ID SEC" in h or "ID_SEC" in h or h == raw_headers[-1]][0]

            rows, sec_set, pos_set = [], set(), set()
            for r in reader:
                if not r or len(r) < 4:
                    continue
                if len(r) < len(raw_headers):
                    r += [""] * (len(raw_headers) - len(r))
                sec_val  = r[idx_sec].strip()
                pos_val  = r[idx_pos].strip()
                est_val  = r[idx_est].strip().upper()
                rep_val  = r[idx_rep].strip().upper()
                cant_val = r[idx_cant].strip()

                v = {
                    "ID":             r[idx_id].strip().zfill(3),
                    "NOMBRE / DESC":  r[idx_nom].strip(),
                    "SECCION":        sec_val,
                    "POSICION":       pos_val,
                    "ESTADO":         "TENGO" in est_val or "✓" in est_val or est_val == "TRUE",
                    "REPE":           rep_val in ("SI", "SÍ") or rep_val == "TRUE",
                    "CANTIDAD_REPES": int(cant_val) if cant_val.isdigit() else 0,
                    "ID SECCION":     r[idx_idsec].strip()
                }
                rows.append(v)
                if v["SECCION"]: sec_set.add(v["SECCION"])
                if v["POSICION"]: pos_set.add(v["POSICION"])

            df                    = pd.DataFrame(rows, columns=HEADERS)
            df["ESTADO"]          = df["ESTADO"].astype(bool)
            df["REPE"]            = df["REPE"].astype(bool)
            df["CANTIDAD_REPES"]  = df["CANTIDAD_REPES"].astype(int)

            st.session_state.full_data        = df
            st.session_state.lista_secciones  = ["TODAS"] + sorted([s for s in sec_set if s])
            st.session_state.lista_posiciones = ["TODAS"] + sorted([p for p in pos_set if p])
            st.session_state.last_uploaded    = uploaded.name
            add_log_entry("SISTEMA", f"CSV cargado: {len(df)} cromos")
            st.rerun()
        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")

    if not st.session_state.full_data.empty:
        csv_data = get_csv_download_data()

        st.markdown("⚠️ **¡AVISO IMPORTANTE!**")
        st.markdown(
            f"<p style='color:{t_mid};font-size:12px;margin-top:-10px;'>"
            "Para elegir donde guardar el archivo y poder machacar el viejo en tu Escritorio de golpe, "
            "activa esto en tu navegador:</p>",
            unsafe_allow_html=True
        )

        with st.expander("🌐 Activar reemplazo en Chrome / Edge"):
            st.markdown(
                "1. Entra en **Configuracion** del navegador (los 3 puntos arriba a la derecha).\n"
                "2. Ve a **Descargas** (menú izquierdo).\n"
                "3. Activa: **'Preguntar donde se guardara cada archivo antes de descargarlo'**."
            )

        st.markdown("<br>", unsafe_allow_html=True)

        st.download_button(
            label="💾 DESCARGAR CSV MODIFICADO",
            data=csv_data,
            file_name="AlbumVirtual_Mundial_2026.csv",
            mime="text/csv",
            key="btn_download_premium"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 REINICIAR APP", key="btn_reload_clean"):
            st.session_state.full_data        = pd.DataFrame(columns=HEADERS)
            st.session_state.lista_secciones  = ["TODAS"]
            st.session_state.lista_posiciones = ["TODAS"]
            st.session_state.last_uploaded    = None
            st.rerun()

    LOG_COLORS = {
        "CONSEGUIDO": gr_hi, "ELIMINADO": r_hi, "SOBRE": cyan,
        "GUARDADO":   g_hi,  "SISTEMA":  t_mid,
    }
    with st.expander("📜 ACTIVITY LOG · LIVE", expanded=False):
        if st.session_state.logs:
            for entry in st.session_state.logs[:60]:
                color = LOG_COLORS.get(entry["ACCION"], "#00ff88")
                st.markdown(
                    f"<p style='color:{color};font-family:Consolas;"
                    f"font-size:11px;margin:2px 0;'>"
                    f"[{entry['HORA']}] <b>{entry['ACCION']}</b>"
                    f" — {entry['DETALLE']}</p>",
                    unsafe_allow_html=True,
                )
        else:
            st.caption("Sin actividad registrada.")

# Botones filtro + sobre
c1, c2, c3, _spacer, c_sobre = st.columns([1.2, 1.2, 1.2, 3.5, 2])

CAT_ACTIVE = st.session_state.cat_filter

def _cat_label(name):
    return f"▶ {name}" if CAT_ACTIVE == name else name

with c1:
    if st.button(_cat_label("TODOS"),  key="btn_todos"):
        set_cat_filter("TODOS");  st.rerun()
with c2:
    if st.button(_cat_label("FALTAN"), key="btn_faltan"):
        set_cat_filter("FALTAN"); st.rerun()
with c3:
    if st.button(_cat_label("REPES"),  key="btn_repes"):
        set_cat_filter("REPES");  st.rerun()
with c_sobre:
    sobre_label = "🔒 CERRAR SOBRE" if st.session_state.show_sobre else "✨ ABRIR SOBRE"
    if st.button(sobre_label, key="btn_sobre"):
        st.session_state.show_sobre = not st.session_state.show_sobre
        st.rerun()

CAT_BADGE_COLOR = {"TODOS": g_hi, "FALTAN": r_hi, "REPES": cyan}
st.markdown(
    f"<p style='color:{CAT_BADGE_COLOR[CAT_ACTIVE]};"
    f"font-family:Consolas;font-size:12px;margin-bottom:8px;'>"
    f"▶ FILTRO ACTIVO: {CAT_ACTIVE}</p>",
    unsafe_allow_html=True,
)

# Panel sobre
if st.session_state.show_sobre:
    st.markdown(
        f"<div class='sobre-panel'>"
        f"<h3 style='color:{g_hi};margin-top:0;'>"
        "✨ PACK OPENING · SELECCIONA LOS 7 CROMOS DEL SOBRE</h3>"
        f"<p style='color:{t_mid};font-family:Consolas;font-size:12px;margin-top:-10px;'>"
        "Escribe nombre o ID en cada hueco para filtrar</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    opciones_busqueda = [""] + [
        f"{row['ID']} - {row['NOMBRE / DESC']}"
        for _, row in st.session_state.full_data.iterrows()
    ]

    selected_ids = []
    row1_cols    = st.columns(4)
    row2_cols    = st.columns(4)
    all_slots    = row1_cols + row2_cols

    for i in range(7):
        with all_slots[i]:
            st.markdown(
                f"<p style='color:{g_lo};font-family:Consolas;"
                f"font-size:11px;margin-bottom:2px;'>#{i+1}</p>",
                unsafe_allow_html=True,
            )
            val = st.selectbox(
                f"slot_{i}",
                opciones_busqueda,
                key=f"sobre_slot_{i}",
                label_visibility="collapsed",
            )
            if val and " - " in val:
                selected_ids.append(val.split(" - ")[0])

    st.markdown("<br>", unsafe_allow_html=True)
    btn_ok, btn_cancel, _ = st.columns([2.5, 2, 5.5])

    with btn_ok:
        if st.button("✅  REGISTRAR SOBRE COMPLETO", key="btn_confirmar_sobre"):
            if selected_ids:
                resumen = procesar_sobre(selected_ids)
                st.session_state.show_sobre = False
                for line in resumen:
                    st.success(line)
                st.rerun()
            else:
                st.warning("No has seleccionado ningun cromo valido.")
    with btn_cancel:
        if st.button("❌  CANCELAR", key="btn_cancel_sobre"):
            st.session_state.show_sobre = False
            st.rerun()

    st.markdown(
        f"<hr style='border:1px solid {bd};margin:16px 0 8px;'>",
        unsafe_allow_html=True,
    )

# Tabla principal
filtered_df = get_filtered_df()
st.markdown(
    f"<p style='color:{t_dim};font-size:12px;margin-bottom:4px;'>"
    f"Mostrando <b style='color:{t_mid};'>{len(filtered_df)}</b> cromos</p>",
    unsafe_allow_html=True,
)

if filtered_df.empty:
    st.info("No hay cromos que coincidan con los filtros activos o el album esta vacio. Sube tu CSV en la barra lateral para empezar.")
else:
    with st.form("contenedor_rapido"):
        edited = st.data_editor(
            filtered_df,
            column_config={},
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
        )
        guardar_tabla = st.form_submit_button("⚡ ACEPTAR CAMBIOS EN TABLA")

    if guardar_tabla:
        if handle_click(filtered_df, edited):
            st.toast("⚡ Cambios aplicados. ¡Pulsa el boton dorado de la barra lateral para bajar tu CSV!", icon="ℹ️")
            st.rerun()

# Footer
st.markdown(
    f"""
    <div class="footer">
        <span class="brand">FERNANDO ROMERO MORENO ®</span>
        <span class="sep">|</span>
        Panini 2026 · Album Digital
        <span class="sep">|</span>
        © {datetime.now().year} · Todos los derechos reservados
        <span class="sep">|</span>
    </div>
    """,
    unsafe_allow_html=True,
)
