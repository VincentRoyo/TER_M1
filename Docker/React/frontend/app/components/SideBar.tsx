import React, {type BaseSyntheticEvent, type ReactElement, useEffect, useState} from "react";
import {Accordion, Button, Collapse, ListGroup, Offcanvas} from "react-bootstrap";
import type {PlotLocation, SideBarProps, SubPlot} from "~/Types";
import SearchBar from "~/components/SearchBar";
import {sortNamePlot, sortNameSubPlot} from "~/utils";

export default function SideBar(props: SideBarProps): ReactElement {

    const [selected, setSelected] = useState<string>("");
    const [selectedSubPlot, setSelectedSubPlot] = useState<string>("");
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

    useEffect(() => {
        if (props.selectedPlot) {
            const selectedPlot: PlotLocation | undefined = props.elements.find(el => el.plot_id === props.selectedPlot);

            if (selectedPlot) {
                setPlotOpen(selectedPlot);
                setInitialSubElements(selectedPlot.sub_plots);
                setSubElements(selectedPlot.sub_plots);
            }

            if (props.selectedSubPlot && selectedPlot) {
                const selectedSubPlot: SubPlot | undefined = selectedPlot?.sub_plots.find(el => el.idSubPlot.toString() === props.selectedSubPlot?.toString());
                if (selectedSubPlot) {
                    props.handleClickSubPlot(selectedPlot, selectedSubPlot);
                    setSelectedSubPlot(props.selectedSubPlot.toString());
                    setSelected(props.selectedPlot);
                }
            } else if (selectedPlot) {
                props.handleClickPlot(selectedPlot);
                setSelected(props.selectedPlot.toString());
                setSelectedSubPlot("");
            }

            setShow(true);
        }
    }, [props.selectedPlot, props.selectedSubPlot]);

    return (
        <>
            <Button variant={"light"} onClick={handleShow} className="m-3"
                    style={{position: "absolute", top: 20, left: 20, zIndex: 1000, borderRadius: "50%" }}>
                <i className="bi bi-search fs-4"></i>
            </Button>

            <Offcanvas show={show} onHide={handleClose} backdrop={false} style={{ border: "none" }}>
                <Offcanvas.Header closeButton className="d-flex" style={{ gap: "5vh" }}>
                    <Offcanvas.Title>Plots</Offcanvas.Title>
                    <SearchBar handleChange={handleChangeSearchBar} value={valueSearchBar} />
                </Offcanvas.Header>

                <Offcanvas.Body className="p-0">
                    <Accordion activeKey={selected}>
                        {elements.map((item, index) => (
                            <Accordion.Item eventKey={item.plot_id} key={index}>
                                <Accordion.Header
                                    onClick={() => {
                                        if (selected === item.plot_id) {
                                            setSelected("");
                                            setSelectedSubPlot("");
                                            setPlotOpen(null);
                                            setSubElements([]);
                                        } else {
                                            setSelected(item.plot_id);
                                            setPlotOpen(item);
                                            setInitialSubElements(item.sub_plots);
                                            setSubElements(item.sub_plots);
                                            props.handleClickPlot(item);
                                        }
                                    }}
                                    className={`${
                                        selected === item.plot_id ? 'bg-primary text-white' : ''
                                    }`}
                                >
                                    {item.plot_id}
                                </Accordion.Header>

                                <Accordion.Body>
                                    <ListGroup variant="flush">
                                        {subElements.map((subPlot, subIndex) => (
                                            <ListGroup.Item
                                                key={`${item.plot_id}-${subIndex}`}
                                                action
                                                active={selectedSubPlot === subPlot.idSubPlot.toString()}
                                                onClick={() => {
                                                    setSelectedSubPlot(subPlot.idSubPlot.toString());
                                                    props.handleClickSubPlot(item, subPlot);
                                                }}
                                                className={`${
                                                    selectedSubPlot === subPlot.idSubPlot.toString() ? '' : 'bg-transparent'
                                                }`}
                                            >
                                                {subPlot.idSubPlot}
                                            </ListGroup.Item>
                                        ))}
                                    </ListGroup>
                                </Accordion.Body>
                            </Accordion.Item>
                        ))}
                    </Accordion>
                </Offcanvas.Body>
            </Offcanvas>
        </>
    )
}