import React, {useState} from "react";
import MapGL from "~/components/MapGL";
import type {Locations, MapZoom, PlotLocation, SubPlot} from "~/Types";
import {plotLocationLoader, treesLocationLoader} from "~/loaders";
import SideBar from "~/components/SideBar";
import {getCenter, sortNamePlot, sortNameSubPlot} from "~/utils";

export async function clientLoader(): Promise<Locations> {
    return {plotLocation: await plotLocationLoader(), treesLocation: await treesLocationLoader()};
}

export default function Map({loaderData}: { loaderData: Locations }): React.ReactElement {
    const [mapZoom, setMapZoom] = useState<MapZoom>();
    const [selectedPlot, setSelectedPlot] = useState<string | null>(null);
    const [selectedSubPlot, setSelectedSubPlot] = useState<string | null>(null);

    let {plotLocation, treesLocation} = loaderData;

    plotLocation = plotLocation.map(plot => (
        {
            ...plot,
            sub_plots: [...plot.sub_plots].sort(sortNameSubPlot)
        }
    )).sort(sortNamePlot)

    function handleClickPlot(plot: PlotLocation): void {
        setMapZoom({zoom: 17, coordinates: getCenter(plot.location.geometry.coordinates[0]), pitch: 50})
    }

    function handleClickSubPlot(subPlot: SubPlot): void {
        setMapZoom({zoom: 21, coordinates: getCenter(subPlot.location.geometry.coordinates[0]), pitch: 50})

    }

    return (
        <>
            <div style={{position: "relative", height: "100vh"}}>
                <SideBar elements={plotLocation} handleClickPlot={handleClickPlot}
                         handleClickSubPlot={handleClickSubPlot} selectedPlot={selectedPlot} selectedSubPlot={selectedSubPlot} />
                <MapGL geoJsonData={plotLocation} treesJsonData={treesLocation} mapZoom={mapZoom}
                       onPlotClick={(plotId) => {
                           setSelectedPlot(plotId);
                           setSelectedSubPlot(null);
                       }}
                       onSubPlotClick={(plotId, subPlotId) => {
                           setSelectedPlot(plotId);
                           setSelectedSubPlot(subPlotId);
                       }}/>
            </div>
        </>

    );
}
