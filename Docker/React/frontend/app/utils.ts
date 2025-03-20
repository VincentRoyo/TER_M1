import type {Point} from "geojson";

export function getCenter(points: Point[] | undefined): Point {
    if (!points || points.length === 0) return {
        type: "Point",
        coordinates: []
    }

    let sumX = 0, sumY = 0;

    points.forEach(point => {
        sumX += point[0];
        sumY += point[1];
    });

    return {
        type: "Point",
        coordinates: [sumX / points.length, sumY / points.length]
    }
}

export function sortNamePlot(a: string, b: string): number {
    const numA = parseFloat(a);
    const numB = parseFloat(b);

    // Vérifier si les deux éléments sont des nombres
    const isNumA = !isNaN(numA);
    const isNumB = !isNaN(numB);

    if (isNumA && isNumB) {
        return numA - numB; // Tri numérique
    } else if (isNumA) {
        return -1; // Les nombres avant les textes
    } else if (isNumB) {
        return 1; // Les textes après les nombres
    } else {
        return a.localeCompare(b, undefined, {numeric: true}); // Tri alphabétique intelligent
    }
}