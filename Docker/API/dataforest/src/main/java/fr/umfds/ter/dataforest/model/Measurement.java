package fr.umfds.ter.dataforest.model;

import lombok.Data;

@Data
public class Measurement {
    private Census census;
    private Status status;
}
