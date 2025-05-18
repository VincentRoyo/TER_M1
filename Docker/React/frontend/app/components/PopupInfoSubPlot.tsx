import React, {useEffect, useState} from "react";
import type {InfoSubPlot, PopupInfoSubPlotProps} from "~/Types";
import API from "~/API";
import {Col, Container, Row, Spinner} from "react-bootstrap";

export default function PopupInfoSubPlot({plot, subPlot, tabIndex }: PopupInfoSubPlotProps): React.ReactElement {

    const [data, setData] = useState<InfoSubPlot | undefined>();
    const [isLoading, setIsLoading] = useState<boolean>(true);

    useEffect(() => {
        API.getInfosSubPlot(plot, subPlot).then(response => {
            setData(response);
            setIsLoading(false);
        });
    }, [subPlot]);

    if (isLoading) {
        return (
            <div className="loading-container">
                <Spinner role="status"></Spinner>
            </div>
        );
    }

    return (
        <>
            {data ?
                <>
                    {tabIndex === 0 && (
                        <div>
                            <p>Cet onglet contient les informations générales sur le sous-plot.</p>
                            <p>Forêt : <strong>{ data.forest }</strong> <br/>
                                Plot : <strong>{ data?.idPlot }</strong> <br/>
                            </p>
                            <Container className="infos">
                                <Row>
                                    <Col xs={6}><p className="panelLabel">Nombre d'arbres</p></Col>
                                </Row>
                                <Row>
                                    <Col xs={6}><p className="panelValue">{ data.nbTrees }</p></Col>
                                </Row>
                            </Container>
                        </div>
                    )}

                    {tabIndex === 1 && (
                        <div className="overflow-auto" style={{ maxHeight: '50vh' }}>
                            <p>Cet onglet contient des informations sur la diversité dans le sous-plot.</p>
                            <p>Nombre d'espèces différentes : <strong>{ data.species_distribution.length }</strong>  <br/>
                                Indice de Shannon : <strong>{ data.shannon.toFixed(2) }</strong> <br/>
                            </p>
                            <table className="table">
                                <thead>
                                <tr>
                                    <th>Espèce</th>
                                    <th>Nombre</th>
                                    <th>Distribution</th>
                                </tr>
                                </thead>
                                <tbody>
                                {data.species_distribution.sort((a,b) => b.count - a.count).map( (info) =>
                                    <tr key={info.species}>
                                        <td>{info.species ? info.species : "Inconnu"} </td>
                                        <td>{info.count} {info.count == 1 ? "arbre" : "arbres"} </td>
                                        <td><strong>{(info.distribution * 100).toFixed(2) }%</strong></td>
                                    </tr>
                                )}
                                </tbody>
                            </table>
                        </div>
                    )}
                </> : <></>
            }
        </>
    )
}