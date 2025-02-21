import type {ApiResponse, PlotLocation} from "~/Types";

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
    }
}


export default API;