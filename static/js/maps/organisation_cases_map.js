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

    const DEPRIVATION_PRIMARY_SOURCE_ID = "deprivation-source-primary";
    const DEPRIVATION_PRIMARY_LAYER_ID = "deprivation-layer-primary";
    const DEPRIVATION_SECONDARY_SOURCE_ID = "deprivation-source-secondary";
    const DEPRIVATION_SECONDARY_LAYER_ID = "deprivation-layer-secondary";
    let activeLayerSignature = null;
    let forcedPrimaryLayerName = null;
    const boundaryContextLayerIds = [];
    const boundaryOverlayLayerIdsById = {};

    function addBoundaryOverlays(overlays) {
      if (!Array.isArray(overlays) || overlays.length === 0) {
        return;
      }

      overlays.forEach(function (overlay) {
        if (!overlay || !overlay.id) {
          return;
        }

        const sourceId = `${overlay.id}-source`;
        const lineLayerId = `${overlay.id}-line`;
        const fillLayerId = `${overlay.id}-fill`;
        const linePaint = overlay.linePaint ||
          overlay.paint || {
            "line-color": "#003087",
            "line-width": 1.5,
            "line-opacity": 0.8,
          };
        const fillPaint = overlay.fillPaint || {
          "fill-color": "#000000",
          "fill-opacity": 0,
        };

        if (map.getLayer(fillLayerId)) {
          map.removeLayer(fillLayerId);
        }
        if (map.getLayer(lineLayerId)) {
          map.removeLayer(lineLayerId);
        }
        if (map.getSource(sourceId)) {
          map.removeSource(sourceId);
        }

        if (overlay.sourceType === "geojson") {
          map.addSource(sourceId, {
            type: "geojson",
            data: overlay.data || { type: "FeatureCollection", features: [] },
          });
        } else {
          if (!overlay.tilesBaseUrl || !overlay.sourceLayer) {
            return;
          }
          map.addSource(sourceId, {
            type: "vector",
            tiles: [overlay.tilesBaseUrl],
            minzoom: overlay.minzoom != null ? overlay.minzoom : 0,
            maxzoom: overlay.maxzoom != null ? overlay.maxzoom : 14,
          });
        }

        const beforeId =
          overlay.beforeLayerId && map.getLayer(overlay.beforeLayerId)
            ? overlay.beforeLayerId
            : undefined;

        const fillLayerConfig = {
          id: fillLayerId,
          type: "fill",
          source: sourceId,
          paint: fillPaint,
        };
        const lineLayerConfig = {
          id: lineLayerId,
          type: "line",
          source: sourceId,
          paint: linePaint,
        };

        if (overlay.sourceType !== "geojson") {
          fillLayerConfig["source-layer"] = overlay.sourceLayer;
          lineLayerConfig["source-layer"] = overlay.sourceLayer;
        }

        map.addLayer(fillLayerConfig, beforeId);
        map.addLayer(lineLayerConfig, beforeId);
        boundaryContextLayerIds.push(fillLayerId);
        boundaryOverlayLayerIdsById[overlay.id] = {
          fillLayerId: fillLayerId,
          lineLayerId: lineLayerId,
          visible: true,
        };
      });
    }

    function setBoundaryOverlayVisibility(overlayId, isVisible) {
      const overlayLayers = boundaryOverlayLayerIdsById[overlayId];
      if (!overlayLayers) {
        return;
      }

      const visibility = isVisible ? "visible" : "none";

      if (map.getLayer(overlayLayers.fillLayerId)) {
        map.setLayoutProperty(
          overlayLayers.fillLayerId,
          "visibility",
          visibility,
        );
      }
      if (map.getLayer(overlayLayers.lineLayerId)) {
        map.setLayoutProperty(
          overlayLayers.lineLayerId,
          "visibility",
          visibility,
        );
      }

      overlayLayers.visible = isVisible;
    }

    function wireBoundaryLegendToggles() {
      const toggleButtons = document.querySelectorAll("[data-boundary-toggle]");
      if (!toggleButtons || toggleButtons.length === 0) {
        return;
      }

      toggleButtons.forEach(function (button) {
        const overlayId = button.getAttribute("data-boundary-toggle");
        if (!overlayId || !boundaryOverlayLayerIdsById[overlayId]) {
          button.style.opacity = "0.45";
          button.style.cursor = "not-allowed";
          return;
        }

        const setLegendState = function (isVisible) {
          button.setAttribute("aria-pressed", isVisible ? "true" : "false");
          button.style.opacity = isVisible ? "1" : "0.5";
          button.style.filter = isVisible ? "none" : "grayscale(100%)";
        };

        setLegendState(true);

        button.addEventListener("click", function () {
          const current = boundaryOverlayLayerIdsById[overlayId];
          if (!current) {
            return;
          }
          const nextVisibility = !current.visible;
          setBoundaryOverlayVisibility(overlayId, nextVisibility);
          setLegendState(nextVisibility);
        });
      });
    }

    function removeDeprivationLayersAndSources() {
      if (map.getLayer(DEPRIVATION_PRIMARY_LAYER_ID)) {
        map.removeLayer(DEPRIVATION_PRIMARY_LAYER_ID);
      }
      if (map.getLayer(DEPRIVATION_SECONDARY_LAYER_ID)) {
        map.removeLayer(DEPRIVATION_SECONDARY_LAYER_ID);
      }
      if (map.getSource(DEPRIVATION_PRIMARY_SOURCE_ID)) {
        map.removeSource(DEPRIVATION_PRIMARY_SOURCE_ID);
      }
      if (map.getSource(DEPRIVATION_SECONDARY_SOURCE_ID)) {
        map.removeSource(DEPRIVATION_SECONDARY_SOURCE_ID);
      }
    }

    function addDeprivationFillLayer(
      sourceId,
      layerId,
      sourceLayer,
      beforeId,
      filter,
    ) {
      map.addSource(sourceId, {
        type: "vector",
        tiles: [`${tilesBaseUrl}/${sourceLayer}/{z}/{x}/{y}.pbf`],
        minzoom: 0,
        maxzoom: 14,
      });

      const layerConfig = {
        id: layerId,
        type: "fill",
        source: sourceId,
        "source-layer": sourceLayer,
        paint: {
          "fill-color": imdFillColor(),
          "fill-opacity": 0.45,
          "fill-outline-color": "rgba(255,255,255,0.15)",
        },
      };

      if (filter) {
        layerConfig.filter = filter;
      }

      map.addLayer(layerConfig, beforeId);
    }

    function addDeprivationLayers(beforeId) {
      const primaryLayerName =
        forcedPrimaryLayerName || getLayerName(imdEra, map.getZoom());
      const useEngland2025OverlayMode = imdEra === "2021";
      const secondaryLayerName = getLayerName("2011", map.getZoom());
      const nextSignature = useEngland2025OverlayMode
        ? `${primaryLayerName}|${secondaryLayerName}`
        : primaryLayerName;

      // Avoid rebuilding the same layer/source on every zoomend.
      if (
        activeLayerSignature === nextSignature &&
        map.getLayer(DEPRIVATION_PRIMARY_LAYER_ID)
      ) {
        return;
      }

      removeDeprivationLayersAndSources();

      if (useEngland2025OverlayMode) {
        // Draw non-England nations from 2011-era (Wales/Scotland/N. Ireland).
        addDeprivationFillLayer(
          DEPRIVATION_SECONDARY_SOURCE_ID,
          DEPRIVATION_SECONDARY_LAYER_ID,
          secondaryLayerName,
          beforeId,
          ["!=", ["get", "nation"], "england"],
        );

        // Draw England from 2021-era (2025 IMD) on top.
        addDeprivationFillLayer(
          DEPRIVATION_PRIMARY_SOURCE_ID,
          DEPRIVATION_PRIMARY_LAYER_ID,
          primaryLayerName,
          beforeId,
          ["==", ["get", "nation"], "england"],
        );
      } else {
        addDeprivationFillLayer(
          DEPRIVATION_PRIMARY_SOURCE_ID,
          DEPRIVATION_PRIMARY_LAYER_ID,
          primaryLayerName,
          beforeId,
        );
      }

      activeLayerSignature = nextSignature;
    }

    map.on("error", function (e) {
      const msg = e && e.error && e.error.message ? e.error.message : "";

      // If the high-detail layer intermittently 500s, gracefully fall back.
      if (msg.includes("public.uk_master_") && msg.includes("_z8_10")) {
        forcedPrimaryLayerName = `public.uk_master_${imdEra}_z5_7`;
        addDeprivationLayers("cases-layer");
      }
    });

    map.on("load", function () {
      // 1. Deprivation tiles (no beforeId yet - cases-layer added next)
      addDeprivationLayers();
      map.on("zoomend", function () {
        forcedPrimaryLayerName = null;
        addDeprivationLayers("cases-layer");
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
      wireBoundaryLegendToggles();

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

      function handleDeprivationHover(e) {
        const availableDeprivationLayers = [
          DEPRIVATION_PRIMARY_LAYER_ID,
          DEPRIVATION_SECONDARY_LAYER_ID,
        ].filter(function (layerId) {
          return !!map.getLayer(layerId);
        });

        if (availableDeprivationLayers.length === 0) {
          return;
        }

        // If cursor is over a case/lead-centre point, keep point popups on top.
        const topPointFeatures = map.queryRenderedFeatures(e.point, {
          layers: ["org-layer", "cases-layer"],
        });
        if (topPointFeatures && topPointFeatures.length > 0) {
          return;
        }

        const deprivationFeatures = map.queryRenderedFeatures(e.point, {
          layers: availableDeprivationLayers,
        });
        if (!deprivationFeatures || deprivationFeatures.length === 0) {
          popup.remove();
          return;
        }

        map.getCanvas().style.cursor = "pointer";
        const props = deprivationFeatures[0].properties;
        const areaName = props["area_name"] || "Unknown area";
        const areaCode = props["code"] || "-";
        const laName = props["la_name"] || "N/A";
        const laCode = props["la_code"] || "N/A";
        const decile =
          props["imd_decile"] === 0 ? "No data" : props["imd_decile"];

        const boundaryByType = {};
        if (boundaryContextLayerIds.length > 0) {
          const boundaryFeatures = map.queryRenderedFeatures(e.point, {
            layers: boundaryContextLayerIds,
          });
          (boundaryFeatures || []).forEach(function (feature) {
            const featureProps = feature.properties || {};
            const boundaryType = featureProps["boundary_type"] || "Boundary";
            if (!boundaryByType[boundaryType]) {
              boundaryByType[boundaryType] = featureProps;
            }
          });
        }

        function formatBoundaryLine(label, boundaryProps) {
          if (!boundaryProps) {
            return "";
          }
          const name =
            boundaryProps["boundary_name"] ||
            boundaryProps["name"] ||
            "Unknown";
          const code =
            boundaryProps["boundary_code"] ||
            boundaryProps["ods_code"] ||
            boundaryProps["region_code"] ||
            "N/A";
          const cases =
            boundaryProps["case_count"] != null
              ? boundaryProps["case_count"]
              : "0";
          return `${label}: ${name} (${code}) [${cases} cases]`;
        }

        const nhsRegionLine = formatBoundaryLine(
          "NHS Region",
          boundaryByType["NHS England Region"],
        );
        const icbLine = formatBoundaryLine(
          "ICB",
          boundaryByType["Integrated Care Board"],
        );
        const lhbLine = formatBoundaryLine(
          "LHB",
          boundaryByType["Local Health Board"],
        );

        let boundaryContextHtml = "";
        if (nhsRegionLine) {
          boundaryContextHtml += `<br>${nhsRegionLine}`;
        }
        if (icbLine) {
          boundaryContextHtml += `<br>${icbLine}`;
        }
        if (lhbLine) {
          boundaryContextHtml += `<br>${lhbLine}`;
        }

        popup
          .setLngLat(e.lngLat)
          .setHTML(
            `<strong>${areaName}</strong><br>Code: ${areaCode}<br>LA: ${laName} (${laCode})<br>IMD decile: ${decile}<sup>†</sup>${boundaryContextHtml}`,
          )
          .addTo(map);
      }

      map.on("mousemove", function (e) {
        handleDeprivationHover(e);
      });
      map.on("mouseout", function () {
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
