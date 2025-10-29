package com.flowlite.identifyservice.domain.repositories;

import com.flowlite.identifyservice.domain.entities.VerificationCode;

import java.util.Optional;

/**
 * Repositorio para gestión de códigos de verificación en Redis
 */
public interface VerificationCodeRepository {
    
    /**
     * Guarda un código de verificación en Redis con TTL
     * @param verificationCode Código de verificación a guardar
     * @param ttlSeconds TTL en segundos
     */
    void save(VerificationCode verificationCode, long ttlSeconds);
    
    /**
     * Busca un código de verificación por email y código
     * @param email Email del usuario
     * @param code Código de 6 dígitos
     * @return Código de verificación si existe
     */
    Optional<VerificationCode> findByEmailAndCode(String email, String code);
    
    /**
     * Busca un código de verificación por token
     * @param token Token asociado al código
     * @return Código de verificación si existe
     */
    Optional<VerificationCode> findByToken(String token);
    
    /**
     * Busca un código de verificación por código de 6 dígitos
     * @param code Código de 6 dígitos
     * @return Código de verificación si existe
     */
    Optional<VerificationCode> findByCode(String code);
    
    /**
     * Elimina un código de verificación
     * @param email Email del usuario
     * @param code Código de 6 dígitos
     */
    void delete(String email, String code);
    
    /**
     * Elimina un código de verificación por token
     * @param token Token asociado al código
     */
    void deleteByToken(String token);
    
    /**
     * Verifica si existe un código activo para un email
     * @param email Email del usuario
     * @return true si existe un código activo
     */
    boolean existsActiveCodeForEmail(String email);
    
    /**
     * Obtiene el código activo para un email
     * @param email Email del usuario
     * @return Código activo si existe
     */
    Optional<String> findActiveCodeForEmail(String email);
}
