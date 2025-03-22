import type {PlotLocation, Point, SubPlot} from "~/Types";


export function getCenter(points: Point[] | undefined): Point {
    if (!points || points.length === 0) return [0,0];

    let sumX = 0, sumY = 0;

    points.forEach(point => {
        sumX += point[0];
        sumY += point[1];
    });

    return [sumX / points.length, sumY / points.length];
}

export function sortNamePlot(a: PlotLocation, b: PlotLocation): number {
    const nameA: string = a.plot_id;
    const nameB: string = b.plot_id;

    const numA = parseFloat(nameA);
    const numB = parseFloat(nameB);

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
        return nameA.localeCompare(nameB, undefined, {numeric: true}); // Tri alphabétique intelligent
    }
}

export function sortNameSubPlot(a: SubPlot, b: SubPlot): number {
    return a.idSubPlot - b.idSubPlot;
}