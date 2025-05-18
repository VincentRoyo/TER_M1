import type {
    GeoJsonObject,
    GeoJsonProperties,
    GeometryCollection,
    LineString,
    MultiLineString,
    MultiPoint,
    MultiPolygon
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

export type Point = [number, number];

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
    mapZoom: MapZoom | undefined;
    geoJsonData?: PlotLocation[];
    treesJsonData?: Feature[];
    onPlotClick: (plotId: string) => void;
    onSubPlotClick: (plotId: string, subPlotId: string) => void;
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
    elements: PlotLocation[];
    handleClickPlot: (plot: PlotLocation) => void;
    handleClickSubPlot: (plot: PlotLocation, subPlot: SubPlot) => void;
    selectedPlot: string | null;
    selectedSubPlot: string | null;
}

export interface MapZoom {
    zoom: number,
    pitch: number,
    coordinates: Point
}

export interface PopupInfoProps {
    plot?: string;
    subPlot?: string;
}

export interface TabProps {
    tab: string[];
    tabIndex: number;
    setTabIndex: (index: number) => void;
}

export interface TabProps {
    tabIndex: number;
    setTabIndex: (index: number) => void;
}

export interface PopupInfoPlotProps {
    plot: string;
    tabIndex: number;
}

export interface PopupInfoSubPlotProps {
    plot: string;
    subPlot: string;
    tabIndex: number;
}

export interface InfoPlot {
    idPlot: string;
    forest: string;
    area: number;
    nbTrees: number;
    density: number;
    shannon: number;
    species_distribution: SpeciesDistribution[];
}

export interface InfoSubPlot {
    idSubPlot: string;
    idPlot: string;
    forest: string;
    area: number;
    nbTrees: number;
    density: number;
    shannon: number;
    species_distribution: SpeciesDistribution[];
}

export interface SpeciesDistribution {
    species: string;
    count: number;
    distribution: number;
}

export enum HttpMethods {
    GET = 'GET',
    POST = 'POST',
    PATCH = 'PATCH',
    DELETE = 'DELETE',
}
