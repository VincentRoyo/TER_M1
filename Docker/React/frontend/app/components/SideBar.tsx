import React, {type BaseSyntheticEvent, type ReactElement, useState} from "react";
import {Button, Collapse, ListGroup, Offcanvas} from "react-bootstrap";
import type {PlotLocation, SideBarProps, SubPlot} from "~/Types";
import SearchBar from "~/components/SearchBar";
import {sortNamePlot, sortNameSubPlot} from "~/utils";

export default function SideBar(props: SideBarProps): ReactElement {

    const [selected, setSelected] = useState<string>("");
    const [plotOpen, setPlotOpen] = useState<PlotLocation | null>(null);

    const [elements, setElements] = useState<PlotLocation[]>(props.elements);
    const [initialSubElements, setInitialSubElements] = useState<SubPlot[]>([]);
    const [subElements, setSubElements] = useState<SubPlot[]>([]);

    const [valueSearchBar, setValueSearchBar] = useState<string>("");

    const [show, setShow] = useState(false);

    const handleClose = () => setShow(false);
    const handleShow = () => setShow(true);

    function handleChangeSearchBar(element: BaseSyntheticEvent) {
        const value: string = element.target.value;
        setValueSearchBar(value)

        if (value !== "") {
            const filtered = props.elements.filter(element => element.plot_id.toLowerCase().trim().includes(value.toLowerCase().trim()));

            if (plotOpen) {
                if (!filtered.find(element => element.plot_id === plotOpen.plot_id)) {
                    filtered.push(plotOpen);
                }
                const subFiltered: SubPlot[] = initialSubElements.filter(element => element.idSubPlot.toString().includes(value)).sort(sortNameSubPlot);
                setSubElements(subFiltered);
            }
            filtered.sort(sortNamePlot)
            setElements(filtered);
        } else {
            setElements(props.elements);
            setSubElements(initialSubElements);
        }
    }

    return (
        <>
            <Button variant="primary" onClick={handleShow} className="m-3"
                    style={{position: "absolute", top: 20, left: 20, zIndex: 1000}}>
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
                            <div key={index}>
                                <ListGroup.Item
                                    action
                                    active={selected === item.plot_id}
                                    onClick={() => {
                                        setSelected(item.plot_id);
                                        setPlotOpen(item)
                                        setInitialSubElements(item.sub_plots)
                                        setSubElements(item.sub_plots)
                                        props.handleClickPlot(item)
                                    }}
                                >
                                    {item.plot_id}
                                </ListGroup.Item>

                                <Collapse in={plotOpen?.plot_id === item.plot_id}>
                                    <div className="bg-secondary bg-opacity-25 ps-4 border-start border-2 border-dark">
                                        <ListGroup variant="flush">
                                            {subElements.map((subPlot, subIndex) => (
                                                <ListGroup.Item action
                                                                active={selected === subPlot.idSubPlot.toString()}
                                                                key={`${item.plot_id}-${subIndex}`}
                                                                onClick={() => {
                                                                    setSelected(subPlot.idSubPlot.toString());
                                                                    props.handleClickSubPlot(subPlot);
                                                                }}
                                                                className={`${selected === subPlot.idSubPlot.toString() ? '' : 'bg-transparent'}`}>
                                                    {subPlot.idSubPlot}
                                                </ListGroup.Item>
                                            ))}
                                        </ListGroup>
                                    </div>
                                </Collapse>
                            </div>
                        ))}
                    </ListGroup>
                </Offcanvas.Body>
            </Offcanvas>
        </>
    )
}