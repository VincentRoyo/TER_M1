import React, {type SyntheticEvent, useEffect, useState} from "react";
import DeckGL from "@deck.gl/react";
import {GeoJsonLayer, TextLayer} from "@deck.gl/layers";
import {Map} from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';
import type {Feature, GeoJSON, MapGLProps, Point, TextMap} from "~/Types";
import {Layer, type PickingInfo} from "@deck.gl/core";
import {getCenter} from "~/utils";

/**
 * TODO REGARDER LE PROBLEME DE ZOOM QUAND ON CLIQUE SUR UN PLOT DANS LA SIDEBAR (POSSIBLE QUE L'UTILISATION DE MAPZOOM SOIT UTILISEE AU LIEU DU ZOOM DE DECKGL DE L'UTILISATEUR CAR GETLAYERS CHANGE L'ETAT ET REFRESH LE COMPOSANT)
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

    function handleLayerClick(info: PickingInfo): void {
        if (info.object?.properties?.name) {
            const plotId = info.object.properties.parent_plot_id ?? info.object.properties.name;
            const subPlotId = info.object.properties.sub_plot_id || null;

            if (subPlotId) {
                console.log(plotId);
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
                    getPointRadius: 100,
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
                    getPointRadius: 100,
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
                    getFillColor: [144, 238, 144],
                    getPointRadius: 0.2,
                    lineWidthMaxPixels: 5,
                    pickable: true,
                    onClick: handleLayerClick
                }));
            } else if (currentZoom >= 21) {
                layers.push(new GeoJsonLayer({
                    id: "geojson-layer-trees",
                    data: geoJsonTrees,
                    filled: true,
                    getFillColor: [144, 238, 144],
                    getPointRadius: 0.5,
                    lineWidthMaxPixels: 5,
                    pickable: true,
                    onClick: handleLayerClick
                }));
            } else if (currentZoom >= 19) {
                layers.push(new GeoJsonLayer({
                    id: "geojson-layer-trees",
                    data: geoJsonTrees,
                    filled: true,
                    getFillColor: [144, 238, 144],
                    getPointRadius: 1,
                    lineWidthMaxPixels: 10,
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
        getLayers(params.viewState.zoom);
        clearInterval(intervalBearing);
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