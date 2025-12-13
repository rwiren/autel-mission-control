// =============================================================================
// FILE: src/dashboards/mission_control.flux
// DESCRIPTION: Master query library for Autel Mission Control Dashboard
// VERSION: 2.0.0 (Includes RTK & Satellite Logic)
// =============================================================================

// -----------------------------------------------------------------------------
// QUERY A: LIVE FLIGHT MAP (Geomap Panel)
// Logic: Extracts Position, Heading, and RTK Status.
//        Filters out "Null Island" (0,0 coordinates).
// -----------------------------------------------------------------------------
from(bucket: "telemetry")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "telemetry")
  |> filter(fn: (r) => r["_field"] == "lat" or r["_field"] == "lon" or r["_field"] == "heading" or r["_field"] == "pos_type_raw")
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
  // SAFETY: Remove invalid GPS points (0,0)
  |> filter(fn: (r) => r.lat != 0.0) 
  |> map(fn: (r) => ({
      r with
      // Map raw fields to visualization friendly names
      lat: r.lat,
      lon: r.lon,
      rtk_status: r.pos_type_raw,
      heading: r.heading
    }))
  |> keep(columns: ["_time", "lat", "lon", "rtk_status", "heading", "drone_sn"])

// -----------------------------------------------------------------------------
// QUERY B: INSTRUMENT CLUSTER (Stat Panels)
// Logic: Returns the single most recent value for Alt, Batt, Sats, Speed
// -----------------------------------------------------------------------------
from(bucket: "telemetry")
  |> range(start: -1m) // Only look at the last minute for "Live" stats
  |> filter(fn: (r) => r["_measurement"] == "telemetry")
  |> filter(fn: (r) => r["_field"] == "alt" or r["_field"] == "batt" or r["_field"] == "sat_count")
  |> last()

// -----------------------------------------------------------------------------
// QUERY C: SIGNAL HEALTH (Time Series Graph)
// Logic: Plots Satellite count over time to see drops
// -----------------------------------------------------------------------------
from(bucket: "telemetry")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "telemetry")
  |> filter(fn: (r) => r["_field"] == "sat_count")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> yield(name: "Satellite Strength")
