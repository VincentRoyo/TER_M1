import type {ApiResponse, PlotLocation} from "~/Types";
import type {GeoJSON} from "geojson";

const API_URL: string = import.meta.env.VITE_APP_API_URL;

const API = {
    getPlotLocation: async (): ApiResponse<PlotLocation[]> => {
        try {
            const response = await fetch(`${API_URL}/geoplot`, {method: "GET"});
            if (!response.ok) return {error: "Error fetching location of plot"};
            const data: PlotLocation[] = (await response.json()) as PlotLocation[];
            return {data};
        } catch (error: Error) {
            return {error: error.message};
        }
    },
    getTreesLocation: async (): ApiResponse<GeoJSON[]> => {
        try {
            const response = await fetch(`${API_URL}/allgeo`, {method: "GET"});
            if (!response.ok) return {error: "Error fetching trees"};
            const data: GeoJSON[] = (await response.json()) as GeoJSON[];
            return {data};
        } catch (error: Error) {
            return {error: error.message};
        }
    }
}


export default API;