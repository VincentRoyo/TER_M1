import type {Feature, GeoJSON} from "geojson";

export interface PlotLocation {
    plot_id: string;
    location: Feature
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
    treesJsonData?: GeoJSON[];
}

export interface TextMap {
    name: string;
    coordinates: [number, number];
}

export interface Locations {
    plotLocation: PlotLocation[];
    treesLocation: GeoJSON[];
}
