package com.flowlite.identifyservice.infrastructure.dtos;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PreregisterResponse {
    private String message;
    private String status;
    private String email;
    private String note;
}


