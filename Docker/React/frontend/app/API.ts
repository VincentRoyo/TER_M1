import {type ApiResponse, type Feature, HttpMethods, type PlotLocation} from "~/Types";
import type {GeoJSON} from "geojson";

const API_URL: string = import.meta.env.VITE_APP_API_URL;

const config = {
    url: API_URL,
    options: {
        headers: { 'content-type': 'application/json' },
    },
};

async function handleErrors(response: Response): Promise<Response> {
    if (!response.ok) {
        try {
            const result = await response.json();
            const errorMessage: string = result.message ?? result['hydra:description'] ?? 'Unknown error';
            throw new Error(errorMessage);
        } catch (error) {
            throw new Error("Failed to parse error response");
        }
    }
    return response;
}

const sendRequest = async <T>(endpoint: string, method: HttpMethods, payload?: Record<string, any>): Promise<ApiResponse<T>> => {
    let request: RequestInit = {method, headers: {}, body: null};

    const contentType = {'Content-Type': method === HttpMethods.PATCH ? 'application/merge-patch+json' : 'application/json'};

    request.method = method;
    request.headers = {
        ...contentType,
    }

    if(payload){
        request.body = JSON.stringify({ ...payload });
    }

    const response = await fetch(`${config.url}/${endpoint}`, request);

    await handleErrors(response);

    return (await response.json());
}

const API = {
    getPlotLocation: async (): ApiResponse<PlotLocation[]> => {
        try {
            const response = await sendRequest(`geoplot`, HttpMethods.GET);
            const data: PlotLocation[] = response as PlotLocation[];
            return {data};
        } catch (error: Error) {
            return {error: error.message};
        }
    },
    getTreesLocation: async (): ApiResponse<Feature[]> => {
        try {
            const response = await fetch(`${API_URL}/allgeo`, {method: "GET"});
            if (!response.ok) return {error: "Error fetching trees"};
            const data: Feature[] = (await response.json()) as Feature[];
            return {data};
        } catch (error: Error) {
            return {error: error.message};
        }
    }
}


export default API;