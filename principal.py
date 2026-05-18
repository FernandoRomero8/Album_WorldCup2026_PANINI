import streamlit as st
import pandas as pd
from datetime import datetime
import os
import csv

st.set_page_config(
    page_title="PANINI 2026 · ÁLBUM DIGITAL",
    layout="wide",
    initial_sidebar_state="expanded"
)

C = {
    "bg_deep":   "#06090f", "bg_panel": "#0c1220", "bg_card":  "#101828",
    "bg_input":  "#080e1a", "gold_hi":  "#ffd700", "gold_lo":  "#c9960c",
    "gold_glow": "#ffe566", "cyan":     "#00d4ff", "green_hi": "#05d68a",
    "green_bg":  "#021a0e", "red_hi":   "#ff4060", "red_bg":   "#1a0008",
    "text_hi":   "#ddeeff", "text_mid": "#7a9ec0", "text_dim": "#354a61",
    "border":    "#1c3352", "sep":      "#111d30", "row_alt":  "#0b1522",
}

HEADERS    = ["ID", "NOMBRE / DESC", "SECCIÓN", "POSICIÓN",
              "ESTADO", "REPE", "CANTIDAD_REPES", "ID SECCIÓN"]
FILE_NAME  = "AlbumVirtual_Mundial_2026.csv"
LOG_FILE   = "registro.csv"

g_hi   = C["gold_hi"];  g_lo  = C["gold_lo"];  g_gl  = C["gold_glow"]
bg_d   = C["bg_deep"];  bg_p  = C["bg_panel"]; bg_c  = C["bg_card"]
bd     = C["border"];   t_hi  = C["text_hi"];  t_mid = C["text_mid"]
t_dim  = C["text_dim"]; cyan  = C["cyan"];     r_hi  = C["red_hi"]
gr_hi  = C["green_hi"]; sep   = C["sep"]

st.markdown(f"""
<style>
/* ── General ── */
.stApp {{
    background-color: {bg_d};
    color: {t_hi};
    font-family: "Segoe UI", sans-serif;
}}
/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background-color: {bg_p};
    border-right: 1px solid {bd};
}}
[data-testid="stSidebar"] * {{ color: {t_hi} !important; }}
/* ── Buttons ── */
.stButton>button {{
    background: linear-gradient(135deg, {g_hi}, {g_lo});
    color: {bg_d} !important;
    font-family: "Segoe UI Semibold", sans-serif;
    font-size: 13px; font-weight: bold; border: none;
    border-radius: 6px; padding: 7px 18px;
    box-shadow: 0 0 8px {g_hi}33;
    transition: all .2s ease-in-out; width: 100%;
}}
.stButton>button:hover {{
    background: {g_gl};
    box-shadow: 0 0 15px {g_gl}aa;
    transform: scale(1.02);
}}
/* ── Data editor ── */
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
/* ── Selectbox / Inputs ── */
div[data-testid="stSelectbox"] > div,
div[data-testid="stTextInput"] > div > div {{
    background-color: {C["bg_input"]} !important;
    border: 1px solid {bd} !important;
    border-radius: 6px !important;
    color: {t_hi} !important;
}}
/* ── Progress bar ── */
div[data-testid="stProgress"] > div > div {{
    background-color: {gr_hi} !important;
}}
/* ── Expander ── */
details summary {{
    color: {cyan} !important;
    font-family: "Consolas", monospace;
    font-size: 12px;
}}
/* ── Pack opening panel ── */
.sobre-panel {{
    background: {bg_p};
    border: 1px solid {cyan};
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 16px;
}}
/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 10px; height: 10px; }}
::-webkit-scrollbar-track {{ background: {bg_d}; }}
::-webkit-scrollbar-thumb {{
    background: {bg_p};
    border: 2px solid {bg_d};
    border-radius: 4px;
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
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not file_exists:
            w.writerow(["FECHA", "HORA", "ACCION", "DETALLE"])
        w.writerow([entry["FECHA"], entry["HORA"], accion, detalle])


def _normalize_col(name: str) -> str:
    """Normaliza un nombre de columna quitando tildes y pasando a mayúsculas."""
    return (
        name.strip().upper()
        .replace("Á", "A").replace("É", "E").replace("Í", "I")
        .replace("Ó", "O").replace("Ú", "U").replace("Ü", "U") )

def load_data():
    if not os.path.exists(FILE_NAME):
        st.session_state.full_data = pd.DataFrame(columns=HEADERS)
        return
    df = None
    for enc in ("utf-8-sig", "latin-1", "utf-8", "cp1252"):
        try:
            df = pd.read_csv(
                FILE_NAME,
                sep=";",
                encoding=enc,
                dtype=str,
                keep_default_na=False,
            )
            # Si la primera columna contiene ";", el separador es distinto
            if len(df.columns) == 1:
                df = pd.read_csv(
                    FILE_NAME,
                    sep=",",
                    encoding=enc,
                    dtype=str,
                    keep_default_na=False,
                )
            break
        except Exception:
            continue

    if df is None or df.empty:
        st.error("❌ No se pudo leer el CSV. Comprueba el formato.")
        st.session_state.full_data = pd.DataFrame(columns=HEADERS)
        return

    # ── 2. Limpiar nombres de columna y hacer matching flexible ───────────────
    df.columns = [c.strip() for c in df.columns]

    # Mapa: nombre_normalizado → nombre_real en el CSV
    csv_col_norm = {_normalize_col(c): c for c in df.columns}

    rename_map = {}
    for h in HEADERS:
        h_norm = _normalize_col(h)
        if h not in df.columns and h_norm in csv_col_norm:
            rename_map[csv_col_norm[h_norm]] = h

    if rename_map:
        df = df.rename(columns=rename_map)

    # Añadir columnas que falten (mejor que fallar)
    for h in HEADERS:
        if h not in df.columns:
            df[h] = ""

    df = df[HEADERS].copy()

    # ── 3. Limpiar valores y convertir tipos ──────────────────────────────────
    # Strip en todas las celdas de texto
    str_cols = ["ID", "NOMBRE / DESC", "SECCIÓN", "POSICIÓN", "ID SECCIÓN"]
    for col in str_cols:
        df[col] = df[col].str.strip()

    # ESTADO → bool
    df["ESTADO"] = df["ESTADO"].str.strip().str.upper().apply(
        lambda x: "TENGO" in x
    )

    # REPE → bool
    df["REPE"] = df["REPE"].str.strip().str.upper().apply(
        lambda x: x == "SI"
    )

    # CANTIDAD_REPES → int
    df["CANTIDAD_REPES"] = (
        pd.to_numeric(df["CANTIDAD_REPES"], errors="coerce")
        .fillna(0)
        .astype(int)
    )

    # ── 4. Construir listas de secciones y posiciones ─────────────────────────
    sec_set = set(df["SECCIÓN"].dropna().unique()) - {""}
    pos_set = set(df["POSICIÓN"].dropna().unique()) - {""}

    st.session_state.full_data        = df
    st.session_state.lista_secciones  = ["TODAS"] + sorted(sec_set)
    st.session_state.lista_posiciones = ["TODAS"] + sorted(pos_set)
    add_log_entry("SISTEMA", f"Datos cargados: {len(df)} cromos · "
                             f"{len(sec_set)} secciones · {len(pos_set)} posiciones")
    
def get_csv_download_data():
    df = st.session_state.full_data
    output = csv.StringIO()
    w = csv.DictWriter(output, fieldnames=HEADERS, delimiter=";")
    w.writeheader()
    for _, row in df.iterrows():
        r = dict(row)
        r["ESTADO"] = "TENGO" if r["ESTADO"] else "FALTA"
        r["REPE"]   = "SI"    if r["REPE"]   else "NO"
        w.writerow(r)
    return output.getvalue()

def get_filtered_df() -> pd.DataFrame:
    df  = st.session_state.full_data.copy()
    if df.empty:
        return df

    q   = st.session_state.get("search_input",    "").strip().lower()
    sf  = st.session_state.get("filter_seccion",  "TODAS")
    pf  = st.session_state.get("filter_posicion", "TODAS")
    cat = st.session_state.cat_filter

    # ── Búsqueda de texto ─────────────────────────────────────────────────────
    if q:
        # Busca en ID, nombre, sección y posición (más rápido que apply completo)
        mask = (
            df["ID"].str.lower().str.contains(q, na=False)
            | df["NOMBRE / DESC"].str.lower().str.contains(q, na=False)
            | df["SECCIÓN"].str.lower().str.contains(q, na=False)
            | df["POSICIÓN"].str.lower().str.contains(q, na=False)
        )
        df = df[mask]

    # ── Filtro sección ────────────────────────────────────────────────────────
    if sf and sf not in ("TODAS", ""):
        df = df[df["SECCIÓN"].str.strip() == sf.strip()]

    # ── Filtro posición ───────────────────────────────────────────────────────
    if pf and pf not in ("TODAS", ""):
        df = df[df["POSICIÓN"].str.strip() == pf.strip()]

    # ── Filtro categoría (TODOS / FALTAN / REPES) ─────────────────────────────
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
        o = orig_r.iloc[i]
        e = edit_r.iloc[i]

        mask = full["ID"] == o["ID"]
        if not mask.any():
            continue
        fi     = full[mask].index[0]
        nombre = full.at[fi, "NOMBRE / DESC"]

        o_estado, e_estado = bool(o["ESTADO"]), bool(e["ESTADO"])
        if o_estado != e_estado:
            full.at[fi, "ESTADO"] = e_estado
            if e_estado:
                add_log_entry("CONSEGUIDO", f"Añadido {nombre}")
            else:
                full.at[fi, "REPE"]          = False
                full.at[fi, "CANTIDAD_REPES"] = 0
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
            full.at[fi, "REPE"]          = True
            full.at[fi, "CANTIDAD_REPES"] = actual + 1
            resumen.append(f"🔁 {p_id_norm} - {nombre} (REPE x{actual + 1})")
            add_log_entry("SOBRE", f"REPE: {p_id_norm} - {nombre} (Total: {actual+1})")

    with open("historico_sobres.txt", "a", encoding="utf-8") as f:
        short = [s.split(" - ")[0].lstrip("✨🔁 ") for s in resumen]
        f.write(f"[{ahora}] {', '.join(short)}\n")

    st.session_state.full_data = full
    return resumen


# ── Carga inicial ──────────────────────────────────────────────────────────────
if not st.session_state.data_loaded:
    load_data()
    st.session_state.data_loaded = True

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("### ⚽")
st.title("MUNDIAL 2026 · ÁLBUM DIGITAL")
st.markdown(
    f"<p style='color:{t_mid};font-family:Consolas;margin-top:-15px;'>"
    "P A N I N I   C O L L E C T I O N   T R A C K E R</p>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<hr style='border:1px solid {g_lo};margin:5px 0 20px;'>",
    unsafe_allow_html=True,
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f"<h3 style='color:{g_hi};font-family:\"Segoe UI Semibold\",sans-serif;'>"
        "FILTROS DE BÚSQUEDA</h3>",
        unsafe_allow_html=True,
    )

    st.text_input(
        "📝 JUGADOR / NOMBRE / ID",
        placeholder="Escribe para buscar...",
        key="search_input",
    )

    # ── Selectboxes: reconstruir si la sección guardada ya no existe ──────────
    secciones  = st.session_state.lista_secciones
    posiciones = st.session_state.lista_posiciones

    sec_idx = 0
    if st.session_state.get("filter_seccion") in secciones:
        sec_idx = secciones.index(st.session_state["filter_seccion"])

    pos_idx = 0
    if st.session_state.get("filter_posicion") in posiciones:
        pos_idx = posiciones.index(st.session_state["filter_posicion"])

    st.selectbox("🗂️ SECCIÓN",  secciones,  index=sec_idx,  key="filter_seccion")
    st.selectbox("🎯 POSICIÓN", posiciones, index=pos_idx,  key="filter_posicion")

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
        f"<p style='color:{t_dim};font-size:12px;'>📁 {FILE_NAME}</p>",
        unsafe_allow_html=True,
    )
    uploaded = st.file_uploader("📂 CARGAR CSV", type=["csv"], label_visibility="collapsed")
    if uploaded is not None:
        raw = uploaded.read().decode("latin-1")
        with open(FILE_NAME, "w", encoding="latin-1") as f:
            f.write(raw)
        st.session_state.data_loaded = False
        st.rerun()

    col_save, col_reload = st.columns(2)
    with col_save:
        if st.button("💾 GUARDAR", key="btn_save"):
            save_data()
    with col_reload:
        if st.button("🔄 RECARGAR", key="btn_reload"):
            st.session_state.data_loaded = False
            st.rerun()

    st.markdown("---")

    LOG_COLORS = {
        "CONSEGUIDO": gr_hi, "ELIMINADO": r_hi, "SOBRE": cyan,
        "GUARDADO": g_hi,    "SISTEMA":  t_mid,
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
    row1_cols = st.columns(4)
    row2_cols = st.columns(4)
    all_slots = row1_cols + row2_cols

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
                st.warning("No has seleccionado ningún cromo válido.")

    with btn_cancel:
        if st.button("❌  CANCELAR", key="btn_cancel_sobre"):
            st.session_state.show_sobre = False
            st.rerun()

    st.markdown(
        f"<hr style='border:1px solid {bd};margin:16px 0 8px;'>",
        unsafe_allow_html=True,
    )
─
filtered_df = get_filtered_df()

st.markdown(
    f"<p style='color:{t_dim};font-size:12px;margin-bottom:4px;'>"
    f"Mostrando <b style='color:{t_mid};'>{len(filtered_df)}</b> cromos</p>",
    unsafe_allow_html=True,
)

if filtered_df.empty:
    st.info("No hay cromos que coincidan con los filtros activos.")
else:
    edited = st.data_editor(
        filtered_df,
        column_config={
            "ID": st.column_config.TextColumn(
                "ID", disabled=True, width="small"),
            "NOMBRE / DESC": st.column_config.TextColumn(
                "NOMBRE / DESC", disabled=True, width="large"),
            "SECCIÓN": st.column_config.TextColumn(
                "SECCIÓN", disabled=True, width="medium"),
            "POSICIÓN": st.column_config.TextColumn(
                "POSICIÓN", disabled=True, width="small"),
            "ESTADO": st.column_config.CheckboxColumn(
                "✅ TENGO",
                help="Marca si tienes el cromo",
                width="small",
            ),
            "REPE": st.column_config.CheckboxColumn(
                "🔁 REPE",
                help="¿Tienes repetidos?",
                width="small",
            ),
            "CANTIDAD_REPES": st.column_config.NumberColumn(
                "# REPES",
                help="Cantidad de repetidos (+1 / −1)",
                min_value=0,
                step=1,
                width="small",
            ),
            "ID SECCIÓN": st.column_config.TextColumn(
                "ID SEC.", disabled=True, width="small"),
        },
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
    )

    if handle_click(filtered_df, edited):
        st.rerun()
