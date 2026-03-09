"""
sheets_sync.py
Two-way sync between Django database and Google Sheets.

Dashboard → Sheets: instantly on every add/change/delete
Sheets → Dashboard: automatically every 2 minutes via background thread
"""

import os
import threading
import time
import gspread
from google.oauth2.service_account import Credentials
from django.conf import settings

# ─── CONFIG ───────────────────────────────────────────────────────────────────
SPREADSHEET_ID = "1ioMgrsK4ooTWB8UIm5MeG3saNz7IlAzKCX-kgBD6zlo"
KEY_FILE       = os.path.join(settings.BASE_DIR, "maersk-wms-dashboard-117b9b99410b.json")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SHEET_INBOUND    = "Inbound"
SHEET_OUTBOUND   = "Outbound"
SHEET_SKU        = "SKU Masterlist"

HEADERS_INBOUND  = ["License Plate", "Truck Types", "Notes (Remarks)", "Status", "Registered By", "Date & Time"]
HEADERS_OUTBOUND = ["License Plate", "Truck Types", "Destination", "Notes (Remarks)", "Status", "Registered By", "Date & Time"]
HEADERS_SKU      = ["SAP CODE", "SAP NAME", "CSE/Pallet"]

INBOUND_STATUSES  = ["Waiting", "Unloading", "Loading Completed"]
OUTBOUND_STATUSES = ["Waiting", "Loading", "Ready to Depart", "Departed"]
TRUCK_TYPES       = ["Engkel", "CDD", "Fuso", "Trailer", "Pickup"]

# ─── CONNECTION ───────────────────────────────────────────────────────────────
def get_client():
    creds = Credentials.from_service_account_file(KEY_FILE, scopes=SCOPES)
    return gspread.authorize(creds)

def get_sheet(client, sheet_name):
    return client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)

def fmt_dt(dt):
    if not dt:
        return ""
    try:
        from django.utils import timezone
        local = dt.astimezone(timezone.get_current_timezone())
        return local.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return str(dt)[:16]


# ══════════════════════════════════════════════════════════════════════════════
#  PUSH: Dashboard → Google Sheets
# ══════════════════════════════════════════════════════════════════════════════

def sync_inbound():
    """Push all inbound trucks from database to Google Sheets."""
    try:
        from .models import InboundTruck
        client = get_client()
        sheet  = get_sheet(client, SHEET_INBOUND)
        sheet.clear()
        rows = [HEADERS_INBOUND]
        for t in InboundTruck.objects.select_related('registered_by__profile').all():
            profile = getattr(getattr(t, 'registered_by', None), 'profile', None)
            registered_by = profile.full_name if profile and profile.full_name else (t.registered_by.username if t.registered_by else "")
            rows.append([t.license_plate, t.truck_type, t.notes or "", t.status, registered_by, fmt_dt(t.created_at)])
        sheet.update(rows, "A1")
        sheet.format("A1:F1", {"textFormat": {"bold": True}})
        print(f"[Sheets →] Inbound: {len(rows)-1} rows written.")
    except Exception as e:
        print(f"[Sheets ERROR] Inbound push failed: {e}")


def sync_outbound():
    """Push all outbound trucks from database to Google Sheets."""
    try:
        from .models import OutboundTruck
        client = get_client()
        sheet  = get_sheet(client, SHEET_OUTBOUND)
        sheet.clear()
        rows = [HEADERS_OUTBOUND]
        for t in OutboundTruck.objects.select_related('registered_by__profile').all():
            profile = getattr(getattr(t, 'registered_by', None), 'profile', None)
            registered_by = profile.full_name if profile and profile.full_name else (t.registered_by.username if t.registered_by else "")
            rows.append([t.license_plate, t.truck_type, t.destination or "", t.notes or "", t.status, registered_by, fmt_dt(t.created_at)])
        sheet.update(rows, "A1")
        sheet.format("A1:G1", {"textFormat": {"bold": True}})
        print(f"[Sheets →] Outbound: {len(rows)-1} rows written.")
    except Exception as e:
        print(f"[Sheets ERROR] Outbound push failed: {e}")


def sync_sku():
    """Push all SKUs from database to Google Sheets."""
    try:
        from .models import SKU
        client = get_client()
        sheet  = get_sheet(client, SHEET_SKU)
        sheet.clear()
        rows = [HEADERS_SKU]
        for s in SKU.objects.all():
            rows.append([s.sku_number, s.product_name, s.cse_per_pallet])
        sheet.update(rows, "A1")
        sheet.format("A1:C1", {"textFormat": {"bold": True}})
        print(f"[Sheets →] SKU Masterlist: {len(rows)-1} rows written.")
    except Exception as e:
        print(f"[Sheets ERROR] SKU push failed: {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  PULL: Google Sheets → Dashboard (every 2 minutes)
# ══════════════════════════════════════════════════════════════════════════════

def pull_sku_from_sheets():
    """
    Read SKU Masterlist from Google Sheets and update the database.
    - New rows in sheets → added to database
    - Changed rows → updated in database
    - Rows deleted from sheets → deleted from database
    """
    try:
        from .models import SKU
        client = get_client()
        sheet  = get_sheet(client, SHEET_SKU)
        rows   = sheet.get_all_values()

        if len(rows) < 2:
            return  # Only header or empty — skip

        # Skip header row
        data_rows = rows[1:]

        # Collect SAP codes currently in sheet
        sheet_codes = set()
        for row in data_rows:
            if len(row) < 3:
                continue
            sku_number   = str(row[0]).strip()
            product_name = str(row[1]).strip()
            cse_str      = str(row[2]).strip()

            if not sku_number or not product_name:
                continue

            # Parse CSE/Pallet — default to 1 if invalid
            try:
                cse = int(float(cse_str))
                if cse < 1:
                    cse = 1
            except (ValueError, TypeError):
                cse = 1

            sheet_codes.add(sku_number)

            # Update or create in database
            SKU.objects.update_or_create(
                sku_number=sku_number,
                defaults={"product_name": product_name, "cse_per_pallet": cse}
            )

        # Delete SKUs that were removed from the sheet
        SKU.objects.exclude(sku_number__in=sheet_codes).delete()

        print(f"[← Sheets] SKU pull: {len(sheet_codes)} SKUs synced from sheet.")

    except Exception as e:
        print(f"[Sheets ERROR] SKU pull failed: {e}")


def pull_inbound_from_sheets():
    """
    Read Inbound sheet and update database.
    Only syncs: License Plate, Truck Type, Notes, Status.
    (Registered By and Date are managed by the dashboard)
    """
    try:
        from .models import InboundTruck
        client = get_client()
        sheet  = get_sheet(client, SHEET_INBOUND)
        rows   = sheet.get_all_values()

        if len(rows) < 2:
            return

        data_rows = rows[1:]
        sheet_plates = set()

        for row in data_rows:
            if len(row) < 1:
                continue
            plate  = str(row[0]).strip().upper()
            ttype  = str(row[1]).strip() if len(row) > 1 else "Engkel"
            notes  = str(row[2]).strip() if len(row) > 2 else ""
            status = str(row[3]).strip() if len(row) > 3 else "Waiting"

            if not plate:
                continue

            # Validate values
            if ttype not in TRUCK_TYPES:
                ttype = "Engkel"
            if status not in INBOUND_STATUSES:
                status = "Waiting"

            sheet_plates.add(plate)

            # Update existing or create new
            truck, created = InboundTruck.objects.get_or_create(license_plate=plate)
            truck.truck_type = ttype
            truck.notes      = notes
            truck.status     = status
            truck.save()

        print(f"[← Sheets] Inbound pull: {len(sheet_plates)} trucks synced from sheet.")

    except Exception as e:
        print(f"[Sheets ERROR] Inbound pull failed: {e}")


def pull_outbound_from_sheets():
    """
    Read Outbound sheet and update database.
    """
    try:
        from .models import OutboundTruck
        client = get_client()
        sheet  = get_sheet(client, SHEET_OUTBOUND)
        rows   = sheet.get_all_values()

        if len(rows) < 2:
            return

        data_rows = rows[1:]
        sheet_plates = set()

        for row in data_rows:
            if len(row) < 1:
                continue
            plate  = str(row[0]).strip().upper()
            ttype  = str(row[1]).strip() if len(row) > 1 else "Engkel"
            dest   = str(row[2]).strip() if len(row) > 2 else ""
            notes  = str(row[3]).strip() if len(row) > 3 else ""
            status = str(row[4]).strip() if len(row) > 4 else "Waiting"

            if not plate:
                continue

            if ttype not in TRUCK_TYPES:
                ttype = "Engkel"
            if status not in OUTBOUND_STATUSES:
                status = "Waiting"

            sheet_plates.add(plate)

            truck, created = OutboundTruck.objects.get_or_create(license_plate=plate)
            truck.truck_type   = ttype
            truck.destination  = dest
            truck.notes        = notes
            truck.status       = status
            truck.save()

        print(f"[← Sheets] Outbound pull: {len(sheet_plates)} trucks synced from sheet.")

    except Exception as e:
        print(f"[Sheets ERROR] Outbound pull failed: {e}")


def pull_all_from_sheets():
    """Pull all three sheets into the database."""
    print("[← Sheets] Running full pull from Google Sheets...")
    pull_sku_from_sheets()
    pull_inbound_from_sheets()
    pull_outbound_from_sheets()
    print("[← Sheets] Full pull complete.")


# ══════════════════════════════════════════════════════════════════════════════
#  BACKGROUND SYNC LOOP (runs every 2 minutes automatically)
# ══════════════════════════════════════════════════════════════════════════════

_sync_thread_started = False

def start_background_sync():
    """
    Start a background thread that pulls from Google Sheets every 2 minutes.
    Call this once when Django starts up (from apps.py ready()).
    """
    global _sync_thread_started
    if _sync_thread_started:
        return
    _sync_thread_started = True

    def loop():
        # Wait 10 seconds after startup before first pull
        time.sleep(10)
        while True:
            try:
                pull_all_from_sheets()
            except Exception as e:
                print(f"[Sheets ERROR] Background sync error: {e}")
            # Wait 2 minutes before next pull
            time.sleep(120)

    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
    print("[Sheets Sync] Background sync started — pulling from Google Sheets every 2 minutes.")
