import React, {type ChangeEventHandler, type ReactElement} from "react";
import {Col, Form, Row} from "react-bootstrap";

/**
 * @description SearchBar to use in every case needed to search something
 * @param handleChange
 * @param value
 * @returns {JSX.Element}
 */
export function SearchBar({handleChange, value}: {handleChange: ChangeEventHandler, value: string}): ReactElement {
    return (
        <>
            <Form>
                <Row>
                    <Col xs="auto">
                        <Form.Control
                            type="text"
                            placeholder="Rechercher"
                            className=" mr-sm-2"
                            onChange={handleChange}
                            value={value}
                        />
                    </Col>
                </Row>
            </Form>
        </>
    );
}

const searchBar = React.memo(SearchBar);

export default SearchBar;