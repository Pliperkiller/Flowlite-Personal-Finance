package com.flowlite.identifyservice.infrastructure.controllers;

import com.flowlite.identifyservice.application.dto.*;
import com.flowlite.identifyservice.application.services.TermsService;
import com.flowlite.identifyservice.domain.entities.TermsVersion;
import com.flowlite.identifyservice.domain.entities.UserTermsAcceptance;
import com.flowlite.identifyservice.domain.valueobjects.AcceptanceType;
import com.flowlite.identifyservice.infrastructure.security.jwt.JwtTokenProvider;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;
import java.util.stream.Collectors;

/**
 * Controller for managing Terms and Conditions versioning
 */
@RestController
@RequestMapping("/terms")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "Terms & Conditions", description = "Endpoints for managing terms and conditions acceptance")
public class TermsController {

    private final TermsService termsService;
    private final JwtTokenProvider jwtTokenProvider;

    @GetMapping("/current")
    @Operation(
        summary = "Get current active terms version",
        description = "Returns the currently active terms and conditions or privacy policy"
    )
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Terms version retrieved successfully"),
        @ApiResponse(responseCode = "404", description = "No active terms found")
    })
    public ResponseEntity<?> getCurrentTerms(
            @RequestParam(defaultValue = "TERMS_OF_SERVICE")
            @Parameter(description = "Type of terms: TERMS_OF_SERVICE or PRIVACY_POLICY")
            String type) {

        log.info("Fetching current terms for type: {}", type);

        Optional<TermsVersion> currentTerms = termsService.getCurrentTermsVersion(type);

        if (currentTerms.isEmpty()) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(Map.of("message", "No active terms found for type: " + type));
        }

        TermsVersionResponse response = TermsDtoMapper.toTermsVersionResponse(currentTerms.get());
        return ResponseEntity.ok(response);
    }

    @GetMapping("/{versionId}")
    @Operation(
        summary = "Get specific terms version by ID",
        description = "Returns a specific terms version"
    )
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Terms version retrieved successfully"),
        @ApiResponse(responseCode = "404", description = "Terms version not found")
    })
    public ResponseEntity<?> getTermsVersion(@PathVariable UUID versionId) {
        log.info("Fetching terms version: {}", versionId);

        Optional<TermsVersion> terms = termsService.getTermsVersion(versionId);

        if (terms.isEmpty()) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(Map.of("message", "Terms version not found"));
        }

        TermsVersionResponse response = TermsDtoMapper.toTermsVersionResponse(terms.get());
        return ResponseEntity.ok(response);
    }

    @GetMapping("/history")
    @Operation(
        summary = "Get terms version history",
        description = "Returns all versions for a specific terms type"
    )
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "History retrieved successfully")
    })
    public ResponseEntity<?> getTermsHistory(
            @RequestParam(defaultValue = "TERMS_OF_SERVICE")
            @Parameter(description = "Type of terms")
            String type) {

        log.info("Fetching terms history for type: {}", type);

        List<TermsVersion> history = termsService.getTermsHistory(type);
        List<TermsVersionResponse> response = history.stream()
                .map(TermsDtoMapper::toTermsVersionResponse)
                .collect(Collectors.toList());

        return ResponseEntity.ok(response);
    }

    @PostMapping("/accept")
    @SecurityRequirement(name = "Bearer Authentication")
    @Operation(
        summary = "Accept terms and conditions",
        description = "Records user's acceptance of a specific terms version. Requires JWT authentication."
    )
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Terms accepted successfully"),
        @ApiResponse(responseCode = "400", description = "Invalid terms version or already accepted"),
        @ApiResponse(responseCode = "401", description = "Unauthorized - Invalid or missing JWT token")
    })
    public ResponseEntity<?> acceptTerms(
            @Valid @RequestBody AcceptTermsRequest request,
            @RequestHeader("Authorization") String authHeader,
            HttpServletRequest httpRequest) {

        // Extract user ID from JWT token
        String token = authHeader.replace("Bearer ", "");
        UUID userId = jwtTokenProvider.getUserIdFromToken(token);

        log.info("User {} accepting terms version {}", userId, request.getTermsVersionId());

        try {
            // Capture IP and User Agent if not provided
            String ipAddress = request.getIpAddress() != null ?
                request.getIpAddress() : httpRequest.getRemoteAddr();
            String userAgent = request.getUserAgent() != null ?
                request.getUserAgent() : httpRequest.getHeader("User-Agent");
            String acceptanceMethod = request.getAcceptanceMethod() != null ?
                request.getAcceptanceMethod() : "WEB";

            UserTermsAcceptance acceptance = termsService.acceptTerms(
                    userId,
                    request.getTermsVersionId(),
                    AcceptanceType.INITIAL_SIGNUP, // Can be parameterized
                    ipAddress,
                    userAgent,
                    acceptanceMethod,
                    request.getAcceptedFromCountry(),
                    request.getAcceptedFromCity()
            );

            // Get version number for response
            Optional<TermsVersion> termsVersion = termsService.getTermsVersion(request.getTermsVersionId());
            String versionNumber = termsVersion.map(TermsVersion::getVersionNumber).orElse(null);

            TermsAcceptanceResponse response = TermsDtoMapper.toTermsAcceptanceResponse(acceptance, versionNumber);

            return ResponseEntity.ok(Map.of(
                    "message", "Terms accepted successfully",
                    "acceptance", response
            ));

        } catch (IllegalArgumentException e) {
            log.error("Error accepting terms: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(Map.of("error", e.getMessage()));
        }
    }

    @GetMapping("/status")
    @SecurityRequirement(name = "Bearer Authentication")
    @Operation(
        summary = "Check user's terms acceptance status",
        description = "Returns whether the authenticated user needs to accept new terms. Requires JWT authentication."
    )
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Status retrieved successfully"),
        @ApiResponse(responseCode = "401", description = "Unauthorized - Invalid or missing JWT token")
    })
    public ResponseEntity<?> getTermsStatus(
            @RequestParam(defaultValue = "TERMS_OF_SERVICE")
            @Parameter(description = "Type of terms")
            String type,
            @RequestHeader("Authorization") String authHeader) {

        // Extract user ID from JWT token
        String token = authHeader.replace("Bearer ", "");
        UUID userId = jwtTokenProvider.getUserIdFromToken(token);

        log.info("Checking terms status for user {} and type {}", userId, type);

        // Get current active version
        Optional<TermsVersion> currentVersion = termsService.getCurrentTermsVersion(type);

        // Get user's latest acceptance
        Optional<UserTermsAcceptance> acceptance = termsService.getUserLatestAcceptance(userId, type);

        if (currentVersion.isEmpty()) {
            return ResponseEntity.ok(Map.of(
                    "message", "No active terms available",
                    "needsAcceptance", false
            ));
        }

        TermsStatusResponse statusResponse = TermsDtoMapper.toTermsStatusResponse(
                userId,
                currentVersion.get(),
                acceptance.orElse(null)
        );

        return ResponseEntity.ok(statusResponse);
    }

    @GetMapping("/acceptance/history")
    @SecurityRequirement(name = "Bearer Authentication")
    @Operation(
        summary = "Get user's acceptance history",
        description = "Returns all terms acceptances for the authenticated user. Requires JWT authentication."
    )
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "History retrieved successfully"),
        @ApiResponse(responseCode = "401", description = "Unauthorized - Invalid or missing JWT token")
    })
    public ResponseEntity<?> getAcceptanceHistory(@RequestHeader("Authorization") String authHeader) {

        // Extract user ID from JWT token
        String token = authHeader.replace("Bearer ", "");
        UUID userId = jwtTokenProvider.getUserIdFromToken(token);

        log.info("Fetching acceptance history for user {}", userId);

        List<UserTermsAcceptance> acceptances = termsService.getUserAcceptanceHistory(userId);

        List<TermsAcceptanceResponse> response = acceptances.stream()
                .map(acc -> {
                    Optional<TermsVersion> version = termsService.getTermsVersion(acc.getTermsVersionId());
                    String versionNumber = version.map(TermsVersion::getVersionNumber).orElse("Unknown");
                    return TermsDtoMapper.toTermsAcceptanceResponse(acc, versionNumber);
                })
                .collect(Collectors.toList());

        return ResponseEntity.ok(response);
    }

    // Admin endpoints (would require admin role check in production)

    @PostMapping("/admin/create")
    @SecurityRequirement(name = "Bearer Authentication")
    @Operation(
        summary = "[ADMIN] Create new terms version",
        description = "Creates a new terms version in DRAFT status. Admin only."
    )
    @ApiResponses(value = {
        @ApiResponse(responseCode = "201", description = "Terms version created successfully"),
        @ApiResponse(responseCode = "400", description = "Invalid request or version already exists"),
        @ApiResponse(responseCode = "401", description = "Unauthorized")
    })
    public ResponseEntity<?> createTermsVersion(@Valid @RequestBody CreateTermsVersionRequest request) {
        log.info("Creating new terms version: {}", request.getVersionNumber());

        try {
            TermsVersion termsVersion = TermsDtoMapper.toTermsVersion(request);
            TermsVersion created = termsService.createTermsVersion(termsVersion);
            TermsVersionResponse response = TermsDtoMapper.toTermsVersionResponse(created);

            return ResponseEntity.status(HttpStatus.CREATED)
                    .body(Map.of(
                            "message", "Terms version created successfully",
                            "termsVersion", response
                    ));

        } catch (IllegalArgumentException e) {
            log.error("Error creating terms version: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(Map.of("error", e.getMessage()));
        }
    }

    @PostMapping("/admin/publish/{versionId}")
    @SecurityRequirement(name = "Bearer Authentication")
    @Operation(
        summary = "[ADMIN] Publish terms version",
        description = "Activates a terms version and supersedes the current one. Admin only."
    )
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Terms version published successfully"),
        @ApiResponse(responseCode = "400", description = "Invalid version ID"),
        @ApiResponse(responseCode = "401", description = "Unauthorized")
    })
    public ResponseEntity<?> publishTermsVersion(@PathVariable UUID versionId) {
        log.info("Publishing terms version: {}", versionId);

        try {
            TermsVersion published = termsService.publishTermsVersion(versionId);
            TermsVersionResponse response = TermsDtoMapper.toTermsVersionResponse(published);

            return ResponseEntity.ok(Map.of(
                    "message", "Terms version published successfully",
                    "termsVersion", response
            ));

        } catch (IllegalArgumentException | IllegalStateException e) {
            log.error("Error publishing terms version: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(Map.of("error", e.getMessage()));
        }
    }

    @GetMapping("/admin/stats/{versionId}")
    @SecurityRequirement(name = "Bearer Authentication")
    @Operation(
        summary = "[ADMIN] Get acceptance statistics",
        description = "Returns statistics for a terms version. Admin only."
    )
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Statistics retrieved successfully"),
        @ApiResponse(responseCode = "401", description = "Unauthorized")
    })
    public ResponseEntity<?> getAcceptanceStats(@PathVariable UUID versionId) {
        log.info("Fetching acceptance stats for version: {}", versionId);

        long acceptanceCount = termsService.getAcceptanceCount(versionId);

        return ResponseEntity.ok(Map.of(
                "termsVersionId", versionId,
                "totalAcceptances", acceptanceCount
        ));
    }
}
