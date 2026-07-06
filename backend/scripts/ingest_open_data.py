"""Loads real Delaware DOT open data into Postgres for the Bridge & Roadway
Data Dashboard:

- National Bridge Inventory (NBI): parsed from the bundled `data/DE25.txt`
  static extract (FHWA, https://www.fhwa.dot.gov/bridge/nbi/2025/delimited/DE25.txt).
- FARS crash data: fetched live from the NHTSA CrashAPI. Skipped gracefully
  if the endpoint is unreachable (some networks block it).
- HPMS pavement condition: fetched live from the FHWA/USDOT ArcGIS
  FeatureServer for Delaware. Skipped gracefully on failure.

Safe to re-run: bridges are upserted by NBI structure number; crash/pavement
records are only inserted if the tables are empty.
"""
import csv
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.session import SessionLocal
from app.models.enums import BridgeConditionEnum
from app.models.opendata import Bridge, CrashRecord, PavementSegment

NBI_FILE = Path(__file__).resolve().parent.parent / "data" / "DE25.txt"

COUNTY_MAP = {1: "Kent", 3: "New Castle", 5: "Sussex"}

OWNER_MAP = {
    1: "State Highway Agency",
    2: "County Highway Agency",
    3: "Town or Township Highway Agency",
    4: "City or Municipal Highway Agency",
    11: "State Park, Forest, or Reservation Agency",
    12: "Local Park, Forest or Reservation Agency",
    21: "Other State Agency",
    25: "Other Local Agency",
    26: "Private",
    27: "Railroad",
    31: "State Toll Authority",
    32: "Local Toll Authority",
    60: "Other Federal Agency",
}

MATERIAL_MAP = {
    1: "Concrete",
    2: "Concrete Continuous",
    3: "Steel",
    4: "Steel Continuous",
    5: "Prestressed Concrete",
    6: "Prestressed Concrete Continuous",
    7: "Wood or Timber",
    8: "Masonry",
    9: "Aluminum, Wrought Iron, or Cast Iron",
    0: "Other",
}

DESIGN_MAP = {
    1: "Slab",
    2: "Stringer/Multi-beam or Girder",
    3: "Girder and Floorbeam System",
    4: "Tee Beam",
    5: "Box Beam or Girders - Multiple",
    6: "Box Beam or Girders - Single/Spread",
    7: "Frame",
    8: "Orthotropic",
    9: "Truss - Deck",
    10: "Truss - Thru",
    11: "Arch - Deck",
    12: "Arch - Thru",
    13: "Suspension",
    14: "Stayed Girder",
    15: "Movable - Lift",
    16: "Movable - Bascule",
    17: "Movable - Swing",
    18: "Tunnel",
    19: "Culvert",
    20: "Mixed Types",
    21: "Segmental Box Girder",
    22: "Channel Beam",
    0: "Other",
}


def _int_or_none(value: str) -> int | None:
    value = (value or "").strip().strip("'")
    if not value or not value.lstrip("-").isdigit():
        return None
    return int(value)


def _parse_coord(raw: str, degree_digits: int) -> float | None:
    raw = (raw or "").strip().strip("'")
    if not raw or len(raw) < degree_digits + 6 or int(raw) == 0:
        return None
    try:
        degrees = int(raw[:degree_digits])
        minutes = int(raw[degree_digits : degree_digits + 2])
        seconds = int(raw[degree_digits + 2 : degree_digits + 6]) / 100.0
        return round(degrees + minutes / 60 + seconds / 3600, 6)
    except ValueError:
        return None


def _classify_condition(deck: int | None, superstructure: int | None, substructure: int | None) -> BridgeConditionEnum:
    ratings = [r for r in (deck, superstructure, substructure) if r is not None]
    if not ratings:
        return BridgeConditionEnum.unknown
    if any(r <= 4 for r in ratings):
        return BridgeConditionEnum.poor
    if all(r >= 7 for r in ratings):
        return BridgeConditionEnum.good
    return BridgeConditionEnum.fair


def ingest_bridges(db) -> int:
    if not NBI_FILE.exists():
        print(f"NBI file not found at {NBI_FILE} — skipping bridge ingestion.")
        return 0

    existing = {b.nbi_structure_number for b in db.query(Bridge.nbi_structure_number).all()}
    count = 0

    with open(NBI_FILE, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f, delimiter=",", quotechar="'")
        for row in reader:
            structure_number = (row.get("STRUCTURE_NUMBER_008") or "").strip().strip("'")
            if not structure_number or structure_number in existing:
                continue

            county_code = _int_or_none(row.get("COUNTY_CODE_003", ""))
            owner_code = _int_or_none(row.get("OWNER_022", ""))
            material_code = _int_or_none(row.get("STRUCTURE_KIND_043A", ""))
            design_code = _int_or_none(row.get("STRUCTURE_TYPE_043B", ""))
            deck = _int_or_none(row.get("DECK_COND_058", ""))
            superstructure = _int_or_none(row.get("SUPERSTRUCTURE_COND_059", ""))
            substructure = _int_or_none(row.get("SUBSTRUCTURE_COND_060", ""))
            structural_eval = _int_or_none(row.get("STRUCTURAL_EVAL_067", ""))

            bridge = Bridge(
                nbi_structure_number=structure_number,
                state="DE",
                county=COUNTY_MAP.get(county_code),
                facility_carried=(row.get("FACILITY_CARRIED_007") or "").strip().strip("'") or None,
                feature_intersected=(row.get("FEATURES_DESC_006A") or "").strip().strip("'") or None,
                year_built=_int_or_none(row.get("YEAR_BUILT_027", "")),
                adt=_int_or_none(row.get("ADT_029", "")),
                latitude=_parse_coord(row.get("LAT_016", ""), 2),
                longitude=(
                    -lon_val if (lon_val := _parse_coord(row.get("LONG_017", ""), 3)) is not None else None
                ),
                deck_condition=deck,
                superstructure_condition=superstructure,
                substructure_condition=substructure,
                structural_evaluation=structural_eval,
                owner=OWNER_MAP.get(owner_code, f"Code {owner_code}" if owner_code is not None else None),
                material_type=MATERIAL_MAP.get(material_code, "Other") if material_code is not None else None,
                design_type=DESIGN_MAP.get(design_code, "Other") if design_code is not None else None,
                condition=_classify_condition(deck, superstructure, substructure),
            )
            db.add(bridge)
            count += 1

    db.commit()
    return count


def ingest_crashes(db) -> int:
    if db.query(CrashRecord).count() > 0:
        return 0

    inserted = 0
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; RoadwayAIInspector/1.0)"}
        with httpx.Client(timeout=20, headers=headers) as client:
            resp = client.get(
                "https://crashviewer.nhtsa.dot.gov/CrashAPI/crashes/GetCrashesByLocation",
                params={"fromCaseYear": 2019, "toCaseYear": 2022, "state": 10, "format": "json"},
            )
            resp.raise_for_status()
            data = resp.json()

        results = data.get("Results") or []
        records = results[0] if results and isinstance(results[0], list) else results
        for rec in records:
            db.add(
                CrashRecord(
                    state="DE",
                    county=rec.get("COUNTYNAME") or rec.get("County"),
                    case_year=_int_or_none(str(rec.get("CASEYEAR") or rec.get("CaseYear") or "")),
                    fatalities=_int_or_none(str(rec.get("FATALS") or rec.get("Fatals") or "0")) or 0,
                    route=rec.get("ROUTENAME") or rec.get("Route"),
                    weather=rec.get("WEATHER1NAME") or rec.get("Weather"),
                    light_condition=rec.get("LGT_CONDNAME") or rec.get("LightCondition"),
                    latitude=float(rec["LATITUDE"]) if rec.get("LATITUDE") else None,
                    longitude=float(rec["LONGITUD"]) if rec.get("LONGITUD") else None,
                )
            )
            inserted += 1
        db.commit()
    except Exception as exc:  # noqa: BLE001
        print(f"FARS crash data unavailable, skipping ({exc}).")
        db.rollback()

    return inserted


def ingest_pavement(db) -> int:
    if db.query(PavementSegment).count() > 0:
        return 0

    inserted = 0
    try:
        with httpx.Client(timeout=20) as client:
            resp = client.get(
                "https://geo.dot.gov/server/rest/services/Hosted/Delaware_2018_PR/FeatureServer/0/query",
                params={
                    "where": "1=1",
                    "outFields": "*",
                    "resultRecordCount": 300,
                    "f": "json",
                },
            )
            resp.raise_for_status()
            data = resp.json()

        for feature in data.get("features") or []:
            attrs = feature.get("attributes", {})
            geometry = feature.get("geometry", {})
            paths = geometry.get("paths") or []
            lon, lat = (paths[0][0][0], paths[0][0][1]) if paths and paths[0] else (None, None)

            db.add(
                PavementSegment(
                    state="DE",
                    route=attrs.get("route_name") or attrs.get("route_id"),
                    county=COUNTY_MAP.get(attrs.get("county_code")),
                    iri=attrs.get("iri"),
                    psr=attrs.get("psr"),
                    surface_type=str(attrs.get("surface_type")) if attrs.get("surface_type") is not None else None,
                    through_lanes=attrs.get("through_lanes"),
                    aadt=attrs.get("aadt"),
                    latitude=lat,
                    longitude=lon,
                )
            )
            inserted += 1
        db.commit()
    except Exception as exc:  # noqa: BLE001
        print(f"HPMS pavement data unavailable, skipping ({exc}).")
        db.rollback()

    return inserted


def run() -> None:
    db = SessionLocal()
    try:
        bridges = ingest_bridges(db)
        print(f"Inserted {bridges} bridges from NBI Delaware extract.")
        crashes = ingest_crashes(db)
        print(f"Inserted {crashes} crash records from FARS.")
        pavement = ingest_pavement(db)
        print(f"Inserted {pavement} pavement segments from HPMS.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
