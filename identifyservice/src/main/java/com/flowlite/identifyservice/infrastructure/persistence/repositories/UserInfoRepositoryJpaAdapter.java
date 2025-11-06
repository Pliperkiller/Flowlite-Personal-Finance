package com.flowlite.identifyservice.infrastructure.persistence.repositories;

import com.flowlite.identifyservice.domain.entities.UserInfo;
import com.flowlite.identifyservice.domain.repositories.UserInfoRepository;
import com.flowlite.identifyservice.infrastructure.persistence.mappers.UserInfoMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;

@Repository
@RequiredArgsConstructor
public class UserInfoRepositoryJpaAdapter implements UserInfoRepository {

    private final JpaUserInfoRepository jpaUserInfoRepository;

    @Override
    public Optional<UserInfo> findById(UUID id) {
        return jpaUserInfoRepository.findById(id)
                .map(UserInfoMapper::toDomain);
    }

    @Override
    public Optional<UserInfo> findByUserId(UUID userId) {
        return jpaUserInfoRepository.findByIdUser(userId)
                .map(UserInfoMapper::toDomain);
    }

    @Override
    public Optional<UserInfo> findByNumeroIdentificacion(String numeroIdentificacion) {
        return jpaUserInfoRepository.findByNumeroIdentificacion(numeroIdentificacion)
                .map(UserInfoMapper::toDomain);
    }

    @Override
    public Optional<UserInfo> findByTelefono(String telefono) {
        return jpaUserInfoRepository.findByTelefono(telefono)
                .map(UserInfoMapper::toDomain);
    }

    @Override
    public List<UserInfo> findByNombreCompleto(String primerNombre, String segundoNombre, 
                                             String primerApellido, String segundoApellido) {
        return jpaUserInfoRepository.findByPrimerNombreAndSegundoNombreAndPrimerApellidoAndSegundoApellido(
                primerNombre, segundoNombre, primerApellido, segundoApellido)
                .stream()
                .map(UserInfoMapper::toDomain)
                .collect(Collectors.toList());
    }

    @Override
    public List<UserInfo> findByPrimerNombre(String primerNombre) {
        return jpaUserInfoRepository.findByPrimerNombre(primerNombre)
                .stream()
                .map(UserInfoMapper::toDomain)
                .collect(Collectors.toList());
    }

    @Override
    public List<UserInfo> findByPrimerApellido(String primerApellido) {
        return jpaUserInfoRepository.findByPrimerApellido(primerApellido)
                .stream()
                .map(UserInfoMapper::toDomain)
                .collect(Collectors.toList());
    }

    @Override
    public List<UserInfo> findByCiudad(String ciudad) {
        return jpaUserInfoRepository.findByCiudad(ciudad)
                .stream()
                .map(UserInfoMapper::toDomain)
                .collect(Collectors.toList());
    }

    @Override
    public List<UserInfo> findByDepartamento(String departamento) {
        return jpaUserInfoRepository.findByDepartamento(departamento)
                .stream()
                .map(UserInfoMapper::toDomain)
                .collect(Collectors.toList());
    }

    @Override
    public List<UserInfo> findUsersWithCompleteInfo() {
        return jpaUserInfoRepository.findUsersWithCompleteInfo()
                .stream()
                .map(UserInfoMapper::toDomain)
                .collect(Collectors.toList());
    }

    @Override
    public List<UserInfo> findActiveUsers() {
        // La tabla actual no tiene columna 'activo', retornar todos los usuarios
        return jpaUserInfoRepository.findAll()
                .stream()
                .map(UserInfoMapper::toDomain)
                .collect(Collectors.toList());
    }

    @Override
    public UserInfo save(UserInfo userInfo) {
        var entity = UserInfoMapper.toEntity(userInfo);
        var saved = jpaUserInfoRepository.save(entity);
        return UserInfoMapper.toDomain(saved);
    }

    @Override
    public void deleteById(UUID id) {
        jpaUserInfoRepository.deleteById(id);
    }

    @Override
    public void deleteByUserId(UUID userId) {
        jpaUserInfoRepository.findByIdUser(userId)
                .ifPresent(entity -> jpaUserInfoRepository.deleteById(entity.getIdUser()));
    }

    @Override
    public boolean existsByUserId(UUID userId) {
        return jpaUserInfoRepository.existsByIdUser(userId);
    }

    @Override
    public boolean existsByNumeroIdentificacion(String numeroIdentificacion) {
        return jpaUserInfoRepository.existsByNumeroIdentificacion(numeroIdentificacion);
    }

    @Override
    public boolean existsByTelefono(String telefono) {
        return jpaUserInfoRepository.existsByTelefono(telefono);
    }
}
