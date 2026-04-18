(function () {
  function getLayerName(era, zoom) {
    // Keep z8 in the medium bucket to avoid expensive z8_10 fetches at boundary zoom.
    const bucket = zoom <= 4 ? "z0_4" : zoom <= 8 ? "z5_7" : "z8_10";
    return `public.uk_master_${era}_${bucket}`;
  }

  function imdFillColor() {
    return [
      "case",
      ["==", ["get", "imd_decile"], 0],
      "#cccccc",
      // England - reds
      ["==", ["get", "nation"], "england"],
      [
        "interpolate",
        ["linear"],
        ["get", "imd_decile"],
        1,
        "#67000d",
        3,
        "#a50f15",
        5,
        "#ef3b2c",
        7,
        "#fb6a4a",
        10,
        "#fee5d9",
      ],
      // Scotland - blues
      ["==", ["get", "nation"], "scotland"],
      [
        "interpolate",
        ["linear"],
        ["get", "imd_decile"],
        1,
        "#08306b",
        3,
        "#2171b5",
        5,
        "#6baed6",
        7,
        "#bdd7e7",
        10,
        "#eff3ff",
      ],
      // Wales - greens
      ["==", ["get", "nation"], "wales"],
      [
        "interpolate",
        ["linear"],
        ["get", "imd_decile"],
        1,
        "#00441b",
        3,
        "#238b45",
        5,
        "#74c476",
        7,
        "#bae4b3",
        10,
        "#edf8e9",
      ],
      // N. Ireland - oranges
      ["==", ["get", "nation"], "northern_ireland"],
      [
        "interpolate",
        ["linear"],
        ["get", "imd_decile"],
        1,
        "#7f2704",
        3,
        "#d94801",
        5,
        "#fd8d3c",
        7,
        "#fdbe85",
        10,
        "#feedde",
      ],
      "#cccccc",
    ];
  }

  function initialiseOrganisationCasesMap(config) {
    const {
      containerId,
      tilesBaseUrl,
      imdEra,
      orgLng,
      orgLat,
      orgName,
      casesGeojson,
      boundaryOverlays,
    } = config;

    const container = document.getElementById(containerId);
    if (!container) {
      return;
    }

    // Bail out gracefully if no organisation coordinates.
    if (orgLng === null || orgLat === null) {
      container.innerHTML =
        '<p style="padding:1em;color:#666;">Map unavailable: organisation has no coordinates.</p>';
      return;
    }

    const map = new maplibregl.Map({
      container: containerId,
      // Use an inline style so we do not depend on fetching an external style.json,
      // which can delay or block map.on("load") when the URL is slow or fails.
      style: {
        version: 8,
        glyphs: "https://fonts.openmaptiles.org/{fontstack}/{range}.pbf",
        sources: {
          basemap: {
            type: "raster",
            tiles: [
              "https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",
              "https://b.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",
            ],
            tileSize: 256,
            attribution:
              "© <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors © <a href='https://carto.com/'>CARTO</a>",
          },
        },
        layers: [
          {
            id: "basemap-layer",
            type: "raster",
            source: "basemap",
            minzoom: 0,
            maxzoom: 19,
          },
        ],
      },
      center: [orgLng, orgLat],
      zoom: 8,
    });

    let activeLayerName = null;

    function addBoundaryOverlays(overlays) {
      if (!Array.isArray(overlays) || overlays.length === 0) {
        return;
      }

      overlays.forEach(function (overlay) {
        if (
          !overlay ||
          !overlay.id ||
          !overlay.tilesBaseUrl ||
          !overlay.sourceLayer
        ) {
          return;
        }

        const sourceId = `${overlay.id}-source`;
        const layerId = `${overlay.id}-layer`;
        const layerType = overlay.layerType || "line";
        const paint = overlay.paint || {
          "line-color": "#003087",
          "line-width": 1.5,
          "line-opacity": 0.8,
        };

        if (map.getLayer(layerId)) {
          map.removeLayer(layerId);
        }
        if (map.getSource(sourceId)) {
          map.removeSource(sourceId);
        }

        map.addSource(sourceId, {
          type: "vector",
          tiles: [overlay.tilesBaseUrl],
          minzoom: overlay.minzoom != null ? overlay.minzoom : 0,
          maxzoom: overlay.maxzoom != null ? overlay.maxzoom : 14,
        });

        const beforeId =
          overlay.beforeLayerId && map.getLayer(overlay.beforeLayerId)
            ? overlay.beforeLayerId
            : undefined;

        map.addLayer(
          {
            id: layerId,
            type: layerType,
            source: sourceId,
            "source-layer": overlay.sourceLayer,
            paint: paint,
          },
          beforeId,
        );
      });
    }

    function addDeprivationLayer(beforeId, forcedLayerName) {
      const layerName = forcedLayerName || getLayerName(imdEra, map.getZoom());

      // Avoid rebuilding the same layer/source on every zoomend.
      if (activeLayerName === layerName && map.getLayer("deprivation-layer")) {
        return;
      }

      if (map.getLayer("deprivation-layer")) {
        map.removeLayer("deprivation-layer");
      }
      if (map.getSource("deprivation-source")) {
        map.removeSource("deprivation-source");
      }

      map.addSource("deprivation-source", {
        type: "vector",
        tiles: [`${tilesBaseUrl}/${layerName}/{z}/{x}/{y}.pbf`],
        minzoom: 0,
        maxzoom: 14,
      });

      map.addLayer(
        {
          id: "deprivation-layer",
          type: "fill",
          source: "deprivation-source",
          "source-layer": layerName,
          paint: {
            "fill-color": imdFillColor(),
            "fill-opacity": 0.45,
            "fill-outline-color": "rgba(255,255,255,0.15)",
          },
        },
        beforeId,
      );

      activeLayerName = layerName;
    }

    map.on("error", function (e) {
      const msg = e && e.error && e.error.message ? e.error.message : "";

      // If the high-detail layer intermittently 500s, gracefully fall back.
      if (msg.includes("public.uk_master_") && msg.includes("_z8_10")) {
        addDeprivationLayer("cases-layer", `public.uk_master_${imdEra}_z5_7`);
      }
    });

    map.on("load", function () {
      // 1. Deprivation tiles (no beforeId yet - cases-layer added next)
      addDeprivationLayer();
      map.on("zoomend", function () {
        addDeprivationLayer("cases-layer");
      });

      // 2. Case locations (patients)
      map.addSource("cases-source", {
        type: "geojson",
        data: casesGeojson,
      });
      map.addLayer({
        id: "cases-layer",
        type: "circle",
        source: "cases-source",
        paint: {
          "circle-radius": 7,
          "circle-color": "#e91e8c", // RCPCH pink
          "circle-opacity": 0.9,
          "circle-stroke-width": 1,
          "circle-stroke-color": "#ffffff",
        },
      });

      // 3. Selected organisation marker (dark blue)
      map.addLayer({
        id: "org-layer",
        type: "circle",
        source: {
          type: "geojson",
          data: {
            type: "Feature",
            geometry: { type: "Point", coordinates: [orgLng, orgLat] },
            properties: { name: orgName },
          },
        },
        paint: {
          "circle-radius": 10,
          "circle-color": "#003087", // RCPCH dark blue
          "circle-opacity": 1,
          "circle-stroke-width": 2,
          "circle-stroke-color": "#ffffff",
        },
      });

      // 4. Optional generic boundary overlays for gradual migration from Plotly maps.
      addBoundaryOverlays(boundaryOverlays);

      // 5. Popups on hover
      const popup = new maplibregl.Popup({
        closeButton: false,
        closeOnClick: false,
      });

      map.on("mousemove", "cases-layer", function (e) {
        map.getCanvas().style.cursor = "pointer";
        const props = e.features[0].properties;
        const caseOrgName = props["epilepsy12_sites__organisation__name"] || "";
        const distMi =
          props["distance_mi"] != null
            ? Number(props["distance_mi"]).toFixed(2)
            : "-";
        const distKm =
          props["distance_km"] != null
            ? Number(props["distance_km"]).toFixed(2)
            : "-";
        popup
          .setLngLat(e.lngLat)
          .setHTML(
            `<strong>${caseOrgName}</strong><br>Distance: ${distMi} mi (${distKm} km)`,
          )
          .addTo(map);
      });
      map.on("mouseleave", "cases-layer", function () {
        map.getCanvas().style.cursor = "";
        popup.remove();
      });

      map.on("mousemove", "org-layer", function (e) {
        map.getCanvas().style.cursor = "pointer";
        const props = e.features[0].properties;
        popup
          .setLngLat(e.lngLat)
          .setHTML(`<strong>Lead centre</strong><br>${props.name || orgName}`)
          .addTo(map);
      });
      map.on("mouseleave", "org-layer", function () {
        map.getCanvas().style.cursor = "";
        popup.remove();
      });

      map.on("mousemove", "deprivation-layer", function (e) {
        // If cursor is over a case/lead-centre point, keep point popups on top.
        const topPointFeatures = map.queryRenderedFeatures(e.point, {
          layers: ["org-layer", "cases-layer"],
        });
        if (topPointFeatures && topPointFeatures.length > 0) {
          return;
        }

        map.getCanvas().style.cursor = "pointer";
        const props = e.features[0].properties;
        const areaName = props["area_name"] || "Unknown area";
        const areaCode = props["code"] || "-";
        const laName = props["la_name"] || "N/A";
        const laCode = props["la_code"] || "N/A";
        const decile =
          props["imd_decile"] === 0 ? "No data" : props["imd_decile"];
        popup
          .setLngLat(e.lngLat)
          .setHTML(
            `<strong>${areaName}</strong><br>Code: ${areaCode}<br>LA: ${laName} (${laCode})<br>IMD decile: ${decile}`,
          )
          .addTo(map);
      });
      map.on("mouseleave", "deprivation-layer", function () {
        map.getCanvas().style.cursor = "";
        popup.remove();
      });
    });

    map.addControl(new maplibregl.NavigationControl(), "top-right");
  }

  window.RCPCHMaps = window.RCPCHMaps || {};
  window.RCPCHMaps.initialiseOrganisationCasesMap =
    initialiseOrganisationCasesMap;
})();
