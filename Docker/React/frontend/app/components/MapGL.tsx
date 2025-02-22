import React from "react";
import DeckGL, {ZoomWidget} from "@deck.gl/react";
import {GeoJsonLayer, TextLayer} from "@deck.gl/layers";
import {Map} from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';
import type {MapGLProps, TextMap} from "~/Types";
import type {GeoJSON} from "geojson";
import {Layer} from "@deck.gl/core";
import {getCenter} from "~/utils";

export default function MapGL({
                                  longitude = -53.97510147,
                                  latitude = 5.486270905,
                                  zoom = 10,
                                  geoJsonData,
                                  treesJsonData,
                              }: MapGLProps): React.ReactElement {



    function getLayers(): Layer[] {
        const layers: Layer[] = [];
        const textData: TextMap[] = [];

        if (geoJsonData && treesJsonData) {

            const geoJsonPlots: GeoJSON = {
                type: "FeatureCollection",
                features: geoJsonData.map(plot => {
                    if (plot.location.geometry.type === "Polygon") {
                        textData.push({
                            name: plot.plot_id.normalize("NFD").replace(/[\u0300-\u036f]/g, ""),
                            coordinates: getCenter(plot.location.geometry.coordinates[0])
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



    return (
        <DeckGL
            initialViewState={{
                longitude,
                latitude,
                zoom
            }}
            controller
            layers={
                getLayers()
            }
        >

            <Map reuseMaps mapStyle="https://basemaps.cartocdn.com/gl/dark-matter-nolabels-gl-style/style.json"/>
            <ZoomWidget id="zoom-widget" placement="top-left"/>
        </DeckGL>
    )
}