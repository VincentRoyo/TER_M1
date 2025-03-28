import React, {useState} from "react";
import type {PopupInfoProps} from "~/Types";
import NavBar from "~/components/NavBar";
import PopupInfoPlot from "~/components/PopupInfoPlot";
import PopupInfoSubPlot from "~/components/PopupInfoSubPlot";
import {Offcanvas} from "react-bootstrap";

export default function PopupInfo({subPlot, plot}: PopupInfoProps): React.ReactElement {

    const show: boolean = plot || subPlot;

    const [tabIndex, setTabIndex] = useState<number>(0);

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
                    <Offcanvas.Title>{plot ? `Informations du plot ${plot}` : `Informations du sous-plot ${subPlot}`}</Offcanvas.Title>
                </Offcanvas.Header>
                <NavBar tabIndex={tabIndex} setTabIndex={setTabIndex} />
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