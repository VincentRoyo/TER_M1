import React, {useState} from "react";
import MapGL from "~/components/MapGL";
import type {Locations, MapZoom, PlotLocation, SubPlot} from "~/Types";
import {plotLocationLoader, treesLocationLoader} from "~/loaders";
import SideBar from "~/components/SideBar";
import {getCenter, sortNamePlot, sortNameSubPlot} from "~/utils";
import PopupInfo from "~/components/PopupInfo";

export async function clientLoader(): Promise<Locations> {
    return {plotLocation: await plotLocationLoader(), treesLocation: await treesLocationLoader()};
}

export default function Map({loaderData}: { loaderData: Locations }): React.ReactElement {
    const [mapZoom, setMapZoom] = useState<MapZoom>();
    const [selectedPlot, setSelectedPlot] = useState<string | null>(null);
    const [selectedSubPlot, setSelectedSubPlot] = useState<string | null>(null);

    /*
        States pour la popup d'infos
     */
    const [showPopup, setShowPopup] = useState<boolean>(false);
    const [selectedPlotForPop, setSelectedPlotForPop] = useState<string | undefined>();
    const [selectedPlotForSubPop, setSelectedPlotForSubPop] = useState<string | undefined>();


    let {plotLocation, treesLocation, treesInfo} = loaderData;

    plotLocation = plotLocation.map(plot => (
        {
            ...plot,
            sub_plots: [...plot.sub_plots].sort(sortNameSubPlot)
        }
    )).sort(sortNamePlot);

    function handleClickPlot(plot: PlotLocation): void {
        setMapZoom({zoom: 17, coordinates: getCenter(plot.location.geometry.coordinates[0]), pitch: 50})
        setSelectedPlotForPop(plot.plot_id);
        setSelectedPlotForSubPop(undefined);
    }

    function handleClickSubPlot(plot: PlotLocation, subPlot: SubPlot): void {
        setMapZoom({zoom: 21, coordinates: getCenter(subPlot.location.geometry.coordinates[0]), pitch: 50});
        setSelectedPlotForSubPop(subPlot.idSubPlot.toString());
        setSelectedPlotForPop(plot.plot_id);
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

                <PopupInfo plot={selectedPlotForPop} subPlot={selectedPlotForSubPop}/>
            </div>
        </>

    );
}
