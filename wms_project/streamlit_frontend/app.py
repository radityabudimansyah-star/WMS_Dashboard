"""
WMS Dashboard — Streamlit Frontend
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import api_client as api

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WMS Portal",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Hide Streamlit default footer only */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
/* Keep header visible so sidebar toggle works */
header {visibility: visible;}
[data-testid="stHeader"] {background: #0b0f1a; border-bottom: 1px solid #242d42;}

/* Main background */
.stApp {
    background: #0b0f1a;
    color: #e2e8f0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #141927 !important;
    border-right: 1px solid #242d42;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* Metric cards */
[data-testid="metric-container"] {
    background: #141927;
    border: 1px solid #242d42;
    border-radius: 12px;
    padding: 16px 20px;
}

/* Buttons */
.stButton > button {
    background: #1c2436;
    color: #e2e8f0;
    border: 1px solid #242d42;
    border-radius: 8px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    transition: all 0.15s;
}
.stButton > button:hover {
    background: #4f8ef7;
    border-color: #4f8ef7;
    color: white;
}

/* Inputs */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stTextArea > div > div > textarea {
    background: #1c2436 !important;
    color: #e2e8f0 !important;
    border: 1px solid #242d42 !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Dataframe / tables */
[data-testid="stDataFrame"] {
    border: 1px solid #242d42;
    border-radius: 10px;
    overflow: hidden;
}

/* Divider */
hr { border-color: #242d42; }

/* Status pill styles */
.status-waiting    { background:#fef3c7; color:#92400e; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600; }
.status-unloading  { background:#dbeafe; color:#1e3a8a; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600; }
.status-completed  { background:#d1fae5; color:#064e3b; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600; }
.status-loading    { background:#ede9fe; color:#4c1d95; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600; }
.status-ready      { background:#fce7f3; color:#831843; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600; }
.status-departed   { background:#f1f5f9; color:#334155; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600; }

.page-title {
    font-family: 'Syne', sans-serif;
    font-size: 26px;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 4px;
}
.page-sub {
    font-size: 14px;
    color: #64748b;
    margin-bottom: 24px;
}
.role-badge {
    display:inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ─── CONSTANTS ────────────────────────────────────────────────────────────────
ROLE_LABELS = {
    "inbound_admin":  "Inbound Admin",
    "outbound_admin": "Outbound Admin",
    "security":       "Security",
    "checker":        "Checker",
    "picker":         "Picker",
    "supervisor":     "Supervisor",
}

ROLE_COLORS = {
    "inbound_admin":  "#3b82f6",
    "outbound_admin": "#f59e0b",
    "security":       "#10b981",
    "checker":        "#8b5cf6",
    "picker":         "#ec4899",
    "supervisor":     "#ef4444",
}

TRUCK_TYPES       = ["Engkel", "CDD", "Fuso", "Trailer", "Pickup"]
INBOUND_STATUSES  = ["Waiting", "Unloading", "Loading Completed"]
OUTBOUND_STATUSES = ["Waiting", "Loading", "Ready to Depart", "Departed"]

STATUS_EMOJI = {
    "Waiting":           "⏳",
    "Unloading":         "📤",
    "Loading Completed": "✅",
    "Loading":           "📥",
    "Ready to Depart":   "🟢",
    "Departed":          "🏁",
}


def has_role(*roles):
    return st.session_state.get("role") in roles


def fmt_dt(iso_str):
    if not iso_str:
        return "—"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%d %b %Y  %H:%M")
    except Exception:
        return iso_str[:16]


# ─── SESSION STATE INIT ───────────────────────────────────────────────────────
for key in ["token", "username", "role", "full_name", "logged_in"]:
    if key not in st.session_state:
        st.session_state[key] = None
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False


# ══════════════════════════════════════════════════════════════════════════════
#  LOGIN PAGE
# ══════════════════════════════════════════════════════════════════════════════
def render_login():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align:center; margin-bottom:32px;'>
            <div style='font-size:48px; margin-bottom:12px;'>📦</div>
            <div style='font-family:Syne,sans-serif; font-size:28px; font-weight:800; color:#e2e8f0;'>WMS Portal</div>
            <div style='font-size:14px; color:#64748b; margin-top:4px;'>Warehouse Management System</div>
        </div>
        """, unsafe_allow_html=True)

        with st.container():
            username = st.text_input("Username", placeholder="Enter your username", label_visibility="visible")
            password = st.text_input("Password", placeholder="Enter your password", type="password")
            st.markdown("<br>", unsafe_allow_html=True)
            login_btn = st.button("Sign In →", use_container_width=True, type="primary")

            if login_btn:
                if not username or not password:
                    st.error("Please enter both username and password.")
                else:
                    with st.spinner("Signing in..."):
                        data, code = api.login(username, password)
                    if code == 200:
                        st.session_state["token"]     = data["token"]
                        st.session_state["username"]  = data["username"]
                        st.session_state["role"]      = data["role"]
                        st.session_state["full_name"] = data["full_name"]
                        st.session_state["logged_in"] = True
                        st.rerun()
                    else:
                        st.error(data.get("error", "Login failed. Please try again."))

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("""
        <div style='font-size:12px; color:#475569; text-align:center; line-height:2;'>
        <b style='color:#64748b;'>Demo Accounts</b><br>
        admin / admin123 &nbsp;·&nbsp; outadmin / out123<br>
        security / sec123 &nbsp;·&nbsp; checker1 / check123<br>
        picker1 / pick123 &nbsp;·&nbsp; supervisor / super123
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
def render_sidebar():
    role       = st.session_state["role"]
    full_name  = st.session_state["full_name"] or st.session_state["username"]
    role_label = ROLE_LABELS.get(role, role)
    role_color = ROLE_COLORS.get(role, "#64748b")

    with st.sidebar:
        st.markdown("""
        <div style='padding:8px 0 20px; border-bottom:1px solid #242d42; margin-bottom:20px;'>
            <div style='font-family:Syne,sans-serif; font-size:18px; font-weight:700; color:#e2e8f0; display:flex; align-items:center; gap:8px;'>
                <span style='width:10px;height:10px;border-radius:50%;background:linear-gradient(135deg,#4f8ef7,#34d399);display:inline-block;'></span>
                WMS Portal
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style='background:#1c2436; border:1px solid #242d42; border-radius:10px; padding:14px; margin-bottom:20px;'>
            <div style='font-size:15px; font-weight:600; color:#e2e8f0;'>{full_name}</div>
            <div style='margin-top:6px;'>
                <span style='background:{role_color}22; color:{role_color}; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:700;'>
                    {role_label}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation based on role
        pages = []
        pages.append(("📊  Dashboard",     "dashboard"))

        if has_role("inbound_admin", "supervisor", "security", "checker"):
            pages.append(("🚛  Inbound Trucks",  "inbound"))
        if has_role("outbound_admin", "supervisor", "security", "picker"):
            pages.append(("🚚  Outbound Trucks", "outbound"))
        if has_role("inbound_admin", "outbound_admin", "supervisor", "checker", "picker"):
            pages.append(("📋  SKU Masterlist",  "sku"))

        if "current_page" not in st.session_state:
            st.session_state["current_page"] = pages[0][1]

        st.markdown("<div style='font-size:10px; font-weight:700; letter-spacing:1.5px; color:#475569; margin-bottom:8px;'>NAVIGATION</div>", unsafe_allow_html=True)

        for label, key in pages:
            is_active = st.session_state["current_page"] == key
            btn_style = "primary" if is_active else "secondary"
            if st.button(label, key=f"nav_{key}", use_container_width=True, type=btn_style):
                st.session_state["current_page"] = key
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.divider()
        if st.button("🚪  Sign Out", use_container_width=True):
            api.logout()
            for k in ["token", "username", "role", "full_name", "logged_in", "current_page"]:
                st.session_state[k] = None
            st.session_state["logged_in"] = False
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD PAGE
# ══════════════════════════════════════════════════════════════════════════════
def render_dashboard():
    st.markdown('<div class="page-title">📊 Operations Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Live warehouse activity — inbound & outbound</div>', unsafe_allow_html=True)

    stats = api.get_dashboard_stats()
    ib    = stats.get("inbound",  {})
    ob    = stats.get("outbound", {})

    # Inbound metrics
    st.markdown("#### 🚛 Inbound")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Trucks",       ib.get("total", 0))
    c2.metric("⏳ Waiting",          ib.get("waiting", 0))
    c3.metric("📤 Unloading",        ib.get("unloading", 0))
    c4.metric("✅ Completed",         ib.get("loading_completed", 0))

    st.markdown("<br>", unsafe_allow_html=True)

    # Outbound metrics
    st.markdown("#### 🚚 Outbound")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Trucks",        ob.get("total", 0))
    c2.metric("⏳ Waiting",           ob.get("waiting", 0))
    c3.metric("📥 Loading",           ob.get("loading", 0))
    c4.metric("🟢 Ready to Depart",   ob.get("ready_to_depart", 0))
    c5.metric("🏁 Departed",          ob.get("departed", 0))

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"#### 📋 SKU Masterlist — **{stats.get('sku_count', 0)}** SKUs registered")

    st.divider()

    # Recent activity side by side
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("##### Recent Inbound Trucks")
        trucks = api.get_inbound_trucks()
        if trucks:
            df = pd.DataFrame([{
                "Plate":  t["license_plate"],
                "Type":   t["truck_type"],
                "Status": STATUS_EMOJI.get(t["status"], "") + " " + t["status"],
                "Time":   fmt_dt(t["created_at"]),
            } for t in trucks[:8]])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No inbound trucks yet.")

    with col_r:
        st.markdown("##### Recent Outbound Trucks")
        trucks = api.get_outbound_trucks()
        if trucks:
            df = pd.DataFrame([{
                "Plate":       t["license_plate"],
                "Type":        t["truck_type"],
                "Destination": t.get("destination") or "—",
                "Status":      STATUS_EMOJI.get(t["status"], "") + " " + t["status"],
            } for t in trucks[:8]])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No outbound trucks yet.")


# ══════════════════════════════════════════════════════════════════════════════
#  INBOUND PAGE
# ══════════════════════════════════════════════════════════════════════════════
def render_inbound():
    st.markdown('<div class="page-title">🚛 Inbound Trucks</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Manage arriving trucks and unloading status</div>', unsafe_allow_html=True)

    can_register = has_role("security", "inbound_admin", "supervisor")
    can_edit     = has_role("inbound_admin", "supervisor")

    # ── Register new truck ────────────────────────────────────────────────────
    if can_register:
        with st.expander("➕ Register New Inbound Truck", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                plate = st.text_input("License Plate *", placeholder="e.g. B 1234 ABC", key="ib_plate")
                ttype = st.selectbox("Truck Type *", TRUCK_TYPES, key="ib_type")
            with col2:
                notes = st.text_area("Notes (optional)", placeholder="Delivery note no., supplier, remarks...", key="ib_notes", height=100)

            if st.button("✅ Register Truck", type="primary", key="ib_submit"):
                if not plate.strip():
                    st.error("License plate is required.")
                else:
                    data, code = api.create_inbound_truck({
                        "license_plate": plate.strip().upper(),
                        "truck_type":    ttype,
                        "notes":         notes.strip(),
                        "status":        "Waiting",
                    })
                    if code == 201:
                        st.success(f"✅ Truck **{plate.upper()}** registered successfully!")
                        st.rerun()
                    else:
                        st.error(str(data))

    # ── Truck list ────────────────────────────────────────────────────────────
    trucks = api.get_inbound_trucks()

    if not trucks:
        st.info("No inbound trucks registered yet.")
        return

    st.markdown(f"**{len(trucks)} truck(s) recorded**")
    st.divider()

    for t in trucks:
        status     = t["status"]
        emoji      = STATUS_EMOJI.get(status, "")
        plate      = t["license_plate"]
        ttype      = t["truck_type"]
        registered = t.get("registered_by_name", "—")
        time_str   = fmt_dt(t["created_at"])
        notes      = t.get("notes") or "—"

        with st.container():
            cols = st.columns([2, 1.5, 2, 2, 2, 1.5, 0.5])
            cols[0].markdown(f"**{plate}**")
            cols[1].markdown(f"`{ttype}`")
            cols[2].markdown(f"{emoji} **{status}**")
            cols[3].markdown(f"<small style='color:#64748b;'>{time_str}</small>", unsafe_allow_html=True)
            cols[4].markdown(f"<small>{notes}</small>", unsafe_allow_html=True)
            cols[5].markdown(f"<span style='font-size:12px;color:#64748b;'>By: {registered}</span>", unsafe_allow_html=True)

            if can_edit:
                with cols[5]:
                    new_status = st.selectbox(
                        "Status",
                        INBOUND_STATUSES,
                        index=INBOUND_STATUSES.index(status),
                        key=f"ib_status_{t['id']}",
                        label_visibility="collapsed",
                    )
                    if new_status != status:
                        api.update_inbound_truck(t["id"], {"status": new_status})
                        st.rerun()
                if cols[6].button("🗑", key=f"ib_del_{t['id']}", help="Delete truck"):
                    api.delete_inbound_truck(t["id"])
                    st.rerun()

            st.divider()


# ══════════════════════════════════════════════════════════════════════════════
#  OUTBOUND PAGE
# ══════════════════════════════════════════════════════════════════════════════
def render_outbound():
    st.markdown('<div class="page-title">🚚 Outbound Trucks</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Manage outgoing delivery trucks</div>', unsafe_allow_html=True)

    can_register = has_role("security", "outbound_admin", "supervisor")
    can_edit     = has_role("outbound_admin", "supervisor")

    # ── Register new truck ────────────────────────────────────────────────────
    if can_register:
        with st.expander("➕ Register New Outbound Truck", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                plate       = st.text_input("License Plate *", placeholder="e.g. B 5678 XYZ", key="ob_plate")
                ttype       = st.selectbox("Truck Type *", TRUCK_TYPES, key="ob_type")
            with col2:
                destination = st.text_input("Destination", placeholder="e.g. Gudang Bekasi", key="ob_dest")
                notes       = st.text_area("Notes (optional)", placeholder="DO number, remarks...", key="ob_notes", height=70)

            if st.button("✅ Register Truck", type="primary", key="ob_submit"):
                if not plate.strip():
                    st.error("License plate is required.")
                else:
                    data, code = api.create_outbound_truck({
                        "license_plate": plate.strip().upper(),
                        "truck_type":    ttype,
                        "destination":   destination.strip(),
                        "notes":         notes.strip(),
                        "status":        "Waiting",
                    })
                    if code == 201:
                        st.success(f"✅ Truck **{plate.upper()}** registered for outbound!")
                        st.rerun()
                    else:
                        st.error(str(data))

    # ── Truck list ────────────────────────────────────────────────────────────
    trucks = api.get_outbound_trucks()

    if not trucks:
        st.info("No outbound trucks registered yet.")
        return

    st.markdown(f"**{len(trucks)} truck(s) recorded**")
    st.divider()

    for t in trucks:
        status  = t["status"]
        emoji   = STATUS_EMOJI.get(status, "")
        plate   = t["license_plate"]
        ttype   = t["truck_type"]
        dest    = t.get("destination") or "—"
        time_str = fmt_dt(t["created_at"])

        with st.container():
            cols = st.columns([2, 1.5, 2, 2, 2, 1.5, 0.5])
            cols[0].markdown(f"**{plate}**")
            cols[1].markdown(f"`{ttype}`")
            cols[2].markdown(f"📍 {dest}")
            cols[3].markdown(f"{emoji} **{status}**")
            cols[4].markdown(f"<small style='color:#64748b;'>{time_str}</small>", unsafe_allow_html=True)

            if can_edit:
                with cols[5]:
                    new_status = st.selectbox(
                        "Status",
                        OUTBOUND_STATUSES,
                        index=OUTBOUND_STATUSES.index(status),
                        key=f"ob_status_{t['id']}",
                        label_visibility="collapsed",
                    )
                    if new_status != status:
                        api.update_outbound_truck(t["id"], {"status": new_status})
                        st.rerun()
                if cols[6].button("🗑", key=f"ob_del_{t['id']}", help="Delete truck"):
                    api.delete_outbound_truck(t["id"])
                    st.rerun()

            st.divider()


# ══════════════════════════════════════════════════════════════════════════════
#  SKU MASTERLIST PAGE
# ══════════════════════════════════════════════════════════════════════════════
def render_sku():
    st.markdown('<div class="page-title">📋 SKU Masterlist</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Pallet configuration reference — CSE per pallet for each SKU</div>', unsafe_allow_html=True)

    can_edit = has_role("inbound_admin", "supervisor")

    if not can_edit:
        st.info("👁 **View only.** Contact Inbound Admin to add or modify SKUs.")

    # ── Add new SKU ───────────────────────────────────────────────────────────
    if can_edit:
        with st.expander("➕ Add New SKU", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                new_sku_no   = st.text_input("SKU Number *", placeholder="e.g. SKU-011", key="sku_no")
            with col2:
                new_sku_name = st.text_input("Product Name *", placeholder="e.g. Aqua Botol 1.5L", key="sku_name")
            with col3:
                new_cse      = st.number_input("CSE per Pallet *", min_value=1, max_value=9999, value=48, key="sku_cse")

            if st.button("✅ Add SKU", type="primary", key="sku_add"):
                if not new_sku_no.strip() or not new_sku_name.strip():
                    st.error("SKU number and product name are required.")
                else:
                    data, code = api.create_sku({
                        "sku_number":     new_sku_no.strip().upper(),
                        "product_name":   new_sku_name.strip(),
                        "cse_per_pallet": new_cse,
                    })
                    if code == 201:
                        st.success(f"✅ SKU **{new_sku_no.upper()}** added!")
                        st.rerun()
                    else:
                        st.error(str(data))

    # ── Search bar ────────────────────────────────────────────────────────────
    search = st.text_input("🔍 Search SKU", placeholder="Type SKU number or product name to filter...", key="sku_search")

    skus = api.get_skus(search=search)

    st.markdown(f"Showing **{len(skus)}** SKU(s)" + (f" matching **'{search}'**" if search else ""))
    st.divider()

    if not skus:
        st.info("No SKUs found." if search else "No SKUs in masterlist yet.")
        return

    # ── Edit state ────────────────────────────────────────────────────────────
    if "editing_sku" not in st.session_state:
        st.session_state["editing_sku"] = None

    # ── Table header ──────────────────────────────────────────────────────────
    hcols = st.columns([0.5, 2, 4, 2, 2] if can_edit else [0.5, 2, 4, 2])
    hcols[0].markdown("**#**")
    hcols[1].markdown("**SKU Number**")
    hcols[2].markdown("**Product Name**")
    hcols[3].markdown("**CSE / Pallet**")
    if can_edit:
        hcols[4].markdown("**Actions**")
    st.divider()

    for i, s in enumerate(skus, 1):
        editing = st.session_state["editing_sku"] == s["id"]

        if editing and can_edit:
            # Inline edit row
            ec1, ec2, ec3, ec4 = st.columns([2, 4, 2, 2])
            with ec1:
                e_sku  = st.text_input("SKU", value=s["sku_number"],    key=f"e_sku_{s['id']}", label_visibility="collapsed")
            with ec2:
                e_name = st.text_input("Name", value=s["product_name"], key=f"e_name_{s['id']}", label_visibility="collapsed")
            with ec3:
                e_cse  = st.number_input("CSE", value=s["cse_per_pallet"], min_value=1, key=f"e_cse_{s['id']}", label_visibility="collapsed")
            with ec4:
                sc1, sc2 = st.columns(2)
                if sc1.button("💾", key=f"save_{s['id']}", help="Save changes"):
                    api.update_sku(s["id"], {"sku_number": e_sku, "product_name": e_name, "cse_per_pallet": e_cse})
                    st.session_state["editing_sku"] = None
                    st.rerun()
                if sc2.button("✕", key=f"cancel_{s['id']}", help="Cancel"):
                    st.session_state["editing_sku"] = None
                    st.rerun()
        else:
            cols = st.columns([0.5, 2, 4, 2, 2] if can_edit else [0.5, 2, 4, 2])
            cols[0].markdown(f"<small style='color:#64748b;'>{i}</small>", unsafe_allow_html=True)
            cols[1].markdown(f"`{s['sku_number']}`")
            cols[2].markdown(f"{s['product_name']}")
            cols[3].markdown(
                f"<span style='font-family:Syne,sans-serif;font-size:20px;font-weight:700;color:#34d399;'>{s['cse_per_pallet']}</span>"
                f"<span style='font-size:12px;color:#64748b;'> CSE</span>",
                unsafe_allow_html=True
            )
            if can_edit:
                ac1, ac2 = cols[4].columns(2)
                if ac1.button("✏️", key=f"edit_{s['id']}", help="Edit SKU"):
                    st.session_state["editing_sku"] = s["id"]
                    st.rerun()
                if ac2.button("🗑", key=f"del_{s['id']}", help="Delete SKU"):
                    api.delete_sku(s["id"])
                    st.rerun()

        st.divider()


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN ROUTER
# ══════════════════════════════════════════════════════════════════════════════
def main():
    if not st.session_state.get("logged_in"):
        render_login()
        return

    render_sidebar()

    page = st.session_state.get("current_page", "dashboard")
    if page == "dashboard":
        render_dashboard()
    elif page == "inbound":
        render_inbound()
    elif page == "outbound":
        render_outbound()
    elif page == "sku":
        render_sku()


if __name__ == "__main__":
    main()
