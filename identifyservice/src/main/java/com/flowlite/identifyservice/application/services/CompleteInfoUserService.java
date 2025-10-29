package com.flowlite.identifyservice.application.services;

import com.flowlite.identifyservice.domain.entities.UserInfo;
import com.flowlite.identifyservice.domain.repositories.UserInfoRepository;
import com.flowlite.identifyservice.domain.valueobjects.IdentificationType;
import lombok.*;
import lombok.experimental.FieldDefaults;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Servicio para gestionar la información completa de usuarios
 */
@Service
@RequiredArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
@Slf4j
public class CompleteInfoUserService {

    UserInfoRepository userInfoRepository;

    /**
     * Crea o actualiza la información personal de un usuario
     */
    @Transactional
    public UserInfo saveUserInfo(@NonNull UUID userId, @NonNull String primerNombre, String segundoNombre, 
                               @NonNull String primerApellido, String segundoApellido, @NonNull String telefono,
                               String direccion, String ciudad, String departamento, String pais,
                               LocalDate fechaNacimiento, @NonNull String numeroIdentificacion,
                               @NonNull IdentificationType tipoIdentificacion, String genero,
                               String estadoCivil, String ocupacion) {
        
        // Verificar si ya existe información para este usuario
        Optional<UserInfo> existingInfo = userInfoRepository.findByUserId(userId);
        
        UserInfo userInfo;
        if (existingInfo.isPresent()) {
            // Actualizar información existente
            userInfo = existingInfo.get();
            userInfo.actualizarInformacion(primerNombre, segundoNombre, primerApellido, 
                                         segundoApellido, telefono, direccion, ciudad, departamento);
            userInfo.actualizarIdentificacion(numeroIdentificacion, tipoIdentificacion);
            
            // Actualizar campos adicionales
            userInfo.setGenero(genero);
            userInfo.setEstadoCivil(estadoCivil);
            userInfo.setOcupacion(ocupacion);
            userInfo.setPais(pais);
            userInfo.setFechaNacimiento(fechaNacimiento);
        } else {
            // Crear nueva información
            userInfo = UserInfo.builder()
                    .id(UUID.randomUUID())
                    .userId(userId)
                    .primerNombre(primerNombre)
                    .segundoNombre(segundoNombre)
                    .primerApellido(primerApellido)
                    .segundoApellido(segundoApellido)
                    .telefono(telefono)
                    .direccion(direccion)
                    .ciudad(ciudad)
                    .departamento(departamento)
                    .pais(pais)
                    .fechaNacimiento(fechaNacimiento)
                    .numeroIdentificacion(numeroIdentificacion)
                    .tipoIdentificacion(tipoIdentificacion)
                    .genero(genero)
                    .estadoCivil(estadoCivil)
                    .ocupacion(ocupacion)
                    .createdAt(LocalDateTime.now())
                    .updatedAt(LocalDateTime.now())
                    .activo(true)
                    .build();
        }
        
        return userInfoRepository.save(userInfo);
    }

    /**
     * Obtiene la información personal de un usuario
     */
    public Optional<UserInfo> getUserInfo(@NonNull UUID userId) {
        return userInfoRepository.findByUserId(userId);
    }

    /**
     * Obtiene la información personal por ID
     */
    public Optional<UserInfo> getUserInfoById(@NonNull UUID userInfoId) {
        return userInfoRepository.findById(userInfoId);
    }

    /**
     * Busca usuarios por nombre completo
     */
    public List<UserInfo> searchByFullName(@NonNull String primerNombre, String segundoNombre, 
                                          @NonNull String primerApellido, String segundoApellido) {
        return userInfoRepository.findByNombreCompleto(primerNombre, segundoNombre, 
                                                     primerApellido, segundoApellido);
    }

    /**
     * Busca usuarios por primer nombre
     */
    public List<UserInfo> searchByFirstName(@NonNull String primerNombre) {
        return userInfoRepository.findByPrimerNombre(primerNombre);
    }

    /**
     * Busca usuarios por primer apellido
     */
    public List<UserInfo> searchByLastName(@NonNull String primerApellido) {
        return userInfoRepository.findByPrimerApellido(primerApellido);
    }

    /**
     * Busca usuarios por ciudad
     */
    public List<UserInfo> searchByCity(@NonNull String ciudad) {
        return userInfoRepository.findByCiudad(ciudad);
    }

    /**
     * Busca usuarios por departamento
     */
    public List<UserInfo> searchByDepartment(@NonNull String departamento) {
        return userInfoRepository.findByDepartamento(departamento);
    }

    /**
     * Obtiene todos los usuarios con información completa
     */
    public List<UserInfo> getUsersWithCompleteInfo() {
        return userInfoRepository.findUsersWithCompleteInfo();
    }

    /**
     * Obtiene todos los usuarios activos
     */
    public List<UserInfo> getActiveUsers() {
        return userInfoRepository.findActiveUsers();
    }

    /**
     * Verifica si un usuario tiene información personal
     */
    public boolean hasUserInfo(@NonNull UUID userId) {
        return userInfoRepository.existsByUserId(userId);
    }

    /**
     * Verifica si un número de identificación ya está en uso
     */
    public boolean isIdentificationInUse(@NonNull String numeroIdentificacion) {
        return userInfoRepository.existsByNumeroIdentificacion(numeroIdentificacion);
    }

    /**
     * Verifica si un teléfono ya está en uso
     */
    public boolean isPhoneInUse(@NonNull String telefono) {
        return userInfoRepository.existsByTelefono(telefono);
    }

    /**
     * Desactiva la información personal de un usuario
     */
    @Transactional
    public void deactivateUserInfo(@NonNull UUID userId) {
        userInfoRepository.findByUserId(userId)
                .ifPresent(userInfo -> {
                    userInfo.desactivar();
                    userInfoRepository.save(userInfo);
                });
    }

    /**
     * Activa la información personal de un usuario
     */
    @Transactional
    public void activateUserInfo(@NonNull UUID userId) {
        userInfoRepository.findByUserId(userId)
                .ifPresent(userInfo -> {
                    userInfo.activar();
                    userInfoRepository.save(userInfo);
                });
    }

    /**
     * Elimina la información personal de un usuario
     */
    @Transactional
    public void deleteUserInfo(@NonNull UUID userId) {
        userInfoRepository.deleteByUserId(userId);
    }

    /**
     * Elimina la información personal por ID
     */
    @Transactional
    public void deleteUserInfoById(@NonNull UUID userInfoId) {
        userInfoRepository.deleteById(userInfoId);
    }

    /**
     * Valida si la información personal está completa
     */
    public boolean isUserInfoComplete(@NonNull UUID userId) {
        return userInfoRepository.findByUserId(userId)
                .map(UserInfo::tieneInformacionCompleta)
                .orElse(false);
    }
}
