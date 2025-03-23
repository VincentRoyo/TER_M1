import {
    type ApiResponse,
    type Feature,
    HttpMethods,
    type InfoPlot,
    type InfoSubPlot,
    type PlotLocation,
    type Point
} from "~/Types";

const API_URL: string = import.meta.env.VITE_APP_API_URL;

const config = {
    url: API_URL,
    options: {
        headers: {'content-type': 'application/json'},
    },
};

async function handleErrors(response: Response): Promise<Response> {
    if (!response.ok) {
        try {
            const result: any = await response.json();
            const errorMessage: string = result.message ?? result['hydra:description'] ?? 'Unknown error';
            throw new Error(errorMessage);
        } catch (error) {
            throw new Error(`Error with request : ${JSON.stringify(error)}`);
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

    if (payload) {
        request.body = JSON.stringify({...payload});
    }

    const response = await fetch(`${config.url}/${endpoint}`, request);

    try {
        await handleErrors(response);
    } catch (error: any) {
        return {error: error.message}
    }

    return {data: (await response.json())};
}

const API = {
    getPlotLocation: async (): Promise<PlotLocation[] | undefined> => {
        const response: ApiResponse<PlotLocation[]> = await sendRequest<PlotLocation[]>(`geoplot`, HttpMethods.GET);
        if (response.data) {
            return response.data;
        } else return undefined;
    },
    getTreesLocation: async (): ApiResponse<Feature<Point>[]> => { //TODO FAIRE PAREIL QUE LA PREMIERE METHODE
        try {
            const response = await fetch(`${API_URL}/allgeo`, {method: "GET"});
            if (!response.ok) return {error: "Error fetching trees"};
            const data: Feature<Point>[] = (await response.json()) as Feature<Point>[];
            return {data};
        } catch (error: Error) {
            return {error: error.message};
        }
    },
    getInfosPlot: async (idPlot: string): Promise<InfoPlot> => {
        const response: ApiResponse<InfoPlot> = await sendRequest<InfoPlot>(`infoplot/${idPlot}`, HttpMethods.GET);
        if (response.data) {
            return response.data;
        } else return undefined;
    },
    getInfosSubPlot: async (idSubPlot: string): Promise<InfoSubPlot> => {
        const response: ApiResponse<InfoSubPlot> = await sendRequest<InfoSubPlot>(`infosubplot/${idSubPlot}`, HttpMethods.GET);
        if (response.data) {
            return response.data;
        } else return undefined;
    }
}


export default API;