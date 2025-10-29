package com.flowlite.identifyservice.domain.repositories;

import com.flowlite.identifyservice.domain.entities.UserInfo;
import lombok.NonNull;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Repositorio para la gestión de información personal de usuarios
 */
public interface UserInfoRepository {

    /**
     * Busca información de usuario por su ID
     */
    Optional<UserInfo> findById(@NonNull UUID id);
    
    /**
     * Busca información de usuario por el ID del usuario asociado
     */
    Optional<UserInfo> findByUserId(@NonNull UUID userId);
    
    /**
     * Busca información de usuario por número de identificación
     */
    Optional<UserInfo> findByNumeroIdentificacion(@NonNull String numeroIdentificacion);
    
    /**
     * Busca información de usuario por teléfono
     */
    Optional<UserInfo> findByTelefono(@NonNull String telefono);
    
    /**
     * Busca información de usuario por nombre completo
     */
    List<UserInfo> findByNombreCompleto(@NonNull String primerNombre, String segundoNombre, 
                                      @NonNull String primerApellido, String segundoApellido);
    
    /**
     * Busca información de usuario por primer nombre
     */
    List<UserInfo> findByPrimerNombre(@NonNull String primerNombre);
    
    /**
     * Busca información de usuario por primer apellido
     */
    List<UserInfo> findByPrimerApellido(@NonNull String primerApellido);
    
    /**
     * Busca información de usuario por ciudad
     */
    List<UserInfo> findByCiudad(@NonNull String ciudad);
    
    /**
     * Busca información de usuario por departamento
     */
    List<UserInfo> findByDepartamento(@NonNull String departamento);
    
    /**
     * Busca todos los usuarios con información completa
     */
    List<UserInfo> findUsersWithCompleteInfo();
    
    /**
     * Busca todos los usuarios activos
     */
    List<UserInfo> findActiveUsers();
    
    /**
     * Guarda o actualiza información de usuario
     */
    UserInfo save(@NonNull UserInfo userInfo);
    
    /**
     * Elimina información de usuario por ID
     */
    void deleteById(@NonNull UUID id);
    
    /**
     * Elimina información de usuario por ID de usuario
     */
    void deleteByUserId(@NonNull UUID userId);
    
    /**
     * Verifica si existe información para un usuario
     */
    boolean existsByUserId(@NonNull UUID userId);
    
    /**
     * Verifica si existe información con un número de identificación
     */
    boolean existsByNumeroIdentificacion(@NonNull String numeroIdentificacion);
    
    /**
     * Verifica si existe información con un teléfono
     */
    boolean existsByTelefono(@NonNull String telefono);
}
