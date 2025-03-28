import type {Feature, PlotLocation, Point} from "~/Types";
import API from "~/API";

export async function plotLocationLoader(): Promise<PlotLocation[]> {
    const res: PlotLocation[] | undefined = await API.getPlotLocation();
    if (res) {
        return res;
    } else return [];
}

export async function treesLocationLoader(): Promise<Feature<Point>[]> {
    const res: Feature<Point>[] = await API.getTreesLocation();
    if (res) {
        return res;
    } else return [];
}
