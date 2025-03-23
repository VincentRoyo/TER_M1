import React, {useEffect, useState} from "react";
import API from "~/API";
import {Col, Row, Container, Spinner} from "react-bootstrap";
import "../styles/panel.css"
import type {PopupInfoPlotProps} from "~/Types";


export default function PopupInfoPlot({ plot, tabIndex }: PopupInfoPlotProps): React.ReactElement {

    // TODO : FIXER PROBLEME D'UPDATE EN CHOISISSANT UN AUTRE PLOT + FAIRE LE SUBPLOT

    const [data, setData] = useState<any>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);

    useEffect(() => {
        API.getInfosPlot(plot).then(response => {
            setData(response);
            setIsLoading(false);
        });
    }, [plot]);

    console.log(data)

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
                <div>
                    <p>Cet onglet contient des informations sur la diversité dans le plot.</p>
                    <p>Nombre d'espèces différentes : <br/>
                        Indice de Shannon : <strong>{ data.shannon.toFixed(2) }</strong>
                    </p>
                </div>
            )}

            {tabIndex === 2 && (
                <div>
                    <p>Cet onglet contient des informations sur la densité dans le plot.</p>
                    <p>Densité moyenne : <strong>{ data.density } arbres/ha</strong></p>
                </div>
            )}
        </>
    )
}