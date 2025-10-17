package com.flowlite.identifyservice.domain.valueobjects;

import lombok.Value;

@Value
public class Password {

    String value; // hash, nunca la clave en texto plano

    public Password(String value) {
        if (value == null || value.length() < 60) { // ejemplo: bcrypt hash
            throw new IllegalArgumentException("Password inválido o sin hash");
        }
        this.value = value;
    }

}
