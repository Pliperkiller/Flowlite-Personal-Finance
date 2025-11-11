package com.flowlite.identifyservice.application.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotNull;
import lombok.*;
import lombok.experimental.FieldDefaults;

import java.util.UUID;

/**
 * DTO for accepting terms and conditions
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
@Schema(description = "Request to accept terms and conditions")
public class AcceptTermsRequest {

    @NotNull(message = "Terms version ID is required")
    @Schema(description = "ID of the terms version being accepted", example = "550e8400-e29b-41d4-a716-446655440000", required = true)
    UUID termsVersionId;

    @Schema(description = "IP address (auto-captured if not provided)", example = "192.168.1.100")
    String ipAddress;

    @Schema(description = "User agent (auto-captured if not provided)", example = "Mozilla/5.0...")
    String userAgent;

    @Schema(description = "Method of acceptance", example = "WEB")
    String acceptanceMethod;

    @Schema(description = "Country from which acceptance was made", example = "Colombia")
    String acceptedFromCountry;

    @Schema(description = "City from which acceptance was made", example = "Bogotá")
    String acceptedFromCity;
}
