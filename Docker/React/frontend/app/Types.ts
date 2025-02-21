import type {GeoJSON} from "geojson";

export interface PlotLocation {
    plot_id: string;
    location: GeoJSON
    sub_plots: SubPlot[]
}

export interface SubPlot {
    idSubPlot: number;
    location: GeoJSON
}

export interface ApiResponse<T> {
    data?: T;
    error?: string;
}

export interface MapGLProps {
    longitude?: number;
    latitude?: number;
    zoom?: number;
    geoJsonData?: PlotLocation[];
}
