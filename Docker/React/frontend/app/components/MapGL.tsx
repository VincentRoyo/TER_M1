import React from "react";
import DeckGL from "@deck.gl/react";
import {GeoJsonLayer} from "@deck.gl/layers";
import {Map} from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';
import type {MapGLProps} from "~/Types";
import type {GeoJSON} from "geojson";

export default function MapGL({
                                  longitude = -53.97510147,
                                  latitude = 5.486270905,
                                  zoom = 10,
                                  geoJsonData
                              }: MapGLProps): React.ReactElement {

    function getJsonLayer(): GeoJsonLayer[] {
        let geoJsonLayers: GeoJsonLayer[] = [];

        if (geoJsonData) {

            const geoJsonPlots: GeoJSON = {
                type: "FeatureCollection",
                features: geoJsonData.map(plot => plot.location)
            };

            const geoJsonSubPlots: GeoJSON = {
                type: "FeatureCollection",
                features: geoJsonData.map(plot => plot.sub_plots.map(subPlot => subPlot.location)).flat()
            };

            geoJsonLayers.push(new GeoJsonLayer({
                id: "geojson-layer-plot",
                data: geoJsonPlots,
                filled: true,
                getFillColor: [255, 0, 0],
                getPointRadius: 100
            }));


            geoJsonLayers.push(new GeoJsonLayer({
                id: "geojson-layer-sub-plot",
                data: geoJsonSubPlots,
                filled: true,
                getFillColor: [0, 0, 255],
                getPointRadius: 100
            }));
        }

        return geoJsonLayers;
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
                getJsonLayer()
            }
        >
            <Map reuseMaps mapStyle="https://basemaps.cartocdn.com/gl/dark-matter-nolabels-gl-style/style.json"/>
        </DeckGL>
    )
}