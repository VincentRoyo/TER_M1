import React, {type BaseSyntheticEvent, type ReactElement, useState} from "react";
import {Button, ListGroup, Offcanvas} from "react-bootstrap";
import type {SideBarProps} from "~/Types";
import SearchBar from "~/components/SearchBar";
import {sortNamePlot} from "~/utils";

export default function SideBar(props: SideBarProps): ReactElement {

    const [selected, setSelected] = useState<number|null>(null);
    const [elements, setElements] = useState<string[]>(props.elements.sort(sortNamePlot));

    const [valueSearchBar, setValueSearchBar] = useState<string>("");

    const [show, setShow] = useState(false);

    const handleClose = () => setShow(false);
    const handleShow = () => setShow(true);

    function handleChangeSearchBar(element : BaseSyntheticEvent) {
        const value: string = element.target.value;
        setValueSearchBar(value)

        if (value !== "") {
            const filtered = props.elements.filter(element => element.toLowerCase().trim().includes(value.toLowerCase().trim())).sort(sortNamePlot)
            setElements(filtered);
        } else {
            setElements(props.elements);
        }
    }

    return (
        <>
            <Button variant="primary" onClick={handleShow} className="m-3" style={{ position: "absolute", top: 20, left: 20, zIndex: 1000 }} >
                ☰ Afficher carte
            </Button>

            <Offcanvas show={show} onHide={handleClose} backdrop={false}>
                <Offcanvas.Header closeButton className="d-flex" style={{gap: "5vh"}}>
                    <Offcanvas.Title>Plots</Offcanvas.Title>
                    <SearchBar handleChange={handleChangeSearchBar} value={valueSearchBar}/>
                </Offcanvas.Header>
                <Offcanvas.Body className="p-0">
                    <ListGroup variant="flush">
                        {elements.map((item, index) => (
                            <ListGroup.Item
                                key={index}
                                action
                                active={selected === index}
                                onClick={() => {
                                    setSelected(index)
                                    props.handleClickPlot(item)
                                }}
                            >
                                {item}
                            </ListGroup.Item>
                        ))}
                    </ListGroup>
                </Offcanvas.Body>
            </Offcanvas>
        </>
    )
}