package com.flowlite.identifyservice.domain.valueobjects;

import lombok.Value;

import java.util.regex.Pattern;

@Value
public class Email {

    String value;

    public Email(String value) {
        if (value == null || !Pattern.matches("^[\\w-\\.]+@([\\w-]+\\.)+[\\w-]{2,4}$", value)) {
            throw new IllegalArgumentException("Email inválido");
        }
        this.value = value.toLowerCase();
    }

}
