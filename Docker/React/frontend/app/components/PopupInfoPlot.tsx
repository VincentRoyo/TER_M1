import React, {useEffect, useState} from "react";
import API from "~/API";
import {Col, Row, Container, Spinner} from "react-bootstrap";
import "../styles/panel.css"
import type {PopupInfoPlotProps} from "~/Types";


export default function PopupInfoPlot({ plot, tabIndex }: PopupInfoPlotProps): React.ReactElement {

    const [data, setData] = useState<any>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);

    useEffect(() => {
        setIsLoading(true);
        API.getInfosPlot(plot).then(response => {
            setData(response);
            setIsLoading(false);
        });
    }, [plot]);

    if (isLoading) {
        return (
            <div className="loading-container">
                <Spinner role="status"></Spinner>
            </div>
        );
    }

    return (
        <>
            {tabIndex === 0 && (
                <div>
                    <p>Cet onglet contient les informations générales sur le plot.</p>
                    <p>Forêt : <strong>{ data.forest }</strong></p>
                    <Container className="infos">
                        <Row>
                            <Col xs={6}><p className="panelLabel">Superficie</p></Col>
                            <Col xs={6}><p className="panelLabel">Nombre d'arbres</p></Col>
                        </Row>
                        <Row>
                            <Col xs={6}><p className="panelValue">{ data.area } ha</p></Col>
                            <Col xs={6}><p className="panelValue">{ data.nbTrees }</p></Col>
                        </Row>
                    </Container>
                </div>
            )}

            {tabIndex === 1 && (
                <div className="overflow-auto" style={{ maxHeight: '50vh' }}>
                    <p>Cet onglet contient des informations sur la diversité dans le plot.</p>
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

            {tabIndex === 2 && (
                <div>
                    <p>Cet onglet contient des informations sur la densité dans le plot.</p>
                    <p>Densité moyenne : <strong>{ data.density.toFixed(0) } arbres/ha</strong></p>
                </div>
            )}
        </>
    )
}