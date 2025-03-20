import React, {useEffect} from "react";
import DeckGL from "@deck.gl/react";
import {GeoJsonLayer, TextLayer} from "@deck.gl/layers";
import {Map} from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';
import type {GeoJSON, MapGLProps, TextMap} from "~/Types";
import {Layer} from "@deck.gl/core";
import {getCenter} from "~/utils";

/**
 * TODO REGARDER LE PROBLEME DE ZOOM QUAND ON CLIQUE SUR UN PLOT DANS LA SIDEBAR (POSSIBLE QUE L'UTILISATION DE MAPZOOM SOIT UTILISEE AU LIEU DU ZOOM DE DECKGL DE L'UTILISATEUR CAR GETLAYERS CHANGE L'ETAT ET REFRESH LE COMPOSANT)
 * @param mapZoom
 * @param geoJsonData
 * @param treesJsonData
 * @constructor
 */
export default function MapGL({
                                  mapZoom,
                                  geoJsonData,
                                  treesJsonData,
                              }: MapGLProps): React.ReactElement {

    const [layers, setLayers] = React.useState<Layer[]>([]);
    const [intervalBearing, setIntervalBearing] = React.useState<NodeJS.Timeout>();
    const [bearing, setBearing] = React.useState<number>(0);

    useEffect(() => {
        if (mapZoom.zoom === 17) {
            const interval = setInterval(() => {
                setBearing((prevState) =>(prevState+0.5)%360)
            }, 20)
            getLayers();
            setIntervalBearing(interval);
            return () => clearInterval(interval);
        }
    }, [mapZoom])

    useEffect(() => {
        getLayers();
    }, []);

    function getLayers(currentZoom: number = mapZoom.zoom): void {
        const layers: Layer[] = [];
        const textData: TextMap[] = [];

        if (geoJsonData && treesJsonData) {

            const geoJsonPlots: GeoJSON = {
                type: "FeatureCollection",
                features: geoJsonData.map(plot => {
                    if (plot.location.geometry.type === "Polygon") {
                        const coords: number[] = getCenter(plot.location.geometry.coordinates[0]).coordinates;
                        textData.push({
                            name: plot.plot_id.normalize("NFD").replace(/[\u0300-\u036f]/g, ""),
                            coordinates: [coords[0], coords[1]]
                        });
                    }
                    return plot.location;
                })
            };

            layers.push(new GeoJsonLayer({
                id: "geojson-layer-plot",
                data: geoJsonPlots,
                filled: true,
                getFillColor: [255, 0, 0],
                getPointRadius: 100
            }));

            if (currentZoom >= 17) {
                const geoJsonSubPlots: GeoJSON = {
                    type: "FeatureCollection",
                    features: geoJsonData.map(plot => plot.sub_plots.map(subPlot => subPlot.location)).flat()
                };

                layers.push(new GeoJsonLayer({
                    id: "geojson-layer-sub-plot",
                    data: geoJsonSubPlots,
                    filled: true,
                    getFillColor: [0, 0, 255],
                    getPointRadius: 100
                }));
            }

            if (currentZoom >= 19) {
                const geoJsonTrees: GeoJSON = {
                    type: "FeatureCollection",
                    features: treesJsonData
                }

                layers.push(new GeoJsonLayer({
                    id: "geojson-layer-trees",
                    data: geoJsonTrees,
                    filled: true,
                    getFillColor: [144, 238, 144],
                    getPointRadius: 1.5
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
            initialViewState={{
                longitude: mapZoom.coordinates.coordinates[0],
                latitude: mapZoom.coordinates.coordinates[1],
                zoom: mapZoom.zoom,
                pitch: mapZoom.pitch,
                bearing
            }}
            controller
            layers={layers}
            onViewStateChange={handleViewStateChange}
        >

            <Map reuseMaps mapStyle="https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json" />
        </DeckGL>
    )
}