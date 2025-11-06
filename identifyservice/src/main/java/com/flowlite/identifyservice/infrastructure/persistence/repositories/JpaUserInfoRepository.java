package com.flowlite.identifyservice.infrastructure.persistence.repositories;

import com.flowlite.identifyservice.infrastructure.persistence.entities.UserInfoEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface JpaUserInfoRepository extends JpaRepository<UserInfoEntity, UUID> {

    Optional<UserInfoEntity> findByIdUser(UUID idUser);

    Optional<UserInfoEntity> findByNumeroIdentificacion(String numeroIdentificacion);

    Optional<UserInfoEntity> findByTelefono(String telefono);

    List<UserInfoEntity> findByPrimerNombreAndSegundoNombreAndPrimerApellidoAndSegundoApellido(
        String primerNombre, String segundoNombre, String primerApellido, String segundoApellido);

    List<UserInfoEntity> findByPrimerNombre(String primerNombre);

    List<UserInfoEntity> findByPrimerApellido(String primerApellido);

    List<UserInfoEntity> findByCiudad(String ciudad);

    List<UserInfoEntity> findByDepartamento(String departamento);

    @Query("SELECT u FROM UserInfoEntity u WHERE u.primerNombre IS NOT NULL AND u.primerNombre != '' " +
           "AND u.primerApellido IS NOT NULL AND u.primerApellido != '' " +
           "AND u.telefono IS NOT NULL AND u.telefono != '' " +
           "AND u.numeroIdentificacion IS NOT NULL AND u.numeroIdentificacion != ''")
    List<UserInfoEntity> findUsersWithCompleteInfo();

    boolean existsByIdUser(UUID idUser);

    boolean existsByNumeroIdentificacion(String numeroIdentificacion);

    boolean existsByTelefono(String telefono);
}
