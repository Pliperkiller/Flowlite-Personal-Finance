package com.flowlite.identifyservice.domain.valueobjects;

import lombok.Value;

@Value
public class Username {

    String value;

    public Username(String value) {
        if (value == null || value.length() < 3) {
            throw new IllegalArgumentException("El nombre de usuario debe tener al menos 3 caracteres");
        }
        this.value = value;
    }

}
