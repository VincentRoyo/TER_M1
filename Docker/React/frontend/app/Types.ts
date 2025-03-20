import type {
    GeoJsonObject,
    GeoJsonProperties,
    GeometryCollection,
    LineString,
    MultiLineString,
    MultiPoint,
    MultiPolygon,
    Point
} from "geojson";


export type Geometry = Point | MultiPoint | LineString | MultiLineString | Polygon | MultiPolygon | GeometryCollection;

export interface FeatureCollection<G extends Geometry | null = Geometry, P = GeoJsonProperties> extends GeoJsonObject {
    type: "FeatureCollection";
    features: Array<Feature<G, P>>;
}

export type GeoJSON<G extends Geometry | null = Geometry, P = GeoJsonProperties> =
    | G
    | Feature<G, P>
    | FeatureCollection<G, P>;

export interface Polygon extends GeoJsonObject {
    type: "Polygon";
    coordinates: Point[][];
}

export interface Feature<G extends Geometry | null = Geometry, P = GeoJsonProperties> extends GeoJsonObject {
    type: "Feature";
    geometry: G;
    id?: string | number | undefined;
    properties: P;
}

export interface PlotLocation {
    plot_id: string;
    location: Feature<Polygon>
    sub_plots: SubPlot[]
}

export interface SubPlot {
    idSubPlot: number;
    location: Feature<Polygon>
}

export interface ApiResponse<T> {
    data?: T;
    error?: string;
}

export interface MapGLProps {
    mapZoom: MapZoom;
    geoJsonData?: PlotLocation[];
    treesJsonData?: Feature[];
}

export interface TextMap {
    name: string;
    coordinates: [number, number];
}

export interface Locations {
    plotLocation: PlotLocation[];
    treesLocation: Feature<Point>[];
}

export interface SideBarProps {
    elements: string[],
    handleClickPlot: (plotName: string) => void
}

export interface MapZoom {
    zoom: number,
    pitch: number,
    coordinates: Point
}

export enum HttpMethods {
    GET = 'GET',
    POST = 'POST',
    PATCH = 'PATCH',
    DELETE = 'DELETE',
}
