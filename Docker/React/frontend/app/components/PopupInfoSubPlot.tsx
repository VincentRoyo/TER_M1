import React, {useEffect, useState} from "react";
import type {PopupInfoSubPlotProps} from "~/Types";
import API from "~/API";
import {Col, Container, Row, Spinner} from "react-bootstrap";

export default function PopupInfoSubPlot({ subPlot, tabIndex }: PopupInfoSubPlotProps): React.ReactElement {

    const [data, setData] = useState<any>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);

    useEffect(() => {
        API.getInfosSubPlot(subPlot).then(response => {
            setData(response);
            setIsLoading(false);
        });
    }, []);

    if (isLoading) {
        return (
            <div className="loading-container">
                <Spinner animation="border" role="status">
                    <span className="visually-hidden">Chargement...</span>
                </Spinner>
            </div>
        );
    }

    return (
        <>
            {tabIndex === 0 && (
                <div>
                    <p>Cet onglet contient les informations générales sur le sub-plot.</p>
                    <p>Forêt : <strong>{ data.forest }</strong> <br/>
                        Plot : <strong>{ data.plot })</strong>
                    </p>
                    <Container className="infos">
                        <Row>
                            <Col xs={6}><p className="panelLabel">Superficie</p></Col>
                            <Col xs={6}><p className="panelLabel">Nombre d'arbres</p></Col>
                        </Row>
                        <Row>
                            <Col xs={6}><p className="panelValue">{ data.area }</p></Col>
                            <Col xs={6}><p className="panelValue">{ data.nbTrees }</p></Col>
                        </Row>
                    </Container>
                </div>
            )}

            {tabIndex === 1 && (
                <div>
                    <p>Cet onglet contient des informations sur la diversité dans le sub-plot.</p>
                    <p>Nombre d'espèces différentes : <strong>{ data.shannon }</strong></p>
                </div>
            )}

            {tabIndex === 2 && (
                <div>
                    <p>Cet onglet contient des informations sur la densité dans le sub-plot.</p>
                    <p>Densité moyenne : <strong>{ data.density }</strong></p>
                </div>
            )}
        </>
    )
}