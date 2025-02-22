import type {ApiResponse, PlotLocation} from "~/Types";
import API from "~/API";
import type {GeoJSON} from "geojson";

export async function plotLocationLoader(): Promise<PlotLocation[]> {
    const res: ApiResponse<PlotLocation[]> = await API.getPlotLocation();
    if (res.error) {
        console.error(res.error);
        return [];
    } else return res.data;
}

export async function treesLocationLoader(): Promise<GeoJSON[]> {
    const res: ApiResponse<GeoJSON[]> = await API.getTreesLocation();
    if (res.error) {
        console.error(res.error);
        return [];
    } else return res.data;
}
