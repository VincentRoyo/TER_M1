import React, {useState} from "react";
import type {PopupInfoProps} from "~/Types";
import NavBar from "~/components/NavBar";
import PopupInfoPlot from "~/components/PopupInfoPlot";
import PopupInfoSubPlot from "~/components/PopupInfoSubPlot";
import {Offcanvas} from "react-bootstrap";

export default function PopupInfo({subPlot, plot}: PopupInfoProps): React.ReactElement {

    const show: boolean = plot || subPlot;

    const [tabIndex, setTabIndex] = useState<number>(0);

    const tabPlot = ["Général", "Diversité", "Densité"];
    const tabSubPlot = ["Général", "Diversité"];

    return (
            <Offcanvas
                show={show}
                placement="end"
                backdrop={false}
                scroll={true}
                style={{
                    position: "absolute",
                    top: 20,
                    right: 20,
                    width: "40vh",
                    height: "fit-content",
                    zIndex: 1000,
                    overflowY: 'auto',
                    border: "none"
                }}
            >
                <Offcanvas.Header>
                    <Offcanvas.Title>{subPlot ? `Informations du sous-plot ${subPlot}` : `Informations du plot ${plot}`}</Offcanvas.Title>
                </Offcanvas.Header>
                    {subPlot && plot ? (
                        <NavBar tab={tabSubPlot} tabIndex={tabIndex} setTabIndex={setTabIndex} />
                    ) : (
                        <NavBar tab={tabPlot} tabIndex={tabIndex} setTabIndex={setTabIndex} />
                    )}
                <Offcanvas.Body>
                    {subPlot && plot ? (
                        <PopupInfoSubPlot plot={plot} subPlot={subPlot} tabIndex={tabIndex} />
                    ) : (
                        plot && <PopupInfoPlot plot={plot} tabIndex={tabIndex} />
                    )}
                </Offcanvas.Body>
            </Offcanvas>
    )
}