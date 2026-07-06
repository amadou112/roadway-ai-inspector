"use client";

import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import { Bridge } from "@/lib/types";
import { STATUS_COLORS } from "@/lib/chart-colors";

const CONDITION_COLOR: Record<string, string> = {
  good: STATUS_COLORS.good,
  fair: STATUS_COLORS.warning,
  poor: STATUS_COLORS.critical,
  unknown: STATUS_COLORS.neutral,
};

export default function BridgeMap({ bridges }: { bridges: Bridge[] }) {
  const withCoords = bridges.filter((b) => b.latitude && b.longitude);
  const center: [number, number] =
    withCoords.length > 0
      ? [withCoords[0].latitude as number, withCoords[0].longitude as number]
      : [39.15, -75.5];

  return (
    <MapContainer center={center} zoom={9} scrollWheelZoom={false} style={{ height: 420, width: "100%" }}>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {withCoords.map((b) => (
        <CircleMarker
          key={b.id}
          center={[b.latitude as number, b.longitude as number]}
          radius={7}
          pathOptions={{
            color: CONDITION_COLOR[b.condition],
            fillColor: CONDITION_COLOR[b.condition],
            fillOpacity: 0.8,
          }}
        >
          <Popup>
            <div className="text-xs">
              <p className="font-semibold">{b.facility_carried || "Unnamed structure"}</p>
              <p>over {b.feature_intersected || "—"}</p>
              <p>NBI #{b.nbi_structure_number}</p>
              <p>Built {b.year_built || "—"}</p>
              <p className="capitalize">Condition: {b.condition}</p>
            </div>
          </Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}
