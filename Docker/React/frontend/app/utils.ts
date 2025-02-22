import type {Point} from "geojson";

export function getCenter(points: Point[]): [number, number] {
    if (points.length === 0) return [0,0];
    let sumX = 0, sumY = 0;

    points.forEach(point => {
        sumX += point[0];
        sumY += point[1];
    });

    return [
        sumX/points.length,
        sumY/points.length,
    ]
}