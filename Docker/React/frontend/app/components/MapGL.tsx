import React, {type SyntheticEvent, useEffect, useMemo, useState} from "react";
import DeckGL from "@deck.gl/react";
import {GeoJsonLayer, TextLayer} from "@deck.gl/layers";
import {Map} from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';
import type {Feature, GeoJSON, MapGLProps, Point, TextMap} from "~/Types";
import {Layer, type PickingInfo} from "@deck.gl/core";
import {getCenter} from "~/utils";

/**
 * TODO GERER LES INFOS DES ARBRES QUAND ON CLIQUE DESSUS (APPARITION D'UNE POPUP AVEC LES INFOS)
 * @param mapZoom
 * @param geoJsonData
 * @param treesJsonData
 * @param zoomPlot
 * @constructor
 */
export default function MapGL({
                                  mapZoom,
                                  geoJsonData,
                                  treesJsonData,
                                  onPlotClick,
                                  onSubPlotClick
                              }: MapGLProps): React.ReactElement {

    const [mapZoomState, setMapZoomState] = useState(mapZoom);
    const [layers, setLayers] = React.useState<Layer[]>([]);
    const [intervalBearing, setIntervalBearing] = React.useState<NodeJS.Timeout>();
    const [bearing, setBearing] = React.useState<number>(0);

    const treeColor = useMemo(() => {
        const colorMap: Record<string, [number, number, number]> = {};

        treesJsonData?.forEach((tree: Feature) => {

            const family = tree.properties?.tree?.species?.family;
            if (family && !colorMap[family]) {
                colorMap[family] = getColorFromHash(family);
            }
        });

        return colorMap;
    }, []);

    useEffect(() => {
        if (mapZoom) {
            const interval = setInterval(() => {
                setBearing((prevState) =>(prevState+0.5)%360)
            }, 20)
            getLayers(mapZoom.zoom);
            setIntervalBearing(interval);
            setMapZoomState(mapZoom);
            return () => clearInterval(interval);
        }
    }, [mapZoom])


    useEffect(() => {
        getLayers();
    }, []);

    useEffect(() => {
        getLayers(mapZoomState?.zoom || 10);
    }, [mapZoomState?.zoom]);

    function handleLayerClick(info: PickingInfo): void {
        if (info.object?.properties?.name) {
            const plotId = info.object.properties.parent_plot_id ?? info.object.properties.name;
            const subPlotId = info.object.properties.sub_plot_id || null;

            if (subPlotId) {
                onSubPlotClick(plotId, subPlotId);
            } else {
                onPlotClick(plotId);
            }
        }
    }

    function getLayers(currentZoom: number = 10): void {
        const layers: Layer[] = [];
        const textData: TextMap[] = [];

        if (geoJsonData && treesJsonData) {

            if (currentZoom < 19) {
                const geoJsonPlots: GeoJSON = {
                    type: "FeatureCollection",
                    features: geoJsonData.map(plot => {
                        if (plot.location.geometry.type === "Polygon") {
                            const coords: Point = getCenter(plot.location.geometry.coordinates[0]);
                            textData.push({
                                name: plot.plot_id.normalize("NFD").replace(/[\u0300-\u036f]/g, ""),
                                coordinates: [coords[0], coords[1]]
                            });
                        }
                        return {
                            type: "Feature",
                            geometry: plot.location.geometry,
                            properties: {
                                name: plot.plot_id,
                                plot_id: plot.plot_id,
                            }
                        };
                    })
                };

                layers.push(new GeoJsonLayer({
                    id: "geojson-layer-plot",
                    data: geoJsonPlots,
                    filled: true,
                    getFillColor: [255, 0, 0],
                    getPointRadius: 5,
                    getLineWidth:0.5,
                    pickable: true,
                    onClick: handleLayerClick
                }));
            }

            if (currentZoom >= 17) {
                const geoJsonSubPlots: GeoJSON = {
                    type: "FeatureCollection",
                    features: geoJsonData
                        .map(plot => plot.sub_plots.map(subPlot => ({
                            type: "Feature",
                            geometry: subPlot.location.geometry,
                            properties: {
                                name: subPlot.idSubPlot,
                                sub_plot_id: subPlot.idSubPlot,
                                parent_plot_id: plot.plot_id
                            }
                        })))
                        .flat()
                };

                layers.push(new GeoJsonLayer({
                    id: "geojson-layer-sub-plot",
                    data: geoJsonSubPlots,
                    filled: true,
                    getFillColor: [0, 0, 255],
                    getPointRadius: 5,
                    getLineWidth: 0.2,
                    pickable: true,
                    onClick: handleLayerClick
                }));
            }

            const geoJsonTrees: GeoJSON = {
                type: "FeatureCollection",
                features: treesJsonData
            }

            if (currentZoom >= 23) {
                layers.push(new GeoJsonLayer({
                    id: "geojson-layer-trees",
                    data: geoJsonTrees,
                    filled: true,
                    getFillColor: (feature: Feature) => {
                        const family = feature.properties?.tree?.species?.family;
                        return treeColor[family] ?? [100, 100, 100];
                    },
                    getPointRadius: 0.2,
                    pickable: true,
                    onClick: handleLayerClick
                }));
            } else if (currentZoom >= 21) {
                layers.push(new GeoJsonLayer({
                    id: "geojson-layer-trees",
                    data: geoJsonTrees,
                    filled: true,
                    getFillColor: (feature: Feature) => {
                        const family = feature.properties?.tree?.species?.family;
                        return treeColor[family] ?? [100, 100, 100];
                    },
                    getPointRadius: 0.5,
                    lineWidthMaxPixels: 0.5,
                    pickable: true,
                    onClick: handleLayerClick
                }));
            } else if (currentZoom >= 19) {
                layers.push(new GeoJsonLayer({
                    id: "geojson-layer-trees",
                    data: geoJsonTrees,
                    filled: true,
                    getFillColor: (feature: Feature) => {
                        const family = feature.properties?.tree?.species?.family;
                        return treeColor[family] ?? [100, 100, 100];
                    },
                    getPointRadius: 1,
                    lineWidthMaxPixels: 0.5,
                    pickable: true,
                    onClick: handleLayerClick
                }));
            }


            layers.push(new TextLayer<TextMap>({
                id: "text-layer-plot-name",
                data: textData,
                getPosition: (tm: TextMap) => tm.coordinates,
                getText: (tm: TextMap) => tm.name,
                getAlignmentBaseline: 'center',
                getColor: [255, 128, 0],
                getSize: 16,
                getTextAnchor: 'middle',
                pickable: true
            }));
        }
        setLayers(layers);
    }

    function handleViewStateChange(params) {
        clearInterval(intervalBearing)
        setMapZoomState({
            coordinates: [params.viewState.longitude, params.viewState.latitude],
            zoom: params.viewState.zoom,
            pitch: params.viewState.pitch,
            bearing: params.viewState.bearing,
        });
    }

    function getColorFromHash(family: string): [number, number, number] {
        let hash = 0;
        for (let i = 0; i < family.length; i++) {
            hash = family.charCodeAt(i) + ((hash << 5) - hash);
        }

        const r = (hash >> 0) & 0xFF;
        const g = (hash >> 8) & 0xFF;
        const b = (hash >> 16) & 0xFF;

        return [r, g, b];
    }

    return (
        <DeckGL
            initialViewState={
            mapZoomState ? {
                longitude: mapZoomState.coordinates[0],
                latitude: mapZoomState.coordinates[1],
                zoom: mapZoomState.zoom,
                pitch: mapZoomState.pitch,
                bearing,
                maxZoom: 24
            } : {
                longitude: -53.97510147,
                latitude: 5.486270905,
                zoom: 10,
                pitch: 0,
                bearing,
                maxZoom: 24
            }}
            controller
            layers={layers}
            onViewStateChange={handleViewStateChange}
        >

            <Map maxZoom={24} reuseMaps mapStyle="https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json" />
        </DeckGL>
    )
}