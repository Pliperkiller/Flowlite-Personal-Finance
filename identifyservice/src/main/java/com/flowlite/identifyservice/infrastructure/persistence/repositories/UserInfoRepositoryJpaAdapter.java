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
        return jpaUserInfoRepository.findByUserId(userId)
                .map(UserInfoMapper::toDomain);
    }

    @Override
    public Optional<UserInfo> findByIdentificationNumber(String identificationNumber) {
        return jpaUserInfoRepository.findByIdentificationNumber(identificationNumber)
                .map(UserInfoMapper::toDomain);
    }

    @Override
    public Optional<UserInfo> findByPhone(String phone) {
        return jpaUserInfoRepository.findByPhone(phone)
                .map(UserInfoMapper::toDomain);
    }

    @Override
    public List<UserInfo> findByFullName(String firstName, String middleName,
                                         String lastName, String secondLastName) {
        return jpaUserInfoRepository.findByFirstNameAndMiddleNameAndLastNameAndSecondLastName(
                firstName, middleName, lastName, secondLastName)
                .stream()
                .map(UserInfoMapper::toDomain)
                .collect(Collectors.toList());
    }

    @Override
    public List<UserInfo> findByFirstName(String firstName) {
        return jpaUserInfoRepository.findByFirstName(firstName)
                .stream()
                .map(UserInfoMapper::toDomain)
                .collect(Collectors.toList());
    }

    @Override
    public List<UserInfo> findByLastName(String lastName) {
        return jpaUserInfoRepository.findByLastName(lastName)
                .stream()
                .map(UserInfoMapper::toDomain)
                .collect(Collectors.toList());
    }

    @Override
    public List<UserInfo> findByCity(String city) {
        return jpaUserInfoRepository.findByCity(city)
                .stream()
                .map(UserInfoMapper::toDomain)
                .collect(Collectors.toList());
    }

    @Override
    public List<UserInfo> findByState(String state) {
        return jpaUserInfoRepository.findByState(state)
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
        return jpaUserInfoRepository.findAll()
                .stream()
                .map(UserInfoMapper::toDomain)
                .filter(UserInfo::isActive)
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
        jpaUserInfoRepository.findByUserId(userId)
                .ifPresent(entity -> jpaUserInfoRepository.deleteById(entity.getUserId()));
    }

    @Override
    public boolean existsByUserId(UUID userId) {
        return jpaUserInfoRepository.existsByUserId(userId);
    }

    @Override
    public boolean existsByIdentificationNumber(String identificationNumber) {
        return jpaUserInfoRepository.existsByIdentificationNumber(identificationNumber);
    }

    @Override
    public boolean existsByPhone(String phone) {
        return jpaUserInfoRepository.existsByPhone(phone);
    }
}
