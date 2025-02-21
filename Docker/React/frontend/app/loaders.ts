import type {ApiResponse, PlotLocation} from "~/Types";
import API from "~/API";

export async function plotLocationLoader(): Promise<PlotLocation[]> {
    const res: ApiResponse<PlotLocation[]> = await API.getPlotLocation();
    if (res.error) {
        console.error(res.error);
        return [];
    } else return res.data;
}
