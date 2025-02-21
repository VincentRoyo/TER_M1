import React from "react";
import MapGL from "~/components/MapGL";
import type {PlotLocation} from "~/Types";
import {plotLocationLoader} from "~/loaders";

export async function clientLoader(): Promise<PlotLocation[]> {
    return plotLocationLoader();
}

export default function Map({loaderData}: {loaderData: PlotLocation[]}): React.ReactElement {
    return (
        <>
            <div style={{ width: "100vw", height: "100vh" }}>
                <MapGL geoJsonData={loaderData}/>
            </div>
        </>
    )
}