import {index, route, type RouteConfig} from "@react-router/dev/routes";

export default [
    index("routes/home.tsx"),
    route("map", "./routes/Map.tsx")
] satisfies RouteConfig;
