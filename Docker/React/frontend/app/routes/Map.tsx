import React, {useState} from "react";
import MapGL from "~/components/MapGL";
import type {Locations, MapZoom} from "~/Types";
import {plotLocationLoader, treesLocationLoader} from "~/loaders";
import SideBar from "~/components/SideBar";
import {getCenter} from "~/utils";

export async function clientLoader(): Promise<Locations> {
    return {plotLocation: await plotLocationLoader(), treesLocation: await treesLocationLoader()};
}

export default function Map({loaderData}: { loaderData: Locations }): React.ReactElement {
    const [mapZoom, setMapZoom] = useState<MapZoom>({
        zoom: 10,
        coordinates: {
            type: "Point",
            coordinates: [-53.97510147, 5.486270905],
        },
        pitch: 0
    });

    const {plotLocation, treesLocation} = loaderData;
    const plotNames: string[] = plotLocation.map(plot => plot.plot_id);


    function handleClickPlot(plotName: string): void {
        const plot = plotLocation.find(plot => plot.plot_id === plotName);
        setMapZoom({zoom: 17, coordinates: getCenter(plot?.location.geometry.coordinates[0]), pitch: 50})
    }

    return (
        <>
            <div style={{position: "relative", height: "100vh"}}>
                <SideBar elements={plotNames} handleClickPlot={handleClickPlot}/>
                <MapGL geoJsonData={plotLocation} treesJsonData={treesLocation} mapZoom={mapZoom}/>
            </div>
        </>

    );
}
