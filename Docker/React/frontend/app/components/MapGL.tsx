import React, {useEffect} from "react";
import DeckGL, {ZoomWidget} from "@deck.gl/react";
import {GeoJsonLayer, TextLayer} from "@deck.gl/layers";
import {Map} from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';
import type {GeoJSON, MapGLProps, TextMap} from "~/Types";
import {Layer} from "@deck.gl/core";
import {getCenter} from "~/utils";

export default function MapGL({
                                  mapZoom,
                                  geoJsonData,
                                  treesJsonData,
                              }: MapGLProps): React.ReactElement {


    const [intervalBearing, setIntervalBearing] = React.useState<NodeJS.Timeout>();
    const [bearing, setBearing] = React.useState<number>(0);

    useEffect(() => {

        if (mapZoom.zoom === 17) {
            const interval = setInterval(() => {
                setBearing((prevState) =>(prevState+1)%360)
            }, 50)

            setIntervalBearing(interval);
            return () => clearInterval(interval);
        }

    }, [mapZoom])

    function getLayers(): Layer[] {
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

            const geoJsonSubPlots: GeoJSON = {
                type: "FeatureCollection",
                features: geoJsonData.map(plot => plot.sub_plots.map(subPlot => subPlot.location)).flat()
            };

            const geoJsonTrees: GeoJSON = {
                type: "FeatureCollection",
                features: treesJsonData
            }

            layers.push(new GeoJsonLayer({
                id: "geojson-layer-plot",
                data: geoJsonPlots,
                filled: true,
                getFillColor: [255, 0, 0],
                getPointRadius: 100
            }));

            layers.push(new GeoJsonLayer({
                id: "geojson-layer-sub-plot",
                data: geoJsonSubPlots,
                filled: true,
                getFillColor: [0, 0, 255],
                getPointRadius: 100
            }));
            

            layers.push(new GeoJsonLayer({
                id: "geojson-layer-trees",
                data: geoJsonTrees,
                filled: true,
                getFillColor: [144, 238, 144],
                getPointRadius: 1.5
            }));


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

        return layers;
    }

    function handleViewStateChange() {
        setBearing(0);
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
            layers={
                getLayers()
            }
            onViewStateChange={handleViewStateChange}
        >

            <Map reuseMaps mapStyle="https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json" />
        </DeckGL>
    )
}