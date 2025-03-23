import React, { useState } from "react";
import { Navbar, Nav, Container } from "react-bootstrap";
import type {TabProps} from "~/Types";

export default function NavBar({ tabIndex, setTabIndex }: TabProps): React.ReactElement {

    return (
        <Navbar expand="lg" className="bg-body-tertiary">
            <Container>
                <Nav className="w-100 d-flex justify-content-evenly">
                    {["Général", "Diversité", "Densité"].map((item, index) => (
                        <Nav.Link
                            key={index}
                            style={tabIndex === index ? { borderBottom: "3px solid dodgerblue", fontWeight: "bold" } : {}}
                            onClick={() => setTabIndex(index)}
                        >
                            {item}
                        </Nav.Link>
                    ))}
                </Nav>
            </Container>
        </Navbar>
    );
}
