import type {ApiResponse, Feature, PlotLocation, Point} from "~/Types";
import API from "~/API";

export async function plotLocationLoader(): Promise<PlotLocation[]> {
    const res: PlotLocation[] | undefined = await API.getPlotLocation();
    if (res) {
        return res;
    } else return [];
}

export async function treesLocationLoader(): Promise<Feature<Point>[]> {
    //TODO CHANGER COMME LA REQUETE D'AVANT
    const res: ApiResponse<Feature<Point>[]> = await API.getTreesLocation();
    if (res.error) {
        console.error(res.error);
        return [];
    } else return res.data;
}
