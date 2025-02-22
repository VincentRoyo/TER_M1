import React, {useEffect} from "react";
import MapGL from "~/components/MapGL";
import type {Locations, PlotLocation} from "~/Types";
import {plotLocationLoader, treesLocationLoader} from "~/loaders";
import type {GeoJSON} from "geojson";


export async function clientLoader(): Promise<Locations> {
    return {plotLocation: await plotLocationLoader(), treesLocation: await treesLocationLoader()};
}

export default function Map({loaderData}: {loaderData: GeoJSON[]}): React.ReactElement {
    const {plotLocation, treesLocation} = loaderData;
    return (
        <>
            <div style={{ width: "100vw", height: "100vh" }}>
                <MapGL geoJsonData={plotLocation} treesJsonData={treesLocation}/>
            </div>
        </>
    )
}